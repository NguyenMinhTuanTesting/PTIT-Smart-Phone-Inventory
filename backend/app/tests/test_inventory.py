from backend.app.models import Brand, Product, ProductVariant, InventoryItem, ItemStatus
from datetime import date

def setup_test_data(db_session):
    b = Brand(name="TestBrand")
    db_session.add(b)
    db_session.commit()
    
    p = Product(name="TestPhone", brand_id=b.id, release_date=date.today())
    db_session.add(p)
    db_session.commit()
    
    v = ProductVariant(product_id=p.id, sku="SKU-TEST-1", ram="8GB", rom="256GB", color="Black", base_price=1000)
    db_session.add(v)
    db_session.commit()
    
    return v

def test_inbound(client, db_session):
    v = setup_test_data(db_session)
    
    payload = {
        "variant_id": v.id,
        "supplier": "Test Supplier",
        "price": 800,
        "imeis": ["123456789012345", "123456789012346"]
    }
    
    res = client.post("/api/v1/inventory/inbound", json=payload)
    assert res.status_code == 200
    
    stock = db_session.query(InventoryItem).filter(InventoryItem.status == ItemStatus.IN_STOCK).all()
    assert len(stock) == 2

def test_outbound_success(client, db_session):
    v = setup_test_data(db_session)
    
    # Add stock first
    payload_in = {
        "variant_id": v.id,
        "supplier": "Test Supplier",
        "price": 800,
        "imeis": ["111111111111111", "222222222222222"]
    }
    client.post("/api/v1/inventory/inbound", json=payload_in)
    
    # Sell 1 item
    payload_out = {
        "variant_id": v.id,
        "customer_info": "John Doe",
        "price": 1000,
        "quantity": 1,
        "discount": 0.0
    }
    res = client.post("/api/v1/inventory/outbound", json=payload_out)
    assert res.status_code == 200
    
    stock = db_session.query(InventoryItem).filter(InventoryItem.status == ItemStatus.IN_STOCK).all()
    sold = db_session.query(InventoryItem).filter(InventoryItem.status == ItemStatus.SOLD).all()
    
    assert len(stock) == 1
    assert len(sold) == 1

def test_outbound_insufficient_stock(client, db_session):
    v = setup_test_data(db_session)
    
    payload_out = {
        "variant_id": v.id,
        "customer_info": "Jane Doe",
        "price": 1000,
        "quantity": 5, # No stock available
        "discount": 0.0
    }
    res = client.post("/api/v1/inventory/outbound", json=payload_out)
    assert res.status_code == 400
