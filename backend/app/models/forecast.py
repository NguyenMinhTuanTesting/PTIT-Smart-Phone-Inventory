from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Date, Float
from datetime import date
from .base import Base

class ForecastLog(Base):
    __tablename__ = "forecast_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"), index=True)
    forecast_date: Mapped[date] = mapped_column(Date, index=True)
    expected_sales: Mapped[float] = mapped_column(Float)
    r2_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    mae: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    variant = relationship("ProductVariant")
