from contextlib import asynccontextmanager
from typing import AsyncIterator

from app.core.db import session_maker
from app.repositories.repository import ProductRepository
from app.services.product_service import ProductService

@asynccontextmanager
async def get_product_service() -> AsyncIterator[ProductService]:
    async with session_maker() as session:
        yield ProductService(ProductRepository(session))