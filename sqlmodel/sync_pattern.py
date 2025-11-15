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
# PATTERN 1: SESSION (ORM) - Auto-commit, Auto-rollback, Auto-close
# ============================================================================
# Use for: Working with SQLModel objects, relationships, type safety


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Session with automatic transaction management."""
    session = SessionLocal()
    try:
        yield session
        session.commit()  # Auto-commit on success
    except Exception:
        session.rollback()  # Auto-rollback on error
        raise
    finally:
        session.close()  # Auto-close, return to pool


def pattern_1_session():
    """Pattern 1: Session-based ORM operations"""
    print("\n=== PATTERN 1: SESSION (ORM) ===")

    # Insert using ORM (auto-flush on commit, explicit flush not needed)
    with get_session() as db:
        user = TestUser(name="Bob")
        db.add(user)
        # No manual flush needed - auto-flushes on commit (line 66)

    # Flush demo: Get auto-generated ID before commit
    with get_session() as db:
        user = TestUser(name="Charlie")
        db.add(user)
        print(f"Before flush: ID = {user.id}")  # None

        db.flush()  # Explicit flush: Send INSERT to DB, get ID back (no commit yet)
        print(f"After flush: ID = {user.id}")  # Populated!
        # Use case: Need ID to create related objects before commit

    # Query using ORM (auto-flush before query, explicit flush not needed)
    with get_session() as db:
        user = TestUser(name="Diana")
        db.add(user)
        # Auto-flush happens HERE before execute() - no manual flush needed
        result = db.execute(select(TestUser)).scalars().all()
        print(f"Users via Session: {[u.name for u in result]}")


# ============================================================================
# PATTERN 2: CONNECTION (MANUAL) - Manual everything
# ============================================================================
# Use for: Fine-grained transaction control, raw SQL with manual commits


def pattern_2_connection_manual():
    """Pattern 2: Connection with manual transaction management"""
    print("\n=== PATTERN 2: CONNECTION (MANUAL TRANSACTION) ===")

    conn: Connection = engine.connect()
    try:
        conn.execute(
            text("INSERT INTO test_users (name) VALUES (:name)"), {"name": "Charlie"}
        )
        conn.commit()  # Manual commit required

        result = conn.execute(text("SELECT name FROM test_users"))
        print(f"Users via Connection: {[row[0] for row in result]}")

    except Exception:
        conn.rollback()  # Manual rollback required
        raise
    finally:
        conn.close()  # Manual close required


# ============================================================================
# PATTERN 3: CONNECTION.BEGIN() - Auto-commit, Auto-rollback, Auto-close
# ============================================================================
# Use for: Raw SQL with automatic transaction management


def pattern_3_connection_begin():
    """Pattern 3: Connection with automatic transaction (begin)"""
    print("\n=== PATTERN 3: CONNECTION.BEGIN (AUTO-TRANSACTION) ===")

    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO test_users (name) VALUES (:name)"), {"name": "Diana"}
        )

        result = conn.execute(text("SELECT name FROM test_users"))
        print(f"Users via Begin: {[row[0] for row in result]}")


# ============================================================================
# PATTERN 4: ENGINE.CONNECT() - Manual commit, Auto-rollback, Auto-close
# ============================================================================
# Use for: Multiple transactions in one connection, manual commit control


def pattern_4_engine_connect_context():
    """Pattern 4: Engine.connect() with context manager"""
    print("\n=== PATTERN 4: ENGINE.CONNECT (CONTEXT MANAGER) ===")

    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO test_users (name) VALUES (:name)"), {"name": "Eve"}
        )
        conn.commit()  # Manual commit required

        result = conn.execute(text("SELECT COUNT(*) FROM test_users"))
        count = result.scalar()
        print(f"Total users: {count}")


# ============================================================================
# COMPARISON TABLE
# ============================================================================

"""
TRANSACTION MANAGEMENT COMPARISON:

┌──────────────────────────┬─────────────┬───────────────┬────────────┬─────────────┐
│ Pattern                  │ Auto-Commit │ Auto-Rollback │ Auto-Close │ Works With  │
├──────────────────────────┼─────────────┼───────────────┼────────────┼─────────────┤
│ 1. get_session()         │     ✅      │      ✅       │     ✅      │ ORM Models  │
│ 2. conn (manual)         │     ❌      │      ❌       │     ❌      │ Raw SQL     │
│ 3. engine.begin()        │     ✅      │      ✅       │     ✅      │ Raw SQL     │
│ 4. engine.connect()      │     ❌      │      ✅       │     ✅      │ Raw SQL     │
└──────────────────────────┴─────────────┴───────────────┴────────────┴─────────────┘

* Rollback only if commit() is NOT called


DECISION TREE:

1. Working with SQLModel objects/relationships?
   → Use get_session() (Pattern 1)

2. Raw SQL with automatic transaction?
   → Use engine.begin() (Pattern 3)

3. Raw SQL with multiple separate transactions?
   → Use engine.connect() (Pattern 4)

4. Raw SQL with full manual control?
   → Use conn manual (Pattern 2)


KEY DIFFERENCES:

Session vs Connection:
  Session   → ORM layer, works with objects, identity map, relationships
  Connection → Raw SQL, lower-level, lighter weight, no ORM features

engine.begin() vs engine.connect():
  begin()   → Automatic commit/rollback (like get_session for raw SQL)
  connect() → Manual commit, auto-rollback if uncommitted, auto-close
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
