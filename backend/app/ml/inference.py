import os
import joblib
import pandas as pd
from datetime import date, timedelta
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..models import ProductVariant, Product
from .features import is_holiday_or_campaign

def get_model():
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts", "demand_model.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")
    return joblib.load(model_path)

def get_latest_sales(db: Session, variant_id: int, days: int = 14):
    from sqlalchemy import text
    query = """
    SELECT o.order_date, SUM(d.quantity) as daily_sales
    FROM sales_orders o
    JOIN sales_details d ON o.id = d.order_id
    WHERE d.variant_id = :variant_id
    GROUP BY o.order_date
    ORDER BY o.order_date DESC
    LIMIT :days
    """
    result = db.execute(text(query), {"variant_id": variant_id, "days": days}).fetchall()
    
    sales = []
    for r in result:
        sales.append({"order_date": r[0], "daily_sales": r[1]})
        
    return pd.DataFrame(sales)

def predict_demand(sku_id: int, target_period_days: int) -> float:
    db = SessionLocal()
    try:
        variant = db.query(ProductVariant).filter(ProductVariant.id == sku_id).first()
        if not variant:
            raise ValueError("Variant not found")
            
        product = db.query(Product).filter(Product.id == variant.product_id).first()
        release_date = product.release_date
        
        # Get historical sales to compute rolling means
        recent_sales_df = get_latest_sales(db, sku_id, 14)
        if len(recent_sales_df) < 1:
            rolling_mean_7d = 0
            rolling_mean_14d = 0
        else:
            rolling_mean_7d = recent_sales_df.head(7)['daily_sales'].mean()
            rolling_mean_14d = recent_sales_df['daily_sales'].mean()
            
        model = get_model()
        
        total_predicted = 0.0
        current_date = date.today()
        
        features_list = []
        
        for i in range(target_period_days):
            target_date = current_date + timedelta(days=i)
            days_since_release = (target_date - release_date).days
            
            # Predict with average zero discount for future baseline
            import math
            features = {
                'variant_id': variant.id,
                'base_price': variant.base_price,
                'days_since_release': days_since_release,
                'expected_decay': math.exp(-0.002 * days_since_release),
                'discount_rate': 0.0,
                'is_holiday_or_campaign': is_holiday_or_campaign(target_date),
                'rolling_mean_7d': rolling_mean_7d,
                'rolling_mean_14d': rolling_mean_14d,
                'day_of_week': target_date.weekday(),
                'month': target_date.month
            }
            features_list.append(features)
            
        df_pred = pd.DataFrame(features_list)
        
        preds = model.predict(df_pred)
        total_predicted = float(preds.sum())
        
        return total_predicted
    finally:
        db.close()

if __name__ == "__main__":
    # Test inference
    db = SessionLocal()
    variant = db.query(ProductVariant).first()
    db.close()
    
    if variant:
        demand = predict_demand(variant.id, 7)
        print(f"Predicted demand for SKU '{variant.sku}' in next 7 days: {demand:.2f} units")
