# Python Class Fundamentals

## Overview
Essential Python class features for writing clean, maintainable object-oriented code.

---

## 1. Properties (`properties.py`)

**What:** Controlled access to attributes using `@property` decorator.

**When to use:**
- Need validation on attribute assignment
- Want computed/derived attributes (read-only)
- Encapsulation without breaking attribute-style access

**Key points:**
```python
@property          # Getter
@attribute.setter  # Setter with validation
@attribute.deleter # Optional deleter
```

**Example:**
```python
@property
def age(self) -> int:
    return self._age

@age.setter
def age(self, value: int) -> None:
    if value < 0:
        raise ValueError("Age cannot be negative")
    self._age = value
```

**Benefits:**
- Validation on assignment
- Computed properties (e.g., `is_adult` from `age`)
- Can change internal implementation without breaking API

---

## 2. Class vs Static Methods (`class_vs_static_methods.py`)

### `@classmethod`
**What:** Method that receives the class (`cls`) as first parameter.

**When to use:**
- Alternative constructors
- Factory methods
- Access/modify class attributes

**Example:**
```python
@classmethod
def from_birth_date(cls, username: str, birth_date: str):
    year = int(birth_date.split("-")[0])
    return cls(username, year)  # Returns instance of the class
```

### `@staticmethod`
**What:** Regular function grouped with the class, no special first parameter.

**When to use:**
- Utility functions logically related to the class
- No need to access class or instance data

**Example:**
```python
@staticmethod
def is_valid_username(username: str) -> bool:
    return len(username) >= 3 and username.isalnum()
```

### Comparison

| Type | First Parameter | Access to | Use Case |
|------|----------------|-----------|----------|
| Instance method | `self` | Instance data | Regular operations |
| `@classmethod` | `cls` | Class data | Alternative constructors, class state |
| `@staticmethod` | None | Nothing | Utility functions |

---

## 3. Special Methods (`special_methods.py`)

**What:** "Dunder" (double underscore) methods that customize object behavior.

**Most commonly used:**

| Method | Purpose | Example Usage |
|--------|---------|---------------|
| `__str__` | User-friendly string | `print(obj)` |
| `__repr__` | Developer-friendly representation | Debugging, `repr(obj)` |
| `__eq__` | Equality comparison | `obj1 == obj2` |
| `__hash__` | Make hashable | Use in sets/dicts |
| `__len__` | Length | `len(obj)` |
| `__getitem__` | Index access | `obj[0]` |
| `__contains__` | Membership test | `item in obj` |

**Example:**
```python
def __str__(self) -> str:
    return f"{self.name} - ${self.price}"

def __eq__(self, other) -> bool:
    if not isinstance(other, Product):
        return False
    return self.name == other.name and self.price == other.price
```

**Key rules:**
- `__str__` for users, `__repr__` for developers
- If implementing `__eq__`, also implement `__hash__` for sets/dicts
- Special methods enable Pythonic interfaces

---

## 4. Class Attributes (`class_attributes.py`)

### Instance Attributes
**What:** Unique to each instance, defined in `__init__`.

```python
def __init__(self, name: str):
    self.name = name  # Instance attribute
```

### Class Attributes
**What:** Shared across all instances, defined at class level.

```python
class Counter:
    total_count = 0  # Class attribute - shared

    def __init__(self, name: str):
        self.name = name  # Instance attribute - unique
        Counter.total_count += 1
```

### When to use class attributes:
- Shared configuration (database host, API keys)
- Counters/statistics across all instances
- Default values shared by all instances
- Constants

### Comparison

| Type | Scope | Modified via | Use Case |
|------|-------|--------------|----------|
| Instance | Per instance | `self.attribute` | Unique data per object |
| Class | All instances | `ClassName.attribute` or `cls.attribute` | Shared config/state |

**Warning:** Don't use mutable class attributes (lists/dicts) unless you want shared state!

---

## Quick Reference

```python
class Example:
    # Class attribute
    class_var = 0

    def __init__(self, name):
        # Instance attribute
        self.name = name
        self._private = None

    # Property
    @property
    def private(self):
        return self._private

    # Class method
    @classmethod
    def from_something(cls, data):
        return cls(data)

    # Static method
    @staticmethod
    def utility():
        return "result"

    # Special methods
    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name
```

---

## Running Examples

```bash
python class_fundamentals/properties.py
python class_fundamentals/class_vs_static_methods.py
python class_fundamentals/special_methods.py
python class_fundamentals/class_attributes.py
```
