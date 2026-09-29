from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ....core.database import get_db
from ....schemas.replenishment import ReplenishmentSuggestion, CreatePORequest
from ....services import replenishment_service

router = APIRouter()

@router.get("/suggestions", response_model=List[ReplenishmentSuggestion])
def get_suggestions(db: Session = Depends(get_db)):
    try:
        suggestions = replenishment_service.get_suggestions(db, target_period_days=7)
        return suggestions
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-po")
def create_po(req: CreatePORequest, db: Session = Depends(get_db)):
    try:
        po = replenishment_service.create_po_from_suggestions(db, req.items, req.supplier)
        return {"message": "Purchase Order created successfully", "po_id": po.id, "total_amount": po.total_amount}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
