# SmartPDF-Science Docker Image with GPU support
FROM nvidia/cuda:12.6.0-cudnn9-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PADDLE_USE_CUDNN=0

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    git \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip wheel setuptools

# Copy requirements
COPY requirements.txt .
COPY pyproject.toml .

# Install Python dependencies
RUN pip install paddlepaddle-gpu==3.2.1 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
RUN pip install -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY configs/ ./configs/
COPY scripts/ ./scripts/

# Install package in development mode
RUN pip install -e .

# Create directories
RUN mkdir -p input_pdfs output .cache

# Expose ports
EXPOSE 7860 8000

# Default command (can be overridden)
CMD ["python3", "src/smartpdf/ui/gradio_app.py"]