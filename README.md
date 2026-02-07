# SmartPDF-Science

> AI-powered PDF to DOCX/LaTeX/Markdown converter with GPU acceleration, formula recognition, and LLM post-processing for scientific documents

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![CUDA 12.6](https://img.shields.io/badge/CUDA-12.6-green.svg)](https://developer.nvidia.com/cuda-downloads)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

##  Features

- **GPU-Accelerated OCR** - PaddleOCR-VL with CUDA support
- **Formula Recognition** - Convert mathematical formulas to LaTeX (PP-FormulaNet)
- **AI Post-Processing** - Qwen3-8B for intelligent text correction
- **Multi-Format Export** - DOCX, Markdown, LaTeX, HTML, PDF
- **Web Interface** - Easy-to-use Gradio UI
- **REST API** - FastAPI endpoints for integration
- 🇷🇺🇬🇧 **Multi-Language** - Russian and English support

## Use Cases

- Scientific papers and research articles
- Technical documentation with formulas
- Academic textbooks and lecture notes
- Patents and technical reports
- Mixed language documents

## Architecture

```
PDF Input
    ↓
[Stage 1] PaddleOCR-VL + PP-FormulaNet (GPU)
    ├─ Text extraction
    ├─ Layout detection
    ├─ Table recognition
    └─ Formula → LaTeX conversion
    ↓
[Stage 2] Qwen3-8B (Adaptive Correction)
    ├─ Context-aware text fixing
    ├─ Formula validation
    └─ Structure normalization
    ↓
[Output] Multi-Format Export
    ├─ DOCX (with equations)
    ├─ Markdown (with LaTeX blocks)
    ├─ LaTeX (.tex)
    ├─ HTML (MathJax rendering)
    └─ PDF (via LaTeX compilation)
```

## Requirements

### Hardware
- **GPU**: NVIDIA RTX 3080+ (20GB VRAM recommended)
- **RAM**: 32GB+
- **Storage**: 10GB+ for models

### Software
- Python 3.11+
- CUDA 12.6+
- cuDNN 9.0+

## Quick Start

### 1. Environment Setup

```bash
# Create conda environment
conda create -n smartpdf python=3.11 -y
conda activate smartpdf

# Clone repository
git clone https://github.com/Vittall13/SmartPDF-Science.git
cd SmartPDF-Science

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Web Interface

```bash
python src/ui/gradio_app.py
```

Open browser at `http://localhost:7860`

### 3. Use API

```bash
python src/api/fastapi_app.py
```

API docs at `http://localhost:8000/docs`

## Usage Examples

### Python API

```python
from smartpdf import SmartPDFConverter

converter = SmartPDFConverter(
    device="cuda:0",
    enable_formula=True,
    llm_correction=True
)

# Convert to multiple formats
results = converter.convert(
    "scientific_paper.pdf",
    output_formats=["docx", "latex", "md"]
)

print(f"DOCX: {results['docx']}")
print(f"LaTeX: {results['latex']}")
```

### CLI

```bash
# Single file conversion
smartpdf convert input.pdf --format docx latex

# Batch processing
smartpdf batch ./papers/ --output ./results/

# With custom settings
smartpdf convert input.pdf --format docx \
    --formula-model PP-FormulaNet_plus-L \
    --llm-correction aggressive
```

## Configuration

Edit `configs/default.yaml`:

```yaml
ocr:
  model: PaddleOCR-VL
  device: cuda:0
  use_layout_detection: true
  use_doc_orientation_classify: true

formula:
  model: PP-FormulaNet_plus-L
  confidence_threshold: 0.85

llm:
  model: Qwen/Qwen3-8B
  correction_mode: adaptive  # off, light, adaptive, aggressive
  temperature: 0.3

output:
  formats: [docx, md, latex]
  image_quality: 92
  preserve_layout: true
```

## Performance

| Document Type | Pages/min | GPU Usage | Accuracy |
|---------------|-----------|-----------|----------|
| Simple text | 60-80 | 40-50% | 98%+ |
| Text + formulas | 30-40 | 70-80% | 95%+ |
| Complex formulas | 15-20 | 85-95% | 92%+ |

*Tested on RTX 3080 20GB*

## Project Structure

```
SmartPDF-Science/
├── configs/
│   └── default.yaml
├── src/
│   └── smartpdf/
│       ├── __init__.py
│       ├── core/
│       │   ├── ocr_engine.py
│       │   ├── formula_recognizer.py
│       │   ├── preprocessor.py
│       │   └── postprocessor.py
│       ├── llm/
│       │   ├── qwen_corrector.py
│       │   └── prompts.py
│       ├── exporters/
│       │   ├── docx_exporter.py
│       │   ├── latex_exporter.py
│       │   ├── markdown_exporter.py
│       │   └── html_exporter.py
│       ├── api/
│       │   └── fastapi_app.py
│       └── ui/
│           └── gradio_app.py
├── tests/
├── examples/
├── docker/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Code formatting
black src/
ruff check src/

# Type checking
mypy src/
```

## Docker

```bash
# Build image
docker build -t smartpdf-science .

# Run container
docker run --gpus all -p 7860:7860 smartpdf-science
```

## Models

### PaddleOCR-VL
- **Source**: [HuggingFace](https://huggingface.co/PaddlePaddle/PaddleOCR-VL)
- **Size**: ~2GB
- **Languages**: 100+ including Russian, English

### PP-FormulaNet_plus-L
- **Source**: [PaddleOCR](https://paddleocr.ai)
- **Size**: 698MB
- **Accuracy**: 92.22% (English), 90.64% (Russian)

### Qwen3-8B
- **Source**: [HuggingFace](https://huggingface.co/Qwen/Qwen3-8B)
- **Size**: 8.2B parameters
- **Features**: Thinking mode, multi-language

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## License

MIT License - see [LICENSE](LICENSE) file

## Acknowledgments

- [PaddlePaddle](https://github.com/PaddlePaddle) - OCR engine
- [Qwen Team](https://github.com/QwenLM) - LLM models
- Original PDF2MD_Paddle project

## Contact

Created by [@Vittall13](https://github.com/Vittall13)

---

⭐ Star this repo if you find it useful!
