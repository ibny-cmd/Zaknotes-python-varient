import pytest
from unittest.mock import MagicMock, patch, ANY
import os
from bot_engine import AIStudioBot
from pdf_converter_py import PdfConverter

@pytest.fixture
def mock_bot_deps():
    with patch('bot_engine.BrowserDriver') as MockDriver:
        driver_instance = MockDriver.return_value
        mock_page = MagicMock()
        driver_instance.page = mock_page
        mock_playwright = MagicMock()
        driver_instance.playwright = mock_playwright
        yield driver_instance, mock_page, mock_playwright

@pytest.fixture
def mock_pdf_deps(mock_bot_deps):
    driver_instance, bot_page, mock_playwright = mock_bot_deps
    # Patch subprocess.run globally
    with patch('subprocess.run') as mock_run:
        # We don't patch sync_playwright here because bot_engine will pass its own instance
        # But we need to mock the behavior of that instance (mock_playwright)
        mock_browser = MagicMock()
        mock_page = MagicMock()
        
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        yield mock_run, mock_page

def test_full_pipeline_integration(mock_bot_deps, mock_pdf_deps, tmp_path):
    driver_instance, bot_page, mock_playwright = mock_bot_deps
    mock_run, pdf_page = mock_pdf_deps
    
    # 1. Bot Engine Setup
    bot = AIStudioBot()
    bot.page = bot_page
    # Ensure bot uses the same driver instance
    bot.driver = driver_instance
    
    m = MagicMock()
    m.is_enabled.return_value = True
    m.count.side_effect = [1, 0, 0, 0, 0, 0]
    m.locator.return_value = m
    m.filter.return_value = m
    m.first = m
    m.last = m
    
    bot_page.locator.return_value = m
    bot_page.get_by_label.return_value = m
    bot_page.get_by_text.return_value = m
    bot_page.evaluate.return_value = "# Integrated Test Content"
    
    audio_path = tmp_path / "test.mp3"
    audio_path.write_text("dummy audio")
    
    # Execution
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', MagicMock()):
        md_text, pdf_path = bot.generate_notes(str(audio_path))
    
    # Verifications
    assert md_text == "# Integrated Test Content"
    assert pdf_path.endswith(".pdf")
    
    # Verify PDF Conversion components were triggered
    mock_run.assert_called_once() # Pandoc called once via bot.generate_notes
    pdf_page.goto.assert_called_once() # Playwright goto called
    pdf_page.pdf.assert_called_once() # PDF generated
