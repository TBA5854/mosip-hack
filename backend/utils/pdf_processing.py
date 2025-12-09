from pdf2image import convert_from_path
from PIL import Image
from typing import List
from pathlib import Path
import tempfile


class PDFProcessor:
    """Process PDF documents and convert to images"""
    
    def __init__(self, dpi: int = 300):
        self.dpi = dpi
    
    def convert_pdf_to_images(self, pdf_path: Path) -> List[Image.Image]:
        """
        Convert PDF to list of PIL Images
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of PIL Image objects (one per page)
        """
        try:
            images = convert_from_path(
                str(pdf_path),
                dpi=self.dpi,
                fmt='png'
            )
            return images
        except Exception as e:
            raise RuntimeError(f"PDF conversion failed: {str(e)}")
    
    def extract_page(self, pdf_path: Path, page_num: int) -> Image.Image:
        """Extract a specific page from PDF"""
        images = convert_from_path(
            str(pdf_path),
            dpi=self.dpi,
            first_page=page_num,
            last_page=page_num
        )
        return images[0] if images else None
    
    def get_page_count(self, pdf_path: Path) -> int:
        """Get number of pages in PDF"""
        from PyPDF2 import PdfReader
        try:
            reader = PdfReader(str(pdf_path))
            return len(reader.pages)
        except:
            # Fallback: convert and count
            images = self.convert_pdf_to_images(pdf_path)
            return len(images)
