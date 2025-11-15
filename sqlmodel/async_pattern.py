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
# PATTERN 1: ASYNC SESSION-BASED (ORM) - RECOMMENDED FOR MODEL OPERATIONS
# ============================================================================
# Use when: Working with SQLModel/SQLAlchemy models, need ORM features, handling concurrent requests
# Pros: Type-safe, automatic relationship handling, identity map, non-blocking
# Cons: Slight overhead, more abstraction


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    AsyncSession pattern with automatic transaction management.

    - AsyncSession wraps an AsyncConnection and adds ORM features
    - Commit happens on successful exit, rollback on exception
    - Session is returned to the connection pool on close
    - All operations are non-blocking (await required)
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()  # Await required!
    except Exception:
        await session.rollback()  # Await required!
        raise
    finally:
        await session.close()  # Await required!


async def pattern_1_async_session():
    """Pattern 1: AsyncSession-based ORM operations"""
    print("\n=== PATTERN 1: ASYNC SESSION (ORM) ===")

    # Insert using ORM
    async with get_session() as db:
        user = TestUserAsync(name="Bob")
        db.add(user)
        # Commit happens automatically in __aexit__

    # Query using ORM
    async with get_session() as db:
        result = await db.execute(select(TestUserAsync))  # Must await!
        users = result.scalars().all()
        print(f"Users via AsyncSession: {[u.name for u in users]}")


# ============================================================================
# PATTERN 2: ASYNC CONNECTION WITH MANUAL TRANSACTION CONTROL
# ============================================================================
# Use when: Need fine-grained transaction control, executing raw SQL, bulk operations
# Pros: Full control over transactions, lower overhead than Session, non-blocking
# Cons: Manual commit/rollback required, no ORM features


async def pattern_2_async_connection_manual():
    """Pattern 2: AsyncConnection with manual transaction management"""
    print("\n=== PATTERN 2: ASYNC CONNECTION (MANUAL TRANSACTION) ===")

    # Get a connection from the pool
    conn: AsyncConnection = await engine.connect()  # Must await!
    try:
        # Execute raw SQL
        await conn.execute(
            text("INSERT INTO test_users_async (name) VALUES (:name)"),
            {"name": "Charlie"},
        )

        # Must explicitly commit
        await conn.commit()  # Must await!

        # Query
        result = await conn.execute(text("SELECT name FROM test_users_async"))
        rows = result.fetchall()
        print(f"Users via AsyncConnection: {[row[0] for row in rows]}")

    except Exception:
        # Must explicitly rollback on error
        await conn.rollback()  # Must await!
        raise
    finally:
        # Return connection to pool
        await conn.close()  # Must await!


# ============================================================================
# PATTERN 3: ASYNC CONNECTION WITH AUTOMATIC TRANSACTION (BEGIN)
# ============================================================================
# Use when: Want automatic transaction handling without ORM overhead, non-blocking operations
# Pros: Auto-commit/rollback, cleaner code than manual transaction, non-blocking
# Cons: No ORM features, entire block is one transaction


async def pattern_3_async_connection_begin():
    """Pattern 3: AsyncConnection with automatic transaction (begin)"""
    print("\n=== PATTERN 3: ASYNC CONNECTION.BEGIN (AUTO-TRANSACTION) ===")

    # Context manager automatically begins transaction and commits on exit
    async with engine.begin() as conn:  # async with!
        # Everything in this block is part of one transaction
        await conn.execute(
            text("INSERT INTO test_users_async (name) VALUES (:name)"),
            {"name": "Diana"},
        )

        result = await conn.execute(text("SELECT name FROM test_users_async"))
        rows = result.fetchall()
        print(f"Users via AsyncBegin: {[row[0] for row in rows]}")

        # Automatic commit on successful exit
        # Automatic rollback if exception occurs


# ============================================================================
# PATTERN 4: ASYNC ENGINE.CONNECT() CONTEXT MANAGER
# ============================================================================
# Use when: Want connection pooling with context manager, simpler than manual close
# Pros: Automatic connection cleanup, cleaner than manual close, non-blocking
# Cons: Still need manual transaction control


