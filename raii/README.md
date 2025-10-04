# RAII Pattern (Resource Acquisition Is Initialization)

## Concept

RAII ties resource lifetime to object lifetime. When an object is created, it acquires resources. When destroyed, it releases them. This guarantees cleanup even when exceptions occur.

## Core Principle

**Resources are acquired in initialization and released in destruction.**

In Python, there are **two proper ways** to implement RAII:
1. **Class-based**: `__enter__` and `__exit__` methods
2. **Function-based**: `@contextmanager` decorator from `contextlib`

**Never use `__init__` and `__del__`** - unreliable due to non-deterministic garbage collection.

## When to Use

Use RAII when you need **deterministic resource cleanup**:

✅ **Use for:**
- File handles
- Database connections
- Network sockets
- Locks and semaphores
- Temporary files/directories
- External resources (GPU memory, hardware devices)

❌ **Don't use for:**
- Simple data objects with no resources
- Resources managed by other systems
- When you need explicit control over timing

## How to Use

### 1. Class-Based RAII (Use for complex resources)

```python
class FileHandler:
    def __init__(self, filename, mode='r'):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        # Acquire resource
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Release resource (always called)
        if self.file:
            self.file.close()
        return False  # Don't suppress exceptions

# Usage
with FileHandler("data.txt", "w") as f:
    f.write("Data")
# Resource automatically cleaned up here, even if exception occurs
```

**Use when:** You need state, multiple methods, or complex initialization logic.

### 2. Function-Based RAII (Use for simple resources - PREFERRED)

```python
from contextlib import contextmanager

@contextmanager
def database_connection(host, port):
    # Acquire resource
    conn = create_connection(host, port)
    print(f"Connected to {host}:{port}")

    try:
        yield conn  # Provide resource to caller
    finally:
        # Release resource (always executed)
        conn.close()
        print(f"Disconnected")

# Usage
with database_connection("localhost", 5432) as conn:
    conn.query("SELECT * FROM users")
# Automatically disconnected
```

**Use when:** Simple acquire-release pattern without additional state or methods.

## Opinion: Best Practices

1. **Prefer `@contextmanager` over classes** - 90% of the time it's cleaner and simpler
2. **Use classes only when you need state or multiple methods**
3. **Make cleanup idempotent** - Safe to call multiple times
4. **Don't suppress exceptions** - Return `False` in `__exit__` or don't catch in `finally`
5. **Keep it simple** - One resource per manager
6. **NEVER rely on `__del__`** - It's called by garbage collector (timing unpredictable)

## Anti-patterns

❌ Using `__del__` for cleanup (non-deterministic, unreliable)
❌ Managing multiple unrelated resources in one manager
❌ Swallowing exceptions in `__exit__` or `finally`
❌ Forgetting to use `with` statement
❌ Using class-based approach when function-based would suffice

## Which Pattern to Choose?

**Use `@contextmanager` (function-based) when:**
- Simple acquire-release logic
- No additional state needed
- No other methods required
- Example: temporary files, connections, locks

**Use class-based when:**
- Need to store state
- Need additional methods beyond context management
- Complex initialization logic
- Want to reuse the manager object

## Quick Win

Python's built-in types already use RAII: `open()`, `threading.Lock()`, `sqlite3.connect()`. Just use them with `with` statements.

For custom resources, start with `@contextmanager` - only switch to classes if you need more complexity.
