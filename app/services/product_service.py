from datetime import datetime, timezone
import logging
from typing import Optional
from app.repositories.repository import ProductRepository
from app.schemes.product import ProductBaseS, ProductReadS

logger = logging.getLogger(__name__)


class ProductService:

    def __init__(self, product_repository: ProductRepository) -> None:
        self.product_repository = product_repository

    @staticmethod
    def format_price_history(min_price: float, max_price: float) -> dict:
        return {
            "date": datetime.now(timezone.utc).isoformat(),
            "min_price": min_price,
            "max_price": max_price,
        }

    @staticmethod
    def format_offers_history(offers: list) -> dict:
        return {
            "date": datetime.now(timezone.utc).isoformat(),
            "offers": offers,
        }

    async def create(self, schema: ProductBaseS) -> ProductReadS:
        return await self.product_repository.save(schema)

    async def get_by_product_code(self, product_code: str) -> Optional[ProductReadS]:
        return await self.product_repository.get_by_product_code(product_code)

    async def update_by_difference(
        self, original: ProductReadS, new: ProductBaseS
    ) -> ProductReadS:
        diff = {}
        for field in new.__class__.model_fields:
            new_value = getattr(new, field)
            old_value = getattr(original, field, None)
            if new_value != old_value and new_value is not None:
                diff[field] = new_value

        if original.min_price != new.min_price or original.max_price != new.max_price:
            price_history = original.price_history
            price_history.append(self.format_price_history(min_price=new.min_price, max_price=new.max_price))
            diff["price_history"] = price_history
        
        if original.offers != new.offers:
            offers_history = original.offers_history
            offers_history.append(self.format_offers_history(offers=new.offers))
            diff["offers_history"] = offers_history

        if not diff:
            return original

        return await self.product_repository.update(original.id, diff)
