"""
Constructor Injection Pattern
Dependencies are provided through the class constructor (__init__).
Most common and explicit form of dependency injection.
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
    """Service with dependencies injected via constructor."""

    def __init__(self, logger: Logger, database: Database):
        self.logger = logger
        self.database = database

    def create_user(self, username: str) -> str:
        self.logger.log(f"Creating user: {username}")
        result = self.database.query(f"INSERT INTO users (name) VALUES ('{username}')")
        self.logger.log("User created successfully")
        return result

    def get_user(self, user_id: int) -> str:
        self.logger.log(f"Fetching user: {user_id}")
        result = self.database.query(f"SELECT * FROM users WHERE id = {user_id}")
        return result


if __name__ == "__main__":
    # Manually inject dependencies
    logger = Logger()
    database = Database("postgresql://localhost:5432/mydb")

    # Create service with injected dependencies
    user_service = UserService(logger, database)

    # Use the service
    user_service.create_user("alice")
    print(user_service.get_user(1))

    # Easy to swap dependencies for testing
    test_db = Database("sqlite://memory")
    test_service = UserService(logger, test_db)
    test_service.create_user("bob")
