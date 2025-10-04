import pytest


def test_module_singleton_same_instance():
    """Test that importing returns the same instance."""
    from singleton.module_singleton import db_connection as conn1
    from singleton.module_singleton import db_connection as conn2

    assert conn1 is conn2


def test_module_singleton_state_persistence():
    """Test that state persists across imports."""
    from singleton.module_singleton import db_connection

    # Modify state
    db_connection.connect()
    assert db_connection.connected is True

    # Re-import should have same state
    from singleton.module_singleton import db_connection as conn2
    assert conn2.connected is True


def test_module_singleton_reset():
    """Test resetting singleton state for testing."""
    from singleton.module_singleton import db_connection

    # Reset state before test
    db_connection.connected = False
    db_connection.host = "testhost"

    assert db_connection.host == "testhost"

    # Cleanup
    db_connection.host = "localhost"
    db_connection.connected = False


def test_database_query_without_connection():
    """Test that query raises error when not connected."""
    from singleton.module_singleton import db_connection

    db_connection.connected = False

    with pytest.raises(RuntimeError, match="Not connected to database"):
        db_connection.query("SELECT * FROM users")


def test_database_query_with_connection():
    """Test that query works when connected."""
    from singleton.module_singleton import db_connection

    db_connection.connect()
    result = db_connection.query("SELECT * FROM users")

    assert "Executing: SELECT * FROM users" in result

    # Cleanup
    db_connection.connected = False


def test_database_connection_string():
    """Test connection string format."""
    from singleton.module_singleton import db_connection

    result = db_connection.connect()
    assert result == "Connected to localhost:5432"

    # Cleanup
    db_connection.connected = False