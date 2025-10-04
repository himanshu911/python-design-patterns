"""
RAII Pattern using contextlib.contextmanager
Simpler alternative for function-based context managers.
"""

from contextlib import contextmanager


@contextmanager
def database_connection(host: str, port: int):
    """RAII-style database connection using contextmanager decorator."""
    # Acquire resource
    connection: dict[str, str | int | bool] = {
        "host": host,
        "port": port,
        "active": True,
    }
    print(f"Connected to {host}:{port}")

    try:
        yield connection  # Provide resource to caller
    finally:
        # Release resource (always executed)
        connection["active"] = False
        print(f"Disconnected from {host}:{port}")


@contextmanager
def temporary_file(filename: str):
    """RAII-style temporary file management."""
    import os

    # Acquire
    f = open(filename, "w")
    print(f"Created {filename}")

    try:
        yield f
    finally:
        # Release
        f.close()
        os.remove(filename)
        print(f"Deleted {filename}")


if __name__ == "__main__":
    # Function-based context manager
    with database_connection("localhost", 5432) as conn:
        print(f"Using connection: {conn}")

    # Automatic cleanup
    with temporary_file("temp.txt") as f:
        f.write("Temporary data")
    # File automatically deleted
