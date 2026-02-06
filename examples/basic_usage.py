"""Basic usage example for SmartPDF-Science."""
from pathlib import Path
from smartpdf.core.ocr_engine import SmartOCREngine
from smartpdf.converters.md_to_docx import MarkdownToDOCX


def main():
    print("=" * 50)
    print("SmartPDF-Science - Basic Usage Example")
    print("=" * 50)
    print()
    
    # Initialize OCR engine
    print("[1/3] Initializing OCR engine...")
    ocr = SmartOCREngine(
        use_formula_recognition=True,
        device="gpu:0"  # Change to "cpu" if no GPU
    )
    print("✓ OCR engine ready\n")
    
    # Process PDF
    pdf_path = "input_pdfs/sample.pdf"
    
    if not Path(pdf_path).exists():
        print(f" Error: {pdf_path} not found")
        print("Please place a PDF file in input_pdfs/sample.pdf")
        return
    
    print(f"[2/3] Processing: {pdf_path}")
    result = ocr.process_pdf(pdf_path, output_dir="output")
    
    print(f"✓ Processed {result['pages']} pages in {result['processing_time']:.1f}s")
    print(f"  - Images extracted: {result['images']}")
    print(f"  - Formulas found: {result['formulas']}")
    print()
    
    # Convert to DOCX
    print("[3/3] Converting to DOCX...")
    converter = MarkdownToDOCX()
    output_path = "output/result.docx"
    converter.convert(result["markdown"], output_path)
    print(f"✓ DOCX saved to: {output_path}")
    
    print()
    print("=" * 50)
    print("Done! Check the output directory.")
    print("=" * 50)


if __name__ == "__main__":
    main()