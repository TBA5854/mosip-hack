import os
from pathlib import Path

# Project directories
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "outputs"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# OCR Configuration
OCR_MODEL_NAME = "microsoft/trocr-base-printed"  # Only loaded if handwritten mode
OCR_HANDWRITTEN_MODEL = "microsoft/trocr-base-handwritten"
CONFIDENCE_THRESHOLD = 0.85

# OCR Engine Selection
USE_TESSERACT_BY_DEFAULT = True  # True = Tesseract, False = TrOCR
TESSERACT_CONFIG = r'--oem 3 --psm 6'  # Best for forms/documents

# Quality Score Thresholds
BLUR_THRESHOLD = 100.0
BRIGHTNESS_MIN = 50
BRIGHTNESS_MAX = 200

# Verification Settings
FUZZY_MATCH_THRESHOLD = 85

# VC Configuration
VC_ISSUER_DID = "did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"
VC_CONTEXT = [
    "https://www.w3.org/2018/credentials/v1",
    "https://w3id.org/citizenship/v1"
]

# Supported file types
ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
