"""Tests for OCR engine."""
import pytest
from pathlib import Path
import tempfile
from smartpdf.core.ocr_engine import SmartOCREngine


class TestOCREngine:
    """Test OCR engine functionality."""
    
    @pytest.fixture
    def ocr_engine(self):
        """Create OCR engine instance."""
        return SmartOCREngine(
            use_formula_recognition=False,  # Skip formula for speed
            device="cpu"  # Use CPU for tests
        )
    
    def test_engine_initialization(self, ocr_engine):
        """Test that engine initializes correctly."""
        assert ocr_engine is not None
        assert ocr_engine.vl is not None
    
    @pytest.mark.skipif(not Path("tests/fixtures/sample.pdf").exists(),
                       reason="Sample PDF not available")
    def test_process_pdf(self, ocr_engine):
        """Test PDF processing."""
        pdf_path = "tests/fixtures/sample.pdf"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = ocr_engine.process_pdf(pdf_path, tmpdir)
            
            assert "markdown" in result
            assert isinstance(result["markdown"], str)
            assert result["pages"] > 0
    
    def test_process_nonexistent_pdf(self, ocr_engine):
        """Test error handling for missing PDF."""
        with pytest.raises(FileNotFoundError):
            ocr_engine.process_pdf("nonexistent.pdf")