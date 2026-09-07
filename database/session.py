import traceback
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from learning.config import db_settings as settings

engine = create_async_engine(
    url=settings.POSTGRES_URL,
    echo=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def create_db_tables() -> None:
    try:
        async with engine.begin() as connection:
            await connection.run_sync(SQLModel.metadata.create_all)
    except Exception as exc:  # pragma: no cover - impacted by local DB availability
        print("Database startup check failed:")
        traceback.print_exc()
        raise RuntimeError(f"Database startup check failed: {exc}") from exc


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


# session = Session(bind=engine)

# session.get(Shipment,12701)
# session.add(Shpment())
# session.commit()
