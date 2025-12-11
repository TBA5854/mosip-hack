import cv2
import numpy as np
from PIL import Image
from typing import Dict


class QualityScorer:
    """Score image quality for OCR suitability"""
    
    def __init__(
        self,
        blur_threshold: float = 100.0,
        brightness_min: int = 50,
        brightness_max: int = 200
    ):
        self.blur_threshold = blur_threshold
        self.brightness_min = brightness_min
        self.brightness_max = brightness_max
    
    def score_image(self, image: Image.Image) -> Dict:
        """
        Calculate comprehensive quality scores
        
        Returns:
            Dict with blur, brightness, contrast scores and recommendations
        """
        # Convert to OpenCV format
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Calculate metrics
        blur_score = self._calculate_blur(gray)
        brightness_score = self._calculate_brightness(gray)
        contrast_score = self._calculate_contrast(gray)
        
        # Determine quality status
        quality_status = self._get_quality_status(
            blur_score,
            brightness_score,
            contrast_score
        )
        
        return {
            "blur_score": round(blur_score, 2),
            "blur_status": "Good" if blur_score > self.blur_threshold else "Blurry",
            "brightness_score": round(brightness_score, 2),
            "brightness_status": self._get_brightness_status(brightness_score),
            "contrast_score": round(contrast_score, 2),
            "overall_quality": quality_status,
            "recommendations": self._get_recommendations(
                blur_score,
                brightness_score,
                contrast_score
            )
        }
    
    def _calculate_blur(self, gray_image: np.ndarray) -> float:
        """
        Calculate blur score using Laplacian variance
        Higher score = less blur (sharper image)
        """
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
        variance = laplacian.var()
        return variance
    
    def _calculate_brightness(self, gray_image: np.ndarray) -> float:
        """Calculate average brightness (0-255)"""
        return float(np.mean(gray_image))
    
    def _calculate_contrast(self, gray_image: np.ndarray) -> float:
        """Calculate contrast using standard deviation"""
        return float(np.std(gray_image))
    
    def _get_brightness_status(self, brightness: float) -> str:
        """Determine brightness status"""
        if brightness < self.brightness_min:
            return "Too Dark"
        elif brightness > self.brightness_max:
            return "Too Bright"
        else:
            return "Good"
    
    def _get_quality_status(
        self,
        blur: float,
        brightness: float,
        contrast: float
    ) -> str:
        """Determine overall quality status"""
        issues = []
        
        if blur < self.blur_threshold:
            issues.append("blurry")
        if brightness < self.brightness_min:
            issues.append("too dark")
        elif brightness > self.brightness_max:
            issues.append("too bright")
        if contrast < 30:
            issues.append("low contrast")
        
        if not issues:
            return "Excellent"
        elif len(issues) == 1:
            return "Good"
        elif len(issues) == 2:
            return "Fair"
        else:
            return "Poor"
    
    def _get_recommendations(
        self,
        blur: float,
        brightness: float,
        contrast: float
    ) -> list:
        """Generate recommendations for image improvement"""
        recommendations = []
        
        if blur < self.blur_threshold:
            recommendations.append("Hold camera steady or use better focus")
        
        if brightness < self.brightness_min:
            recommendations.append("Increase lighting or use flash")
        elif brightness > self.brightness_max:
            recommendations.append("Reduce lighting or adjust exposure")
        
        if contrast < 30:
            recommendations.append("Improve document contrast or lighting conditions")
        
        if not recommendations:
            recommendations.append("Image quality is good for OCR")
        
        return recommendations
