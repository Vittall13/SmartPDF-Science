"""FastAPI REST API for SmartPDF-Science."""
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Literal
import tempfile
import logging
from pathlib import Path
import uuid
import shutil

from smartpdf.core.ocr_engine import SmartOCREngine
from smartpdf.converters.md_to_docx import MarkdownToDOCX
from smartpdf.converters.md_to_latex import MarkdownToLaTeX
from smartpdf.converters.md_to_html import MarkdownToHTML

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SmartPDF-Science API",
    description="AI-powered PDF to DOCX/LaTeX/Markdown converter",
    version="0.1.0"
)

# Global OCR engine (initialized on first request)
ocr_engine: Optional[SmartOCREngine] = None
temp_files = {}  # Track temporary files for cleanup


class ConversionRequest(BaseModel):
    output_format: Literal["md", "docx", "tex", "html"] = "docx"
    use_llm_correction: bool = False


class ConversionResponse(BaseModel):
    job_id: str
    status: str
    pages: Optional[int] = None
    images: Optional[int] = None
    formulas: Optional[int] = None
    processing_time: Optional[float] = None
    download_url: Optional[str] = None


def cleanup_temp_file(filepath: str):
    """Remove temporary file after delay."""
    try:
        Path(filepath).unlink(missing_ok=True)
        logger.info(f"Cleaned up: {filepath}")
    except Exception as e:
        logger.error(f"Error cleaning up {filepath}: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize OCR engine on startup."""
    global ocr_engine
    logger.info("Initializing OCR engine...")
    ocr_engine = SmartOCREngine(
        use_formula_recognition=True,
        device="gpu:0"
    )
    logger.info("API ready!")


@app.get("/")
async def root():
    """API health check."""
    return {
        "name": "SmartPDF-Science API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "ocr_engine": "loaded" if ocr_engine else "not loaded"
    }


@app.post("/convert", response_model=ConversionResponse)
async def convert_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    output_format: Literal["md", "docx", "tex", "html"] = "docx",
    use_llm_correction: bool = False
):
    """Convert PDF to specified format.
    
    Args:
        file: PDF file to convert
        output_format: Output format (md, docx, tex, html)
        use_llm_correction: Use AI correction (slower but better quality)
    
    Returns:
        Conversion job details with download URL
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    job_id = str(uuid.uuid4())
    
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            shutil.copyfileobj(file.file, tmp_pdf)
            pdf_path = tmp_pdf.name
        
        # Process PDF
        logger.info(f"[{job_id}] Processing: {file.filename}")
        result = ocr_engine.process_pdf(pdf_path)
        markdown_text = result["markdown"]
        
        # LLM correction (if requested)
        if use_llm_correction:
            # TODO: Add LLM correction here
            pass
        
        # Convert to requested format
        output_ext = output_format
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{output_ext}",
            mode='w' if output_format == 'md' else 'wb'
        ) as tmp_out:
            output_path = tmp_out.name
        
        if output_format == "md":
            Path(output_path).write_text(markdown_text, encoding="utf-8")
        elif output_format == "docx":
            converter = MarkdownToDOCX()
            converter.convert(markdown_text, output_path)
        elif output_format == "tex":
            converter = MarkdownToLaTeX()
            converter.convert(markdown_text, output_path)
        elif output_format == "html":
            converter = MarkdownToHTML()
            converter.convert(markdown_text, output_path)
        
        # Store output file info
        temp_files[job_id] = output_path
        
        # Schedule cleanup after 1 hour
        background_tasks.add_task(cleanup_temp_file, pdf_path)
        
        logger.info(f"[{job_id}] Completed successfully")
        
        return ConversionResponse(
            job_id=job_id,
            status="completed",
            pages=result["pages"],
            images=result["images"],
            formulas=result["formulas"],
            processing_time=result["processing_time"],
            download_url=f"/download/{job_id}"
        )
    
    except Exception as e:
        logger.exception(f"[{job_id}] Error processing PDF")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{job_id}")
async def download_result(job_id: str, background_tasks: BackgroundTasks):
    """Download converted file.
    
    Args:
        job_id: Job ID from conversion request
    
    Returns:
        File download
    """
    if job_id not in temp_files:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    filepath = temp_files[job_id]
    
    if not Path(filepath).exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type
    ext = Path(filepath).suffix
    media_types = {
        ".md": "text/markdown",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".tex": "application/x-tex",
        ".html": "text/html"
    }
    media_type = media_types.get(ext, "application/octet-stream")
    
    # Schedule file cleanup after download
    background_tasks.add_task(cleanup_temp_file, filepath)
    del temp_files[job_id]
    
    return FileResponse(
        filepath,
        media_type=media_type,
        filename=f"converted{ext}"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)