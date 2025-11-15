"""
SQLAlchemy/SQLModel Asynchronous Patterns
==========================================

This file demonstrates different ways to interact with a database using async SQLAlchemy/SQLModel.

HIERARCHY:
AsyncEngine → AsyncConnection → Transaction → Async Cursor
           → AsyncSession → Transaction (ORM layer)

WHEN TO USE WHICH:
1. AsyncSession (ORM) - Use for: ORM operations, working with models, relationships, concurrent requests
2. AsyncConnection - Use for: Direct SQL, manual transaction control, bulk operations
3. Begin (auto-transaction) - Use for: Guaranteed atomic operations, simpler than manual commits

KEY ASYNC DIFFERENCES FROM SYNC:
- All database operations must be awaited
- Use 'async with' instead of 'with'
- Use 'async def' for functions
- Non-blocking I/O allows concurrent operations
- Requires asyncpg driver (not psycopg2)
- Requires greenlet for some operations
"""

import asyncio
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from sqlmodel import Field, SQLModel, select  # type: ignore

# Load environment variables
load_dotenv()

# Async driver: asyncpg (NOT psycopg2!)
DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@localhost:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)
engine = create_async_engine(DATABASE_URL, echo=True, pool_size=5)

# Async session factory
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)


class TestUserAsync(SQLModel, table=True):
    """
    SQLModel automatically creates table name from class name (lowercase).
    To use custom table name, add: __tablename__ = "custom_name"
    """

    # Override default table name
    __tablename__ = "test_users_async"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    name: str


# ============================================================================
# PATTERN 1: ASYNC SESSION (ORM) - Auto-commit, Auto-rollback, Auto-close
# ============================================================================
# Use for: Working with SQLModel objects, concurrent requests, ORM features


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """AsyncSession with automatic transaction management."""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()  # Auto-commit on success
    except Exception:
        await session.rollback()  # Auto-rollback on error
        raise
    finally:
        await session.close()  # Auto-close, return to pool


async def pattern_1_async_session():
    """Pattern 1: AsyncSession-based ORM operations"""
    print("\n=== PATTERN 1: ASYNC SESSION (ORM) ===")

    # Insert using ORM (auto-flush on commit, explicit flush not needed)
    async with get_session() as db:
        user = TestUserAsync(name="Bob")
        db.add(user)
        # No manual flush needed - auto-flushes on commit (line 80)

    # Flush demo: Get auto-generated ID before commit
    async with get_session() as db:
        user = TestUserAsync(name="Charlie")
        db.add(user)
        print(f"Before flush: ID = {user.id}")  # None

        # Explicit flush: Send INSERT to DB, get ID back (no commit yet)
        await db.flush()
        print(f"After flush: ID = {user.id}")  # Populated!
        # Use case: Need ID to create related objects before commit

    # Query using ORM (auto-flush before query, explicit flush not needed)
    async with get_session() as db:
        user = TestUserAsync(name="Diana")
        db.add(user)
        # Auto-flush happens HERE before execute() - no manual flush needed
        result = await db.execute(select(TestUserAsync))
        users = result.scalars().all()
        print(f"Users via AsyncSession: {[u.name for u in users]}")


# ============================================================================
# PATTERN 2: ASYNC CONNECTION (MANUAL) - Manual everything
# ============================================================================
# Use for: Fine-grained transaction control, raw SQL with manual commits


async def pattern_2_async_connection_manual():
    """Pattern 2: AsyncConnection with manual transaction management"""
    print("\n=== PATTERN 2: ASYNC CONNECTION (MANUAL TRANSACTION) ===")

    conn: AsyncConnection = await engine.connect()
    try:
        await conn.execute(
            text("INSERT INTO test_users_async (name) VALUES (:name)"),
            {"name": "Charlie"},
        )
        await conn.commit()  # Manual commit required

        result = await conn.execute(text("SELECT name FROM test_users_async"))
        rows = result.fetchall()
        print(f"Users via AsyncConnection: {[row[0] for row in rows]}")

    except Exception:
        await conn.rollback()  # Manual rollback required
        raise
    finally:
        await conn.close()  # Manual close required


# ============================================================================
# PATTERN 3: ASYNC CONNECTION.BEGIN() - Auto-commit, Auto-rollback, Auto-close
# ============================================================================
# Use for: Raw SQL with automatic transaction management


async def pattern_3_async_connection_begin():
    """Pattern 3: AsyncConnection with automatic transaction (begin)"""
    print("\n=== PATTERN 3: ASYNC CONNECTION.BEGIN (AUTO-TRANSACTION) ===")

    async with engine.begin() as conn:
        await conn.execute(
            text("INSERT INTO test_users_async (name) VALUES (:name)"),
            {"name": "Diana"},
        )

        result = await conn.execute(text("SELECT name FROM test_users_async"))
        rows = result.fetchall()
        print(f"Users via AsyncBegin: {[row[0] for row in rows]}")


