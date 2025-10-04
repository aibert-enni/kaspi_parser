from datetime import datetime, timezone
from typing import Any
from sqlalchemy import DateTime, Float, Integer, String, func, UUID as SqlUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from uuid import uuid4, UUID

from app.models.base import BaseOrm


class ProductOrm(BaseOrm):
    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(SqlUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    product_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    min_price: Mapped[float] = mapped_column(Float, nullable=False)
    max_price: Mapped[float] = mapped_column(Float, nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)

    price_history: Mapped[list[dict]] = mapped_column(JSONB, default=lambda: [])

    image_links: Mapped[list[str]] = mapped_column(JSONB, default=lambda: [])

    details: Mapped[dict[str, Any]] = mapped_column(JSONB, default=lambda: {})
    offers: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=lambda: [])

    offers_history: Mapped[list[dict]] = mapped_column(JSONB, default=lambda: [])

    sellers_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=datetime.now(timezone.utc),
        server_onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Product(code={self.product_code}, name={self.name}, rating={self.rating})>"