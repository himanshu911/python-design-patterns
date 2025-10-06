"""
RAII Pattern - Resource Acquisition Is Initialization
Resources are acquired during object initialization and released during cleanup.
"""

from types import TracebackType


class FileHandler:
    """RAII-style file handler using context manager."""

    def __init__(self, filename: str, mode: str = "r"):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        """Acquire resource"""
        self.file = open(self.filename, self.mode)
        print(f"Opened {self.filename}")
        return self.file

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: TracebackType):
        """Release resource

        Parameters automatically passed by Python:
        - exc_type: Exception class if error occurred, None otherwise
        - exc_val: Exception instance with error message, None otherwise
        - exc_tb: Traceback object with stack trace, None otherwise

        Return False to propagate exceptions (don't suppress errors).
        Return True would suppress the exception (rarely desired).
        """
        if self.file:
            self.file.close()
            print(f"Closed {self.filename}")
        return False


if __name__ == "__main__":
    # Resource automatically acquired and released
    with FileHandler("data/example.txt", "w") as f:
        f.write("Hello RAII!")
    # File automatically closed here
    with FileHandler("data/example.txt", "r") as f:
        content = f.read()
        print(content)
