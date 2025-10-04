import os
import pytest
from raii.file_handler import FileHandler


@pytest.fixture
def test_file():
    """Fixture to provide test file path and cleanup."""
    filepath = "test_data.txt"
    yield filepath
    # Cleanup: remove file if it exists
    if os.path.exists(filepath):
        os.remove(filepath)


def test_file_handler_creates_and_closes_file(test_file):
    """Test that FileHandler properly opens and closes file."""
    with FileHandler(test_file, "w") as f:
        f.write("Test content")
        assert not f.closed

    # File should be closed after context exits
    assert f.closed


def test_file_handler_writes_content(test_file):
    """Test that content is written correctly."""
    with FileHandler(test_file, "w") as f:
        f.write("Hello RAII!")

    # Verify content was written
    with open(test_file, "r") as f:
        content = f.read()
        assert content == "Hello RAII!"


def test_file_handler_reads_content(test_file):
    """Test that FileHandler can read files."""
    # Create file first
    with open(test_file, "w") as f:
        f.write("Read this content")

    # Read using FileHandler
    with FileHandler(test_file, "r") as f:
        content = f.read()
        assert content == "Read this content"


def test_file_handler_cleanup_on_exception(test_file):
    """Test that file is closed even when exception occurs."""
    file_object = None

    try:
        with FileHandler(test_file, "w") as f:
            file_object = f
            f.write("Data before exception")
            raise ValueError("Simulated error")
    except ValueError:
        pass

    # File should still be closed despite exception
    assert file_object is not None
    assert file_object.closed


def test_file_handler_multiple_operations(test_file):
    """Test multiple write operations."""
    with FileHandler(test_file, "w") as f:
        f.write("Line 1\n")
        f.write("Line 2\n")
        f.write("Line 3\n")

    with open(test_file, "r") as f:
        lines = f.readlines()
        assert len(lines) == 3
        assert lines[0] == "Line 1\n"


def test_file_handler_different_modes(test_file):
    """Test FileHandler with different file modes."""
    # Write mode
    with FileHandler(test_file, "w") as f:
        f.write("Initial content")

    # Append mode
    with FileHandler(test_file, "a") as f:
        f.write(" Appended content")

    # Read mode
    with FileHandler(test_file, "r") as f:
        content = f.read()
        assert content == "Initial content Appended content"
