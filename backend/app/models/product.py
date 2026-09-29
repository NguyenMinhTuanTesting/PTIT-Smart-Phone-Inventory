from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Date
from datetime import date
from .base import Base

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    release_date: Mapped[date] = mapped_column(Date)
    
    brand = relationship("Brand", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product")
