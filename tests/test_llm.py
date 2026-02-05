"""Tests for LLM text correction."""
import pytest
from smartpdf.llm.qwen_corrector import Qwen3Corrector


class TestQwen3Corrector:
    """Test Qwen3 text correction."""
    
    @pytest.fixture
    def corrector(self):
        """Create corrector instance (skipped if model not available)."""
        try:
            return Qwen3Corrector(device="cpu")
        except Exception:
            pytest.skip("Qwen3 model not available")
    
    def test_basic_cleanup(self, corrector):
        """Test basic text cleanup."""
        text = "This  has   extra   spaces ."
        result = corrector._basic_cleanup(text)
        assert "  " not in result
        assert result.endswith(".")
    
    def test_complexity_analysis(self, corrector):
        """Test text complexity analysis."""
        # Simple text
        assert corrector._analyze_complexity("Hello world") == "low"
        
        # Text with formula
        assert corrector._analyze_complexity("Formula: $$E=mc^2$$") == "high"
        
        # Mixed language
        text = "Привет world"
        complexity = corrector._analyze_complexity(text)
        assert complexity in ["medium", "high"]