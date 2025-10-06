"""
Property Decorator - @property
Provides controlled access to attributes with getter/setter/deleter.
Allows validation, computed properties, and encapsulation.
"""


class User:
    """User with validated properties."""

    def __init__(self, username: str, age: int):
        self._username = username
        self._age = age

    @property
    def username(self) -> str:
        """Getter for username."""
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        """Setter with validation."""
        if not value or len(value) < 3:
            raise ValueError("Username must be at least 3 characters")
        self._username = value

    @property
    def age(self) -> int:
        """Getter for age."""
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        """Setter with validation."""
        if value < 0 or value > 150:
            raise ValueError("Age must be between 0 and 150")
        self._age = value

    @property
    def is_adult(self) -> bool:
        """Computed property (read-only)."""
        return self._age >= 18


class Product:
    """Product with price validation."""

    def __init__(self, name: str, price: float):
        self.name = name
        self._price = price

    @property
    def price(self) -> float | None:
        """Get price."""
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        """Set price with validation."""
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = value

    @price.deleter
    def price(self) -> None:
        """Delete price (set to None)."""
        print(f"Deleting price for {self.name}")
        self._price = None


if __name__ == "__main__":
    # User with property validation
    user = User("alice", 25)
    print(f"Username: {user.username}, Age: {user.age}")
    print(f"Is adult: {user.is_adult}")

    # Validation on setter
    user.age = 17
    print(f"After update - Is adult: {user.is_adult}")

    # Computed property is read-only
    try:
        user.is_adult = True  # type: ignore
    except AttributeError as e:
        print(f"\nError: {e}")

    # Invalid username
    try:
        user.username = "ab"
    except ValueError as e:
        print(f"Error: {e}")

    # Product with deleter
    print("\n--- Product example ---")
    product = Product("Laptop", 999.99)
    print(f"{product.name}: ${product.price}")

    del product.price
    print(f"Price after deletion: {product.price}")
