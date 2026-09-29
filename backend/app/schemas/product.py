from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class ProductVariantBase(BaseModel):
    sku: str
    ram: str
    rom: str
    color: str
    base_price: float

class ProductVariantResponse(ProductVariantBase):
    id: int
    product_id: int

    model_config = {"from_attributes": True}

class ProductBase(BaseModel):
    name: str
    release_date: date

class ProductResponse(ProductBase):
    id: int
    brand_id: int
    variants: List[ProductVariantResponse] = []

    model_config = {"from_attributes": True}
