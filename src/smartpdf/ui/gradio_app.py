"""Gradio web interface for SmartPDF-Science."""
import gradio as gr
import logging
from pathlib import Path
import tempfile
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from smartpdf.core.ocr_engine import SmartOCREngine
from smartpdf.converters.md_to_docx import MarkdownToDOCX
from smartpdf.converters.md_to_latex import MarkdownToLaTeX
from smartpdf.converters.md_to_html import MarkdownToHTML

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OCR engine (will be loaded once)
ocr_engine = None


def process_pdf(
    pdf_file,
    output_format: str,
    use_llm_correction: bool,
    progress=gr.Progress()
):
    """Process PDF and convert to selected format."""
    global ocr_engine
    
    try:
        # Initialize OCR if needed
        if ocr_engine is None:
            progress(0.1, desc="Loading OCR engine...")
            ocr_engine = SmartOCREngine(
                use_formula_recognition=True,
                device="gpu:0"
            )
        
        # Process PDF
        progress(0.3, desc="Processing PDF...")
        result = ocr_engine.process_pdf(pdf_file.name)
        markdown_text = result["markdown"]
        
        # LLM correction
        if use_llm_correction:
            progress(0.6, desc="Applying AI correction...")
            # TODO: Add LLM correction here
            pass
        
        # Convert to selected format
        progress(0.8, desc=f"Converting to {output_format}...")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_format}") as tmp:
            output_path = tmp.name
            
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
        
        progress(1.0, desc="Done!")
        
        stats = (
            f"📄 Pages: {result['pages']} | "
            f"🖼️ Images: {result['images']} | "
            f"🔢 Formulas: {result['formulas']} | "
            f"⏱️ Time: {result['processing_time']:.1f}s"
        )
        
        return output_path, stats, markdown_text
    
    except Exception as e:
        logger.exception("Error processing PDF")
        return None, f"❌ Error: {str(e)}", ""


def create_ui():
    """Create Gradio interface."""
    
    with gr.Blocks(title="SmartPDF-Science", theme=gr.themes.Soft()) as app:
        gr.Markdown(
            """
            # 🔬 SmartPDF-Science
            ### AI-powered PDF to DOCX/LaTeX/Markdown converter
            
            Upload your PDF and get perfectly formatted documents with formulas recognized!
            """
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                pdf_input = gr.File(
                    label="📁 Upload PDF",
                    file_types=[".pdf"]
                )
                
                output_format = gr.Radio(
                    choices=["docx", "md", "tex", "html"],
                    value="docx",
                    label="📝 Output Format"
                )
                
                use_llm = gr.Checkbox(
                    label="🤖 Use AI Correction (Qwen3-8B)",
                    value=False,
                    info="Slower but better quality"
                )
                
                submit_btn = gr.Button("🚀 Process", variant="primary", size="lg")
            
            with gr.Column(scale=1):
                stats_output = gr.Textbox(
                    label="📊 Statistics",
                    lines=2
                )
                
                file_output = gr.File(
                    label="💾 Download Result"
                )
                
                preview_output = gr.Textbox(
                    label="👀 Markdown Preview",
                    lines=15,
                    max_lines=20
                )
        
        submit_btn.click(
            fn=process_pdf,
            inputs=[pdf_input, output_format, use_llm],
            outputs=[file_output, stats_output, preview_output]
        )
        
        gr.Markdown(
            """
            ---
            **Features:**
            - 🔥 GPU-accelerated OCR with PaddleOCR
            - 🧮 LaTeX formula recognition
            - 🤖 Optional AI text correction with Qwen3-8B
            - 📊 Table extraction
            - 🖼️ Image preservation
            """
        )
    
    return app


if __name__ == "__main__":
    app = create_ui()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)