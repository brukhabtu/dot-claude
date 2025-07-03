# Iterators and Generators: Memory-Efficient Pythonic Iteration

## Community Attitude: "Generators Are Magic, Custom Iterators Less So"

**Consensus**: Generators are beloved and widely used. Custom iterator classes are respected but considered unnecessary in most cases.

**Modern trend**: Generator functions and expressions dominate. Writing `__iter__`/`__next__` is rare outside of complex data structures.

## What They Actually Do

**Iterators**: Objects that implement the iteration protocol (`__iter__` and `__next__`)
**Generators**: Functions that yield values one at a time, automatically implementing the iterator protocol

```python
# Iterator protocol
class CustomIterator:
    def __iter__(self):
        return self
    
    def __next__(self):
        # Return next item or raise StopIteration
        pass

# Generator function (preferred)
def simple_generator():
    yield 1
    yield 2
    yield 3

# Generator expression (even simpler)
gen_expr = (x**2 for x in range(10))
```

## When Generators Are Worth Using

### 1. Memory-Efficient Data Processing
```python
def read_large_file(filename: str):
    """Process large files without loading everything into memory"""
    with open(filename, 'r') as file:
        for line in file:
            yield line.strip()

# Process 10GB file with constant memory usage
def process_large_file(filename: str):
    for line in read_large_file(filename):
        if line.startswith('ERROR'):
            yield f"Found error: {line}"

# Memory usage: O(1) instead of O(n)
errors = list(process_large_file('huge_log.txt'))
```

### 2. Infinite Sequences
```python
def fibonacci():
    """Generate infinite Fibonacci sequence"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

def primes():
    """Generate infinite prime numbers"""
    def is_prime(n):
        return all(n % i != 0 for i in range(2, int(n**0.5) + 1))
    
    yield 2
    candidate = 3
    while True:
        if is_prime(candidate):
            yield candidate
        candidate += 2

# Use with itertools for powerful combinations
import itertools
first_10_primes = list(itertools.islice(primes(), 10))
```

### 3. Pipeline Processing
```python
def read_data(source):
    """First stage: read raw data"""
    for item in source:
        yield item

def clean_data(data_stream):
    """Second stage: clean data"""
    for item in data_stream:
        cleaned = item.strip().lower()
        if cleaned:
            yield cleaned

def transform_data(data_stream):
    """Third stage: transform data"""
    for item in data_stream:
        yield item.upper()

def filter_data(data_stream, pattern):
    """Fourth stage: filter data"""
    for item in data_stream:
        if pattern in item:
            yield item

# Composable pipeline - processes one item at a time
def process_pipeline(source, pattern):
    pipeline = read_data(source)
    pipeline = clean_data(pipeline)
    pipeline = transform_data(pipeline)
    pipeline = filter_data(pipeline, pattern)
    return pipeline

# Memory efficient: processes item by item
results = list(process_pipeline(['  hello  ', '  WORLD  ', ''], 'HELLO'))
```

### 4. Stateful Iteration
```python
def moving_average(data, window_size):
    """Calculate moving average efficiently"""
    window = []
    for value in data:
        window.append(value)
        if len(window) > window_size:
            window.pop(0)
        
        if len(window) == window_size:
            yield sum(window) / window_size

# Memory efficient for large datasets
data = range(1_000_000)
averages = moving_average(data, window_size=100)
first_10_averages = list(itertools.islice(averages, 10))
```

## When Custom Iterators Are Worth Using

### 1. Complex Data Structures
```python
class BinaryTree:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
    
    def __iter__(self):
        """In-order traversal"""
        return BinaryTreeIterator(self)

class BinaryTreeIterator:
    def __init__(self, root):
        self.stack = []
        self._push_left(root)
    
    def _push_left(self, node):
        while node:
            self.stack.append(node)
            node = node.left
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if not self.stack:
            raise StopIteration
        
        node = self.stack.pop()
        self._push_left(node.right)
        return node.value

# Usage
tree = BinaryTree(2, BinaryTree(1), BinaryTree(3))
for value in tree:  # In-order: 1, 2, 3
    print(value)
```

### 2. Multiple Iteration Modes
```python
class Matrix:
    def __init__(self, data):
        self.data = data
        self.rows = len(data)
        self.cols = len(data[0]) if data else 0
    
    def __iter__(self):
        """Default: iterate by rows"""
        return self.iter_rows()
    
    def iter_rows(self):
        """Iterate row by row"""
        for row in self.data:
            yield row
    
    def iter_cols(self):
        """Iterate column by column"""
        for col_idx in range(self.cols):
            yield [self.data[row_idx][col_idx] for row_idx in range(self.rows)]
    
    def iter_elements(self):
        """Iterate element by element"""
        for row in self.data:
            for element in row:
                yield element

# Usage
matrix = Matrix([[1, 2, 3], [4, 5, 6]])
list(matrix.iter_rows())     # [[1, 2, 3], [4, 5, 6]]
list(matrix.iter_cols())     # [[1, 4], [2, 5], [3, 6]]
list(matrix.iter_elements()) # [1, 2, 3, 4, 5, 6]
```

