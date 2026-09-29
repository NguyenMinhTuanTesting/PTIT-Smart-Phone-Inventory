from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Dict, Any
from ..models import InventoryItem, ItemStatus, ProductVariant, PurchaseOrder, PurchaseDetail, SalesOrder, SalesDetail
from ..schemas.inventory import InboundRequest, OutboundRequest
from datetime import date

def get_stock(db: Session, variant_id: int) -> Optional[Dict[str, Any]]:
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        return None
    count = db.query(func.count(InventoryItem.id)).filter(
        InventoryItem.variant_id == variant_id,
        InventoryItem.status == ItemStatus.IN_STOCK
    ).scalar()
    return {"variant_id": variant_id, "sku": variant.sku, "in_stock_quantity": count}

def handle_inbound(db: Session, req_data: InboundRequest) -> PurchaseOrder:
    po = PurchaseOrder(
        order_date=date.today(),
        supplier=req_data.supplier,
        total_amount=req_data.price * len(req_data.imeis),
        status="COMPLETED"
    )
    db.add(po)
    db.flush()
    
    pd = PurchaseDetail(
        order_id=po.id,
        variant_id=req_data.variant_id,
        quantity=len(req_data.imeis),
        price=req_data.price
    )
    db.add(pd)
    
    for imei in req_data.imeis:
        item = InventoryItem(
            variant_id=req_data.variant_id,
            imei=imei,
            status=ItemStatus.IN_STOCK,
            sales_order_id=None
        )
        db.add(item)
    return po
    
def handle_outbound(db: Session, req_data: OutboundRequest) -> SalesOrder:
    available_items = db.query(InventoryItem).filter(
        InventoryItem.variant_id == req_data.variant_id,
        InventoryItem.status == ItemStatus.IN_STOCK
    ).limit(req_data.quantity).with_for_update().all()
    
    if len(available_items) < req_data.quantity:
        raise ValueError(f"Not enough stock. Only {len(available_items)} available.")
        
    total_amount = req_data.price * req_data.quantity * (1 - req_data.discount)
    so = SalesOrder(
        order_date=date.today(),
        customer_info=req_data.customer_info,
        total_amount=total_amount
    )
    db.add(so)
    db.flush()
    
    sd = SalesDetail(
        order_id=so.id,
        variant_id=req_data.variant_id,
        quantity=req_data.quantity,
        price=req_data.price,
        discount=req_data.discount
    )
    db.add(sd)
    
    for item in available_items:
        item.status = ItemStatus.SOLD
        item.sales_order_id = so.id
        
    return so
