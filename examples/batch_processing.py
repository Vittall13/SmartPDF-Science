"""Batch processing example."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from smartpdf.core.ocr_engine import SmartOCREngine
from smartpdf.converters.md_to_docx import MarkdownToDOCX
import time


def process_single_pdf(pdf_path: Path, ocr: SmartOCREngine, converter: MarkdownToDOCX) -> dict:
    """Process a single PDF file."""
    try:
        start = time.time()
        
        # OCR
        result = ocr.process_pdf(str(pdf_path))
        
        # Convert
        output_path = Path("output") / f"{pdf_path.stem}.docx"
        converter.convert(result["markdown"], str(output_path))
        
        elapsed = time.time() - start
        
        return {
            "file": pdf_path.name,
            "status": "success",
            "pages": result["pages"],
            "time": elapsed,
            "output": str(output_path)
        }
    
    except Exception as e:
        return {
            "file": pdf_path.name,
            "status": "error",
            "error": str(e)
        }


def main():
    print("=" * 50)
    print("SmartPDF-Science - Batch Processing Example")
    print("=" * 50)
    print()
    
    # Find all PDFs
    input_dir = Path("input_pdfs")
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {input_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF files")
    print()
    
    # Initialize engines
    print("Initializing OCR engine...")
    ocr = SmartOCREngine(device="gpu:0")
    converter = MarkdownToDOCX()
    print("✓ Ready\n")
    
    # Process in parallel
    print("Processing files...")
    results = []
    
    # Use 2 workers to avoid overwhelming GPU
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(process_single_pdf, pdf, ocr, converter): pdf
            for pdf in pdf_files
        }
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            if result["status"] == "success":
                print(f"✓ {result['file']}: {result['pages']} pages in {result['time']:.1f}s")
            else:
                print(f"❌ {result['file']}: {result['error']}")
    
    print()
    print("=" * 50)
    
    # Summary
    successful = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - successful
    total_time = sum(r.get("time", 0) for r in results)
    
    print(f"Processed: {successful}/{len(pdf_files)} successful")
    if failed > 0:
        print(f"Failed: {failed}")
    print(f"Total time: {total_time:.1f}s")
    print(f"Average: {total_time/successful:.1f}s per file")
    print("=" * 50)


if __name__ == "__main__":
    main()