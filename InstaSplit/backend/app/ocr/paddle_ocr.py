"""
PaddleOCR implementation (preferred for accuracy).
"""
import numpy as np
from PIL import Image
from .base import OCRInterface, OCRResult


class PaddleOCRExtractor(OCRInterface):
    """PaddleOCR-based text extraction."""
    
    def __init__(self):
        self._ocr = None
        self._available = None
    
    def is_available(self) -> bool:
        """Check if PaddleOCR is installed and working."""
        if self._available is not None:
            return self._available
            
        try:
            from paddleocr import PaddleOCR
            self._available = True
        except ImportError:
            self._available = False
        return self._available
    
    @property
    def name(self) -> str:
        return "PaddleOCR"
    
    def _get_ocr(self):
        """Lazy load PaddleOCR instance."""
        if self._ocr is None:
            from paddleocr import PaddleOCR
            # Use English model, disable angle classification for speed
            self._ocr = PaddleOCR(
                use_angle_cls=True,
                lang='en',
                show_log=False,
                use_gpu=False
            )
        return self._ocr
    
    def extract_text(self, image: Image.Image) -> OCRResult:
        """
        Extract text using PaddleOCR.
        
        Args:
            image: PIL Image
            
        Returns:
            OCRResult with extracted text
        """
        if not self.is_available():
            raise RuntimeError("PaddleOCR is not available")
        
        ocr = self._get_ocr()
        
        # Convert PIL Image to numpy array
        img_array = np.array(image)
        
        # Run OCR
        result = ocr.ocr(img_array, cls=True)
        
        if not result or not result[0]:
            return OCRResult(text="", confidence=0.0, method=self.name)
        
        # Extract text and confidence scores
        lines = []
        confidences = []
        
        for line in result[0]:
            if line:
                text = line[1][0]  # Text is at position [1][0]
                conf = line[1][1]  # Confidence is at position [1][1]
                lines.append(text)
                confidences.append(conf)
        
        # Combine lines with newlines
        full_text = "\n".join(lines)
        
        # Calculate average confidence
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return OCRResult(
            text=full_text,
            confidence=avg_confidence,
            method=self.name
        )
