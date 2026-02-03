"""
Image preprocessing utilities for OCR optimization.
Handles HEIC conversion, rotation, resizing, and enhancement.
"""
import io
from PIL import Image, ImageEnhance
from typing import Tuple


MAX_DIMENSION = 1600  # Maximum long edge dimension


def convert_heic_to_jpg(image_bytes: bytes) -> bytes:
    """
    Convert HEIC image to JPG format.
    
    Args:
        image_bytes: Raw HEIC image bytes
        
    Returns:
        JPG image bytes
    """
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
    except ImportError:
        # If pillow_heif not available, try to open anyway
        pass
    
    img = Image.open(io.BytesIO(image_bytes))
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Save as JPG
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=90)
    output.seek(0)
    return output.read()


def apply_exif_rotation(image: Image.Image) -> Image.Image:
    """
    Rotate image according to EXIF orientation tag.
    
    Args:
        image: PIL Image
        
    Returns:
        Rotated image
    """
    try:
        from PIL import ImageOps
        return ImageOps.exif_transpose(image)
    except Exception:
        return image


def resize_image(image: Image.Image, max_dimension: int = MAX_DIMENSION) -> Image.Image:
    """
    Resize image if it exceeds max_dimension on any side.
    Maintains aspect ratio.
    
    Args:
        image: PIL Image
        max_dimension: Maximum dimension for longest side
        
    Returns:
        Resized image
    """
    width, height = image.size
    
    if width <= max_dimension and height <= max_dimension:
        return image
    
    # Calculate new dimensions maintaining aspect ratio
    if width > height:
        new_width = max_dimension
        new_height = int((max_dimension / width) * height)
    else:
        new_height = max_dimension
        new_width = int((max_dimension / height) * width)
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def enhance_image_for_ocr(image: Image.Image) -> Image.Image:
    """
    Apply light enhancement for better OCR results.
    Increases contrast and sharpness slightly.
    
    Args:
        image: PIL Image
        
    Returns:
        Enhanced image
    """
    # Convert to RGB if not already
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Slight contrast enhancement
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2)
    
    # Slight sharpness enhancement
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.1)
    
    return image


def preprocess_image(image_bytes: bytes, filename: str) -> Tuple[Image.Image, dict]:
    """
    Complete preprocessing pipeline for receipt images.
    
    Args:
        image_bytes: Raw image bytes
        filename: Original filename (to detect HEIC)
        
    Returns:
        Tuple of (processed PIL Image, processing info dict)
    """
    processing_info = {
        'original_format': None,
        'converted': False,
        'rotated': False,
        'resized': False,
        'enhanced': True,
        'original_size': None,
        'final_size': None
    }
    
    # Handle HEIC conversion
    if filename.lower().endswith('.heic'):
        processing_info['original_format'] = 'HEIC'
        image_bytes = convert_heic_to_jpg(image_bytes)
        processing_info['converted'] = True
    
    # Open image
    image = Image.open(io.BytesIO(image_bytes))
    processing_info['original_size'] = image.size
    
    # Apply EXIF rotation
    rotated = apply_exif_rotation(image)
    if rotated != image:
        processing_info['rotated'] = True
        image = rotated
    
    # Resize if needed
    original_size = image.size
    image = resize_image(image)
    if image.size != original_size:
        processing_info['resized'] = True
    
    # Enhance for OCR
    image = enhance_image_for_ocr(image)
    
    processing_info['final_size'] = image.size
    
    return image, processing_info
