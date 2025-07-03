# Context Managers: Python's Beloved Cleanup Pattern

## Community Attitude: "Use Them Everywhere"

**Consensus**: Context managers are universally loved. They're considered one of Python's best features for resource management.

**Modern trend**: Custom context managers are increasingly common. The `contextlib` module makes them easy to create.

## What Context Managers Actually Do

Context managers ensure that setup and cleanup code runs reliably, even when exceptions occur. They implement the context management protocol.

```python
# The protocol
class ContextManager:
    def __enter__(self):
        # Setup code
        return self  # or some resource
    
    def __exit__(self, exc_type, exc_value, traceback):
        # Cleanup code
        # Return True to suppress exceptions
        return False

# Usage
with ContextManager() as resource:
    # Use resource
    pass
# Cleanup happens automatically
```

**You use them constantly:**
```python
with open('file.txt') as f:  # File context manager
    content = f.read()
# File automatically closed

import threading
lock = threading.Lock()
with lock:  # Lock context manager
    # Critical section
    pass
# Lock automatically released
```

## When Context Managers Are Worth Using

### 1. Resource Management (Primary Use Case)
```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def database_connection(db_path: str):
    """Ensure database connection is properly closed"""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()

# Usage
with database_connection('app.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
# Connection automatically closed, even on exception
```

### 2. Temporary State Changes
```python
import os
from contextlib import contextmanager

@contextmanager
def temporary_directory(path: str):
    """Temporarily change working directory"""
    old_path = os.getcwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(old_path)

# Usage
with temporary_directory('/tmp'):
    # Work in /tmp
    with open('temp_file.txt', 'w') as f:
        f.write('temporary data')
# Automatically back to original directory
```

### 3. Performance Monitoring
```python
import time
from contextlib import contextmanager

@contextmanager
def timer(operation_name: str):
    """Time how long an operation takes"""
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print(f"{operation_name} took {end - start:.4f} seconds")

# Usage
with timer("Database query"):
    # Expensive operation
    time.sleep(1)
# Automatically prints timing
```

### 4. Exception Handling
```python
from contextlib import contextmanager
import logging

@contextmanager
def ignore_errors(*exceptions):
    """Suppress specific exceptions"""
    try:
        yield
    except exceptions as e:
        logging.warning(f"Ignored error: {e}")

# Usage
with ignore_errors(FileNotFoundError, PermissionError):
    os.remove('might_not_exist.txt')
# Continues execution even if file doesn't exist
```

## Modern Context Manager Patterns

### 1. Class-Based (Traditional)
```python
import threading

class DatabasePool:
    def __init__(self, max_connections: int):
        self.max_connections = max_connections
        self.connections = []
        self.lock = threading.Lock()
    
    def __enter__(self):
        with self.lock:
            if len(self.connections) < self.max_connections:
                connection = self._create_connection()
                self.connections.append(connection)
                return connection
            else:
                raise RuntimeError("No available connections")
    
    def __exit__(self, exc_type, exc_value, traceback):
        # Return connection to pool
        # Handle cleanup
        return False

# Usage
pool = DatabasePool(max_connections=5)
with pool as conn:
    # Use connection
    pass
```

### 2. Generator-Based (Modern, Preferred)
```python
from contextlib import contextmanager
import tempfile
import os

@contextmanager
def temporary_file(suffix='.tmp'):
    """Create and clean up a temporary file"""
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, 'w') as f:
            yield f, path
    finally:
        if os.path.exists(path):
            os.unlink(path)

# Usage
with temporary_file('.json') as (file, path):
    file.write('{"key": "value"}')
    # File exists and is writable
# File automatically deleted
```

### 3. Async Context Managers
```python
import asyncio
import aiohttp
from contextlib import asynccontextmanager

@asynccontextmanager
async def http_session():
    """Async HTTP session with proper cleanup"""
    session = aiohttp.ClientSession()
    try:
        yield session
    finally:
        await session.close()

# Usage
async def fetch_data():
    async with http_session() as session:
        async with session.get('https://api.example.com') as response:
            return await response.json()
```

### 4. Multiple Context Managers
```python
from contextlib import ExitStack

def process_multiple_files(filenames: list[str]):
    """Process multiple files with proper cleanup"""
    with ExitStack() as stack:
        files = [
            stack.enter_context(open(fname)) 
            for fname in filenames
        ]
        
        # Process all files
        for file in files:
            print(f"Processing {file.name}")
    # All files automatically closed
```

