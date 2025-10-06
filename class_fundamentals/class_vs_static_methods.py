"""
Class Methods vs Static Methods
@classmethod - Operates on the class itself, receives cls as first parameter
@staticmethod - Independent utility function, no access to class or instance
"""

from datetime import datetime


class User:
    """User with alternative constructors and utility methods."""

    total_users = 0  # Class attribute

    def __init__(self, username: str, birth_year: int):
        self.username = username
        self.birth_year = birth_year
        User.total_users += 1

    @classmethod
    def from_birth_date(cls, username: str, birth_date: str):
        """Alternative constructor - creates User from birth date string.

        @classmethod receives cls (the class itself) as first parameter.
        Useful for alternative constructors.
        """
        year = int(birth_date.split("-")[0])
        return cls(username, year)

    @classmethod
    def get_total_users(cls):
        """Access class attributes.

        @classmethod can access and modify class attributes.
        """
        return cls.total_users

    @staticmethod
    def is_valid_username(username: str) -> bool:
        """Utility function that doesn't need class or instance data.

        @staticmethod doesn't receive cls or self.
        Just a regular function grouped with the class.
        """
        return len(username) >= 3 and username.isalnum()

    def get_age(self) -> int:
        """Regular instance method - has access to self."""
        current_year = datetime.now().year
        return current_year - self.birth_year


class MathUtils:
    """Utility class with only static methods."""

    @staticmethod
    def add(a: int, b: int) -> int:
        """Add two numbers - no need for class or instance."""
        return a + b

    @staticmethod
    def is_even(num: int) -> bool:
        """Check if number is even."""
        return num % 2 == 0


if __name__ == "__main__":
    # Regular constructor
    user1 = User("alice", 1990)
    print(f"{user1.username}, Age: {user1.get_age()}")

    # Class method as alternative constructor
    user2 = User.from_birth_date("bob", "1995-05-15")
    print(f"{user2.username}, Age: {user2.get_age()}")

    # Class method to access class attribute
    print(f"\nTotal users: {User.get_total_users()}")

    # Static method - can be called on class or instance
    print(f"\nIs 'ab' valid: {User.is_valid_username('ab')}")
    print(f"Is 'alice' valid: {User.is_valid_username('alice')}")
    print(f"Is 'alice' valid (via instance): {user1.is_valid_username('alice')}")

    # Utility class with only static methods
    print("\n--- Math Utils ---")
    print(f"5 + 3 = {MathUtils.add(5, 3)}")
    print(f"Is 4 even: {MathUtils.is_even(4)}")
