"""
Pydantic models for receipt extraction and bill splitting.
All models enforce strict validation for production use.
"""
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import math


class CategoryEnum(str, Enum):
    """Item categories for classification."""
    FOOD = "food"
    DRINK = "drink"
    FEE = "fee"
    DISCOUNT = "discount"
    TAX = "tax"
    TIP = "tip"
    UNKNOWN = "unknown"


class Confidence(BaseModel):
    """Confidence scores for extraction quality."""
    overall: float = Field(..., ge=0.0, le=1.0, description="Overall extraction confidence")
    fields: Dict[str, float] = Field(default_factory=dict, description="Per-field confidence scores")
    
    @field_validator('overall')
    @classmethod
    def validate_overall(cls, v: float) -> float:
        """Ensure overall confidence is valid."""
        if math.isnan(v) or math.isinf(v):
            return 0.0
        return max(0.0, min(1.0, v))
    
    @field_validator('fields')
    @classmethod
    def validate_fields(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Ensure all field confidence scores are valid."""
        return {k: max(0.0, min(1.0, val)) if not (math.isnan(val) or math.isinf(val)) else 0.0 
                for k, val in v.items()}


class ReceiptItem(BaseModel):
    """Individual line item from a receipt."""
    id: str = Field(..., description="Unique identifier for the item")
    name: str = Field(..., min_length=1, description="Item name")
    quantity: float = Field(default=1.0, gt=0, description="Item quantity")
    unit_price: Optional[float] = Field(None, description="Price per unit")
    total_price: float = Field(..., description="Total price for this item")
    category: Optional[CategoryEnum] = Field(CategoryEnum.UNKNOWN, description="Item category")

    @field_validator('total_price', 'unit_price', 'quantity')
    @classmethod
    def validate_numeric_fields(cls, v: Optional[float], info) -> Optional[float]:
        """Ensure numeric fields are valid (no NaN or Infinity)."""
        if v is None:
            return None
        if math.isnan(v) or math.isinf(v):
            raise ValueError(f"{info.field_name} contains invalid value (NaN or Infinity)")
        if info.field_name == 'total_price':
            if v < -10000 or v > 10000:
                raise ValueError(f"total_price {v} is out of reasonable range")
        return round(v, 2) if info.field_name != 'quantity' else v


class Receipt(BaseModel):
    """Complete receipt with items and totals."""
    merchant_name: Optional[str] = Field(None, description="Restaurant/merchant name")
    currency: str = Field(default="USD", description="Currency code")
    items: List[ReceiptItem] = Field(..., min_length=1, description="List of receipt items")
    subtotal: Optional[float] = Field(None, description="Subtotal before tax/tip")
    tax: Optional[float] = Field(None, ge=0, description="Tax amount")
    service_fee: Optional[float] = Field(None, ge=0, description="Service or delivery fee")
    discount_total: Optional[float] = Field(None, description="Total discounts applied")
    tip: Optional[float] = Field(None, ge=0, description="Tip amount")
    total: float = Field(..., description="Final total amount")
    confidence: Confidence = Field(default_factory=lambda: Confidence(overall=0.0))
    raw_text: Optional[str] = Field(None, description="Raw OCR text")

    @field_validator('subtotal', 'tax', 'service_fee', 'discount_total', 'tip', 'total')
    @classmethod
    def validate_money_fields(cls, v: Optional[float], info) -> Optional[float]:
        """Ensure money fields are valid (no NaN or Infinity)."""
        if v is None:
            return None
        if math.isnan(v) or math.isinf(v):
            raise ValueError(f"{info.field_name} contains invalid value (NaN or Infinity)")
        if info.field_name == 'total':
            if v < 0 or v > 100000:
                raise ValueError(f"total {v} is out of reasonable range")
        return round(v, 2)


class ExtractionResponse(BaseModel):
    """Response from receipt extraction endpoint."""
    receipt: Receipt
    processing_time_ms: float
    ocr_method: str
    llm_used: bool
    vision_used: bool


class Person(BaseModel):
    """Individual person in the group."""
    id: str = Field(..., description="Unique person identifier")
    name: str = Field(..., min_length=1, description="Person's name")


class Group(BaseModel):
    """Group of people splitting the bill."""
    people: List[Person] = Field(..., min_length=1, description="List of people")


class SplitMode(str, Enum):
    """How to split an item among people."""
    EVEN = "even"
    QUANTITY = "quantity"
    FRACTION = "fraction"


class AssignmentShare(BaseModel):
    """How one person's share of an item is calculated."""
    person_id: str
    share_quantity: Optional[float] = Field(None, gt=0, description="Specific quantity for this person")
    share_fraction: Optional[float] = Field(None, gt=0, le=1, description="Fraction of item (0-1)")
    split_mode: SplitMode = Field(default=SplitMode.EVEN, description="How to split this item")


class ItemAssignments(BaseModel):
    """Assignment of items to people."""
    item_id: str
    shares: List[AssignmentShare] = Field(..., min_length=1)


class SplitOptions(BaseModel):
    """Options for bill splitting calculation."""
    tip_mode: Literal["proportional", "even"] = Field(default="proportional")
    discount_mode: Literal["proportional", "even"] = Field(default="proportional")
    tax_mode: Literal["proportional", "even"] = Field(default="proportional")


class SplitRequest(BaseModel):
    """Request to calculate bill split."""
    receipt: Receipt
    group: Group
    assignments: List[ItemAssignments]
    options: SplitOptions = Field(default_factory=SplitOptions)


class PersonBreakdown(BaseModel):
    """Breakdown of charges for one person."""
    person_id: str
    person_name: str
    items_subtotal: float
    discount_share: float
    tax_share: float
    fee_share: float
    tip_share: float
    total_owed: float
    item_details: List[Dict] = Field(default_factory=list)


class ReconciliationInfo(BaseModel):
    """Information about rounding reconciliation."""
    target_total: float
    calculated_total: float
    difference: float
    pennies_adjusted: int


class SplitResponse(BaseModel):
    """Response from bill split calculation."""
    breakdowns: List[PersonBreakdown]
    reconciliation: ReconciliationInfo
    calculation_time_ms: float