## Performance Benefits

### Resource Leak Prevention
```python
# Without context manager (DANGEROUS)
def bad_file_processing():
    files = []
    for i in range(1000):
        f = open(f'file_{i}.txt', 'w')  # File handles leak!
        files.append(f)
        f.write('data')
    # Files never closed - resource leak!

# With context manager (SAFE)
def good_file_processing():
    for i in range(1000):
        with open(f'file_{i}.txt', 'w') as f:
            f.write('data')
    # All files properly closed
```

### Exception Safety
```python
import time

# Without context manager - cleanup might not happen
def unsafe_operation():
    resource = acquire_expensive_resource()
    try:
        # If this raises an exception...
        risky_operation(resource)
        release_expensive_resource(resource)  # This might not run!
    except Exception:
        # Need to remember to clean up here too
        release_expensive_resource(resource)
        raise

# With context manager - cleanup always happens
@contextmanager
def safe_resource():
    resource = acquire_expensive_resource()
    try:
        yield resource
    finally:
        release_expensive_resource(resource)  # Always runs

def safe_operation():
    with safe_resource() as resource:
        risky_operation(resource)
    # Cleanup guaranteed, even on exception
```

## Advanced Patterns

### 1. Suppressing Specific Exceptions
```python
from contextlib import contextmanager

@contextmanager
def suppress_and_log(*exceptions):
    """Suppress exceptions but log them"""
    try:
        yield
    except exceptions as e:
        import logging
        logging.error(f"Suppressed exception: {e}")
        # Return None implicitly suppresses exception

# Usage
with suppress_and_log(ConnectionError, TimeoutError):
    make_network_request()
# Continues execution even if network fails
```

### 2. Conditional Context Management
```python
from contextlib import nullcontext

def process_data(data, use_lock=False):
    """Conditionally use a lock"""
    lock_context = threading.Lock() if use_lock else nullcontext()
    
    with lock_context:
        # Process data
        # Lock is only acquired if use_lock=True
        return transform(data)
```

### 3. Nested Resource Management
```python
@contextmanager
def database_transaction(connection):
    """Database transaction with rollback on error"""
    transaction = connection.begin()
    try:
        yield connection
        transaction.commit()
    except Exception:
        transaction.rollback()
        raise

# Usage
with database_connection('db.sqlite') as conn:
    with database_transaction(conn) as trans_conn:
        trans_conn.execute("INSERT INTO users VALUES (?)", ("Alice",))
        trans_conn.execute("INSERT INTO users VALUES (?)", ("Bob",))
    # Transaction committed only if no exceptions
```

### 4. Context Manager as Decorator
```python
from functools import wraps

def with_timing(func):
    """Decorator that times function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with timer(func.__name__):
            return func(*args, **kwargs)
    return wrapper

@with_timing
def slow_function():
    time.sleep(1)
    return "done"

# Automatically times every call
result = slow_function()  # Prints timing info
```

## Common Pitfalls and Solutions

### 1. Forgetting to Handle Exceptions in __exit__
```python
# BAD: Exception handling missing
class BadContextManager:
    def __exit__(self, exc_type, exc_value, traceback):
        cleanup_resource()  # What if this raises?
        return False

# GOOD: Robust exception handling
class GoodContextManager:
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            cleanup_resource()
        except Exception as cleanup_error:
            if exc_type is None:
                # No original exception, re-raise cleanup error
                raise cleanup_error
            else:
                # Original exception takes precedence
                import logging
                logging.error(f"Cleanup failed: {cleanup_error}")
        return False
```

### 2. Returning Wrong Value from __exit__
```python
# BAD: Accidentally suppressing exceptions
class BadSuppressor:
    def __exit__(self, exc_type, exc_value, traceback):
        print("Cleaning up")
        return True  # BAD: Suppresses ALL exceptions!

# GOOD: Explicit exception handling
class GoodSuppressor:
    def __exit__(self, exc_type, exc_value, traceback):
        print("Cleaning up")
        if exc_type is ValueError:
            print("Suppressing ValueError")
            return True  # Only suppress ValueError
        return False  # Let other exceptions propagate
```

