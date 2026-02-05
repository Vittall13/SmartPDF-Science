"""Qwen3-8B based text correction and enhancement."""
import logging
from typing import Optional, Literal
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

logger = logging.getLogger(__name__)


class Qwen3Corrector:
    """Intelligent text correction using Qwen3-8B."""
    
    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-8B",
        device: str = "cuda",
        load_in_4bit: bool = False
    ):
        """Initialize Qwen3 corrector.
        
        Args:
            model_name: HuggingFace model name
            device: Device to use (cuda, cpu)
            load_in_4bit: Enable 4-bit quantization to save VRAM
        """
        logger.info(f"Loading {model_name}...")
        
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        model_kwargs = {
            "device_map": device,
            "torch_dtype": "auto",
        }
        
        if load_in_4bit:
            from transformers import BitsAndBytesConfig
            model_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16
            )
            logger.info("Using 4-bit quantization")
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            **model_kwargs
        )
        
        logger.info("Qwen3 corrector loaded successfully")
    
    def _analyze_complexity(self, text: str) -> Literal["low", "medium", "high"]:
        """Analyze text complexity to choose processing mode.
        
        Args:
            text: Text to analyze
            
        Returns:
            Complexity level
        """
        # Check for formulas
        has_formulas = any(marker in text for marker in ["$$", "\\(", "\\[", "\\begin"])
        
        # Check for tables
        has_tables = "|" in text and text.count("|") > 5
        
        # Check for mixed languages (Cyrillic + Latin)
        has_cyrillic = any('\u0400' <= c <= '\u04FF' for c in text)
        has_latin = any('a' <= c.lower() <= 'z' for c in text)
        is_mixed = has_cyrillic and has_latin
        
        if has_formulas or (has_tables and len(text) > 500):
            return "high"
        elif is_mixed or has_tables:
            return "medium"
        else:
            return "low"
    
    def correct_text(
        self,
        text: str,
        mode: Optional[Literal["auto", "thinking", "non-thinking"]] = "auto",
        max_new_tokens: int = 2048,
        temperature: float = 0.3
    ) -> str:
        """Correct OCR errors in text.
        
        Args:
            text: Text to correct
            mode: Processing mode (auto selects based on complexity)
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Corrected text
        """
        if not text.strip():
            return text
        
        # Auto-select mode based on complexity
        if mode == "auto":
            complexity = self._analyze_complexity(text)
            if complexity == "high":
                mode = "thinking"
                temperature = 0.1
            elif complexity == "medium":
                mode = "non-thinking"
                temperature = 0.3
            else:
                # For simple text, use basic cleanup
                return self._basic_cleanup(text)
        
        prompt = f"""Fix OCR errors in this text. Preserve markdown formatting, fix typos, broken words, and spacing issues. Keep LaTeX formulas unchanged.

Text:
{text}

Corrected:"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract corrected part (after "Corrected:")
        if "Corrected:" in result:
            result = result.split("Corrected:")[-1].strip()
        
        return result
    
    def _basic_cleanup(self, text: str) -> str:
        """Basic text cleanup without LLM.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Remove multiple spaces
        text = " ".join(text.split())
        
        # Fix common OCR errors
        replacements = {
            " ,": ",",
            " .": ".",
            " :": ":",
            "( ": "(",
            " )": ")",
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text