"""
Base OCR interface for pluggable OCR implementations.
"""
from abc import ABC, abstractmethod
from typing import Tuple
from PIL import Image


class OCRResult:
    """Result from OCR processing."""
    
    def __init__(self, text: str, confidence: float, method: str):
        self.text = text
        self.confidence = confidence
        self.method = method


class OCRInterface(ABC):
    """Abstract base class for OCR implementations."""
    
    @abstractmethod
    def extract_text(self, image: Image.Image) -> OCRResult:
        """
        Extract text from an image.
        
        Args:
            image: PIL Image object
            
        Returns:
            OCRResult with extracted text and confidence
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this OCR method is available/installed."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this OCR implementation."""
        pass
