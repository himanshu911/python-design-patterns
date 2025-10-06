# Dependency Injection Pattern

## Overview
Dependency Injection (DI) is a design pattern where dependencies are provided to an object rather than the object creating them itself. This promotes loose coupling, easier testing, and better code maintainability.

## Core Principle
Instead of a class creating its dependencies internally, the dependencies are "injected" from outside, allowing for flexibility and testability.

---

## Implementations

### 1. Constructor Injection (`constructor_injection.py`)
**Most common and recommended approach.**

Dependencies are passed through the class constructor.

**When to use:**
- Dependencies are required for the object to function
- Dependencies don't change during object lifetime
- You want explicit, clear dependency declaration

**Pros:**
- Dependencies are explicit and immutable
- Object is fully initialized after construction
- Easy to identify all dependencies at a glance

**Cons:**
- Can lead to large constructors if many dependencies exist
- All dependencies must be available at construction time

**Example:**
```python
class UserService:
    def __init__(self, logger: Logger, database: Database):
        self.logger = logger
        self.database = database
```

---

### 2. Method Injection (`method_injection.py`)
Dependencies are passed as parameters to specific methods.

**When to use:**
- Different operations need different dependencies
- Dependency varies per method call
- Same object needs to work with multiple implementations

**Pros:**
- Maximum flexibility - different dependency per call
- No need to store dependency as instance variable
- Clear which method uses which dependency

**Cons:**
- Method signatures can become complex
- Less convenient if same dependency used in multiple methods
- Caller must manage dependency lifecycle

**Example:**
```python
class ReportGenerator:
    def generate_report(self, data_source: DataSource):
        data = data_source.fetch_data()
        return self.format(data)
```

---

### 3. Property Injection (`property_injection.py`)
Dependencies are set via properties/setters after object construction.

**When to use:**
- Dependencies are optional
- Dependencies need to change at runtime
- Plugin/extension systems
- Late binding scenarios

**Pros:**
- Optional dependencies (graceful degradation)
- Can change dependencies after construction
- Good for optional features/plugins

**Cons:**
- Object may be in incomplete state after construction
- Dependencies can be modified unexpectedly
- Less explicit than constructor injection

**Example:**
```python
class UserService:
    @property
    def logger(self) -> Logger | None:
        return self._logger

    @logger.setter
    def logger(self, logger: Logger) -> None:
        self._logger = logger
```

---

## Comparison

| Pattern | Explicitness | Flexibility | Complexity | Best For |
|---------|--------------|-------------|------------|----------|
| Constructor | High | Low | Low | Required dependencies (95% of cases) |
| Method | High | Very High | Medium | Variable dependencies per call |
| Property | Medium | High | Low | Optional dependencies/plugins |

---

## Choosing the Right Pattern

1. **Start with Constructor Injection** - Default choice for 95% of cases
2. **Use Method Injection** - When dependency varies per operation
3. **Use Property Injection** - For optional features and plugins only

**Note:** DI containers (like in Java/C#) are rarely used in Python. Python's dynamic nature and simplicity make them unnecessary overhead for most projects. Stick to simple constructor injection.

---

## Benefits of Dependency Injection

1. **Testability**: Easy to inject mocks/stubs in tests
2. **Loose Coupling**: Classes depend on interfaces, not implementations
3. **Maintainability**: Changes to dependencies don't affect dependent classes
4. **Flexibility**: Easy to swap implementations
5. **Single Responsibility**: Classes focus on their logic, not dependency creation

---

## Running Examples

Each implementation file has a `if __name__ == "__main__"` block demonstrating the pattern:

```bash
python dependency_injection/constructor_injection.py
python dependency_injection/method_injection.py
python dependency_injection/property_injection.py
```
