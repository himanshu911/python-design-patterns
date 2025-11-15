import os
import time
from collections.abc import Generator
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
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
    id: int | None = Field(default=None, primary_key=True)
    name: str


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Flattened equivalent of Depends(get_session)"""
    session = SessionLocal()
    try:
        yield session
        session.commit()  # Explicit commit on success
    except Exception:
        session.rollback()  # Rollback on failure
        raise
    finally:
        session.close()  # Return to pool


def main():
    # Create tables
    SQLModel.metadata.create_all(engine)

    # Your code
    with get_session() as db:
        user = TestUser(name="Alice")
        db.add(user)
        # No await, commit happens in __exit__

    time.sleep(1)  # Simulate work (blocks thread!)

    # Query
    with get_session() as db:
        result = db.execute(select(TestUser)).scalars().all()
        print(f"Users: {[u.name for u in result]}")


if __name__ == "__main__":
    main()
