import streamlit as st
import requests
import pandas as pd
import numpy as np

API_URL = "http://127.0.0.1:8000/api/v1"

st.title("🧠 Đề xuất Nhập hàng Thông minh")

with st.spinner("Đang tính toán dự báo từ mô hình AI..."):
    try:
        res = requests.get(f"{API_URL}/replenishment/suggestions")
        if res.status_code == 200:
            data = res.json()
            df = pd.DataFrame(data)
            
            def highlight_priority(s):
                if s == 'CRITICAL':
                    return 'background-color: #ff4b4b; color: white'
                elif s == 'WARNING':
                    return 'background-color: #ffa421; color: white'
                return 'background-color: #21c354; color: white'

            st.subheader("Bảng Gợi ý Nhập kho")
            
            st.dataframe(df.style.map(highlight_priority, subset=['priority']))
            
            st.subheader("🛠️ Tạo Đơn Nhập Hàng Nhanh (PO)")
            default_skus = []
            if not df.empty:
                default_skus = df[df['priority'] != 'NORMAL']['sku'].tolist()
            selected_skus = st.multiselect("Chọn các SKU cần tạo PO:", df['sku'].tolist() if not df.empty else [], default=default_skus)
            
            if st.button("Tạo Purchase Order"):
                items_to_order = []
                for sku in selected_skus:
                    row = df[df['sku'] == sku].iloc[0]
                    qty = int(row['suggested_order_qty'])
                    if qty == 0:
                        qty = 10 
                    items_to_order.append({"variant_id": int(row['variant_id']), "quantity": qty})
                
                po_payload = {"items": items_to_order, "supplier": "Auto PO System"}
                po_res = requests.post(f"{API_URL}/replenishment/create-po", json=po_payload)
                if po_res.status_code == 200:
                    st.success("Đã tạo PO thành công!")
                else:
                    st.error("Có lỗi xảy ra: " + po_res.text)
                    
            st.markdown("---")
            st.subheader("🔍 What-if Analysis (Mô phỏng Khuyến mãi)")
            st.write("Thử nghiệm thay đổi giả định giảm giá để xem mô hình dự báo điều chỉnh nhu cầu.")
            
            discount_sim = st.slider("Giả định Mức giảm giá (%) sắp tới:", 0, 50, 10)
            target_sku = st.selectbox("Chọn SKU để mô phỏng", df['sku'].tolist() if not df.empty else [])
            
            if st.button("Chạy Mô Phỏng"):
                import sys, os
                sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
                from backend.app.ml.inference import get_model, get_latest_sales
                from backend.app.ml.features import is_holiday_or_campaign
                from backend.app.core.database import SessionLocal
                from backend.app.models import ProductVariant, Product
                from datetime import date, timedelta
                
                db = SessionLocal()
                v = db.query(ProductVariant).filter(ProductVariant.sku == target_sku).first()
                product = db.query(Product).filter(Product.id == v.product_id).first()
                recent_sales_df = get_latest_sales(db, v.id, 14)
                
                rolling_mean_7d = recent_sales_df.head(7)['daily_sales'].mean() if len(recent_sales_df) else 0
                rolling_mean_14d = recent_sales_df['daily_sales'].mean() if len(recent_sales_df) else 0
                
                model = get_model()
                features_list = []
                for i in range(7):
                    target_date = date.today() + timedelta(days=i)
                    days_since_release = (target_date - product.release_date).days
                    
                    import math
                    features = {
                        'variant_id': v.id,
                        'base_price': v.base_price,
                        'days_since_release': days_since_release,
                        'expected_decay': math.exp(-0.002 * days_since_release),
                        'discount_rate': discount_sim / 100.0,
                        'is_holiday_or_campaign': is_holiday_or_campaign(target_date),
                        'rolling_mean_7d': rolling_mean_7d,
                        'rolling_mean_14d': rolling_mean_14d,
                        'day_of_week': target_date.weekday(),
                        'month': target_date.month
                    }
                    features_list.append(features)
                    
                df_pred = pd.DataFrame(features_list)
                sim_demand = float(model.predict(df_pred).sum())
                
                row = df[df['sku'] == target_sku].iloc[0]
                orig_demand = row['predicted_demand']
                
                st.write(f"**Dự báo gốc (0% chiết khấu):** {orig_demand:.2f} máy")
                st.write(f"**Dự báo mô phỏng ({discount_sim}% chiết khấu):** {sim_demand:.2f} máy")
                st.write(f"**Lượng nhập kho nên tăng thêm:** {max(0, int(sim_demand - orig_demand))} máy")
                
                db.close()
                
    except Exception as e:
        st.error(f"Không thể kết nối đến Backend hoặc Lỗi: {e}")
