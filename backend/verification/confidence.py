from typing import Dict, List


class ConfidenceCalculator:
    """Calculate confidence scores for verification results"""
    
    @staticmethod
    def calculate_field_confidence(
        ocr_value: str,
        form_value: str,
        match_score: float
    ) -> Dict:
        """Calculate detailed confidence metrics for a field"""
        return {
            "match_score": match_score,
            "length_difference": abs(len(str(ocr_value)) - len(str(form_value))),
            "confidence_level": ConfidenceCalculator._get_confidence_level(match_score)
        }
    
    @staticmethod
    def _get_confidence_level(score: float) -> str:
        """Convert numeric score to confidence level"""
        if score >= 0.95:
            return "Very High"
        elif score >= 0.85:
            return "High"
        elif score >= 0.70:
            return "Medium"
        elif score >= 0.50:
            return "Low"
        else:
            return "Very Low"
    
    @staticmethod
    def calculate_overall_confidence(field_results: Dict) -> Dict:
        """Calculate overall confidence across all fields"""
        scores = [
            result["confidence"]
            for result in field_results.values()
            if "confidence" in result
        ]
        
        if not scores:
            return {"overall_score": 0.0, "level": "No Data"}
        
        avg_score = sum(scores) / len(scores)
        
        return {
            "overall_score": round(avg_score, 3),
            "level": ConfidenceCalculator._get_confidence_level(avg_score),
            "fields_checked": len(scores),
            "fields_matched": sum(1 for s in scores if s >= 0.85)
        }
