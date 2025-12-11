from PIL import Image
import pytesseract
import cv2
import numpy as np
import re
from typing import Tuple, Dict
from datetime import datetime


class OCRExtractor:
    def __init__(self, model_name: str = "microsoft/trocr-base-printed"):
        """Initialize OCR extractor"""
        self.model_name = model_name
        self.trocr_loaded = False
        self.trocr_processor = None
        self.trocr_model = None
        self.device = None
        
        print("OCR Extractor initialized")
        print("✓ Tesseract OCR ready (default for printed text)")
        print("✓ TrOCR will load on-demand for handwritten text")
    
    def _load_trocr(self):
        """Lazy load TrOCR only when needed"""
        if self.trocr_loaded:
            return
        
        try:
            print("Loading TrOCR model for handwritten text...")
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            import torch
            
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.trocr_processor = TrOCRProcessor.from_pretrained(self.model_name)
            self.trocr_model = VisionEncoderDecoderModel.from_pretrained(self.model_name)
            self.trocr_model.to(self.device)
            self.trocr_model.eval()
            self.trocr_loaded = True
            print(f"✓ TrOCR loaded on {self.device}")
        except Exception as e:
            print(f"❌ Failed to load TrOCR: {e}")
    
    def _preprocess_for_tesseract(self, image: Image.Image) -> Image.Image:
        """
        Minimal preprocessing for Tesseract
        
        Tesseract has built-in preprocessing, so we keep it light
        """
        # Convert to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Check quality
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Light denoising only
        if blur_score < 500:
            denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
        else:
            denoised = gray
        
        # Convert back to RGB
        rgb = cv2.cvtColor(denoised, cv2.COLOR_GRAY2RGB)
        return Image.fromarray(rgb)
    
    def extract_text_tesseract(self, image: Image.Image) -> str:
        """Extract text using Tesseract OCR"""
        try:
            # Minimal preprocessing
            processed = self._preprocess_for_tesseract(image)
            
            # Configure Tesseract
            config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(processed, config=config, lang='eng')
            
            # If empty, try different PSM
            if not text.strip():
                print("   Trying PSM 3...")
                config = r'--oem 3 --psm 3'
                text = pytesseract.image_to_string(processed, config=config, lang='eng')
            
            return text.strip()
        except Exception as e:
            print(f"❌ Tesseract error: {e}")
            return ""
    
    def extract_text_trocr(self, image: Image.Image) -> str:
        """Extract text using TrOCR (for handwritten)"""
        if not self.trocr_loaded:
            self._load_trocr()
        
        if not self.trocr_loaded:
            return ""
        
        try:
            import torch
            
            pixel_values = self.trocr_processor(
                images=image,
                return_tensors="pt"
            ).pixel_values.to(self.device)
            
            with torch.no_grad():
                generated_ids = self.trocr_model.generate(
                    pixel_values,
                    max_new_tokens=100
                )
            
            text = self.trocr_processor.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0]
            
            return text.strip()
        except Exception as e:
            print(f"❌ TrOCR error: {e}")
            return ""
    
    def extract_text(self, image: Image.Image, use_handwritten: bool = False) -> str:
        """Extract text from image"""
        if use_handwritten:
            print("   Using TrOCR (handwritten mode)")
            return self.extract_text_trocr(image)
        else:
            print("   Using Tesseract (printed text mode)")
            return self.extract_text_tesseract(image)
    
    def extract_fields(
        self,
        image: Image.Image,
        use_handwritten: bool = False
    ) -> Tuple[Dict, str]:
        """Extract structured fields from document"""
        print("=" * 80)
        print(f"🔍 OCR Mode: {'TrOCR (Handwritten)' if use_handwritten else 'Tesseract (Printed)'}")
        
        # Extract raw text
        raw_text = self.extract_text(image, use_handwritten=use_handwritten)
        
        # Debug output
        print("📄 RAW OCR OUTPUT:")
        print("-" * 80)
        if raw_text:
            preview = raw_text[:300] + "..." if len(raw_text) > 300 else raw_text
            print(preview)
            print(f"\nTotal: {len(raw_text)} characters, {len(raw_text.split())} words")
        else:
            print("⚠️ NO TEXT EXTRACTED!")
        print("-" * 80)
        
        # Parse structured fields
        fields = self._parse_fields(raw_text)
        
        print("📋 PARSED STRUCTURED FIELDS:")
        if fields:
            for key, value in fields.items():
                print(f"  ✓ {key}: {value}")
        else:
            print("  ⚠️ No structured fields found")
        print("=" * 80)
        
        return fields, raw_text
    
    def _parse_fields(self, text: str) -> Dict:
        """Parse extracted text into structured fields"""
        if not text or len(text) < 5:
            return {}
        
        fields = {}
        
        # Name
        name_patterns = [
            r"(?:Applicant'?s?\s+)?(?:name|Name|NAME)[\s:]+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+)",
            r"(?:Student|Candidate)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                if 5 <= len(name) <= 50 and len(name.split()) >= 2:
                    fields["name"] = name
                    break
        
        # DOB
        dob_patterns = [
            r"(?:DOB|Date of Birth|Birth Date)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        ]
        for pattern in dob_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields["dob"] = self._normalize_date(match.group(1))
                break
        
        # Email
        email_match = re.search(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", text)
        if email_match:
            fields["email"] = email_match.group(0)
        
        # Phone
        phone_patterns = [
            r"(?:Mobile|Phone|Tel)[\s/]*(?:No\.?)?[\s:]*(\d{10})",
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                fields["phone"] = match.group(1)
                break
        
        # Gender
        gender_match = re.search(r"(?:Gender|Sex)[\s:]*\b(MALE|FEMALE|Male|Female)\b", text)
        if gender_match:
            fields["gender"] = gender_match.group(1).capitalize()
        
        # Address
        address_match = re.search(
            r"(?:Address|ADDRESS)[\s:]+(.+?)(?=\n(?:PIN|Email|Phone|$))",
            text,
            re.IGNORECASE | re.DOTALL
        )
        if address_match:
            address = " ".join(address_match.group(1).split())
            if 15 <= len(address) <= 300:
                fields["address"] = address
        
        return fields
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date to YYYY-MM-DD"""
        formats = [
            "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y",
            "%d/%m/%y", "%Y-%m-%d"
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        return date_str
