"""
Module-level Singleton Pattern
The module itself acts as a singleton since Python only imports a module once.
"""


class DatabaseConnection:
    def __init__(self):
        self.host = "localhost"
        self.port = 5432
        self.connected = False

    def connect(self):
        self.connected = True
        return f"Connected to {self.host}:{self.port}"

    def query(self, sql: str):
        if not self.connected:
            raise RuntimeError("Not connected to database")
        return f"Executing: {sql}"


# Create a single instance at module level
db_connection = DatabaseConnection()


if __name__ == "__main__":
    # Example usage
    print("First reference:")
    print(db_connection.connect())
    print(db_connection.query("SELECT * FROM users"))

    # Demonstrate it's the same instance
    print("\nSecond reference:")
    from module_singleton import db_connection as db2

    print(f"Same instance: {db_connection is db2}")
    print(f"Already connected: {db2.connected}")
