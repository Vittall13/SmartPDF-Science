#!/bin/bash
# Launch FastAPI server

echo "=================================="
echo "Starting SmartPDF-Science API"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if FastAPI is installed
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "ERROR: FastAPI not found. Run ./scripts/setup.sh first."
    exit 1
fi

echo "Launching FastAPI on http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn src.smartpdf.api.fastapi_app:app --host 0.0.0.0 --port 8000 --reload