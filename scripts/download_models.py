"""Download and cache required models."""
import os
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_paddleocr_models():
    """Download PaddleOCR models."""
    logger.info("Downloading PaddleOCR models...")
    
    # PaddleOCR will auto-download on first use
    # But we can pre-download to cache
    from paddleocr import PaddleOCRVL
    
    logger.info("Initializing PaddleOCR-VL (will download models if needed)...")
    
    vl = PaddleOCRVL(
        use_layout_detection=True,
        use_formula_recognition=True,
        formula_recognition_model_name="PP-FormulaNet_plus-L",
        device="gpu:0" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
    )
    
    logger.info("✅ PaddleOCR models ready!")
    return vl


def download_qwen_model():
    """Download Qwen3-8B model."""
    logger.info("Downloading Qwen3-8B model...")
    logger.info("⚠️  This will download ~16GB and may take a while...")
    
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    model_name = "Qwen/Qwen3-8B"
    cache_dir = Path(".cache/huggingface")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Downloading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        cache_dir=str(cache_dir)
    )
    
    logger.info("Downloading model...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        cache_dir=str(cache_dir),
        torch_dtype="auto"
    )
    
    logger.info("✅ Qwen3-8B model ready!")
    return model, tokenizer


def main():
    """Download all required models."""
    logger.info("="*50)
    logger.info("SmartPDF-Science Model Downloader")
    logger.info("="*50)
    logger.info("")
    
    # Download PaddleOCR models
    logger.info("[1/2] PaddleOCR Models")
    try:
        download_paddleocr_models()
    except Exception as e:
        logger.error(f"Failed to download PaddleOCR models: {e}")
        return 1
    
    logger.info("")
    
    # Ask about Qwen3
    logger.info("[2/2] Qwen3-8B Model (optional, for text correction)")
    response = input("🤖 Download Qwen3-8B (~16GB)? This enables AI text correction. [y/N]: ")
    
    if response.lower() in ['y', 'yes']:
        try:
            download_qwen_model()
        except Exception as e:
            logger.error(f"Failed to download Qwen3 model: {e}")
            logger.info("⚠️  You can still use the app without LLM correction")
    else:
        logger.info("⏭️  Skipping Qwen3-8B. You can download it later if needed.")
    
    logger.info("")
    logger.info("="*50)
    logger.info("✅ Model download completed!")
    logger.info("="*50)
    logger.info("")
    logger.info("You can now run:")
    logger.info("  - UI: ./scripts/run_ui.sh")
    logger.info("  - API: ./scripts/run_api.sh")
    logger.info("")
    
    return 0


if __name__ == "__main__":
    exit(main())