#!/bin/bash

echo "==================================="
echo "MOSIP OCR Verification System"
echo "==================================="

# Check Python version
python3 --version

# Navigate to backend
cd backend/

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Download models (first time only)
echo "Downloading TrOCR model..."
python3 -c "from transformers import TrOCRProcessor, VisionEncoderDecoderModel; TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed'); VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')"

# Start server
echo "Starting server at http://localhost:8000"
python3 main.py
