"""
Deterministic parser for extracting receipt data from OCR text.
Uses regex and heuristics before calling LLM.
"""
import re
import uuid
from typing import Dict, List, Optional, Tuple
from ..schemas import Receipt, ReceiptItem, Confidence, CategoryEnum


class ReceiptParser:
    """Deterministic parser for receipt OCR text."""
    
    # Common receipt patterns
    TOTAL_PATTERNS = [
        r'total[\s:]*\$?\s*(\d+\.?\d*)',
        r'amount due[\s:]*\$?\s*(\d+\.?\d*)',
        r'balance[\s:]*\$?\s*(\d+\.?\d*)',
    ]
    
    SUBTOTAL_PATTERNS = [
        r'sub[\s-]?total[\s:]*\$?\s*(\d+\.?\d*)',
        r'subtotal[\s:]*\$?\s*(\d+\.?\d*)',
    ]
    
    TAX_PATTERNS = [
        r'tax[\s:]*\$?\s*(\d+\.?\d*)',
        r'sales tax[\s:]*\$?\s*(\d+\.?\d*)',
    ]
    
    TIP_PATTERNS = [
        r'tip[\s:]*\$?\s*(\d+\.?\d*)',
        r'gratuity[\s:]*\$?\s*(\d+\.?\d*)',
    ]
    
    # Line item pattern: item name followed by price
    ITEM_PATTERN = r'^(.+?)\s+\$?\s*(\d+\.?\d{0,2})$'
    
    def __init__(self):
        pass
    
    def _extract_field(self, text: str, patterns: List[str]) -> Optional[float]:
        """Extract a numeric field using regex patterns."""
        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None
    
    def _extract_merchant_name(self, lines: List[str]) -> Optional[str]:
        """Try to extract merchant name from first few lines."""
        # Usually merchant name is in first 3 lines
        for line in lines[:3]:
            line = line.strip()
            # Skip lines that are just numbers or addresses
            if line and not re.match(r'^\d+$', line) and len(line) > 3:
                # Skip if it looks like an address (contains numbers and street words)
                if not re.search(r'\d+\s+(st|street|ave|avenue|rd|road|blvd)', line, re.I):
                    return line
        return None
    
    def _extract_items(self, lines: List[str]) -> List[ReceiptItem]:
        """Extract line items from text."""
        items = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines that look like totals or metadata
            lower_line = line.lower()
            if any(kw in lower_line for kw in ['total', 'tax', 'tip', 'subtotal', 'gratuity', 'payment', 'change']):
                continue
            
            # Try to match item pattern
            match = re.match(self.ITEM_PATTERN, line)
            if match:
                name = match.group(1).strip()
                price_str = match.group(2)
                
                try:
                    price = float(price_str)
                    
                    # Skip if price seems unreasonable for a single item
                    if 0.01 <= price <= 500:
                        item = ReceiptItem(
                            id=str(uuid.uuid4()),
                            name=name,
                            quantity=1.0,
                            unit_price=price,
                            total_price=price,
                            category=self._classify_item(name)
                        )
                        items.append(item)
                except ValueError:
                    continue
        
        return items
    
    def _classify_item(self, name: str) -> CategoryEnum:
        """Simple classification of items."""
        name_lower = name.lower()
        
        if any(kw in name_lower for kw in ['drink', 'soda', 'juice', 'coffee', 'tea', 'water', 'beer', 'wine']):
            return CategoryEnum.DRINK
        elif any(kw in name_lower for kw in ['fee', 'service', 'delivery']):
            return CategoryEnum.FEE
        elif any(kw in name_lower for kw in ['discount', 'coupon', 'promo']):
            return CategoryEnum.DISCOUNT
        else:
            return CategoryEnum.FOOD
    
    def _calculate_confidence(self, receipt: Receipt, text: str) -> Confidence:
        """Calculate confidence score for the extraction."""
        scores = {}
        
        # Check if we found a total
        if receipt.total > 0:
            scores['total'] = 1.0
        else:
            scores['total'] = 0.0
        
        # Check if we found items
        if receipt.items:
            scores['items'] = min(1.0, len(receipt.items) / 5.0)
        else:
            scores['items'] = 0.0
        
        # Check if items sum is close to subtotal/total
        items_sum = sum(item.total_price for item in receipt.items)
        
        if receipt.subtotal:
            diff = abs(items_sum - receipt.subtotal)
            tolerance = receipt.subtotal * 0.1  # 10% tolerance
            scores['items_sum_match'] = max(0.0, 1.0 - (diff / max(tolerance, 1.0)))
        else:
            scores['items_sum_match'] = 0.5
        
        # Check text quality
        numeric_lines = sum(1 for line in text.split('\n') if re.search(r'\d', line))
        total_lines = len([l for l in text.split('\n') if l.strip()])
        
        if total_lines > 0:
            scores['text_quality'] = min(1.0, numeric_lines / total_lines)
        else:
            scores['text_quality'] = 0.0
        
        # Overall confidence
        overall = sum(scores.values()) / len(scores) if scores else 0.0
        
        return Confidence(overall=overall, fields=scores)
    
    def parse(self, ocr_text: str, ocr_confidence: float) -> Tuple[Optional[Receipt], Confidence]:
        """
        Parse OCR text into a Receipt object.
        
        Args:
            ocr_text: Raw OCR text
            ocr_confidence: OCR engine's confidence score
            
        Returns:
            Tuple of (Receipt or None, Confidence)
        """
        if not ocr_text or len(ocr_text.strip()) < 10:
            return None, Confidence(overall=0.0, fields={'text_length': 0.0})
        
        lines = ocr_text.split('\n')
        
        # Extract fields
        merchant_name = self._extract_merchant_name(lines)
        total = self._extract_field(ocr_text, self.TOTAL_PATTERNS)
        subtotal = self._extract_field(ocr_text, self.SUBTOTAL_PATTERNS)
        tax = self._extract_field(ocr_text, self.TAX_PATTERNS)
        tip = self._extract_field(ocr_text, self.TIP_PATTERNS)
        items = self._extract_items(lines)
        
        # Must have total and at least one item
        if not total or not items:
            return None, Confidence(overall=0.0, fields={'has_total': 1.0 if total else 0.0, 'has_items': 1.0 if items else 0.0})
        
        # Create receipt
        receipt = Receipt(
            merchant_name=merchant_name,
            currency="USD",
            items=items,
            subtotal=subtotal,
            tax=tax,
            service_fee=None,
            discount_total=None,
            tip=tip,
            total=total,
            raw_text=ocr_text
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(receipt, ocr_text)
        
        # Factor in OCR confidence
        confidence.overall = (confidence.overall + ocr_confidence) / 2.0
        confidence.fields['ocr_confidence'] = ocr_confidence
        
        return receipt, confidence