# ============================================================================
# PATTERN 4: ASYNC ENGINE.CONNECT() - Manual commit, Auto-rollback, Auto-close
# ============================================================================
# Use for: Multiple transactions in one connection, manual commit control


async def pattern_4_async_engine_connect_context():
    """Pattern 4: AsyncEngine.connect() with context manager"""
    print("\n=== PATTERN 4: ASYNC ENGINE.CONNECT (CONTEXT MANAGER) ===")

    async with engine.connect() as conn:
        await conn.execute(
            text("INSERT INTO test_users_async (name) VALUES (:name)"), {"name": "Eve"}
        )
        await conn.commit()  # Manual commit required

        result = await conn.execute(text("SELECT COUNT(*) FROM test_users_async"))
        count = result.scalar()
        print(f"Total users: {count}")


# ============================================================================
# PATTERN 5: CONCURRENT OPERATIONS (UNIQUE TO ASYNC)
# ============================================================================
# Use for: Multiple independent operations running concurrently


async def pattern_5_concurrent_operations():
    """Pattern 5: Concurrent async operations using asyncio.gather"""
    print("\n=== PATTERN 5: CONCURRENT OPERATIONS ===")

    async def insert_user(name: str):
        async with get_session() as db:
            user = TestUserAsync(name=name)
            db.add(user)
        return f"Inserted {name}"

    async def count_users():
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM test_users_async"))
            return result.scalar()

    async def get_all_users():
        async with get_session() as db:
            result = await db.execute(select(TestUserAsync))
            users = result.scalars().all()
            return [u.name for u in users]

    # Execute all operations concurrently (not sequentially!)
    results = await asyncio.gather(
        insert_user("Frank"),
        insert_user("Grace"),
        count_users(),
        get_all_users(),
        return_exceptions=True,
    )

    print(f"Concurrent results: {results}")


# ============================================================================
# COMPARISON TABLE
# ============================================================================

"""
TRANSACTION MANAGEMENT COMPARISON (ASYNC):

┌──────────────────────────┬─────────────┬───────────────┬────────────┬─────────────┐
│ Pattern                  │ Auto-Commit │ Auto-Rollback │ Auto-Close │ Works With  │
├──────────────────────────┼─────────────┼───────────────┼────────────┼─────────────┤
│ 1. get_session()         │     ✅      │      ✅       │     ✅     │ ORM Models  │
│ 2. conn (manual)         │     ❌      │      ❌       │     ❌     │ Raw SQL     │
│ 3. engine.begin()        │     ✅      │      ✅       │     ✅     │ Raw SQL     │
│ 4. engine.connect()      │     ❌      │      ✅*      │     ✅     │ Raw SQL     │
│ 5. asyncio.gather()      │     N/A     │      N/A      │    N/A     │ Concurrent  │
└──────────────────────────┴─────────────┴───────────────┴────────────┴─────────────┘

* Rollback only if commit() is NOT called


DECISION TREE (ASYNC):

1. Working with SQLModel objects/relationships?
   → Use get_session() (Pattern 1)

2. Raw SQL with automatic transaction?
   → Use engine.begin() (Pattern 3)

3. Raw SQL with multiple separate transactions?
   → Use engine.connect() (Pattern 4)

4. Raw SQL with full manual control?
   → Use conn manual (Pattern 2)

5. Multiple independent operations concurrently?
   → Use asyncio.gather() (Pattern 5)


KEY DIFFERENCES:

AsyncSession vs AsyncConnection:
  AsyncSession   → ORM layer, works with objects, identity map, relationships
  AsyncConnection → Raw SQL, lower-level, lighter weight, no ORM features

engine.begin() vs engine.connect():
  begin()   → Automatic commit/rollback (like get_session for raw SQL)
  connect() → Manual commit, auto-rollback if uncommitted, auto-close

Async vs Sync:
  Async → Non-blocking I/O, high concurrency, use for web apps (FastAPI)
  Sync  → Blocking I/O, simpler, use for scripts/CLI tools


ASYNC REQUIREMENTS:

1. Always use 'await':        await conn.execute(...)
2. Use 'async with':          async with engine.connect() as conn:
3. Use asyncpg driver:        postgresql+asyncpg://...
4. Install dependencies:      asyncpg, greenlet, sqlalchemy[asyncio]
5. Avoid blocking ops:        await asyncio.sleep(1)  # not time.sleep(1)
"""


async def main():
    # Create tables (must use run_sync for metadata operations)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Clear table for demo
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM test_users_async"))

    # Run all patterns
    await pattern_1_async_session()
    await pattern_2_async_connection_manual()
    await pattern_3_async_connection_begin()
    await pattern_4_async_engine_connect_context()
    await pattern_5_concurrent_operations()


if __name__ == "__main__":
    asyncio.run(main())
