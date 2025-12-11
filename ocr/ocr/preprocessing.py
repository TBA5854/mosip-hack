import cv2
import numpy as np
from PIL import Image


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess image for OCR
    
    IMPORTANT: Keep preprocessing MINIMAL for Tesseract
    Tesseract works best with clean, readable images - not over-processed ones
    """
    # Convert to RGB first
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert to numpy array
    img_array = np.array(image)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # OPTION 1: Minimal preprocessing (RECOMMENDED for most documents)
    # Just denoise lightly
    denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
    
    # Convert back to RGB (Tesseract expects RGB)
    result = cv2.cvtColor(denoised, cv2.COLOR_GRAY2RGB)
    
    return Image.fromarray(result)


def preprocess_image_aggressive(image: Image.Image) -> Image.Image:
    """
    Aggressive preprocessing for very poor quality images
    
    WARNING: Use only for extremely low-quality scans
    Normal documents will become UNREADABLE with this!
    """
    # Convert to RGB first
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert to numpy array
    img_array = np.array(image)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # Adaptive thresholding (THIS IS WHAT BREAKS YOUR TEXT!)
    thresh = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )
    
    # Deskew
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) > 0:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        if abs(angle) > 0.5:
            (h, w) = thresh.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            thresh = cv2.warpAffine(
                thresh,
                M,
                (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
    
    # Convert back to RGB
    rgb_image = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
    
    return Image.fromarray(rgb_image)


def preprocess_for_tesseract(image: Image.Image) -> Image.Image:
    """
    Optimal preprocessing for Tesseract OCR
    
    Tesseract has built-in preprocessing, so we keep it minimal:
    - Convert to RGB
    - Light denoising only
    - NO thresholding (Tesseract does this internally)
    """
    # Convert to RGB
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # For high-quality images (like your passport), return as-is!
    # Tesseract works best with original images
    img_array = np.array(image)
    
    # Check if image is already clean (high contrast, not blurry)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    if blur_score > 500:  # Good quality image
        # Minimal processing - just slight denoising
        denoised = cv2.fastNlMeansDenoising(gray, None, h=5, templateWindowSize=7, searchWindowSize=21)
        result = cv2.cvtColor(denoised, cv2.COLOR_GRAY2RGB)
        return Image.fromarray(result)
    else:
        # Poor quality - denoise more
        denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
        result = cv2.cvtColor(denoised, cv2.COLOR_GRAY2RGB)
        return Image.fromarray(result)
