"""Advanced usage example with LLM correction."""
from pathlib import Path
from smartpdf.core.ocr_engine import SmartOCREngine
from smartpdf.llm.qwen_corrector import Qwen3Corrector
from smartpdf.converters.md_to_docx import MarkdownToDOCX
from smartpdf.converters.md_to_latex import MarkdownToLaTeX
from smartpdf.utils.config import get_config
from smartpdf.utils.logger import setup_logging


def main():
    # Setup logging
    setup_logging(level="INFO", log_file="logs/advanced_example.log")
    
    # Load config
    config = get_config("configs/default.yaml")
    
    print("=" * 50)
    print("SmartPDF-Science - Advanced Usage Example")
    print("With LLM Text Correction")
    print("=" * 50)
    print()
    
    # Initialize OCR engine
    print("[1/4] Initializing OCR engine...")
    ocr = SmartOCREngine(
        use_formula_recognition=True,
        formula_model=config.get("ocr.formula_model"),
        device=config.get("ocr.device")
    )
    print("✓ OCR engine ready\n")
    
    # Initialize LLM corrector
    print("[2/4] Loading Qwen3-8B for text correction...")
    print("⚠️  This will use ~8GB VRAM")
    corrector = Qwen3Corrector(
        model_name=config.get("llm.model_name"),
        device=config.get("llm.device"),
        load_in_4bit=config.get("llm.load_in_4bit")
    )
    print("✓ LLM ready\n")
    
    # Process PDF
    pdf_path = "input_pdfs/sample.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ Error: {pdf_path} not found")
        return
    
    print(f"[3/4] Processing: {pdf_path}")
    result = ocr.process_pdf(pdf_path, output_dir="output")
    markdown_text = result["markdown"]
    
    print(f"✓ OCR completed: {result['pages']} pages, {result['formulas']} formulas")
    print()
    
    # Apply LLM correction
    print("[4/4] Applying AI text correction...")
    corrected_text = corrector.correct_text(
        markdown_text,
        mode="auto"  # Auto-selects best mode based on complexity
    )
    print("✓ Text corrected\n")
    
    # Save multiple formats
    print("Saving outputs...")
    
    # DOCX
    docx_converter = MarkdownToDOCX()
    docx_path = "output/corrected.docx"
    docx_converter.convert(corrected_text, docx_path)
    print(f"  ✓ DOCX: {docx_path}")
    
    # LaTeX
    latex_converter = MarkdownToLaTeX()
    latex_path = "output/corrected.tex"
    latex_converter.convert(corrected_text, latex_path)
    print(f"  ✓ LaTeX: {latex_path}")
    
    # Markdown
    md_path = "output/corrected.md"
    Path(md_path).write_text(corrected_text, encoding="utf-8")
    print(f"  ✓ Markdown: {md_path}")
    
    print()
    print("=" * 50)
    print("✅ Done! All formats saved to output/")
    print("=" * 50)


if __name__ == "__main__":
    main()