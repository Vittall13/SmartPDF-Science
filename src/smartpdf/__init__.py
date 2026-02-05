"""SmartPDF-Science: AI-powered PDF converter with GPU acceleration."""

__version__ = "0.1.0"
__author__ = "Vittall13"

from .core.ocr_engine import SmartOCREngine
from .llm.qwen_corrector import Qwen3Corrector

__all__ = ["SmartOCREngine", "Qwen3Corrector"]