# Singleton Pattern

## Concept

Singleton ensures a class has only one instance and provides a global point of access to it. All requests for the instance return the same object.

## Core Principle

**One class, one instance, global access.**

## When to Use

Use Singleton when you need **exactly one instance** of a class:

✅ **Use for:**
- Configuration managers
- Logging systems
- Database connection pools
- Cache managers
- Thread pools
- Hardware interface access (printer spoolers, device drivers)

❌ **Don't use for:**
- As a substitute for global variables
- When testing requires multiple instances
- When parallel instances might be needed later
- As a replacement for dependency injection

## How to Use in Python

### 1. Module-Level Singleton (PREFERRED - Most Pythonic)

```python
# config.py
class Config:
    def __init__(self):
        self.setting = "value"

# Create single instance at module level
config = Config()

# Usage
from config import config
```

**Why prefer this?** Python modules are inherently singletons. Simple, idiomatic, no magic.

### 2. Classic Singleton (Use when explicit control needed)

```python
class Singleton:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

# Usage
instance1 = Singleton()
instance2 = Singleton()
assert instance1 is instance2  # Same object
```

## Opinion: Best Practices

1. **Use module-level singletons** - 95% of the time, this is all you need
2. **Make them immutable after initialization** - Prevent accidental state changes
3. **Consider dependency injection instead** - Better for testing and flexibility
4. **Thread-safety matters** - Use locks if initialization isn't thread-safe
5. **Don't abuse it** - Singletons introduce global state (often an anti-pattern)

## Anti-patterns

❌ Using Singleton for everything (global state pollution)
❌ Hard-coding dependencies to singletons (makes testing hard)
❌ Lazy initialization without thread safety
❌ Mocking hell in tests due to global state

## Testing Considerations

Singletons make testing harder because:
- State persists between tests
- Hard to mock or replace
- Can create test coupling

**Solution:** Either:
- Use dependency injection instead of Singletons
- Add a `reset()` method for tests (but this breaks the pattern guarantee)
- Use module-level instances that can be monkey-patched in tests

## Quick Win

**In Python, just use a module with module-level instances.** Don't overthink it.

```python
# logger.py
import logging
logger = logging.getLogger(__name__)

# Usage anywhere
from logger import logger
logger.info("Simple and Pythonic")
```
