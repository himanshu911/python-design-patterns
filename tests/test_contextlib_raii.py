import os

from raii.contextlib_raii import database_connection, temporary_file


def test_database_connection_context_manager():
    """Test that database_connection properly manages connection."""
    with database_connection("localhost", 5432) as conn:
        assert conn is not None
        assert conn["host"] == "localhost"
        assert conn["port"] == 5432
        assert conn["active"] is True

    # Connection should be inactive after context exits
    assert conn["active"] is False


def test_database_connection_multiple_uses():
    """Test multiple database connections."""
    with database_connection("host1", 3306) as conn1:
        assert conn1["host"] == "host1"
        assert conn1["port"] == 3306

    with database_connection("host2", 5432) as conn2:
        assert conn2["host"] == "host2"
        assert conn2["port"] == 5432


def test_database_connection_cleanup_on_exception():
    """Test that connection is closed even when exception occurs."""
    conn_ref = None

    try:
        with database_connection("localhost", 5432) as conn:
            conn_ref = conn
            assert conn["active"] is True
            raise RuntimeError("Simulated error")
    except RuntimeError:
        pass

    # Connection should still be cleaned up
    assert conn_ref is not None
    assert conn_ref["active"] is False


def test_temporary_file_creates_and_deletes():
    """Test that temporary_file creates and automatically deletes file."""
    filename = "temp_test.txt"

    with temporary_file(filename) as f:
        assert not f.closed
        f.write("Temporary content")
        assert os.path.exists(filename)

    # File should be deleted after context exits
    assert not os.path.exists(filename)


def test_temporary_file_writes_content():
    """Test that content is written to temporary file."""
    filename = "temp_test2.txt"

    with temporary_file(filename) as f:
        f.write("Test data")
        f.flush()  # Ensure data is written

        # Read while file is still open (in another handle)
        with open(filename) as read_f:
            content = read_f.read()
            assert content == "Test data"

    # File should be deleted
    assert not os.path.exists(filename)


def test_temporary_file_cleanup_on_exception():
    """Test that temporary file is deleted even when exception occurs."""
    filename = "temp_exception.txt"

    try:
        with temporary_file(filename) as f:
            f.write("Data before exception")
            assert os.path.exists(filename)
            raise ValueError("Simulated error")
    except ValueError:
        pass

    # File should still be deleted despite exception
    assert not os.path.exists(filename)


def test_temporary_file_nested_context():
    """Test nested temporary file contexts."""
    file1 = "temp1.txt"
    file2 = "temp2.txt"

    with temporary_file(file1) as f1:
        f1.write("File 1")
        assert os.path.exists(file1)

        with temporary_file(file2) as f2:
            f2.write("File 2")
            assert os.path.exists(file2)

        # File 2 should be deleted
        assert not os.path.exists(file2)

    # File 1 should be deleted
    assert not os.path.exists(file1)
