from pydantic import BaseModel
from typing import List

class ReplenishmentSuggestion(BaseModel):
    variant_id: int
    sku: str
    current_stock: int
    predicted_demand: float
    safety_stock: float
    reorder_point: float
    suggested_order_qty: int
    priority: str

class POSKURequest(BaseModel):
    variant_id: int
    quantity: int

class CreatePORequest(BaseModel):
    items: List[POSKURequest]
    supplier: str = "Default Supplier"
