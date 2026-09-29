import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from ..core.config import settings

def load_data():
    engine = create_engine(settings.DATABASE_URL)
    
    query = """
    SELECT 
        o.order_date,
        d.variant_id,
        v.product_id,
        p.release_date,
        v.base_price,
        SUM(d.quantity) as daily_sales,
        AVG(d.discount) as avg_discount
    FROM sales_orders o
    JOIN sales_details d ON o.id = d.order_id
    JOIN product_variants v ON d.variant_id = v.id
    JOIN products p ON v.product_id = p.id
    GROUP BY o.order_date, d.variant_id, v.product_id, p.release_date, v.base_price
    ORDER BY d.variant_id, o.order_date
    """
    df = pd.read_sql(query, engine)
    
    # Ensure datetime format
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['release_date'] = pd.to_datetime(df['release_date'])
    
    return df

def is_holiday_or_campaign(date):
    month = date.month
    day = date.day
    
    # Tet approximate (Feb 1 - 15)
    if month == 2 and 1 <= day <= 15:
        return 1
    # Black Friday/Sale (Nov 20-30, Nov 11)
    if (month == 11 and 20 <= day <= 30) or (month == 11 and day == 11):
        return 1
    # Back to school
    if month in [8, 9]:
        return 1
    return 0

def extract_features(df):
    # Sort by variant and date just in case
    df = df.sort_values(by=['variant_id', 'order_date'])
    
    df['days_since_release'] = (df['order_date'] - df['release_date']).dt.days
    df['expected_decay'] = np.exp(-0.002 * df['days_since_release'])
    df['discount_rate'] = df['avg_discount']
    df['is_holiday_or_campaign'] = df['order_date'].apply(is_holiday_or_campaign)
    df['day_of_week'] = df['order_date'].dt.dayofweek
    df['month'] = df['order_date'].dt.month
    
    # Calculate rolling means
    df['rolling_mean_7d'] = df.groupby('variant_id')['daily_sales'].transform(
        lambda x: x.shift(1).rolling(window=7, min_periods=1).mean()
    ).fillna(0)
    
    df['rolling_mean_14d'] = df.groupby('variant_id')['daily_sales'].transform(
        lambda x: x.shift(1).rolling(window=14, min_periods=1).mean()
    ).fillna(0)
    
    return df
