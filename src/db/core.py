from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from db.config import settings

async_engine = create_async_engine(
    url=settings.database_url,
    echo=True,
    poolclass=NullPool,
)


async_session_factory = async_sessionmaker(async_engine)


async def get_async_session():
    """Генератор асинхронной сессии."""
    async with async_session_factory() as async_session:
        yield async_session
