# MOSIP OCR Verification System

Complete offline OCR-based document verification system with Verifiable Credential generation for the MOSIP Decode Hackathon 2025.

## Features

✅ **Offline OCR Extraction** using TrOCR (Microsoft Vision Transformer)
✅ **Multi-page PDF Support**
✅ **Real-time Image Quality Scoring** (blur, brightness, contrast)
✅ **Field-by-Field Data Verification** with confidence scores
✅ **Manual Correction UI** for OCR errors
✅ **Verifiable Credential Generation** (W3C compliant)
✅ **QR Code Generation** for wallet import (INJI compatible)
✅ **Fuzzy Matching** for text fields
✅ **RESTful API Architecture**

## Installation

### Prerequisites

- Python 3.9+
- pip
- Tesseract OCR (for fallback OCR)
- poppler-utils (for PDF processing)

### System Dependencies

#### Ubuntu/Debian:
```
sudo apt-get update
sudo apt-get install -y python3-pip poppler-utils tesseract-ocr
```


#### Windows:
1. Install [poppler for Windows](http://blog.alivate.com.au/poppler-windows/)
2. Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)

### Python Dependencies

Navigate to backend directory
cd backend/

Create virtual environment
python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

Install requirements
pip install -r requirements.txt

Download TrOCR model (first run only)
python -c "from transformers import TrOCRProcessor, VisionEncoderDecoderModel; TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed'); VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')"


## Running the Application

### Start Backend Server


```
cd backend/
source venv/bin/activate
python main.py
```


Server will start at: `http://localhost:8000`

### Access Frontend

Open your browser and navigate to:


http://localhost:8000

