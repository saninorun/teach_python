import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from dotenv import load_dotenv

from database.models import Base
from database.orm_query import orm_add_banner_description, orm_create_categories
from common.text_for_db import categories, description_for_info_pages

load_dotenv()

engine = create_async_engine(os.getenv("DB_POSTGR"), echo=True)
session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        await orm_create_categories(session=session, categories=categories)
        await orm_add_banner_description(session=session, data=description_for_info_pages)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
