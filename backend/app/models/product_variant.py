from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Float
from .base import Base

class ProductVariant(Base):
    __tablename__ = "product_variants"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    ram: Mapped[str] = mapped_column(String(20))
    rom: Mapped[str] = mapped_column(String(20))
    color: Mapped[str] = mapped_column(String(50))
    base_price: Mapped[float] = mapped_column(Float)
    
    product = relationship("Product", back_populates="variants")
    inventory_items = relationship("InventoryItem", back_populates="variant")
    sales_details = relationship("SalesDetail", back_populates="variant")
