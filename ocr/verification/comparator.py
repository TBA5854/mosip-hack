from rapidfuzz import fuzz
from typing import Dict, Any
import re
from datetime import datetime


class DataComparator:
    """Compare OCR-extracted data with user-submitted form data"""
    
    def __init__(self, fuzzy_threshold: int = 85):
        self.fuzzy_threshold = fuzzy_threshold
    
    def compare_data(
        self,
        ocr_data: Dict[str, Any],
        form_data: Dict[str, Any]
    ) -> Dict:
        """
        Compare OCR data with form data field by field
        
        Returns verification result with confidence scores
        """
        result = {"fields": {}}
        
        # Get all unique field names
        all_fields = set(ocr_data.keys()) | set(form_data.keys())
        
        for field in all_fields:
            ocr_value = ocr_data.get(field)
            form_value = form_data.get(field)
            
            # Skip if both are None
            if ocr_value is None and form_value is None:
                continue
            
            # Handle missing values
            if ocr_value is None or form_value is None:
                result["fields"][field] = {
                    "ocr_value": ocr_value,
                    "form_value": form_value,
                    "match": False,
                    "confidence": 0.0,
                    "reason": "Missing in OCR" if ocr_value is None else "Missing in form"
                }
                continue
            
            # Compare based on field type
            comparison = self._compare_field(field, ocr_value, form_value)
            result["fields"][field] = comparison
        
        return result
    
    def _compare_field(
        self,
        field_name: str,
        ocr_value: Any,
        form_value: Any
    ) -> Dict:
        """Compare individual field with appropriate method"""
        
        # Normalize values
        ocr_norm = self._normalize_value(ocr_value, field_name)
        form_norm = self._normalize_value(form_value, field_name)
        
        # Date comparison
        if field_name in ["dob", "date", "date_of_birth"]:
            return self._compare_dates(ocr_norm, form_norm, ocr_value, form_value)
        
        # Numeric comparison
        if isinstance(ocr_value, (int, float)) or isinstance(form_value, (int, float)):
            return self._compare_numeric(ocr_norm, form_norm, ocr_value, form_value)
        
        # Text comparison (fuzzy)
        return self._compare_text(ocr_norm, form_norm, ocr_value, form_value)
    
    def _normalize_value(self, value: Any, field_name: str) -> str:
        """Normalize value for comparison"""
        if value is None:
            return ""
        
        # Convert to string
        value_str = str(value).lower().strip()
        
        # Remove special characters for certain fields
        if field_name in ["name", "address"]:
            value_str = re.sub(r"[^\w\s]", "", value_str)
        
        # Remove spaces for phone numbers
        if field_name == "phone":
            value_str = re.sub(r"[^\d+]", "", value_str)
        
        # Normalize whitespace
        value_str = " ".join(value_str.split())
        
        return value_str
    
    def _compare_dates(
        self,
        ocr_norm: str,
        form_norm: str,
        ocr_orig: Any,
        form_orig: Any
    ) -> Dict:
        """Compare date values"""
        # Try to parse dates
        date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]
        
        ocr_date = None
        form_date = None
        
        for fmt in date_formats:
            try:
                ocr_date = datetime.strptime(str(ocr_orig), fmt)
                break
            except ValueError:
                continue
        
        for fmt in date_formats:
            try:
                form_date = datetime.strptime(str(form_orig), fmt)
                break
            except ValueError:
                continue
        
        if ocr_date and form_date:
            match = ocr_date == form_date
            confidence = 1.0 if match else 0.0
        else:
            # Fallback to string comparison
            match = ocr_norm == form_norm
            confidence = 1.0 if match else fuzz.ratio(ocr_norm, form_norm) / 100.0
        
        return {
            "ocr_value": ocr_orig,
            "form_value": form_orig,
            "match": match,
            "confidence": round(confidence, 3)
        }
    
    def _compare_numeric(
        self,
        ocr_norm: str,
        form_norm: str,
        ocr_orig: Any,
        form_orig: Any
    ) -> Dict:
        """Compare numeric values (strict equality)"""
        try:
            ocr_num = float(ocr_orig)
            form_num = float(form_orig)
            match = abs(ocr_num - form_num) < 0.01
            confidence = 1.0 if match else 0.0
        except (ValueError, TypeError):
            match = False
            confidence = 0.0
        
        return {
            "ocr_value": ocr_orig,
            "form_value": form_orig,
            "match": match,
            "confidence": confidence
        }
    
    def _compare_text(
        self,
        ocr_norm: str,
        form_norm: str,
        ocr_orig: Any,
        form_orig: Any
    ) -> Dict:
        """Compare text values using fuzzy matching"""
        # Exact match
        if ocr_norm == form_norm:
            return {
                "ocr_value": ocr_orig,
                "form_value": form_orig,
                "match": True,
                "confidence": 1.0
            }
        
        # Fuzzy match
        similarity = fuzz.ratio(ocr_norm, form_norm)
        match = similarity >= self.fuzzy_threshold
        
        return {
            "ocr_value": ocr_orig,
            "form_value": form_orig,
            "match": match,
            "confidence": round(similarity / 100.0, 3),
            "similarity_score": similarity
        }