## Performance Benefits

### Memory Usage Comparison
```python
import sys

# List comprehension: loads everything into memory
def list_approach(n):
    return [x**2 for x in range(n)]

# Generator: one item at a time
def generator_approach(n):
    return (x**2 for x in range(n))

# Memory comparison
large_list = list_approach(1_000_000)
large_gen = generator_approach(1_000_000)

print(f"List size: {sys.getsizeof(large_list)} bytes")        # ~8MB
print(f"Generator size: {sys.getsizeof(large_gen)} bytes")    # ~200 bytes

# Processing comparison
import time

def time_processing(data_source, name):
    start = time.time()
    result = sum(itertools.islice(data_source, 100_000))
    end = time.time()
    print(f"{name}: {end - start:.4f}s, result: {result}")

# List: creates everything first, then processes
time_processing(list_approach(1_000_000), "List")

# Generator: creates and processes on-demand
time_processing(generator_approach(1_000_000), "Generator")
```

### Lazy Evaluation Benefits
```python
def expensive_operation(x):
    """Simulate expensive computation"""
    time.sleep(0.01)  # 10ms delay
    return x**2

# Eager evaluation: all computed upfront
def eager_processing(data):
    return [expensive_operation(x) for x in data]

# Lazy evaluation: computed on demand
def lazy_processing(data):
    return (expensive_operation(x) for x in data)

data = range(100)

start = time.time()
eager_result = eager_processing(data)
print(f"Eager creation: {time.time() - start:.2f}s")  # ~1 second

start = time.time()
lazy_result = lazy_processing(data)
print(f"Lazy creation: {time.time() - start:.4f}s")   # ~0.0001 seconds

# Only pay cost when you actually use the data
start = time.time()
first_10_lazy = list(itertools.islice(lazy_result, 10))
print(f"First 10 from lazy: {time.time() - start:.2f}s")  # ~0.1 seconds
```

## Modern Generator Patterns

### 1. Generator Delegation with `yield from`
```python
def flatten_nested(nested_list):
    """Flatten arbitrarily nested lists"""
    for item in nested_list:
        if isinstance(item, list):
            yield from flatten_nested(item)  # Recursive delegation
        else:
            yield item

# Usage
nested = [1, [2, 3], [4, [5, 6]], 7]
flat = list(flatten_nested(nested))  # [1, 2, 3, 4, 5, 6, 7]
```

### 2. Generator Context Managers
```python
from contextlib import contextmanager

@contextmanager
def file_processor(filename):
    """Process file with automatic cleanup"""
    file = open(filename, 'r')
    try:
        def line_generator():
            for line in file:
                yield line.strip()
        yield line_generator()
    finally:
        file.close()

# Usage
with file_processor('data.txt') as lines:
    for line in lines:
        process(line)
```

### 3. Async Generators (Python 3.6+)
```python
import asyncio
import aiohttp

async def fetch_urls(urls):
    """Async generator for fetching URLs"""
    async with aiohttp.ClientSession() as session:
        for url in urls:
            async with session.get(url) as response:
                yield await response.text()

# Usage
async def process_websites():
    urls = ['http://example.com', 'http://python.org']
    async for content in fetch_urls(urls):
        print(f"Got {len(content)} bytes")
```

## When NOT to Use Generators

### ❌ Small, Fixed Datasets
```python
# DON'T: Generator overkill for small data
def process_small_list():
    for item in (x**2 for x in [1, 2, 3, 4, 5]):  # Unnecessary
        yield item

# DO: Simple list comprehension
def process_small_list():
    return [x**2 for x in [1, 2, 3, 4, 5]]
```

### ❌ When You Need Random Access
```python
# DON'T: Generator for random access patterns
def bad_matrix_access(data):
    rows = (row for row in data)  # Can't access rows[5]
    return rows

# DO: Keep as list when you need indexing
def good_matrix_access(data):
    return list(data)  # Can access result[5]
```

### ❌ When You Need Length
```python
# DON'T: Generator when you need count
def count_items(data):
    processed = (process(item) for item in data)
    return len(processed)  # Error! Generators don't have len()

# DO: Convert to list or use different approach
def count_items(data):
    processed = [process(item) for item in data]
    return len(processed)

# OR: Use a counter
def count_items(data):
    count = 0
    for item in data:
        process(item)
        count += 1
    return count
```

## Common Pitfalls and Solutions

### 1. Generator Exhaustion
```python
# PROBLEM: Generators can only be consumed once
def numbers():
    for i in range(5):
        yield i

gen = numbers()
list1 = list(gen)  # [0, 1, 2, 3, 4]
list2 = list(gen)  # [] - Empty! Generator exhausted

# SOLUTION: Create generator factory
def numbers():
    return (i for i in range(5))

gen1 = numbers()
gen2 = numbers()
list1 = list(gen1)  # [0, 1, 2, 3, 4]
list2 = list(gen2)  # [0, 1, 2, 3, 4] - Fresh generator
```

