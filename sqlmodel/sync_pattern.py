"""
SQLAlchemy/SQLModel Synchronous Patterns
=========================================

This file demonstrates different ways to interact with a database using SQLAlchemy/SQLModel.

HIERARCHY:
Engine → Connection → Transaction → Cursor (handled internally)
       → Session → Transaction (ORM layer)

WHEN TO USE WHICH:
1. Session (ORM) - Use for: ORM operations, working with models, relationships, unit of work
2. Connection - Use for: Direct SQL, manual transaction control, bulk operations
3. Begin (auto-transaction) - Use for: Guaranteed atomic operations, simpler than manual commits
"""

import os
from collections.abc import Generator
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import Connection, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from sqlmodel import Field, SQLModel, select  # type: ignore

# Load environment variables
load_dotenv()

# Sync driver: psycopg2
DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@localhost:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)
engine = create_engine(DATABASE_URL, echo=True, pool_size=5)

# Sync session factory
SessionLocal = sessionmaker(engine, class_=Session)


class TestUser(SQLModel, table=True):
    """
    SQLModel automatically creates table name from class name (lowercase).
    To use custom table name, add: __tablename__ = "custom_name"
    """

    # Override default table name
    __tablename__ = "test_users"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    name: str


# ============================================================================
# PATTERN 1: SESSION-BASED (ORM) - RECOMMENDED FOR MODEL OPERATIONS
# ============================================================================
# Use when: Working with SQLModel/SQLAlchemy models, need ORM features
# Pros: Type-safe, automatic relationship handling, identity map, unit of work
# Cons: Slight overhead, more abstraction


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Session pattern with automatic transaction management.

    - Session wraps a Connection and adds ORM features
    - Commit happens on successful exit, rollback on exception
    - Session is returned to the connection pool on close
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()  # Explicit commit on success
    except Exception:
        session.rollback()  # Rollback on failure
        raise
    finally:
        session.close()  # Return connection to pool


def pattern_1_session():
    """Pattern 1: Session-based ORM operations"""
    print("\n=== PATTERN 1: SESSION (ORM) ===")

    # Insert using ORM
    with get_session() as db:
        user = TestUser(name="Bob")
        db.add(user)
        # Commit happens automatically in __exit__

    # Query using ORM
    with get_session() as db:
        result = db.execute(select(TestUser)).scalars().all()
        print(f"Users via Session: {[u.name for u in result]}")


# ============================================================================
# PATTERN 2: CONNECTION WITH MANUAL TRANSACTION CONTROL
# ============================================================================
# Use when: Need fine-grained transaction control, executing raw SQL
# Pros: Full control over transactions, lower overhead than Session
# Cons: Manual commit/rollback required, no ORM features


def pattern_2_connection_manual():
    """Pattern 2: Connection with manual transaction management"""
    print("\n=== PATTERN 2: CONNECTION (MANUAL TRANSACTION) ===")

    # Get a connection from the pool
    conn: Connection = engine.connect()
    try:
        # Execute raw SQL
        conn.execute(
            text("INSERT INTO test_users (name) VALUES (:name)"), {"name": "Charlie"}
        )

        # Must explicitly commit
        conn.commit()

        # Query
        result = conn.execute(text("SELECT name FROM test_users"))
        print(f"Users via Connection: {[row[0] for row in result]}")

    except Exception:
        # Must explicitly rollback on error
        conn.rollback()
        raise
    finally:
        # Return connection to pool
        conn.close()


# ============================================================================
# PATTERN 3: CONNECTION WITH AUTOMATIC TRANSACTION (BEGIN)
# ============================================================================
# Use when: Want automatic transaction handling without ORM overhead
# Pros: Auto-commit/rollback, cleaner code than manual transaction
# Cons: No ORM features, entire block is one transaction


def pattern_3_connection_begin():
    """Pattern 3: Connection with automatic transaction (begin)"""
    print("\n=== PATTERN 3: CONNECTION.BEGIN (AUTO-TRANSACTION) ===")

    # Context manager automatically begins transaction and commits on exit
    with engine.begin() as conn:
        # Everything in this block is part of one transaction
        conn.execute(
            text("INSERT INTO test_users (name) VALUES (:name)"), {"name": "Diana"}
        )

        result = conn.execute(text("SELECT name FROM test_users"))
        print(f"Users via Begin: {[row[0] for row in result]}")

        # Automatic commit on successful exit
        # Automatic rollback if exception occurs


# ============================================================================
# PATTERN 4: ENGINE.CONNECT() CONTEXT MANAGER
# ============================================================================
# Use when: Want connection pooling with context manager, simpler than manual close
# Pros: Automatic connection cleanup, cleaner than manual close
# Cons: Still need manual transaction control


def pattern_4_engine_connect_context():
    """Pattern 4: Engine.connect() with context manager"""
    print("\n=== PATTERN 4: ENGINE.CONNECT (CONTEXT MANAGER) ===")

    # Connection automatically closed on exit
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO test_users (name) VALUES (:name)"), {"name": "Eve"}
        )
        conn.commit()  # Still need manual commit

        result = conn.execute(text("SELECT COUNT(*) FROM test_users"))
        count = result.scalar()
        print(f"Total users: {count}")


# ============================================================================
# COMPARISON SUMMARY
# ============================================================================

"""
DECISION TREE:

1. Working with SQLModel classes/relationships?
   → Use SESSION (Pattern 1)

2. Need raw SQL but want auto-transaction?
   → Use CONNECTION.BEGIN (Pattern 3)

3. Need multiple small transactions with fine control?
   → Use CONNECTION with manual commit (Pattern 2)

4. Simple one-off query?
   → Use ENGINE.CONNECT context manager (Pattern 4)


TRANSACTION BEHAVIOR:

Session:
  - Transaction starts on first operation
  - Must call session.commit() or use context manager
  - Can have multiple flushes before commit

Connection (manual):
  - Transaction starts on first operation
  - Must call conn.commit()
  - Full control over savepoints

Connection.begin():
  - Transaction starts immediately
  - Auto-commits on __exit__ (success)
  - Auto-rolls back on exception


CONNECTION vs SESSION:

Connection:
  - Lower level, closer to DBAPI
  - Works with SQL expressions/text
  - No identity map or ORM features
  - Lighter weight

Session:
  - Higher level ORM abstraction
  - Works with model objects
  - Identity map (object caching)
  - Relationship loading
  - Unit of work pattern
"""


def main():
    # Create tables
    SQLModel.metadata.create_all(engine)

    # Clear table for demo
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM test_users"))

    # Run all patterns
    pattern_1_session()
    pattern_2_connection_manual()
    pattern_3_connection_begin()
    pattern_4_engine_connect_context()


if __name__ == "__main__":
    main()
