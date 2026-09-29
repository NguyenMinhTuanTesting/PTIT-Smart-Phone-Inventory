from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Date, Float, Integer
from datetime import date
from .base import Base

class SalesOrder(Base):
    __tablename__ = "sales_orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[date] = mapped_column(Date, index=True)
    customer_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    total_amount: Mapped[float] = mapped_column(Float)
    
    details = relationship("SalesDetail", back_populates="order")
    inventory_items = relationship("InventoryItem", back_populates="sales_order")

class SalesDetail(Base):
    __tablename__ = "sales_details"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("sales_orders.id"), index=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    discount: Mapped[float] = mapped_column(Float, default=0.0)
    
    order = relationship("SalesOrder", back_populates="details")
    variant = relationship("ProductVariant", back_populates="sales_details")