### 2. Exception Handling in Generators
```python
# PROBLEM: Exceptions can leave generators in bad state
def bad_generator():
    try:
        yield 1
        raise ValueError("Something went wrong")
        yield 2  # Never reached
    except ValueError:
        yield "error"

gen = bad_generator()
print(next(gen))  # 1
print(next(gen))  # "error"
print(next(gen))  # StopIteration - generator terminated

# SOLUTION: Proper exception handling
def good_generator():
    yield 1
    try:
        risky_operation()
        yield 2
    except ValueError as e:
        yield f"error: {e}"
        yield 3  # Can continue
```

### 3. Premature Optimization
```python
# PROBLEM: Using generators when lists are fine
def over_engineered(data):
    # Unnecessary for small datasets
    return (expensive_transform(item) for item in data)

# SOLUTION: Profile first, optimize later
def simple_approach(data):
    if len(data) > 10000:  # Only use generator for large datasets
        return (expensive_transform(item) for item in data)
    else:
        return [expensive_transform(item) for item in data]
```

## Testing Generators

```python
import pytest

def test_generator_function():
    """Test generator produces expected values"""
    def count_up_to(n):
        for i in range(n):
            yield i
    
    gen = count_up_to(3)
    assert next(gen) == 0
    assert next(gen) == 1
    assert next(gen) == 2
    
    with pytest.raises(StopIteration):
        next(gen)

def test_generator_with_list():
    """Test generator by converting to list"""
    def even_numbers(limit):
        for i in range(limit):
            if i % 2 == 0:
                yield i
    
    result = list(even_numbers(6))
    assert result == [0, 2, 4]

def test_infinite_generator():
    """Test infinite generator with islice"""
    def fibonacci():
        a, b = 0, 1
        while True:
            yield a
            a, b = b, a + b
    
    import itertools
    first_5 = list(itertools.islice(fibonacci(), 5))
    assert first_5 == [0, 1, 1, 2, 3]
```

## Real-World Examples

### 1. CSV Processing
```python
import csv

def process_large_csv(filename):
    """Process large CSV files efficiently"""
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Clean and validate data
            if row['age'].isdigit() and int(row['age']) >= 18:
                yield {
                    'name': row['name'].strip(),
                    'age': int(row['age']),
                    'email': row['email'].lower()
                }

# Process millions of rows with constant memory
def summarize_users(filename):
    total = 0
    for user in process_large_csv(filename):
        total += user['age']
        if total > 1000000:  # Early termination
            break
    return total
```

### 2. API Pagination
```python
import requests

def paginated_api_data(base_url, params=None):
    """Fetch all pages from paginated API"""
    page = 1
    while True:
        response = requests.get(
            base_url,
            params={**(params or {}), 'page': page}
        )
        data = response.json()
        
        if not data['results']:
            break
            
        for item in data['results']:
            yield item
        
        page += 1

# Usage
for user in paginated_api_data('https://api.example.com/users'):
    process_user(user)
# Automatically handles all pages
```

### 3. Log File Analysis
```python
import re
from datetime import datetime

def parse_log_entries(filename, pattern=None):
    """Parse log files with optional filtering"""
    log_pattern = re.compile(r'(\d{4}-\d{2}-\d{2}) (\w+): (.+)')
    
    with open(filename, 'r') as file:
        for line_no, line in enumerate(file, 1):
            match = log_pattern.match(line.strip())
            if match:
                date_str, level, message = match.groups()
                entry = {
                    'line_no': line_no,
                    'date': datetime.strptime(date_str, '%Y-%m-%d'),
                    'level': level,
                    'message': message
                }
                
                if pattern is None or pattern in message:
                    yield entry

# Find all error messages efficiently
error_gen = parse_log_entries('app.log', pattern='ERROR')
first_10_errors = list(itertools.islice(error_gen, 10))
```

## Decision Matrix

| Use Case | Generator | List | Iterator Class | Reason |
|----------|-----------|------|---------------|---------|
| Large datasets | ✅ | ❌ | ❌ | Memory efficiency |
| Small datasets | ❌ | ✅ | ❌ | Simplicity |
| Infinite sequences | ✅ | ❌ | ❌ | Only viable option |
| Random access | ❌ | ✅ | ❌ | Need indexing |
| Complex traversal | ❌ | ❌ | ✅ | Stateful iteration |
| Pipeline processing | ✅ | ❌ | ❌ | Composability |
| Multiple iterations | ❌ | ✅ | ✅ | Reusability |

## Bottom Line

**Use generators when:**
- Processing large datasets
- Creating infinite sequences
- Building data pipelines
- Memory efficiency matters
- Lazy evaluation is beneficial

**Use lists when:**
- Small, fixed datasets
- Need random access
- Need length/size
- Multiple iterations required

**Use custom iterators when:**
- Complex data structure traversal
- Multiple iteration modes
- Stateful iteration patterns

**Community wisdom**: Generators are one of Python's most powerful features. Use them liberally for large data processing. Avoid custom iterator classes unless you have complex traversal requirements that generators can't handle elegantly.