import asyncio
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sqlmodel import Field, SQLModel, select  # type: ignore

# Load environment variables
load_dotenv()

# Async driver: asyncpg
DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@localhost:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)
engine = create_async_engine(DATABASE_URL, echo=True, pool_size=5)

# Async session factory
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)


class TestUserAsync(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Flattened equivalent of Depends(get_session)"""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()  # Await required!
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def main():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Your code
    async with get_session() as db:
        user = TestUserAsync(name="Alice")
        db.add(user)
        # Commit happens in __aexit__

    await asyncio.sleep(1)  # Non-blocking sleep

    # Query
    async with get_session() as db:
        result = await db.execute(select(TestUserAsync))
        users = result.scalars().all()
        print(f"Users: {[u.name for u in users]}")


if __name__ == "__main__":
    asyncio.run(main())
