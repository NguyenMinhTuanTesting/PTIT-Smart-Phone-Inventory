from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ....core.database import get_db
from ....schemas.inventory import InboundRequest, OutboundRequest, StockResponse
from ....services import inventory_service

router = APIRouter()

@router.get("/stock/{variant_id}", response_model=StockResponse)
def check_stock(variant_id: int, db: Session = Depends(get_db)):
    stock = inventory_service.get_stock(db, variant_id)
    if stock is None:
        raise HTTPException(status_code=404, detail="Variant not found")
    return stock

@router.post("/inbound")
def create_inbound(req: InboundRequest, db: Session = Depends(get_db)):
    try:
        inventory_service.handle_inbound(db, req)
        db.commit()
        return {"message": "Inbound successful"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/outbound")
def create_outbound(req: OutboundRequest, db: Session = Depends(get_db)):
    try:
        order = inventory_service.handle_outbound(db, req)
        db.commit()
        return {"message": "Outbound successful", "order_id": order.id}
    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
