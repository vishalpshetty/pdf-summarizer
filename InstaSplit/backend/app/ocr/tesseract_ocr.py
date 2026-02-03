"""
Tesseract OCR implementation (fallback).
"""
from PIL import Image
from .base import OCRInterface, OCRResult


class TesseractOCRExtractor(OCRInterface):
    """Tesseract-based text extraction."""
    
    def __init__(self):
        self._available = None
    
    def is_available(self) -> bool:
        """Check if Tesseract is installed."""
        if self._available is not None:
            return self._available
            
        try:
            import pytesseract
            # Try to get version to confirm it's working
            pytesseract.get_tesseract_version()
            self._available = True
        except Exception:
            self._available = False
        return self._available
    
    @property
    def name(self) -> str:
        return "Tesseract"
    
    def extract_text(self, image: Image.Image) -> OCRResult:
        """
        Extract text using Tesseract.
        
        Args:
            image: PIL Image
            
        Returns:
            OCRResult with extracted text
        """
        if not self.is_available():
            raise RuntimeError("Tesseract is not available")
        
        import pytesseract
        
        # Extract text
        text = pytesseract.image_to_string(image)
        
        # Get detailed data for confidence calculation
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        # Calculate average confidence from non-empty text blocks
        confidences = [
            float(conf) / 100.0
            for conf, text in zip(data['conf'], data['text'])
            if conf != -1 and text.strip()
        ]
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return OCRResult(
            text=text.strip(),
            confidence=avg_confidence,
            method=self.name
        )
