"""
Property Injection Pattern
Dependencies are set via properties/setters after object construction.
Useful for optional dependencies or when dependency needs to change at runtime.
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
    """Service with optional dependencies set via properties."""

    def __init__(self):
        self._logger: Logger | None = None
        self._database: Database | None = None

    @property
    def logger(self) -> Logger | None:
        return self._logger

    @logger.setter
    def logger(self, logger: Logger) -> None:
        self._logger = logger

    @property
    def database(self) -> Database | None:
        return self._database

    @database.setter
    def database(self, database: Database) -> None:
        self._database = database

    def create_user(self, username: str) -> str:
        """Create user with optional logging and database."""
        if self._logger:
            self._logger.log(f"Creating user: {username}")

        if self._database:
            result = self._database.query(
                f"INSERT INTO users (name) VALUES ('{username}')"
            )
        else:
            result = f"Created user: {username} (no database)"

        if self._logger:
            self._logger.log("User created successfully")

        return result

    def get_user(self, user_id: int) -> str:
        """Get user with optional logging and database."""
        if self._logger:
            self._logger.log(f"Fetching user: {user_id}")

        if self._database:
            result = self._database.query(f"SELECT * FROM users WHERE id = {user_id}")
        else:
            result = f"User({user_id}) (no database)"

        return result


if __name__ == "__main__":
    # Create service without any dependencies (works fine)
    service = UserService()
    print(service.create_user("alice"))
    print(service.get_user(1))

    print("\n--- After injecting logger ---")

    # Inject logger via property
    service.logger = Logger()
    print(service.create_user("bob"))

    print("\n--- After injecting database ---")

    # Inject database via property
    service.database = Database("postgresql://localhost:5432/mydb")
    print(service.create_user("charlie"))
    print(service.get_user(1))

    print("\n--- Change database at runtime ---")

    # Can change dependency at runtime
    service.database = Database("sqlite://memory")
    print(service.create_user("diana"))
