import sys
import os
import pandas as pd
from sqlalchemy import create_engine

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from backend.app.core.config import settings

def verify():
    engine = create_engine(settings.DATABASE_URL)
    
    # Query to compare normal days vs Black Friday (Nov 20-30) vs Tet (Feb 1-15)
    query = """
    SELECT 
        DATE_FORMAT(order_date, '%%Y-%%m') as month,
        SUM(quantity) as total_sold
    FROM sales_orders o
    JOIN sales_details d ON o.id = d.order_id
    GROUP BY month
    ORDER BY month;
    """
    
    df = pd.read_sql(query, engine)
    print("--- DOANH SỐ THEO THÁNG ---")
    print(df.to_string(index=False))
    
    query_spikes = """
    SELECT 
        CASE 
            WHEN MONTH(order_date) = 2 AND DAY(order_date) BETWEEN 1 AND 15 THEN 'Tết (1-15 Feb)'
            WHEN MONTH(order_date) = 11 AND DAY(order_date) BETWEEN 20 AND 30 THEN 'Black Friday (20-30 Nov)'
            ELSE 'Ngày thường'
        END AS period_type,
        AVG(daily_qty) as avg_daily_sales
    FROM (
        SELECT order_date, SUM(quantity) as daily_qty
        FROM sales_orders o
        JOIN sales_details d ON o.id = d.order_id
        GROUP BY order_date
    ) t
    GROUP BY period_type
    ORDER BY avg_daily_sales DESC;
    """
    
    df_spikes = pd.read_sql(query_spikes, engine)
    print("\n--- SO SÁNH DOANH SỐ TRUNG BÌNH NGÀY (TẾT/SALE vs NGÀY THƯỜNG) ---")
    print(df_spikes.to_string(index=False))

if __name__ == "__main__":
    verify()
