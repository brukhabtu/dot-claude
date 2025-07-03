# Abstract Base Classes: The Old Guard vs Modern Protocols

## Community Attitude: "Protocols Are Better"

**Current consensus**: ABCs are in decline. Modern Python favors Protocols for interface definition due to structural typing and better flexibility.

**The shift**: From nominal typing (ABCs) to structural typing (Protocols). Duck typing wins again.

## What ABCs Actually Do

ABCs define contracts that subclasses must implement. They enforce method implementation at class definition time.

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass
    
    @abstractmethod
    def perimeter(self) -> float:
        pass
    
    # Concrete method all shapes share
    def describe(self) -> str:
        return f"Area: {self.area()}, Perimeter: {self.perimeter()}"

class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius
    
    def area(self) -> float:
        return 3.14159 * self.radius ** 2
    
    def perimeter(self) -> float:
        return 2 * 3.14159 * self.radius

# Can't instantiate Shape directly
# shape = Shape()  # TypeError!
```

## When ABCs Are Still Worth Using

### 1. Enforcing Interface Contracts (Inheritance Required)
```python
from abc import ABC, abstractmethod

class DatabaseAdapter(ABC):
    @abstractmethod
    def connect(self) -> None:
        """Establish database connection"""
        pass
    
    @abstractmethod
    def execute(self, query: str) -> list:
        """Execute query and return results"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close database connection"""
        pass
    
    # Shared implementation
    def execute_transaction(self, queries: list[str]) -> None:
        """Execute multiple queries in transaction"""
        try:
            for query in queries:
                self.execute(query)
        except Exception:
            self.rollback()
            raise

class PostgreSQLAdapter(DatabaseAdapter):
    def connect(self) -> None:
        # Implementation required
        self.connection = create_postgres_connection()
    
    def execute(self, query: str) -> list:
        # Implementation required
        return self.connection.execute(query)
    
    def close(self) -> None:
        # Implementation required
        self.connection.close()

# Enforces contract: PostgreSQLAdapter MUST implement all abstract methods
```

### 2. Template Method Pattern
```python
class DataProcessor(ABC):
    def process(self, data: str) -> str:
        """Template method defining the algorithm"""
        cleaned = self.clean_data(data)
        transformed = self.transform_data(cleaned)
        validated = self.validate_data(transformed)
        return validated
    
    @abstractmethod
    def clean_data(self, data: str) -> str:
        pass
    
    @abstractmethod
    def transform_data(self, data: str) -> str:
        pass
    
    def validate_data(self, data: str) -> str:
        # Default implementation can be overridden
        if not data:
            raise ValueError("Data cannot be empty")
        return data

class CSVProcessor(DataProcessor):
    def clean_data(self, data: str) -> str:
        return data.strip()
    
    def transform_data(self, data: str) -> str:
        return data.replace(',', '|')
```

### 3. Registration with Shared Behavior
```python
class Plugin(ABC):
    registry = {}
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.registry[cls.__name__] = cls
    
    @abstractmethod
    def execute(self) -> str:
        pass
    
    @classmethod
    def get_all_plugins(cls):
        return list(cls.registry.values())

class EmailPlugin(Plugin):
    def execute(self) -> str:
        return "Sending email"

class SMSPlugin(Plugin):
    def execute(self) -> str:
        return "Sending SMS"

# Automatic registration + enforced interface
```

## Why Modern Python Prefers Protocols

### Structural vs Nominal Typing
```python
from typing import Protocol

# Protocol: "If it quacks like a duck..."
class Drawable(Protocol):
    def draw(self) -> None: ...

# Any class with a draw() method automatically satisfies this
class Circle:
    def draw(self) -> None:
        print("Drawing circle")

class Square:
    def draw(self) -> None:
        print("Drawing square")

def render(shape: Drawable) -> None:
    shape.draw()

# Works without inheritance!
render(Circle())  # ✅
render(Square())  # ✅

# Even works with existing classes
class ThirdPartyWidget:
    def draw(self) -> None:
        print("Third party draw")

render(ThirdPartyWidget())  # ✅ No modification needed
```

### ABC Equivalent (More Restrictive)
```python
from abc import ABC, abstractmethod

class DrawableABC(ABC):
    @abstractmethod
    def draw(self) -> None:
        pass

# Must explicitly inherit
class Circle(DrawableABC):
    def draw(self) -> None:
        print("Drawing circle")

# Third-party code can't satisfy interface without modification
class ThirdPartyWidget:  # Doesn't inherit from DrawableABC
    def draw(self) -> None:
        print("Third party draw")

def render(shape: DrawableABC) -> None:
    shape.draw()

render(Circle())  # ✅
# render(ThirdPartyWidget())  # ❌ Type error!
```

## Performance Comparison

### Inheritance Overhead
```python
import timeit
from typing import Protocol
from abc import ABC, abstractmethod

# Protocol approach
class FastProtocol(Protocol):
    def process(self) -> int: ...

class FastImpl:
    def process(self) -> int:
        return 42

# ABC approach
class SlowABC(ABC):
    @abstractmethod
    def process(self) -> int:
        pass

class SlowImpl(SlowABC):
    def process(self) -> int:
        return 42

fast_obj = FastImpl()
slow_obj = SlowImpl()

# Method call performance
fast_time = timeit.timeit('obj.process()', globals={'obj': fast_obj}, number=1_000_000)
slow_time = timeit.timeit('obj.process()', globals={'obj': slow_obj}, number=1_000_000)

