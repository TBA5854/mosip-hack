import re
from typing import Dict, Optional


class FieldParser:
    """Advanced field parsing with context awareness"""
    
    @staticmethod
    def parse_indian_documents(text: str) -> Dict:
        """Parse India-specific documents (Aadhaar, PAN, etc.)"""
        fields = {}
        
        # Aadhaar number
        aadhaar = re.search(r"\b\d{4}\s?\d{4}\s?\d{4}\b", text)
        if aadhaar:
            fields["aadhaar"] = aadhaar.group(0).replace(" ", "")
        
        # PAN number
        pan = re.search(r"\b[A-Z]{5}\d{4}[A-Z]\b", text)
        if pan:
            fields["pan"] = pan.group(0)
        
        return fields
    
    @staticmethod
    def parse_address_components(address: str) -> Dict:
        """Parse address into components"""
        components = {}
        
        # Pincode
        pincode = re.search(r"\b\d{6}\b", address)
        if pincode:
            components["pincode"] = pincode.group(0)
        
        # State
        indian_states = [
            "Maharashtra", "Delhi", "Karnataka", "Tamil Nadu",
            "Uttar Pradesh", "Gujarat", "Rajasthan", "Kerala"
        ]
        for state in indian_states:
            if state.lower() in address.lower():
                components["state"] = state
                break
        
        return components
