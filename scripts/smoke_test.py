import sys
import os
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from fastapi.testclient import TestClient
from backend.app.main import app

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def run_smoke_test():
    client = TestClient(app)
    
    logger.info("1. Testing DB connection & API Health...")
    # Using the /api/v1/products/ as a proxy to test DB and app are up
    res = client.get("/api/v1/products/")
    assert res.status_code == 200, f"Failed to get products: {res.text}"
    products = res.json()
    logger.info(f"-> OK. Retrieved {len(products)} products.")

    logger.info("2. Querying Inventory for a specific SKU...")
    # First get a variant ID to test with
    res = client.get("/api/v1/products/1")
    assert res.status_code == 200
    prod = res.json()
    variant = prod["variants"][0]
    sku = variant["sku"]
    
    res = client.get(f"/api/v1/inventory/stock/{variant['id']}")
    assert res.status_code == 200
    stock_info = res.json()
    logger.info(f"-> OK. Stock for {sku} (ID {variant['id']}): {stock_info['in_stock_quantity']}")

    logger.info("3. Calling Forecast Model & Generating Replenishment Suggestions...")
    res = client.get("/api/v1/replenishment/suggestions")
    assert res.status_code == 200
    suggestions = res.json()
    logger.info(f"-> OK. Generated suggestions for {len(suggestions)} SKUs.")
    
    if len(suggestions) == 0:
        logger.error("No suggestions generated!")
        sys.exit(1)
        
    first_suggestion = suggestions[0]
    logger.info(f"-> Sample Suggestion for {first_suggestion['sku']}: "
                f"Predicted Demand={first_suggestion['predicted_demand']}, "
                f"Suggested Qty={first_suggestion['suggested_order_qty']}")

    logger.info("4. Creating Purchase Order (PO)...")
    po_payload = {
        "items": [
            {
                "variant_id": first_suggestion["variant_id"],
                "quantity": 20
            }
        ],
        "supplier": "Smoke Test Supplier"
    }
    res = client.post("/api/v1/replenishment/create-po", json=po_payload)
    assert res.status_code == 200, f"Failed to create PO: {res.text}"
    po_data = res.json()
    logger.info(f"-> OK. Created PO ID {po_data['po_id']} with total amount {po_data['total_amount']}")

    logger.info("5. Simulating Successful Inbound (Nhập kho)...")
    target_vid = first_suggestion["variant_id"]
    
    # Check current stock first
    res = client.get(f"/api/v1/inventory/stock/{target_vid}")
    initial_stock = res.json()["in_stock_quantity"]
    
    inbound_payload = {
        "variant_id": target_vid,
        "supplier": "Smoke Test Supplier",
        "price": 10000000,
        "imeis": ["SMOKE1111111111", "SMOKE2222222222"]
    }
    res = client.post("/api/v1/inventory/inbound", json=inbound_payload)
    assert res.status_code == 200, f"Inbound failed: {res.text}"
    logger.info("-> OK. Inbound successful.")
    
    logger.info("6. Verifying Stock Increased...")
    res = client.get(f"/api/v1/inventory/stock/{first_suggestion['variant_id']}")
    new_stock = res.json()["in_stock_quantity"]
    logger.info(f"-> OK. New stock for {first_suggestion['sku']} is {new_stock} (Expected {initial_stock + 2})")
    assert new_stock == initial_stock + 2

    logger.info("ALL END-TO-END TESTS PASSED")

if __name__ == "__main__":
    try:
        run_smoke_test()
    except Exception as e:
        logger.error(f"SMOKE TEST FAILED: {str(e)}")
        sys.exit(1)