print(f"Protocol: {fast_time:.4f}s")
print(f"ABC:      {slow_time:.4f}s")
# Protocols are slightly faster (no inheritance overhead)
```

## Modern Alternatives to ABCs

### 1. Protocols (Preferred)
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Serializable(Protocol):
    def serialize(self) -> dict: ...
    def deserialize(self, data: dict) -> None: ...

# Works with isinstance() at runtime
class User:
    def serialize(self) -> dict:
        return {"name": self.name}
    
    def deserialize(self, data: dict) -> None:
        self.name = data["name"]

user = User()
assert isinstance(user, Serializable)  # ✅ True
```

### 2. TypedDict for Data Contracts
```python
from typing import TypedDict

class UserData(TypedDict):
    name: str
    age: int
    email: str

def process_user(data: UserData) -> None:
    print(f"Processing {data['name']}")

# No inheritance needed, just structural compatibility
user_dict = {"name": "Alice", "age": 30, "email": "alice@example.com"}
process_user(user_dict)  # ✅ Works
```

### 3. Union Types for Flexibility
```python
from typing import Union, Literal

# Instead of ABC hierarchy
class AudioFile:
    format: Literal["mp3", "wav", "flac"]

class VideoFile:
    format: Literal["mp4", "avi", "mkv"]

MediaFile = Union[AudioFile, VideoFile]

def process_media(file: MediaFile) -> None:
    if isinstance(file, AudioFile):
        # Handle audio
        pass
    elif isinstance(file, VideoFile):
        # Handle video
        pass
```

## When ABCs Still Make Sense

### ✅ Good Use Cases
1. **Framework development** where inheritance is natural
2. **Template method pattern** with shared implementation
3. **Strong contracts** where you control all implementations
4. **Registration patterns** with automatic subclass discovery

### ❌ Poor Use Cases
1. **Simple interfaces** (use Protocols)
2. **Third-party integration** (Protocols are more flexible)
3. **Data structures** (use TypedDict)
4. **Optional interfaces** (Protocols handle this better)

## Migration Strategy: ABC to Protocol

### Before (ABC)
```python
from abc import ABC, abstractmethod

class Processor(ABC):
    @abstractmethod
    def process(self, data: str) -> str:
        pass

class TextProcessor(Processor):
    def process(self, data: str) -> str:
        return data.upper()

def handle_data(processor: Processor, data: str) -> str:
    return processor.process(data)
```

### After (Protocol)
```python
from typing import Protocol

class Processor(Protocol):
    def process(self, data: str) -> str: ...

# No inheritance required
class TextProcessor:
    def process(self, data: str) -> str:
        return data.upper()

# Existing classes automatically work
class LegacyProcessor:
    def process(self, data: str) -> str:
        return data.lower()

def handle_data(processor: Processor, data: str) -> str:
    return processor.process(data)

# Both work without modification
handle_data(TextProcessor(), "hello")  # ✅
handle_data(LegacyProcessor(), "hello")  # ✅
```

## Real-World Examples

### ABCs in Standard Library (Still Used)
```python
import collections.abc

# These are still ABCs because they provide default implementations
class CustomMapping(collections.abc.MutableMapping):
    def __init__(self):
        self._data = {}
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __delitem__(self, key):
        del self._data[key]
    
    def __iter__(self):
        return iter(self._data)
    
    def __len__(self):
        return len(self._data)
    
    # Gets keys(), values(), items() methods for free!
```

### Modern Protocol Approach
```python
from typing import Protocol, TypeVar, Iterator

K = TypeVar('K')
V = TypeVar('V')

class MappingProtocol(Protocol[K, V]):
    def __getitem__(self, key: K) -> V: ...
    def __iter__(self) -> Iterator[K]: ...
    def __len__(self) -> int: ...

# Any dict-like object automatically satisfies this
def process_mapping(mapping: MappingProtocol[str, int]) -> None:
    for key in mapping:
        print(f"{key}: {mapping[key]}")

# Works with built-ins and custom classes
process_mapping({"a": 1, "b": 2})  # ✅
process_mapping(collections.Counter("hello"))  # ✅
```

## Error Patterns to Avoid

### 1. Over-Engineering with ABCs
```python
# DON'T: ABC for simple interface
from abc import ABC, abstractmethod

class Validator(ABC):
    @abstractmethod
    def validate(self, value: str) -> bool:
        pass

class EmailValidator(Validator):
    def validate(self, value: str) -> bool:
        return "@" in value

# DO: Protocol or just a function
def is_valid_email(value: str) -> bool:
    return "@" in value
```

### 2. Mixing ABCs and Protocols
```python
# DON'T: Confusing mix
from abc import ABC
from typing import Protocol

class Confusing(ABC, Protocol):  # Unclear semantics
    pass

# DO: Choose one approach
class ClearProtocol(Protocol):
    def method(self) -> None: ...
```

## Decision Matrix

| Requirement | ABC | Protocol | Other |
|-------------|-----|----------|-------|
| Shared implementation | ✅ | ❌ | Mixin |
| Third-party compatibility | ❌ | ✅ | - |
| Compile-time checking | ✅ | ✅ | - |
| Runtime checking | ✅ | ✅ (with decorator) | - |
| Simple interface | ❌ | ✅ | - |
| Template method pattern | ✅ | ❌ | - |
| Framework development | ✅ | ❌ | - |
| Duck typing | ❌ | ✅ | - |

## Bottom Line

**Use ABCs when:**
- Building frameworks where inheritance makes sense
- Need shared implementation across subclasses
- Template method pattern is appropriate
- You control all implementations

**Use Protocols when:**
- Defining simple interfaces
- Working with third-party code
- Want maximum flexibility
- Embracing duck typing

**Community direction**: Python is moving toward Protocols. New code should prefer structural typing unless you specifically need the features that ABCs provide.

**Modern recommendation**: Start with Protocols. Upgrade to ABCs only when you need shared implementation or template methods.