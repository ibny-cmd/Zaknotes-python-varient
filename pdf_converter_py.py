import subprocess
import os
from playwright.sync_api import sync_playwright

class PdfConverter:
    def __init__(self):
        self.style_css_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdf_converter", "style.css"))

    def convert_md_to_html(self, md_file_path, output_html_path):
        """
        Converts a Markdown file to HTML using Pandoc.
        """
        if not os.path.exists(md_file_path):
            raise FileNotFoundError(f"Markdown file not found: {md_file_path}")

        command = ['pandoc', md_file_path, '-o', output_html_path]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Pandoc conversion failed: {e.stderr}")

    def convert_html_to_pdf(self, html_file_path, output_pdf_path):
        """
        Converts an HTML file to PDF using Playwright's headless Chromium.
        Injects a CSS file for styling.
        """
        if not os.path.exists(html_file_path):
            raise FileNotFoundError(f"HTML file not found: {html_file_path}")
        
        if not os.path.exists(self.style_css_path):
            print(f"Warning: CSS file not found at {self.style_css_path}. PDF might not be styled correctly.")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Go to the HTML file (local file access)
            page.goto(f"file://{html_file_path}")
            
            # Inject CSS
            if os.path.exists(self.style_css_path):
                page.add_style_tag(path=self.style_css_path)
            
            # Generate PDF
            page.pdf(path=output_pdf_path, format="A4")
            
            browser.close()