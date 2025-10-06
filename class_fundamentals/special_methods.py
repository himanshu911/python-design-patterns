"""
Special Methods (Dunder Methods)
Magic methods that customize object behavior.
Most commonly used: __str__, __repr__, __eq__, __hash__, __len__, __getitem__
"""


class Product:
    """Product with string representation and comparison."""

    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def __str__(self) -> str:
        """User-friendly string representation (for print())."""
        return f"{self.name} - ${self.price:.2f}"

    def __repr__(self) -> str:
        """Developer-friendly representation (for debugging)."""
        return f"Product(name='{self.name}', price={self.price})"

    def __eq__(self, other: object) -> bool:
        """Equality comparison (==)."""
        if not isinstance(other, Product):
            return False
        return self.name == other.name and self.price == other.price

    def __hash__(self) -> int:
        """Make object hashable (usable in sets/dicts)."""
        return hash((self.name, self.price))


class ShoppingCart:
    """Shopping cart with list-like behavior."""

    def __init__(self):
        self._items: list[Product] = []

    def add(self, product: Product) -> None:
        """Add product to cart."""
        self._items.append(product)

    def __len__(self) -> int:
        """Length of cart (len())."""
        return len(self._items)

    def __getitem__(self, index: int) -> Product:
        """Access items by index (cart[0])."""
        return self._items[index]

    def __contains__(self, product: Product) -> bool:
        """Check if product in cart (in operator)."""
        return product in self._items

    def __str__(self) -> str:
        """String representation of cart."""
        if not self._items:
            return "Empty cart"
        items_str = ", ".join(str(item) for item in self._items)
        return f"Cart with {len(self)} items: [{items_str}]"


if __name__ == "__main__":
    # Product with __str__ and __repr__
    product1 = Product("Laptop", 999.99)
    print(f"str(product1): {str(product1)}")
    print(f"repr(product1): {repr(product1)}")

    # Equality comparison
    product2 = Product("Laptop", 999.99)
    product3 = Product("Mouse", 29.99)

    print(f"\nproduct1 == product2: {product1 == product2}")
    print(f"product1 == product3: {product1 == product3}")

    # Hashable - can use in set
    products_set = {product1, product2, product3}
    print(f"\nUnique products in set: {len(products_set)}")

    # Shopping cart with special methods
    print("\n--- Shopping Cart ---")
    cart = ShoppingCart()
    cart.add(product1)
    cart.add(product3)

    print(f"Cart length: {len(cart)}")
    print(f"First item: {cart[0]}")
    print(f"Is laptop in cart: {product1 in cart}")
    print(f"Cart: {cart}")
