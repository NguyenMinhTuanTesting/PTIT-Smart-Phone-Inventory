import streamlit as st

st.set_page_config(page_title="Phone Management Dashboard", layout="wide")

st.title("📱 Phone Management ERP System")
st.markdown("""
Chào mừng đến với hệ thống quản lý chuỗi bán lẻ điện thoại.
Hãy chọn các tính năng ở thanh bên trái (Sidebar) để bắt đầu.

- **1. Overview Dashboard**: Xem tổng quan tình hình kinh doanh và kho.
- **2. Quản lý Kho**: Xử lý Inbound (Nhập hàng) và Outbound (Xuất bán).
- **3. Smart Replenishment**: Xem đề xuất đặt hàng thông minh từ AI.
- **4. Model Performance**: Đánh giá hiệu năng của mô hình AI Dự báo nhu cầu.
""")

st.info("💡 Đảm bảo Backend API đang chạy tại http://127.0.0.1:8000")