async def pattern_4_async_engine_connect_context():
    """Pattern 4: AsyncEngine.connect() with context manager"""
    print("\n=== PATTERN 4: ASYNC ENGINE.CONNECT (CONTEXT MANAGER) ===")

    # Connection automatically closed on exit
    async with engine.connect() as conn:  # async with!
        await conn.execute(
            text("INSERT INTO test_users_async (name) VALUES (:name)"), {"name": "Eve"}
        )
        await conn.commit()  # Still need manual commit + await

        result = await conn.execute(text("SELECT COUNT(*) FROM test_users_async"))
        count = result.scalar()
        print(f"Total users: {count}")


# ============================================================================
# PATTERN 5: CONCURRENT OPERATIONS (UNIQUE TO ASYNC)
# ============================================================================
# Use when: Need to execute multiple independent database operations concurrently
# Pros: Significant performance improvement for I/O-bound operations
# Cons: Must ensure operations are truly independent (no shared state issues)


async def pattern_5_concurrent_operations():
    """Pattern 5: Concurrent async operations using asyncio.gather"""
    print("\n=== PATTERN 5: CONCURRENT OPERATIONS ===")

    # Define multiple independent operations
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
        return_exceptions=True,  # Don't fail all if one fails
    )

    print(f"Concurrent results: {results}")


# ============================================================================
# COMPARISON SUMMARY
# ============================================================================

"""
DECISION TREE (ASYNC):

1. Working with SQLModel classes/relationships?
   → Use ASYNC SESSION (Pattern 1)

2. Need raw SQL but want auto-transaction?
   → Use ASYNC CONNECTION.BEGIN (Pattern 3)

3. Need multiple small transactions with fine control?
   → Use ASYNC CONNECTION with manual commit (Pattern 2)

4. Simple one-off query?
   → Use ASYNC ENGINE.CONNECT context manager (Pattern 4)

5. Multiple independent operations that can run concurrently?
   → Use CONCURRENT OPERATIONS with asyncio.gather (Pattern 5)


ASYNC vs SYNC CONSIDERATIONS:

When to use ASYNC:
  ✓ Web applications with concurrent users (FastAPI, aiohttp)
  ✓ I/O-bound operations (multiple DB queries, API calls)
  ✓ Need high concurrency with low memory overhead
  ✓ Modern async frameworks (asyncio ecosystem)

When to use SYNC:
  ✓ Simple scripts or CLI tools
  ✓ CPU-bound operations
  ✓ Existing sync codebase
  ✓ Simpler debugging and error handling


TRANSACTION BEHAVIOR (ASYNC):

AsyncSession:
  - Transaction starts on first operation
  - Must await session.commit()
  - Can have multiple flushes before commit
  - Non-blocking I/O

AsyncConnection (manual):
  - Transaction starts on first operation
  - Must await conn.commit()
  - Full control over savepoints
  - Non-blocking I/O

AsyncConnection.begin():
  - Transaction starts immediately
  - Auto-commits on __aexit__ (success)
  - Auto-rolls back on exception
  - Non-blocking I/O


ASYNC CONNECTION vs ASYNC SESSION:

AsyncConnection:
  - Lower level, closer to DBAPI
  - Works with SQL expressions/text
  - No identity map or ORM features
  - Lighter weight
  - Non-blocking I/O

AsyncSession:
  - Higher level ORM abstraction
  - Works with model objects
  - Identity map (object caching)
  - Relationship loading
  - Unit of work pattern
  - Non-blocking I/O


IMPORTANT ASYNC GOTCHAS:

1. Always use 'await' for DB operations:
   ❌ conn.execute(...)
   ✓ await conn.execute(...)

2. Use 'async with' for context managers:
   ❌ with engine.connect() as conn:
   ✓ async with engine.connect() as conn:

3. Use asyncpg driver (not psycopg2):
   ❌ postgresql://...
   ✓ postgresql+asyncpg://...

4. Install required packages:
   - asyncpg (async driver)
   - greenlet (for run_sync operations)
   - sqlalchemy[asyncio]

5. Avoid blocking operations in async code:
   ❌ time.sleep(1)
   ✓ await asyncio.sleep(1)
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
