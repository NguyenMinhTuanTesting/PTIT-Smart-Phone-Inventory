from pydantic import BaseModel, Field, field_validator
from typing import List
import re

class InboundRequest(BaseModel):
    variant_id: int = Field(..., gt=0)
    supplier: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    imeis: List[str] = Field(..., min_length=1)

    @field_validator('imeis')
    @classmethod
    def validate_imei(cls, v: List[str]) -> List[str]:
        for imei in v:
            if not re.match(r'^[A-Za-z0-9]{15}$', imei):
                raise ValueError("IMEI must be exactly 15 alphanumeric characters")
        return v

class OutboundRequest(BaseModel):
    variant_id: int = Field(..., gt=0)
    customer_info: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    discount: float = Field(0.0, ge=0.0, lt=1.0)

class StockResponse(BaseModel):
    variant_id: int
    sku: str
    in_stock_quantity: int
