from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Product


async def orm_add_product(session: AsyncSession, data: dict):
    session.add(Product(**data))
    await session.commit()


async def orm_get_products(session: AsyncSession):
    query = select(Product)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_product(session: AsyncSession, product_id: int):
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_product(*, session: AsyncSession, product_id: int, data):
    query = update(Product).where(Product.id == product_id).values(**data)
    result = await session.execute(query)
    await session.commit()


async def orm_delete_product(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()
