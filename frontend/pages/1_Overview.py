import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from backend.app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

st.title("📊 Tổng quan Kho (Overview Dashboard)")

kpi1, kpi2, kpi3 = st.columns(3)

query_skus = "SELECT COUNT(*) FROM product_variants"
total_skus = pd.read_sql(query_skus, engine).iloc[0, 0]
kpi1.metric("Tổng số SKU", total_skus)

query_inv_val = """
    SELECT SUM(v.base_price) 
    FROM inventory_items i
    JOIN product_variants v ON i.variant_id = v.id
    WHERE i.status = 'IN_STOCK'
"""
inv_val = pd.read_sql(query_inv_val, engine).iloc[0, 0] or 0
kpi2.metric("Tổng giá trị tồn kho", f"{inv_val:,.0f} đ")

query_sold = """
    SELECT SUM(quantity) FROM sales_details sd
    JOIN sales_orders so ON sd.order_id = so.id
    WHERE MONTH(so.order_date) = MONTH(CURRENT_DATE())
"""
sold_month = pd.read_sql(query_sold, engine).iloc[0, 0] or 0
kpi3.metric("Đã bán trong tháng", f"{sold_month:,.0f} máy")

st.markdown("---")
st.subheader("Cơ cấu tồn kho theo Thương hiệu")

query_brand = """
    SELECT b.name as brand, COUNT(i.id) as stock_count
    FROM inventory_items i
    JOIN product_variants v ON i.variant_id = v.id
    JOIN products p ON v.product_id = p.id
    JOIN brands b ON p.brand_id = b.id
    WHERE i.status = 'IN_STOCK'
    GROUP BY b.name
"""
df_brand = pd.read_sql(query_brand, engine)
if not df_brand.empty:
    st.bar_chart(df_brand.set_index('brand'))
else:
    st.warning("Không có dữ liệu tồn kho.")
