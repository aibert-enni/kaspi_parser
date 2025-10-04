from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.settings import settings

engine = create_async_engine(settings.db.URL, pool_pre_ping=True, pool_recycle=3600)

session_maker = async_sessionmaker(engine, expire_on_commit=False)
