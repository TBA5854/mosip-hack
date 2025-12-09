import qrcode
from PIL import Image
import json
from typing import Dict
import gzip
import base64


class QRGenerator:
    """Generate QR codes for Verifiable Credentials"""
    
    def __init__(self, box_size: int = 10, border: int = 4):
        self.box_size = box_size
        self.border = border
    
    def generate_qr(self, vc_data: Dict, output_path: str) -> None:
        """
        Generate QR code from VC data and save to file
        
        Args:
            vc_data: Verifiable Credential dictionary
            output_path: Path to save QR code image
        """
        # Compress VC data
        compressed_data = self._compress_vc(vc_data)
        
        # Create QR code
        qr = qrcode.QRCode(
            version=None,  # Auto-determine version
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=self.box_size,
            border=self.border,
        )
        
        qr.add_data(compressed_data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)
    
    def generate_qr_with_logo(
        self,
        vc_data: Dict,
        output_path: str,
        logo_path: str = None
    ) -> None:
        """Generate QR code with embedded logo"""
        # Generate base QR
        self.generate_qr(vc_data, output_path)
        
        if logo_path:
            # Open QR and logo
            qr_img = Image.open(output_path)
            logo = Image.open(logo_path)
            
            # Calculate logo size (10% of QR size)
            qr_width, qr_height = qr_img.size
            logo_size = qr_width // 10
            
            # Resize logo
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            
            # Calculate position (center)
            logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
            
            # Paste logo
            qr_img.paste(logo, logo_pos)
            qr_img.save(output_path)
    
    def _compress_vc(self, vc_data: Dict) -> str:
        """Compress VC data for QR code"""
        # Convert to JSON
        json_str = json.dumps(vc_data, separators=(',', ':'))
        
        # Compress
        compressed = gzip.compress(json_str.encode('utf-8'))
        
        # Base64 encode
        encoded = base64.b64encode(compressed).decode('utf-8')
        
        return encoded
    
    @staticmethod
    def decompress_vc(compressed_data: str) -> Dict:
        """Decompress VC data from QR code"""
        # Base64 decode
        decoded = base64.b64decode(compressed_data)
        
        # Decompress
        decompressed = gzip.decompress(decoded)
        
        # Parse JSON
        vc_data = json.loads(decompressed.decode('utf-8'))
        
        return vc_data
