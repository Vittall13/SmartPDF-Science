# Quick Start Guide

## 5-Minute Setup

### Windows

```powershell
# 1. Clone repo
git clone https://github.com/Vittall13/SmartPDF-Science.git
cd SmartPDF-Science

# 2. Setup
python -m venv venv
venv\Scripts\activate
pip install paddlepaddle-gpu==3.2.1 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
pip install -r requirements.txt

# 3. Test
python examples/basic_usage.py
```

### Linux

```bash
# 1. Clone and setup
git clone https://github.com/Vittall13/SmartPDF-Science.git
cd SmartPDF-Science
chmod +x scripts/setup.sh
./scripts/setup.sh

# 2. Run UI
./scripts/run_ui.sh
```

### Docker

```bash
cd SmartPDF-Science/docker
docker-compose up -d

# Open http://localhost:7860
```

---

## First Conversion

### Method 1: Web UI

1. Start UI: `./scripts/run_ui.sh`
2. Open: http://localhost:7860
3. Upload PDF
4. Choose format (DOCX recommended)
5. Click "Process"
6. Download result

### Method 2: Command Line

```bash
# Put PDF in input_pdfs/
cp your_paper.pdf input_pdfs/

# Run
python examples/basic_usage.py

# Check output/
ls output/
```

---

## Common Issues

**"CUDA not found"**
```bash
# Check GPU
nvidia-smi

# Use CPU if no GPU
edit configs/default.yaml → device: "cpu"
```

**"Out of memory"**
```yaml
# Edit configs/default.yaml
llm:
  load_in_4bit: true
```

**"Models not found"**
```bash
python scripts/download_models.py
```

---

## What's Next?

- Read [USAGE.md](USAGE.md) for detailed guide
- Check [examples/](../examples/) for code samples
- Try different output formats
- Enable LLM correction for better quality

---

## Support

- Issues: https://github.com/Vittall13/SmartPDF-Science/issues
- Documentation: [docs/](.)