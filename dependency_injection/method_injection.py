"""
Method Injection Pattern
Dependencies are passed as method parameters instead of constructor.
Useful when different dependencies are needed for different operations.
"""


class Logger:
    """Simple logger for demonstration."""

    def log(self, message: str) -> None:
        print(f"[LOG] {message}")


class Database:
    """Simple database for demonstration."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def query(self, sql: str) -> str:
        return f"Executing on {self.connection_string}: {sql}"


class UserService:
    """Service that accepts dependencies per method call."""

    def create_user(self, username: str, logger: Logger, database: Database) -> str:
        """Create user with dependencies injected per method call."""
        logger.log(f"Creating user: {username}")
        result = database.query(f"INSERT INTO users (name) VALUES ('{username}')")
        logger.log("User created successfully")
        return result

    def get_user(self, user_id: int, logger: Logger, database: Database) -> str:
        """Get user with dependencies injected per method call."""
        logger.log(f"Fetching user: {user_id}")
        result = database.query(f"SELECT * FROM users WHERE id = {user_id}")
        return result


if __name__ == "__main__":
    # Create service once
    service = UserService()

    # Inject dependencies per method call
    logger = Logger()
    db_prod = Database("postgresql://localhost:5432/mydb")

    print("Using production database:")
    service.create_user("alice", logger, db_prod)
    print(service.get_user(1, logger, db_prod))

    # Can use different database for different calls
    db_test = Database("sqlite://memory")

    print("\nUsing test database:")
    service.create_user("bob", logger, db_test)
    print(service.get_user(2, logger, db_test))
