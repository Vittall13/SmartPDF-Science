"""PaddleOCR engine with formula recognition support."""
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

os.environ["PADDLE_USE_CUDNN"] = "0"
from paddleocr import PaddleOCRVL

logger = logging.getLogger(__name__)


class SmartOCREngine:
    """Enhanced OCR engine with formula recognition."""
    
    def __init__(
        self,
        use_layout_detection: bool = True,
        use_formula_recognition: bool = True,
        formula_model: str = "PP-FormulaNet_plus-L",
        use_doc_orientation_classify: bool = True,
        use_doc_unwarping: bool = False,
        device: str = "gpu:0"
    ):
        """Initialize OCR engine.
        
        Args:
            use_layout_detection: Enable layout detection for better structure
            use_formula_recognition: Enable LaTeX formula recognition
            formula_model: Formula recognition model name
            use_doc_orientation_classify: Fix document rotation
            use_doc_unwarping: Enable document unwarping (slower)
            device: Device to use (gpu:0, cpu)
        """
        logger.info("Initializing SmartOCREngine...")
        start = time.time()
        
        self.config = {
            "use_layout_detection": use_layout_detection,
            "format_block_content": True,
            "use_doc_orientation_classify": use_doc_orientation_classify,
            "use_doc_unwarping": use_doc_unwarping,
            "device": device
        }
        
        # Add formula recognition if enabled
        if use_formula_recognition:
            self.config["use_formula_recognition"] = True
            logger.info(f"Formula recognition enabled: {formula_model}")
        else:
            logger.info("Formula recognition disabled")
        
        self.vl = PaddleOCRVL(**self.config)
        
        elapsed = time.time() - start
        logger.info(f"OCR engine initialized in {elapsed:.1f}s")
    
    def process_pdf(
        self,
        pdf_path: str | Path,
        output_dir: Optional[str | Path] = None
    ) -> Dict[str, Any]:
        """Process PDF file and extract content.
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save images (optional)
            
        Returns:
            Dictionary with markdown text, images, and formulas
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        logger.info(f"Processing: {pdf_path.name}")
        start = time.time()
        
        results = self.vl.predict(str(pdf_path))
        
        md_parts = []
        images_saved = 0
        formulas_found = 0
        
        for page_num, res in enumerate(results, 1):
            # Extract markdown text
            if hasattr(res, 'markdown') and 'markdown_texts' in res.markdown:
                md_text = res.markdown['markdown_texts'].strip()
                md_parts.append(f"<!-- Page {page_num} -->\n\n{md_text}")
            
            # Save images if output directory provided
            if output_dir and hasattr(res, 'markdown') and 'markdown_images' in res.markdown:
                output_dir = Path(output_dir)
                for rel_path, img in res.markdown['markdown_images'].items():
                    save_path = output_dir / "images" / pdf_path.stem / rel_path
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    img.save(save_path)
                    images_saved += 1
            
            # Count formulas if present
            if hasattr(res, 'formula_res_list'):
                formulas_found += len(res.formula_res_list)
        
        full_md = "\n\n---\n\n".join(md_parts) if md_parts else ""
        
        elapsed = time.time() - start
        logger.info(
            f"Processed {pdf_path.name} in {elapsed:.1f}s: "
            f"{len(results)} pages, {images_saved} images, {formulas_found} formulas"
        )
        
        return {
            "markdown": full_md,
            "pages": len(results),
            "images": images_saved,
            "formulas": formulas_found,
            "processing_time": elapsed
        }