#!/bin/bash
# Launch Gradio UI

echo "=================================="
echo "Starting SmartPDF-Science UI"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if PaddleOCR is installed
if ! python3 -c "import paddleocr" &> /dev/null; then
    echo "ERROR: PaddleOCR not found. Run ./scripts/setup.sh first."
    exit 1
fi

echo "Launching Gradio UI on http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 src/smartpdf/ui/gradio_app.py