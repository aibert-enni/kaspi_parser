from typing import Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemes.product import ProductBaseS, ProductReadS
from app.models.product import ProductOrm

class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def save(self, schema: ProductBaseS) -> ProductReadS:
        product = ProductOrm(**schema.model_dump())
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return ProductReadS.model_validate(product)
    
    async def get_by_product_code(self, product_code: str) -> Optional[ProductReadS]:
        stmt = select(ProductOrm).where(ProductOrm.product_code == product_code)
        result = await self.session.execute(stmt)
        product = result.scalar_one_or_none()
        if product is None:
            return None
        return ProductReadS.model_validate(product)

    async def update(self, id: UUID, diff: dict) -> ProductReadS:
        stmt = (
            update(ProductOrm)
            .where(ProductOrm.id == id)
            .values(**diff)
            .returning(ProductOrm)
        )

        result = await self.session.execute(stmt)
        updated_row = result.scalar_one()
        await self.session.commit()

        return ProductReadS.model_validate(updated_row)