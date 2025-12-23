import subprocess
import os
from playwright.sync_api import sync_playwright

class PdfConverter:
    def __init__(self):
        # The CSS path is relative to this file
        self.style_css_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdf_converter", "style.css"))

    def convert_md_to_html(self, md_file_path, output_html_path):
        """
        Converts a Markdown file to HTML using a specific Pandoc command.
        """
        if not os.path.exists(md_file_path):
            raise FileNotFoundError(f"Markdown file not found: {md_file_path}")

        # Construct the complex Pandoc command
        command = [
            'pandoc',
            '-f', 'gfm+footnotes+definition_lists+smart+raw_html+tex_math_dollars+tex_math_gfm',
            '-t', 'html',
            '-s',
            '--mathjax',
            '-o', output_html_path,
            md_file_path,
            f'--css={self.style_css_path}'
        ]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Pandoc conversion failed: {e.stderr}")

    def convert_html_to_pdf(self, html_file_path, output_pdf_path, playwright_instance=None):
        """
        Converts an HTML file to PDF using Playwright's headless Chromium.
        Allows passing an existing Playwright instance to avoid asyncio loop conflicts.
        """
        if not os.path.exists(html_file_path):
            raise FileNotFoundError(f"HTML file not found: {html_file_path}")

        absolute_html_path = os.path.abspath(html_file_path)

        def _run_conversion(p):
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"file://{absolute_html_path}")
            # Generate PDF
            page.pdf(path=output_pdf_path, format="A4")
            browser.close()

        if playwright_instance:
            # Reuse existing instance
            _run_conversion(playwright_instance)
        else:
            # Start a new one
            with sync_playwright() as p:
                _run_conversion(p)
