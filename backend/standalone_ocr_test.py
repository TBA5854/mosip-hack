#!/usr/bin/env python3
"""
Standalone OCR Test Script
Tests both Tesseract and TrOCR independently
No FastAPI, no server - just pure OCR testing

Usage:
    python standalone_ocr_test.py <file_path>
    python standalone_ocr_test.py document.pdf
    python standalone_ocr_test.py image.png
"""

import sys
import os
import json
from pathlib import Path
from PIL import Image
import pytesseract
import cv2
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    import torch
    TROCR_AVAILABLE = True
except ImportError:
    TROCR_AVAILABLE = False
    print("⚠️ TrOCR not available (transformers/torch not installed)")

try:
    from pdf2image import convert_from_path
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("⚠️ PDF support not available (pdf2image not installed)")


class StandaloneOCR:
    """Standalone OCR tester"""
    
    def __init__(self):
        self.trocr_processor = None
        self.trocr_model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu" if TROCR_AVAILABLE else None
        
        if TROCR_AVAILABLE:
            print("Loading TrOCR model...")
            self.trocr_processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
            self.trocr_model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')
            if self.device:
                self.trocr_model.to(self.device)
                self.trocr_model.eval()
            print(f"✓ TrOCR loaded on {self.device}")
    
    def load_document(self, file_path):
        """Load PDF or image"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        ext = file_path.suffix.lower()
        
        if ext == '.pdf':
            if not PDF_SUPPORT:
                raise RuntimeError("PDF support not available. Install pdf2image.")
            print(f"Converting PDF to images...")
            images = convert_from_path(str(file_path), dpi=300)
            print(f"✓ Loaded {len(images)} pages from PDF")
            return images
        
        elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            image = Image.open(file_path)
            print(f"✓ Loaded image: {image.size} {image.mode}")
            return [image]
        
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def preprocess_image(self, image):
        """Preprocess image for better OCR"""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        
        # Convert back to RGB for TrOCR
        rgb_image = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
        
        return Image.fromarray(rgb_image)
    
    def calculate_quality_score(self, image):
        """Calculate image quality metrics"""
        img_array = np.array(image)
        
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Blur score (Laplacian variance)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Brightness
        brightness = np.mean(gray)
        
        # Contrast
        contrast = np.std(gray)
        
        return {
            "blur_score": round(blur_score, 2),
            "blur_status": "Good" if blur_score > 100 else "Blurry",
            "brightness": round(brightness, 2),
            "brightness_status": "Good" if 50 <= brightness <= 200 else ("Too Dark" if brightness < 50 else "Too Bright"),
            "contrast": round(contrast, 2)
        }
    
    def ocr_with_tesseract(self, image):
        """Extract text using Tesseract"""
        try:
            config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, config=config)
            return text.strip()
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def ocr_with_trocr(self, image):
        """Extract text using TrOCR"""
        if not TROCR_AVAILABLE:
            return "TrOCR not available"
        
        try:
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
            return f"ERROR: {str(e)}"
    
    def test_document(self, file_path):
        """Test OCR on document and return JSON results"""
        print("\n" + "="*80)
        print(f"TESTING OCR ON: {file_path}")
        print("="*80 + "\n")
        
        # Load document
        images = self.load_document(file_path)
        
        results = {
            "file_path": str(file_path),
            "total_pages": len(images),
            "pages": []
        }
        
        # Process each page
        for idx, image in enumerate(images):
            print(f"\n{'='*80}")
            print(f"PAGE {idx + 1}/{len(images)}")
            print(f"{'='*80}")
            
            page_result = {
                "page_number": idx + 1,
                "image_info": {
                    "size": image.size,
                    "mode": image.mode
                }
            }
            
            # Calculate quality
            print("\n1. Image Quality Analysis...")
            quality = self.calculate_quality_score(image)
            page_result["quality"] = quality
            print(f"   Blur: {quality['blur_score']} ({quality['blur_status']})")
            print(f"   Brightness: {quality['brightness']} ({quality['brightness_status']})")
            print(f"   Contrast: {quality['contrast']}")
            
            # Preprocess
            print("\n2. Preprocessing image...")
            preprocessed = self.preprocess_image(image)
            
            # Tesseract OCR
            print("\n3. Running Tesseract OCR...")
            tesseract_text = self.ocr_with_tesseract(preprocessed)
            page_result["tesseract_ocr"] = {
                "text": tesseract_text,
                "length": len(tesseract_text),
                "word_count": len(tesseract_text.split())
            }
            print(f"   Extracted {len(tesseract_text)} characters, {len(tesseract_text.split())} words")
            if tesseract_text:
                preview = tesseract_text[:200] + "..." if len(tesseract_text) > 200 else tesseract_text
                print(f"   Preview: {preview}")
            
            # TrOCR
            print("\n4. Running TrOCR...")
            trocr_text = self.ocr_with_trocr(preprocessed)
            page_result["trocr_ocr"] = {
                "text": trocr_text,
                "length": len(trocr_text)
            }
            print(f"   Extracted: {trocr_text}")
            
            results["pages"].append(page_result)
        
        return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python standalone_ocr_test.py <file_path>")
        print("\nExamples:")
        print("  python standalone_ocr_test.py document.pdf")
        print("  python standalone_ocr_test.py image.png")
        print("  python standalone_ocr_test.py ../samples/marks_card.pdf")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Initialize OCR
    ocr = StandaloneOCR()
    
    # Test
    results = ocr.test_document(file_path)
    
    # Print results
    print("\n" + "="*80)
    print("FINAL RESULTS (JSON)")
    print("="*80)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Save to file
    output_file = "ocr_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Results saved to: {output_file}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total_tesseract_chars = sum(p["tesseract_ocr"]["length"] for p in results["pages"])
    total_tesseract_words = sum(p["tesseract_ocr"]["word_count"] for p in results["pages"])
    
    print(f"Total Pages: {results['total_pages']}")
    print(f"Tesseract Total: {total_tesseract_chars} characters, {total_tesseract_words} words")
    print(f"Average per page: {total_tesseract_chars // results['total_pages']} chars")
    
    # Show first page full text
    if results["pages"]:
        print("\n" + "="*80)
        print("FIRST PAGE - FULL TEXT (Tesseract)")
        print("="*80)
        print(results["pages"][0]["tesseract_ocr"]["text"])


if __name__ == "__main__":
    main()
