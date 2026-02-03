"""
OCR module for text extraction from images.
"""
from .base import OCRInterface, OCRResult
from .paddle_ocr import PaddleOCRExtractor
from .tesseract_ocr import TesseractOCRExtractor


def get_ocr_extractor() -> OCRInterface:
    """
    Get the best available OCR extractor.
    Prefers PaddleOCR, falls back to Tesseract.
    """
    # Try PaddleOCR first (preferred)
    paddle = PaddleOCRExtractor()
    if paddle.is_available():
        return paddle
    
    # Fall back to Tesseract
    tesseract = TesseractOCRExtractor()
    if tesseract.is_available():
        return tesseract
    
    raise RuntimeError("No OCR implementation available. Install PaddleOCR or Tesseract.")


__all__ = [
    'OCRInterface',
    'OCRResult',
    'PaddleOCRExtractor',
    'TesseractOCRExtractor',
    'get_ocr_extractor'
]
