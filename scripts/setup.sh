#!/bin/bash
# Automated setup script for SmartPDF-Science

set -e  # Exit on error

echo "=================================="
echo "SmartPDF-Science Setup"
echo "=================================="
echo ""

# Check Python version
echo "[1/6] Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python $required_version or higher required. Found: $python_version"
    exit 1
fi
echo "✓ Python $python_version found"

# Check CUDA
echo ""
echo "[2/6] Checking CUDA..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    echo "✓ CUDA available"
else
    echo "⚠️  WARNING: nvidia-smi not found. GPU may not be available."
fi

# Create virtual environment
echo ""
echo "[3/6] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo ""
echo "[4/6] Upgrading pip..."
pip install --upgrade pip wheel setuptools
echo "✓ Pip upgraded"

# Install PaddlePaddle GPU
echo ""
echo "[5/6] Installing PaddlePaddle GPU..."
pip install paddlepaddle-gpu==3.2.1 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
echo "✓ PaddlePaddle installed"

# Install dependencies
echo ""
echo "[6/6] Installing project dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Install package
echo ""
echo "Installing SmartPDF-Science..."
pip install -e .
echo "✓ Package installed"

# Create directories
echo ""
echo "Creating directories..."
mkdir -p input_pdfs output logs .cache
echo "✓ Directories created"

# Test installation
echo ""
echo "Testing installation..."
python3 -c "import paddle; print(f'Paddle version: {paddle.__version__}'); print(f'Device: {paddle.device.get_device()}')"

echo ""
echo "=================================="
echo "✅ Setup completed successfully!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Activate environment: source venv/bin/activate"
echo "2. Download models: python scripts/download_models.py"
echo "3. Run UI: ./scripts/run_ui.sh"
echo "4. Or run API: ./scripts/run_api.sh"
echo ""