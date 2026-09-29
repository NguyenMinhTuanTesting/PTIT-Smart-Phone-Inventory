import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from fastapi.testclient import TestClient
from backend.app.main import app

def test_replenishment():
    client = TestClient(app)
    
    print("--- 1. Testing GET /api/v1/replenishment/suggestions ---")
    response = client.get("/api/v1/replenishment/suggestions")
    assert response.status_code == 200
    suggestions = response.json()
    
    print(f"Total SKUs returned: {len(suggestions)}")
    if len(suggestions) > 0:
        first = suggestions[0]
        print(f"Sample Suggestion: {first}")
        
    print("\n--- 2. Testing POST /api/v1/replenishment/create-po ---")
    if len(suggestions) > 0:
        # We will create a PO for the first variant
        po_payload = {
            "items": [
                {
                    "variant_id": first["variant_id"],
                    "quantity": 50
                }
            ],
            "supplier": "Apple Direct"
        }
        po_res = client.post("/api/v1/replenishment/create-po", json=po_payload)
        assert po_res.status_code == 200
        print(f"PO Creation Response: {po_res.json()}")
        
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    test_replenishment()
