"""
Class Attributes vs Instance Attributes
Class attributes are shared across all instances.
Instance attributes are unique to each instance.
"""


class Counter:
    """Demonstrates class vs instance attributes."""

    total_count = 0  # Class attribute - shared by all instances

    def __init__(self, name: str):
        self.name = name  # Instance attribute - unique to each instance
        self.count = 0  # Instance attribute
        Counter.total_count += 1  # Modify class attribute

    def increment(self) -> None:
        """Increment instance counter."""
        self.count += 1

    @classmethod
    def get_total_count(cls) -> int:
        """Get total count across all instances."""
        return cls.total_count


class DatabaseConnection:
    """Demonstrates shared configuration."""

    host = "localhost"  # Class attribute - shared config
    port = 5432  # Class attribute

    def __init__(self, database: str):
        self.database = database  # Instance attribute - unique per connection

    def get_connection_string(self) -> str:
        """Build connection string using both class and instance attributes."""
        return f"postgresql://{self.host}:{self.port}/{self.database}"

    @classmethod
    def set_host(cls, host: str) -> None:
        """Change host for all connections."""
        cls.host = host


class BankAccount:
    """Demonstrates class attribute for shared data."""

    interest_rate = 0.03  # Class attribute - same for all accounts

    def __init__(self, owner: str, balance: float):
        self.owner = owner  # Instance attribute
        self.balance = balance  # Instance attribute

    def calculate_interest(self) -> float:
        """Calculate interest using class attribute."""
        return self.balance * BankAccount.interest_rate

    @classmethod
    def update_interest_rate(cls, new_rate: float) -> None:
        """Update interest rate for all accounts."""
        cls.interest_rate = new_rate


if __name__ == "__main__":
    # Counter example
    counter1 = Counter("Counter1")
    counter2 = Counter("Counter2")

    counter1.increment()
    counter1.increment()
    counter2.increment()

    print(f"{counter1.name}: {counter1.count}")
    print(f"{counter2.name}: {counter2.count}")
    print(f"Total counters created: {Counter.get_total_count()}")

    # Database connection with shared config
    print("\n--- Database Connections ---")
    db1 = DatabaseConnection("users_db")
    db2 = DatabaseConnection("orders_db")

    print(f"DB1: {db1.get_connection_string()}")
    print(f"DB2: {db2.get_connection_string()}")

    # Change host for all connections
    DatabaseConnection.set_host("prod.example.com")
    print("\nAfter changing host:")
    print(f"DB1: {db1.get_connection_string()}")
    print(f"DB2: {db2.get_connection_string()}")

    # Bank account with shared interest rate
    print("\n--- Bank Accounts ---")
    acc1 = BankAccount("Alice", 1000)
    acc2 = BankAccount("Bob", 2000)

    print(f"Alice interest: ${acc1.calculate_interest():.2f}")
    print(f"Bob interest: ${acc2.calculate_interest():.2f}")

    # Update interest rate for all accounts
    BankAccount.update_interest_rate(0.05)
    print("\nAfter rate change to 5%:")
    print(f"Alice interest: ${acc1.calculate_interest():.2f}")
    print(f"Bob interest: ${acc2.calculate_interest():.2f}")
