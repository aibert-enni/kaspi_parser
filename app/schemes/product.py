from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ProductBaseS(BaseModel):
    product_code: str
    name: str
    min_price: float
    max_price: float
    rating: float
    comments_count: int

    price_history: list[dict]

    image_links: list[str]

    details: dict
    offers: list[dict]

    offers_history: list[dict]

    sellers_count: int

    model_config = ConfigDict(from_attributes=True)

class ProductReadS(ProductBaseS):
    id: UUID

    created_at: datetime
    updated_at: datetime