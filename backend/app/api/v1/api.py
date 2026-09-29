from fastapi import APIRouter
from .endpoints import products, inventory, replenishment

api_router = APIRouter()
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(replenishment.router, prefix="/replenishment", tags=["replenishment"])
