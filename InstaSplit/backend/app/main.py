"""
FastAPI application for receipt extraction and bill splitting.
OCR-first pipeline with LLM fallback.
"""
import os
import time
import tempfile
import math
import json
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import io

from .schemas import (
    ExtractionResponse, SplitRequest, SplitResponse, Receipt, Confidence
)
from .ocr import get_ocr_extractor
from .extraction import ReceiptParser, extract_receipt_with_llm
from .splitting import calculate_split
from .utils.image_processing import preprocess_image


def sanitize_floats(obj):
    """Recursively replace NaN and Infinity with None in nested structures."""
    if isinstance(obj, dict):
        return {k: sanitize_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_floats(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj

# Configuration
MAX_UPLOAD_SIZE = 8 * 1024 * 1024  # 8 MB
CONFIDENCE_THRESHOLD = 0.7  # Threshold to skip LLM


# Custom JSON encoder to handle NaN and Infinity
class SafeJSONEncoder(json.JSONEncoder):
    def encode(self, o):
        if isinstance(o, float):
            if math.isnan(o) or math.isinf(o):
                return 'null'
        return super().encode(o)
    
    def iterencode(self, o, _one_shot=False):
        for chunk in super().iterencode(o, _one_shot):
            yield chunk.replace('NaN', 'null').replace('Infinity', 'null').replace('-Infinity', 'null')


# Initialize FastAPI app
app = FastAPI(
    title="InstaSplit API",
    description="Receipt extraction and bill splitting API with OCR-first pipeline",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "InstaSplit API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    # Check OCR availability
    try:
        ocr = get_ocr_extractor()
        ocr_status = ocr.name
    except Exception as e:
        ocr_status = f"unavailable: {str(e)}"
    
    # Check LLM availability
    llm_status = "configured" if os.getenv("ANTHROPIC_API_KEY") else "missing API key"
    
    return {
        "status": "healthy",
        "ocr": ocr_status,
        "llm": llm_status,
        "vision_fallback": os.getenv("ALLOW_VISION_FALLBACK", "false")
    }


@app.post("/receipt/extract", response_model=ExtractionResponse)
async def extract_receipt(file: UploadFile = File(...)):
    """
    Extract receipt data from uploaded image.
    OCR-first pipeline with LLM fallback.
    
    Args:
        file: Uploaded image file (JPG, PNG, or HEIC)
        
    Returns:
        ExtractionResponse with receipt data
    """
    start_time = time.time()
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read file
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
    
    # Validate size
    if len(contents) > MAX_UPLOAD_SIZE:
        size_mb = len(contents) / (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {size_mb:.2f}MB (max 8MB)"
        )
    
    try:
        # Step 1: Preprocess image
        image, preprocessing_info = preprocess_image(contents, file.filename or "image.jpg")
        
        # Step 2: Run OCR
        ocr_extractor = get_ocr_extractor()
        ocr_result = ocr_extractor.extract_text(image)
        
        # Debug: Print OCR results
        print(f"\n{'='*60}")
        print(f"OCR Method: {ocr_result.method}")
        print(f"OCR Confidence: {ocr_result.confidence}")
        print(f"OCR Text Length: {len(ocr_result.text) if ocr_result.text else 0}")
        print(f"OCR Text Preview:\n{ocr_result.text[:500] if ocr_result.text else 'None'}")
        print(f"{'='*60}\n")
        
        if not ocr_result.text or len(ocr_result.text.strip()) < 20:
            # OCR produced very little text - try vision fallback if enabled
            if os.getenv("ALLOW_VISION_FALLBACK", "false").lower() == "true":
                receipt, llm_metadata = extract_receipt_with_llm(
                    image=image,
                    use_vision=True
                )
                if receipt:
                    processing_time = (time.time() - start_time) * 1000
                    return ExtractionResponse(
                        receipt=receipt,
                        processing_time_ms=processing_time,
                        ocr_method=ocr_result.method,
                        llm_used=True,
                        vision_used=True
                    )
            
            raise HTTPException(
                status_code=422,
                detail="Could not extract sufficient text from image. Please try a clearer photo."
            )
        
        # Step 3: Try deterministic parsing
        parser = ReceiptParser()
        receipt, confidence = parser.parse(ocr_result.text, ocr_result.confidence)
        
        llm_used = False
        vision_used = False
        
        # Step 4: Use LLM if parsing failed or confidence low
        if not receipt or confidence.overall < CONFIDENCE_THRESHOLD:
            print(f"🤖 LLM Extraction triggered (confidence: {confidence.overall if confidence else 'N/A'})")
            receipt, llm_metadata = extract_receipt_with_llm(ocr_text=ocr_result.text)
            llm_used = True
            
            print(f"LLM Result: {llm_metadata}")
            print(f"Receipt extracted: {receipt is not None}")
            
            if not receipt:
                print(f"❌ LLM extraction failed!")
                raise HTTPException(
                    status_code=422,
                    detail="Failed to extract valid receipt data. Please verify the image is clear and contains a receipt."
                )
            
            # Update confidence based on LLM success
            receipt.confidence = Confidence(
                overall=0.8,  # LLM extraction gets reasonable confidence
                fields={'llm_extraction': 1.0}
            )
        else:
            receipt.confidence = confidence
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Create response
        response = ExtractionResponse(
            receipt=receipt,
            processing_time_ms=processing_time,
            ocr_method=ocr_result.method,
            llm_used=llm_used,
            vision_used=vision_used
        )
        
        # Sanitize and return as JSON to avoid float serialization issues
        response_dict = response.model_dump()
        sanitized = sanitize_floats(response_dict)
        return JSONResponse(content=sanitized)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal error during extraction: {str(e)}"
        )


@app.post("/split/calculate", response_model=SplitResponse)
async def calculate_bill_split(request: SplitRequest = Body(...)):
    """
    Calculate bill split among group members.
    
    Args:
        request: SplitRequest with receipt, group, assignments, and options
        
    Returns:
        SplitResponse with per-person breakdowns
    """
    start_time = time.time()
    
    try:
        # Validate that all items are assigned
        assigned_items = {a.item_id for a in request.assignments}
        all_items = {item.id for item in request.receipt.items}
        
        # It's OK if not all items are assigned (user may skip some)
        # But warn if assignments reference non-existent items
        invalid_assignments = assigned_items - all_items
        if invalid_assignments:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid item assignments: {invalid_assignments}"
            )
        
        # Calculate split
        breakdowns, reconciliation = calculate_split(
            receipt=request.receipt,
            group=request.group,
            assignments=request.assignments,
            options=request.options
        )
        
        calculation_time = (time.time() - start_time) * 1000
        
        return SplitResponse(
            breakdowns=breakdowns,
            reconciliation=reconciliation,
            calculation_time_ms=calculation_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Calculation error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
