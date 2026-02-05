"""Tests for format converters."""
import pytest
import tempfile
from pathlib import Path
from smartpdf.converters.md_to_docx import MarkdownToDOCX
from smartpdf.converters.md_to_latex import MarkdownToLaTeX
from smartpdf.converters.md_to_html import MarkdownToHTML


SAMPLE_MARKDOWN = """# Test Document

This is a test paragraph with some **bold** and *italic* text.

## Features

- Item 1
- Item 2
- Item 3

### Formula Example

$$E = mc^2$$

### Table Example

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
"""


class TestMarkdownToDOCX:
    """Test Markdown to DOCX converter."""
    
    def test_conversion(self):
        """Test basic conversion."""
        converter = MarkdownToDOCX()
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            converter.convert(SAMPLE_MARKDOWN, tmp.name)
            assert Path(tmp.name).exists()
            assert Path(tmp.name).stat().st_size > 0
            Path(tmp.name).unlink()


class TestMarkdownToLaTeX:
    """Test Markdown to LaTeX converter."""
    
    def test_conversion(self):
        """Test basic conversion."""
        converter = MarkdownToLaTeX()
        
        with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tmp:
            converter.convert(SAMPLE_MARKDOWN, tmp.name)
            
            content = Path(tmp.name).read_text()
            assert "\\documentclass" in content
            assert "\\begin{document}" in content
            assert "\\end{document}" in content
            
            Path(tmp.name).unlink()


class TestMarkdownToHTML:
    """Test Markdown to HTML converter."""
    
    def test_conversion(self):
        """Test basic conversion."""
        converter = MarkdownToHTML()
        
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
            converter.convert(SAMPLE_MARKDOWN, tmp.name)
            
            content = Path(tmp.name).read_text()
            assert "<!DOCTYPE html>" in content
            assert "MathJax" in content
            
            Path(tmp.name).unlink()