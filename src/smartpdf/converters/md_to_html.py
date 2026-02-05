"""Markdown to HTML converter with MathJax support."""
import logging
import markdown
from pathlib import Path

logger = logging.getLogger(__name__)


class MarkdownToHTML:
    """Convert Markdown to HTML with formula rendering."""
    
    HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Converted Document</title>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 50px auto;
            padding: 20px;
            line-height: 1.6;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>"""
    
    def convert(self, markdown_text: str, output_path: str | Path) -> None:
        """Convert Markdown to HTML.
        
        Args:
            markdown_text: Markdown text to convert
            output_path: Path to save HTML file
        """
        logger.info(f"Converting to HTML: {output_path}")
        
        # Configure markdown extensions
        md = markdown.Markdown(
            extensions=[
                'extra',      # Tables, code blocks, etc.
                'codehilite', # Syntax highlighting
                'toc',        # Table of contents
            ]
        )
        
        # Convert markdown to HTML
        html_content = md.convert(markdown_text)
        
        # Wrap in template
        full_html = self.HTML_TEMPLATE.format(content=html_content)
        
        # Save
        output_path = Path(output_path)
        output_path.write_text(full_html, encoding='utf-8')
        logger.info(f"HTML saved: {output_path}")