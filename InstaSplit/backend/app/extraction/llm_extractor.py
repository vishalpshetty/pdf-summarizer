"""
LLM-based receipt extraction using Anthropic Claude via LangChain.
Only called when deterministic parsing fails or confidence is low.
"""
import os
import json
import base64
import time
from typing import Optional, Tuple
from PIL import Image
import io

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import ValidationError

from ..schemas import Receipt, Confidence


class LLMExtractor:
    """Claude-based receipt extraction with LangChain tracing."""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        # Initialize LangChain Anthropic client
        # Using Claude 3 Haiku (available with current API key)
        self.llm = ChatAnthropic(
            model="claude-3-haiku-20240307",
            anthropic_api_key=self.api_key,
            temperature=0,
            max_tokens=4096
        )
        
        self.vision_enabled = os.getenv("ALLOW_VISION_FALLBACK", "false").lower() == "true"
    
    def _get_extraction_prompt(self) -> str:
        """Get the system prompt for receipt extraction."""
        return """You are a precise receipt data extraction assistant. Extract structured data from receipt text into strict JSON format.

Output ONLY valid JSON matching this exact schema:
{
  "merchant_name": "string or null",
  "currency": "USD",
  "items": [
    {
      "id": "uuid string",
      "name": "item name",
      "quantity": 1.0,
      "unit_price": 10.50 or null,
      "total_price": 10.50,
      "category": "food|drink|fee|discount|tax|tip|unknown"
    }
  ],
  "subtotal": 50.00 or null,
  "tax": 5.00 or null,
  "service_fee": 2.00 or null,
  "discount_total": -5.00 or null,
  "tip": 10.00 or null,
  "total": 62.00
}

Rules:
1. Generate unique UUIDs for each item id
2. Extract ALL line items as separate entries
3. quantity defaults to 1.0 if not specified
4. Classify items: food, drink, fee, discount, tax, tip, or unknown
5. total is REQUIRED and must be the final amount
6. All prices should be positive except discount_total (negative)
7. If a field is unclear, use null (not 0)
8. Return ONLY the JSON object, no markdown, no explanation"""
    
    def extract_from_text(self, ocr_text: str) -> Tuple[Optional[Receipt], dict]:
        """
        Extract receipt data from OCR text using Claude (text-only).
        
        Args:
            ocr_text: Raw OCR text
            
        Returns:
            Tuple of (Receipt or None, extraction metadata)
        """
        start_time = time.time()
        metadata = {
            'method': 'llm_text',
            'model': 'claude-3-5-sonnet',
            'success': False,
            'tokens_used': 0,
            'latency_ms': 0,
            'retry_count': 0
        }
        
        try:
            # Build messages
            messages = [
                SystemMessage(content=self._get_extraction_prompt()),
                HumanMessage(content=f"Extract receipt data from this text:\n\n{ocr_text}")
            ]
            
            # Call LLM with retry logic
            max_retries = 3
            receipt = None
            
            for attempt in range(max_retries):
                try:
                    response = self.llm.invoke(messages)
                    
                    # Track token usage if available
                    if hasattr(response, 'response_metadata'):
                        usage = response.response_metadata.get('usage', {})
                        metadata['tokens_used'] = usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
                    
                    # Parse JSON response
                    content = response.content.strip()
                    
                    # Remove markdown code blocks if present
                    if content.startswith('```'):
                        content = content.split('```')[1]
                        if content.startswith('json'):
                            content = content[4:]
                        content = content.strip()
                    
                    receipt_data = json.loads(content)
                    
                    # Validate with Pydantic
                    receipt = Receipt(**receipt_data)
                    receipt.raw_text = ocr_text
                    
                    metadata['success'] = True
                    break
                    
                except (json.JSONDecodeError, ValidationError) as e:
                    metadata['retry_count'] = attempt + 1
                    if attempt == max_retries - 1:
                        metadata['error'] = str(e)
                        raise
                    # Try again
                    continue
            
            metadata['latency_ms'] = (time.time() - start_time) * 1000
            return receipt, metadata
            
        except Exception as e:
            metadata['latency_ms'] = (time.time() - start_time) * 1000
            metadata['error'] = str(e)
            return None, metadata
    
    def extract_from_vision(self, image: Image.Image) -> Tuple[Optional[Receipt], dict]:
        """
        Extract receipt data directly from image using Claude vision (last resort).
        
        Args:
            image: PIL Image
            
        Returns:
            Tuple of (Receipt or None, extraction metadata)
        """
        if not self.vision_enabled:
            return None, {'method': 'vision', 'error': 'Vision fallback disabled'}
        
        start_time = time.time()
        metadata = {
            'method': 'llm_vision',
            'model': 'claude-3-5-sonnet',
            'success': False,
            'tokens_used': 0,
            'latency_ms': 0,
            'retry_count': 0
        }
        
        try:
            # Convert image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Build vision message
            messages = [
                SystemMessage(content=self._get_extraction_prompt()),
                HumanMessage(content=[
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "Extract all receipt data from this image into the JSON format specified."
                    }
                ])
            ]
            
            # Call vision model
            response = self.llm.invoke(messages)
            
            # Track usage
            if hasattr(response, 'response_metadata'):
                usage = response.response_metadata.get('usage', {})
                metadata['tokens_used'] = usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
            
            # Parse response
            content = response.content.strip()
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()
            
            receipt_data = json.loads(content)
            receipt = Receipt(**receipt_data)
            
            metadata['success'] = True
            metadata['latency_ms'] = (time.time() - start_time) * 1000
            
            return receipt, metadata
            
        except Exception as e:
            metadata['latency_ms'] = (time.time() - start_time) * 1000
            metadata['error'] = str(e)
            return None, metadata


def extract_receipt_with_llm(
    ocr_text: Optional[str] = None,
    image: Optional[Image.Image] = None,
    use_vision: bool = False
) -> Tuple[Optional[Receipt], dict]:
    """
    Convenience function to extract receipt using LLM.
    
    Args:
        ocr_text: OCR text (for text-based extraction)
        image: PIL Image (for vision-based extraction)
        use_vision: Force vision model usage
        
    Returns:
        Tuple of (Receipt or None, metadata)
    """
    extractor = LLMExtractor()
    
    if use_vision and image:
        return extractor.extract_from_vision(image)
    elif ocr_text:
        return extractor.extract_from_text(ocr_text)
    else:
        return None, {'error': 'No input provided'}
