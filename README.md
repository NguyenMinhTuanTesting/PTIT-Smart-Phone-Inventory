# 📱 Phone Management ERP System - Tích hợp AI Dự báo Nhu cầu (Smart Replenishment)

Dự án Hệ thống quản lý chuỗi bán lẻ điện thoại (ERP) tích hợp mô hình Machine Learning dự báo nhu cầu bán hàng và tự động hoá quy trình nhập/xuất kho, được thiết kế chuẩn mực theo Clean Architecture.

## 🚀 Tính năng nổi bật
- **Quản lý danh mục & Tồn kho:** Quản lý bằng mã IMEI chi tiết (Serialized Inventory).
- **Trí tuệ nhân tạo (AI):** Ứng dụng thuật toán Random Forest Regressor phân tích lịch sử bán hàng, chu kỳ tuổi đời sản phẩm, và hiệu ứng ngày lễ để dự báo nhu cầu chính xác (R² Score ~ 0.88).
- **Gợi ý đặt hàng thông minh (Smart Replenishment):** Áp dụng công thức Lead Time Demand và Safety Stock để gợi ý điểm tái đặt hàng (Reorder Point) tối ưu.
- **What-If Analysis:** Mô phỏng sự thay đổi của nhu cầu thị trường khi thay đổi các biến số như chiến dịch giảm giá.
- **Giao diện trực quan:** Bảng điều khiển bằng Streamlit tương tác thời gian thực với Backend FastAPI.

## ⚙️ Cài đặt & Khởi động

### Yêu cầu hệ thống
- Python 3.10+
- Docker & Docker Compose (hoặc MySQL Server 8.0 chạy local)

### Bước 1: Clone và thiết lập môi trường
```bash
git clone https://github.com/NguyenMinhTuanTesting/PTIT-Smart-Phone-Inventory.git
cd phone-management-erp
python -m venv venv

# Kích hoạt môi trường ảo:
# Trên Windows:
.\venv\Scripts\activate
# Trên macOS/Linux:
source venv/bin/activate

# Cài đặt thư viện:
pip install -r requirements.txt
```

### Bước 2: Thiết lập Cơ sở dữ liệu (MySQL)
Khởi động container MySQL được cấu hình sẵn trong `docker-compose.yml`:
```bash
docker-compose up -d
```
> *Lưu ý: Nếu không sử dụng Docker, bạn có thể tự cài MySQL và sửa chuỗi kết nối trong file `backend/app/core/config.py`.*

### Bước 3: Đổ dữ liệu giả lập (Seed Data)
Sinh ra hơn 70.000 dòng dữ liệu lịch sử bán hàng trong vòng 2 năm để phục vụ việc huấn luyện mô hình:
```bash
python scripts/seed_data.py
```

### Bước 4: Huấn luyện Mô hình Machine Learning
Tiến hành huấn luyện mô hình Random Forest dự báo nhu cầu:
```bash
python -m backend.app.ml.train
```

### Bước 5: Khởi động Backend API Server (FastAPI)
Chạy server API ở cổng 8000:
```bash
uvicorn backend.app.main:app --reload
```
> API Docs (Swagger UI) sẽ có tại: `http://127.0.0.1:8000/docs`

### Bước 6: Khởi động Giao diện Dashboard (Streamlit)
Mở một Terminal mới (nhớ kích hoạt lại `venv`) và chạy:
```bash
streamlit run frontend/main.py
```
> Trình duyệt sẽ tự động mở giao diện tại `http://localhost:8501`.

---

## 🧪 Chạy Smoke Test (E2E Testing)
Để đảm bảo toàn bộ luồng nghiệp vụ từ Đầu đến Cuối (End-to-End) bao gồm DB -> Mô hình dự báo -> Khởi tạo Đơn nhập kho (PO) hoạt động tốt:
```bash
python scripts/smoke_test.py
```

---

## 📖 Bảng tài liệu API Endpoints chính

| Endpoint | HTTP Method | Mô tả (Chức năng) |
|----------|------------|---------------------|
| `/api/v1/products/` | `GET` | Lấy danh sách toàn bộ sản phẩm và các biến thể SKU. |
| `/api/v1/products/{id}` | `GET` | Lấy chi tiết một sản phẩm theo ID. |
| `/api/v1/inventory/stock/{variant_id}` | `GET` | Tra cứu số lượng tồn kho khả dụng của một SKU. |
| `/api/v1/inventory/inbound` | `POST` | Nhập kho (nhận List IMEI từ nhà cung cấp). |
| `/api/v1/inventory/outbound` | `POST` | Xuất kho bán hàng (khóa IMEI, tạo Sales Order). |
| `/api/v1/replenishment/suggestions` | `GET` | Gọi mô hình AI tính toán và sinh danh sách gợi ý nhập kho (kèm độ ưu tiên). |
| `/api/v1/replenishment/create-po` | `POST` | Tạo nhanh Đơn đặt hàng (Purchase Order) tự động từ gợi ý của AI. |

---
**Phát triển bởi PTIT Team.**
