# Usage Guide

## Quick Start

### 1. Web UI (Easiest)

```bash
# Start Gradio UI
./scripts/run_ui.sh

# Open browser
http://localhost:7860
```

**Features:**
- Drag & drop PDF upload
- Choose output format (DOCX, MD, LaTeX, HTML)
- Optional AI text correction
- Download results

---

### 2. Command Line

#### Basic Usage

```python
from smartpdf.core.ocr_engine import SmartOCREngine
from smartpdf.converters.md_to_docx import MarkdownToDOCX

# Initialize
ocr = SmartOCREngine(use_formula_recognition=True)

# Process PDF
result = ocr.process_pdf("paper.pdf")

# Convert to DOCX
converter = MarkdownToDOCX()
converter.convert(result["markdown"], "output.docx")
```

#### With LLM Correction

```python
from smartpdf.llm.qwen_corrector import Qwen3Corrector

# Initialize corrector
corrector = Qwen3Corrector()

# Correct text
corrected = corrector.correct_text(result["markdown"], mode="auto")

# Save
converter.convert(corrected, "corrected.docx")
```

---

### 3. REST API

#### Start API Server

```bash
./scripts/run_api.sh

# API docs at: http://localhost:8000/docs
```

#### Use with curl

```bash
# Convert PDF
curl -X POST "http://localhost:8000/convert" \
  -F "file=@paper.pdf" \
  -F "output_format=docx" \
  -F "use_llm_correction=false" \
  -o response.json

# Get job ID from response
job_id=$(jq -r '.job_id' response.json)

# Download result
curl "http://localhost:8000/download/$job_id" -o result.docx
```

#### Use with Python

```python
import requests

# Upload and convert
with open("paper.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/convert",
        files={"file": f},
        data={"output_format": "docx"}
    )

job = response.json()
print(f"Job ID: {job['job_id']}")
print(f"Pages: {job['pages']}")
print(f"Formulas: {job['formulas']}")

# Download
result = requests.get(f"http://localhost:8000{job['download_url']}")
with open("result.docx", "wb") as f:
    f.write(result.content)
```

---

## Configuration

### Edit `configs/default.yaml`

```yaml
ocr:
  device: "gpu:0"  # gpu:0, gpu:1, cpu
  use_formula_recognition: true
  formula_model: "PP-FormulaNet_plus-L"

filter:
  min_area: 5000
  min_score: 0.65

llm:
  model_name: "Qwen/Qwen3-8B"
  load_in_4bit: false  # Set true to save VRAM
```

### Or use programmatically

```python
from smartpdf.utils.config import get_config

config = get_config("configs/default.yaml")
device = config.get("ocr.device")
```

---

## Output Formats

### Markdown (.md)
- Native format
- Best for version control
- Contains LaTeX formulas

### DOCX (.docx)
- Microsoft Word format
- Best for editing
- Formulas as text/images

### LaTeX (.tex)
- Scientific publications
- Compile with pdflatex
- Native formula support

### HTML (.html)
- Web publishing
- MathJax for formulas
- Responsive design

---

## Examples

See `examples/` directory:

1. **basic_usage.py** - Simple conversion
2. **advanced_usage.py** - With LLM correction
3. **api_client.py** - API usage
4. **batch_processing.py** - Process multiple PDFs

```bash
# Run example
python examples/basic_usage.py
```

---

## Tips & Best Practices

### For Best OCR Quality

1. **High-resolution PDFs** - 300 DPI minimum
2. **Clean scans** - No artifacts or noise
3. **Straight text** - Not skewed or rotated
4. **Good contrast** - Black text on white background

### For Formula Recognition

- Use `PP-FormulaNet_plus-L` for best accuracy
- Formulas output as LaTeX code
- Works for printed formulas (not handwritten)

### For Large Documents

- Process in batches (see `batch_processing.py`)
- Use 4-bit quantization for LLM to save VRAM
- Monitor GPU memory with `nvidia-smi`

### Performance Optimization

**Speed priority:**
```yaml
ocr:
  use_layout_detection: false
  use_doc_unwarping: false
```

**Quality priority:**
```yaml
ocr:
  use_layout_detection: true
  use_doc_unwarping: true
```