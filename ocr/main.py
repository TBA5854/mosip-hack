from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import shutil
from pathlib import Path
import uuid

from ocr.preprocessing import preprocess_image
from ocr.extractor import OCRExtractor
from verification.comparator import DataComparator
from utils.pdf_processing import PDFProcessor
from utils.quality_score import QualityScorer
from utils.vc_generator import VCGenerator
from utils.qr_generator import QRGenerator
from config import UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR, ALLOWED_EXTENSIONS

app = FastAPI(
    title="MOSIP OCR Verification System",
    description="Offline OCR-based text extraction and verification system with VC generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
# Fix static files path
import os
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# Initialize components
ocr_extractor = OCRExtractor()
pdf_processor = PDFProcessor()
quality_scorer = QualityScorer()
data_comparator = DataComparator()
vc_generator = VCGenerator()
qr_generator = QRGenerator()


class SubmittedData(BaseModel):
    name: Optional[str] = None
    dob: Optional[str] = None
    age: Optional[int] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))



@app.post("/api/extract")
async def extract_text(
    file: UploadFile = File(...),
    include_quality_score: bool = Form(default=True),
    detect_handwritten: bool = Form(default=False)
):
    """
    OCR Extraction API (API 1)
    Extracts structured text fields from uploaded document
    """
    try:
        # Validate file
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"Unsupported file type: {file_ext}")
        
        # Save uploaded file
        file_id = str(uuid.uuid4())
        upload_path = UPLOAD_DIR / f"{file_id}{file_ext}"
        
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process PDF or image
        if file_ext == '.pdf':
            images = pdf_processor.convert_pdf_to_images(upload_path)
        else:
            from PIL import Image
            images = [Image.open(upload_path)]
        
        # Extract text from all pages
        all_extracted_data = []
        all_raw_text = []
        quality_scores = []
        
        for idx, image in enumerate(images):
            # Quality scoring
            if include_quality_score:
                quality_score = quality_scorer.score_image(image)
                quality_scores.append({
                    "page": idx + 1,
                    **quality_score
                })
            
            # Preprocess image (minimal for Tesseract)
            from ocr.preprocessing import preprocess_for_tesseract
            preprocessed = preprocess_for_tesseract(image)

            
            # OCR extraction
            extracted_data, raw_text = ocr_extractor.extract_fields(
                preprocessed,
                use_handwritten=detect_handwritten
            )
            
            all_extracted_data.append({
                "page": idx + 1,
                "fields": extracted_data
            })
            all_raw_text.append({
                "page": idx + 1,
                "text": raw_text
            })
        
        # Merge multi-page results (use first page as primary)
        primary_fields = all_extracted_data[0]["fields"] if all_extracted_data else {}
        
        response = {
            "file_id": file_id,
            "extracted_fields": primary_fields,
            "pages": all_extracted_data,
            "raw_text": all_raw_text,
            "total_pages": len(images)
        }
        
        if include_quality_score:
            response["quality_scores"] = quality_scores
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(500, f"Extraction failed: {str(e)}")


@app.post("/api/verify")
async def verify_data(
    file: UploadFile = File(...),
    submitted_data: str = Form(...)
):
    """
    Data Verification API (API 2)
    Compares OCR-extracted data with user-submitted form data
    """
    try:
        # Parse submitted data
        try:
            form_data = json.loads(submitted_data)
        except json.JSONDecodeError:
            raise HTTPException(400, "Invalid JSON in submitted_data")
        
        # Validate file
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"Unsupported file type: {file_ext}")
        
        # Save uploaded file
        file_id = str(uuid.uuid4())
        upload_path = UPLOAD_DIR / f"{file_id}{file_ext}"
        
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document
        if file_ext == '.pdf':
            images = pdf_processor.convert_pdf_to_images(upload_path)
        else:
            from PIL import Image
            images = [Image.open(upload_path)]
        
        # Extract OCR data from first page
        preprocessed = preprocess_image(images[0])
        extracted_data, raw_text = ocr_extractor.extract_fields(preprocessed)
        
        # Perform verification
        verification_result = data_comparator.compare_data(
            ocr_data=extracted_data,
            form_data=form_data
        )
        
        # Calculate overall score
        field_scores = [
            field["confidence"] 
            for field in verification_result["fields"].values() 
            if field.get("confidence") is not None
        ]
        overall_score = sum(field_scores) / len(field_scores) if field_scores else 0.0
        
        response = {
            "file_id": file_id,
            "verification_result": verification_result["fields"],
            "overall_score": round(overall_score, 3),
            "overall_match": overall_score >= 0.85,
            "mismatches": [
                field_name 
                for field_name, field_data in verification_result["fields"].items() 
                if not field_data.get("match", False)
            ]
        }
        
        return JSONResponse(content=response)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Verification failed: {str(e)}")


@app.post("/api/generate-vc")
async def generate_verifiable_credential(
    file_id: str = Form(...),
    verified_data: str = Form(...)
):
    """
    Generate Verifiable Credential after successful verification
    """
    try:
        verified_fields = json.loads(verified_data)
        
        # Generate VC
        vc = vc_generator.create_credential(verified_fields)
        
        # Generate QR code
        qr_path = OUTPUT_DIR / f"{file_id}_qr.png"
        qr_generator.generate_qr(vc, str(qr_path))
        
        # Save VC JSON
        vc_path = OUTPUT_DIR / f"{file_id}_vc.json"
        with open(vc_path, "w") as f:
            json.dump(vc, f, indent=2)
        
        return JSONResponse(content={
            "vc": vc,
            "vc_download_url": f"/api/download/vc/{file_id}",
            "qr_download_url": f"/api/download/qr/{file_id}"
        })
    
    except Exception as e:
        raise HTTPException(500, f"VC generation failed: {str(e)}")


@app.get("/api/download/vc/{file_id}")
async def download_vc(file_id: str):
    """Download Verifiable Credential JSON"""
    vc_path = OUTPUT_DIR / f"{file_id}_vc.json"
    if not vc_path.exists():
        raise HTTPException(404, "VC not found")
    return FileResponse(vc_path, filename=f"credential_{file_id}.json")


@app.get("/api/download/qr/{file_id}")
async def download_qr(file_id: str):
    """Download QR code image"""
    qr_path = OUTPUT_DIR / f"{file_id}_qr.png"
    if not qr_path.exists():
        raise HTTPException(404, "QR code not found")
    return FileResponse(qr_path, filename=f"qr_{file_id}.png")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ocr_model": ocr_extractor.model_name,
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
