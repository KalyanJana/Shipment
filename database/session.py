from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from learning.config import db_settings as settings


engine = create_async_engine(
    settings.POSTGRES_URL,
    echo=True,
)


async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def create_db_tables() -> None:

    async with engine.begin() as connection:
        await connection.run_sync(
            SQLModel.metadata.create_all
        )


async def get_session() -> AsyncGenerator[
    AsyncSession,
    None,
]:

    async with async_session_factory() as session:
        yield session