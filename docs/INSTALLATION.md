# Installation Guide

## System Requirements

### Hardware
- **GPU**: NVIDIA GPU with 8GB+ VRAM (RTX 3080 recommended)
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 30GB free space

### Software
- **OS**: Ubuntu 22.04 / Windows 10+ / macOS
- **Python**: 3.11+
- **CUDA**: 12.6+ (for GPU support)
- **Driver**: NVIDIA driver 550+

---

## Option 1: Automated Setup (Recommended)

### Linux/macOS

```bash
# Clone repository
git clone https://github.com/Vittall13/SmartPDF-Science.git
cd SmartPDF-Science

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Download models
python scripts/download_models.py
```

### Windows

```powershell
# Clone repository
git clone https://github.com/Vittall13/SmartPDF-Science.git
cd SmartPDF-Science

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install PaddlePaddle GPU
pip install paddlepaddle-gpu==3.2.1 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Download models
python scripts/download_models.py
```

---

## Option 2: Manual Setup

### Step 1: Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows
```

### Step 2: Install PaddlePaddle GPU

```bash
pip install paddlepaddle-gpu==3.2.1 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
```

**Verify installation:**
```bash
python -c "import paddle; print(paddle.__version__); print(paddle.device.get_device())"
```

Expected output:
```
3.2.1
gpu:0
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Package

```bash
pip install -e .
```

### Step 5: Create Directories

```bash
mkdir -p input_pdfs output logs .cache
```

### Step 6: Download Models

```bash
python scripts/download_models.py
```

---

## Option 3: Docker (Easiest)

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- NVIDIA Container Toolkit

### Install NVIDIA Container Toolkit

```bash
# Ubuntu
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Run with Docker Compose

```bash
cd docker
docker-compose up -d smartpdf-ui
```

Access UI at: http://localhost:7860

---

## Verify Installation

```bash
# Test OCR
python -c "from smartpdf.core.ocr_engine import SmartOCREngine; print('✓ OCR OK')"

# Test converters
python -c "from smartpdf.converters.md_to_docx import MarkdownToDOCX; print('✓ Converters OK')"

# Test LLM (optional)
python -c "from smartpdf.llm.qwen_corrector import Qwen3Corrector; print('✓ LLM OK')"
```

---

## Troubleshooting

### CUDA not detected

```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA version
nvcc --version
```

### PaddlePaddle CPU fallback

If GPU not available, install CPU version:
```bash
pip uninstall paddlepaddle-gpu
pip install paddlepaddle==3.2.1
```

### Import errors

```bash
# Reinstall package
pip install -e . --force-reinstall
```

### Memory issues

Reduce batch size or enable 4-bit quantization in `configs/default.yaml`:
```yaml
llm:
  load_in_4bit: true
```