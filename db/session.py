from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.settings_db import db_settings


engine = create_async_engine(db_settings.get_async_database_url(), echo=False)

SessionMaker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
