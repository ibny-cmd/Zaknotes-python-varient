import pytest
from unittest.mock import MagicMock, patch
import os
import subprocess
from pdf_converter_py import PdfConverter # Import the actual class

@pytest.fixture
def mock_playwright_page():
    return MagicMock()

def test_convert_md_to_html_calls_pandoc(tmp_path):
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test")
    html_output = tmp_path / "output.html"
    
    converter = PdfConverter()
    with patch('subprocess.run') as mock_subprocess_run:
        converter.convert_md_to_html(str(md_file), str(html_output))
        mock_subprocess_run.assert_called_once_with(
            ['pandoc', str(md_file), '-o', str(html_output)],
            check=True, capture_output=True, text=True
        )

def test_convert_html_to_pdf_uses_playwright(tmp_path):
    html_file = tmp_path / "test.html"
    html_file.write_text("<html><body>Test</body></html>")
    pdf_output = tmp_path / "output.pdf"
    
    converter = PdfConverter()
    
    mock_browser = MagicMock()
    mock_page = MagicMock()
    mock_browser.new_page.return_value = mock_page

    mock_playwright_cm = MagicMock()
    mock_playwright_cm.chromium.launch.return_value = mock_browser

    with patch('pdf_converter_py.sync_playwright', return_value=mock_playwright_cm):
        # We need to mock the context manager entry point as well
        with patch.object(mock_playwright_cm, '__enter__', return_value=mock_playwright_cm):
            converter.convert_html_to_pdf(str(html_file), str(pdf_output))
            
            mock_page.goto.assert_called_once_with(f"file://{html_file}")
            mock_page.add_style_tag.assert_called_once_with(path=converter.style_css_path)
            mock_page.pdf.assert_called_once_with(path=str(pdf_output), format="A4")
            mock_browser.close.assert_called_once()