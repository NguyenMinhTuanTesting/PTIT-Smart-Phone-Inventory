from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Enum as SQLEnum
import enum
from .base import Base

class ItemStatus(str, enum.Enum):
    IN_STOCK = "IN_STOCK"
    SOLD = "SOLD"
    DEFECTIVE = "DEFECTIVE"

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"), index=True)
    imei: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    status: Mapped[ItemStatus] = mapped_column(SQLEnum(ItemStatus), default=ItemStatus.IN_STOCK, index=True)
    sales_order_id: Mapped[int | None] = mapped_column(ForeignKey("sales_orders.id"), nullable=True, index=True)
    
    variant = relationship("ProductVariant", back_populates="inventory_items")
    sales_order = relationship("SalesOrder", back_populates="inventory_items")
