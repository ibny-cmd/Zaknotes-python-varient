import subprocess
import os
from playwright.sync_api import sync_playwright

class PdfConverter:
    def __init__(self):
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

    def convert_html_to_pdf(self, html_file_path, output_pdf_path):
        """
        Converts an HTML file to PDF using Playwright's headless Chromium.
        """
        if not os.path.exists(html_file_path):
            raise FileNotFoundError(f"HTML file not found: {html_file_path}")

        # Convert to absolute path to prevent invalid URL errors
        absolute_html_path = os.path.abspath(html_file_path)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Go to the HTML file (local file access)
            page.goto(f"file://{absolute_html_path}")

            # CSS is now handled by Pandoc, so no need to inject it here.

            # Generate PDF
            page.pdf(path=output_pdf_path, format="A4")

            browser.close()