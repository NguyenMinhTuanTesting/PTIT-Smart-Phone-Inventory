import streamlit as st
import requests
import pandas as pd
from sqlalchemy import create_engine
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from backend.app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
API_URL = "http://127.0.0.1:8000/api/v1"

st.title("📦 Quản lý Xuất / Nhập kho")

# Fetch SKUs
query = "SELECT id, sku, base_price FROM product_variants"
df_skus = pd.read_sql(query, engine)
sku_options = {row['sku']: row['id'] for _, row in df_skus.iterrows()}
sku_prices = {row['id']: row['base_price'] for _, row in df_skus.iterrows()}

tab1, tab2 = st.tabs(["Nhập Kho (Inbound)", "Xuất Kho (Outbound)"])

with tab1:
    st.subheader("Tạo Phiếu Nhập Kho")
    with st.form("inbound_form"):
        selected_sku = st.selectbox("Chọn SKU", list(sku_options.keys()))
        supplier = st.text_input("Nhà cung cấp", "Nhà phân phối chính hãng")
        quantity = st.number_input("Số lượng", min_value=1, value=10)
        price = st.number_input("Giá nhập (VNĐ)", min_value=1000.0, value=float(sku_prices.get(sku_options.get(selected_sku, 1), 10000000)))
        
        imeis_text = st.text_area("Danh sách IMEI (Mỗi dòng 1 IMEI, 15 ký tự)", 
                                  help="Nếu để trống, hệ thống sẽ tự sinh giả lập.")
        
        submitted = st.form_submit_button("Tiến hành Nhập kho")
        if submitted:
            variant_id = sku_options[selected_sku]
            
            imeis = []
            if imeis_text.strip():
                imeis = [i.strip() for i in imeis_text.split('\n') if i.strip()]
            else:
                import random, string
                for _ in range(quantity):
                    imeis.append(''.join(random.choices(string.ascii_uppercase + string.digits, k=15)))
            
            if len(imeis) != quantity:
                st.error("Số lượng IMEI phải bằng số lượng nhập.")
            else:
                payload = {
                    "variant_id": variant_id,
                    "supplier": supplier,
                    "price": price,
                    "imeis": imeis
                }
                res = requests.post(f"{API_URL}/inventory/inbound", json=payload)
                if res.status_code == 200:
                    st.success("Nhập kho thành công!")
                else:
                    st.error(f"Lỗi: {res.text}")

with tab2:
    st.subheader("Xuất Kho Bán Hàng")
    with st.form("outbound_form"):
        selected_sku_out = st.selectbox("Chọn SKU xuất", list(sku_options.keys()))
        customer = st.text_input("Khách hàng", "Khách vãng lai")
        quantity_out = st.number_input("Số lượng xuất", min_value=1, value=1)
        discount = st.slider("Chiết khấu", 0.0, 0.5, 0.0)
        
        submitted_out = st.form_submit_button("Tiến hành Xuất bán")
        if submitted_out:
            variant_id = sku_options[selected_sku_out]
            price_out = sku_prices[variant_id]
            
            payload = {
                "variant_id": variant_id,
                "customer_info": customer,
                "price": price_out,
                "quantity": quantity_out,
                "discount": discount
            }
            res = requests.post(f"{API_URL}/inventory/outbound", json=payload)
            if res.status_code == 200:
                st.success(f"Xuất kho thành công! Order ID: {res.json().get('order_id')}")
            else:
                st.error(f"Lỗi: {res.text}")