### 3. Resource Leaks in Generator Context Managers
```python
# BAD: Resource might leak if exception occurs during setup
@contextmanager
def bad_resource_manager():
    resource1 = acquire_resource()
    resource2 = acquire_resource()  # If this fails, resource1 leaks!
    try:
        yield (resource1, resource2)
    finally:
        release_resource(resource1)
        release_resource(resource2)

# GOOD: Proper exception handling during setup
@contextmanager
def good_resource_manager():
    resource1 = acquire_resource()
    try:
        resource2 = acquire_resource()
        try:
            yield (resource1, resource2)
        finally:
            release_resource(resource2)
    finally:
        release_resource(resource1)
```

## Testing Context Managers

```python
import pytest
from unittest.mock import Mock, patch

def test_context_manager_cleanup():
    """Test that cleanup happens even on exception"""
    cleanup_mock = Mock()
    
    @contextmanager
    def test_context():
        try:
            yield "resource"
        finally:
            cleanup_mock()
    
    # Test normal operation
    with test_context() as resource:
        assert resource == "resource"
    cleanup_mock.assert_called_once()
    
    # Test exception handling
    cleanup_mock.reset_mock()
    with pytest.raises(ValueError):
        with test_context():
            raise ValueError("test error")
    cleanup_mock.assert_called_once()  # Cleanup still happened

def test_file_context_manager():
    """Test file operations with context manager"""
    with patch('builtins.open') as mock_open:
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        with open('test.txt') as f:
            f.read()
        
        mock_open.assert_called_once_with('test.txt')
        mock_file.read.assert_called_once()
```

## Real-World Examples

### 1. Database Connection Pool
```python
import queue
import threading
from contextlib import contextmanager

class ConnectionPool:
    def __init__(self, create_connection, max_size=10):
        self.create_connection = create_connection
        self.pool = queue.Queue(maxsize=max_size)
        self.max_size = max_size
        self.current_size = 0
        self.lock = threading.Lock()
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool with automatic return"""
        conn = None
        try:
            conn = self.pool.get_nowait()
        except queue.Empty:
            with self.lock:
                if self.current_size < self.max_size:
                    conn = self.create_connection()
                    self.current_size += 1
                else:
                    conn = self.pool.get()  # Block until available
        
        try:
            yield conn
        finally:
            self.pool.put(conn)

# Usage
pool = ConnectionPool(create_database_connection, max_size=5)

with pool.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
# Connection automatically returned to pool
```

### 2. Temporary Environment Variables
```python
import os
from contextlib import contextmanager

@contextmanager
def temporary_env(**env_vars):
    """Temporarily set environment variables"""
    old_values = {}
    
    # Save old values and set new ones
    for key, value in env_vars.items():
        old_values[key] = os.environ.get(key)
        os.environ[key] = str(value)
    
    try:
        yield
    finally:
        # Restore old values
        for key, old_value in old_values.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value

# Usage
with temporary_env(DEBUG='True', API_KEY='test-key'):
    # Environment variables are set
    app.run()
# Original environment restored
```

### 3. Redis Lock
```python
import redis
import time
from contextlib import contextmanager

@contextmanager
def redis_lock(redis_client, key, timeout=10):
    """Distributed lock using Redis"""
    identifier = str(time.time())
    
    # Acquire lock
    if redis_client.set(key, identifier, nx=True, ex=timeout):
        try:
            yield
        finally:
            # Release lock only if we still own it
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            redis_client.eval(lua_script, 1, key, identifier)
    else:
        raise RuntimeError(f"Could not acquire lock for {key}")

# Usage
redis_client = redis.Redis()
with redis_lock(redis_client, "critical_section"):
    # Only one process can execute this at a time
    perform_critical_operation()
```

## Decision Matrix

| Use Case | Context Manager | Alternative | Reason |
|----------|----------------|-------------|---------|
| Resource cleanup | ✅ | try/finally | Automatic, exception-safe |
| Temporary state | ✅ | Manual save/restore | Guaranteed restoration |
| Exception suppression | ✅ | try/except | Cleaner, reusable |
| Timing operations | ✅ | Manual timing | Automatic, accurate |
| Lock management | ✅ | Manual acquire/release | Exception-safe release |
| File operations | ✅ | Manual close | Built-in, reliable |

## Bottom Line

**Use context managers for:**
- Any resource that needs cleanup (files, connections, locks)
- Temporary state changes
- Exception-safe operations
- Performance monitoring
- Setup/teardown patterns

**Community consensus**: Context managers are one of Python's best features. Use them liberally. The `with` statement should be your first choice for any setup/cleanup scenario.

**Modern best practice**: Prefer `@contextmanager` decorator over class-based context managers for simplicity. Use `ExitStack` for complex scenarios involving multiple resources.