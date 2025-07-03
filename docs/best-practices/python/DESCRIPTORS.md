# Descriptors: The Power Behind Python's Magic

## Community Attitude: "Powerful But Complex"

**Consensus**: Descriptors are the mechanism behind properties, methods, static methods, class methods, and `super()`. They're respected but considered advanced.

**Modern view**: Most developers use descriptors indirectly through `@property`, `@classmethod`, etc. Writing custom descriptors is for library authors and advanced use cases.

## What Descriptors Actually Do

Descriptors define how attribute access is handled for class attributes. They power Python's object model.

```python
# The descriptor protocol
class Descriptor:
    def __get__(self, obj, objtype=None):
        # Called when accessing the attribute
        pass
    
    def __set__(self, obj, value):
        # Called when setting the attribute
        pass
    
    def __delete__(self, obj):
        # Called when deleting the attribute
        pass
```

**You use descriptors every day without knowing it:**
```python
class MyClass:
    @property
    def value(self):  # This IS a descriptor
        return self._value
    
    @classmethod
    def create(cls):  # This too
        return cls()
    
    def method(self):  # And this
        pass
```

## When Descriptors Are Worth Using

### 1. Reusable Validation Logic
```python
class ValidatedAttribute:
    def __init__(self, validator, default=None):
        self.validator = validator
        self.default = default
    
    def __set_name__(self, owner, name):
        self.name = f'_{name}'
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, self.default)
    
    def __set__(self, obj, value):
        validated_value = self.validator(value)
        setattr(obj, self.name, validated_value)

# Reusable across multiple classes
class Person:
    age = ValidatedAttribute(lambda x: max(0, int(x)))
    name = ValidatedAttribute(lambda x: str(x).strip())

class Product:
    price = ValidatedAttribute(lambda x: max(0.0, float(x)))
    quantity = ValidatedAttribute(lambda x: max(0, int(x)))
```

### 2. Computed Properties with Caching
```python
class ExpensiveProperty:
    def __init__(self, func):
        self.func = func
        self.name = func.__name__
    
    def __set_name__(self, owner, name):
        self.name = f'_{name}'
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        
        cache_name = f'{self.name}_cache'
        if not hasattr(obj, cache_name):
            result = self.func(obj)
            setattr(obj, cache_name, result)
            return result
        return getattr(obj, cache_name)

class DataProcessor:
    @ExpensiveProperty
    def processed_data(self):
        # Expensive computation, cached automatically
        return [item.upper() for item in self.raw_data]
```

### 3. Type-Safe Attributes
```python
class TypedAttribute:
    def __init__(self, expected_type):
        self.expected_type = expected_type
    
    def __set_name__(self, owner, name):
        self.name = f'_{name}'
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name)
    
    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(f'Expected {self.expected_type.__name__}, got {type(value).__name__}')
        setattr(obj, self.name, value)

class Configuration:
    port = TypedAttribute(int)
    host = TypedAttribute(str)
    debug = TypedAttribute(bool)
```

## When NOT to Use Descriptors

### ❌ Simple Properties
```python
# DON'T: Descriptor overkill
class AgeDescriptor:
    def __get__(self, obj, objtype=None):
        return obj._age
    
    def __set__(self, obj, value):
        obj._age = max(0, value)

class Person:
    age = AgeDescriptor()

# DO: Simple property
class Person:
    @property
    def age(self):
        return self._age
    
    @age.setter
    def age(self, value):
        self._age = max(0, value)
```

### ❌ One-Off Validation
```python
# DON'T: Custom descriptor for single use
class EmailDescriptor:
    def __set__(self, obj, value):
        if '@' not in value:
            raise ValueError("Invalid email")
        obj._email = value

# DO: Property or validation in __init__
class User:
    def __init__(self, email):
        if '@' not in email:
            raise ValueError("Invalid email")
        self.email = email
```

## Performance Implications

### Descriptor Lookup Cost
```python
import timeit

class SimpleDescriptor:
    def __get__(self, obj, objtype=None):
        return obj._value
    
    def __set__(self, obj, value):
        obj._value = value

class WithDescriptor:
    attr = SimpleDescriptor()
    
    def __init__(self, value):
        self.attr = value

class Regular:
    def __init__(self, value):
        self.attr = value

# Performance comparison
desc_obj = WithDescriptor(42)
reg_obj = Regular(42)

desc_time = timeit.timeit('obj.attr', globals={'obj': desc_obj}, number=1_000_000)
reg_time = timeit.timeit('obj.attr', globals={'obj': reg_obj}, number=1_000_000)

print(f"Descriptor: {desc_time:.4f}s")
print(f"Regular:    {reg_time:.4f}s")
# Descriptor access is ~2-3x slower
```

**Conclusion**: Descriptors have overhead. Use them when the benefits outweigh the cost.

## Modern Alternatives

### 1. Properties (Most Common)
```python
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def fahrenheit(self):
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        self._celsius = (value - 32) * 5/9

# Use when: Single class, simple logic
```

### 2. Pydantic (External Validation)
```python
from pydantic import BaseModel, validator

class User(BaseModel):
    name: str
    age: int
    email: str
    
    @validator('age')
    def age_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Age must be positive')
        return v

# Use when: Data validation, API models
```

### 3. Dataclass with Properties
```python
from dataclasses import dataclass

@dataclass
class Point:
    _x: float
    _y: float
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = float(value)

# Use when: Simple data classes with validation
```

## Real-World Use Cases

### 1. ORM Field Definitions (Django-style)
```python
class Field:
    def __init__(self, **options):
        self.options = options
    
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj._data.get(self.name)
    
    def __set__(self, obj, value):
        if not hasattr(obj, '_data'):
            obj._data = {}
        obj._data[self.name] = self.validate(value)

class CharField(Field):
    def validate(self, value):
        return str(value)

class IntField(Field):
    def validate(self, value):
        return int(value)

class User:
    name = CharField()
    age = IntField()
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
```

### 2. Unit Conversion
```python
class UnitDescriptor:
    def __init__(self, unit, conversion_factor):
        self.unit = unit
        self.factor = conversion_factor
    
    def __set_name__(self, owner, name):
        self.name = f'_{name}_meters'
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        meters = getattr(obj, self.name, 0)
        return meters / self.factor
    
    def __set__(self, obj, value):
        meters = value * self.factor
        setattr(obj, self.name, meters)

class Distance:
    kilometers = UnitDescriptor('km', 1000)
    feet = UnitDescriptor('ft', 0.3048)
    inches = UnitDescriptor('in', 0.0254)
    
    def __init__(self, meters=0):
        self._distance_meters = meters

# d = Distance()
# d.kilometers = 5
# print(d.feet)  # Automatic conversion
```

### 3. Lazy Loading
```python
class LazyProperty:
    def __init__(self, loader_func):
        self.loader = loader_func
        self.__doc__ = loader_func.__doc__
    
    def __set_name__(self, owner, name):
        self.name = f'_{name}'
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        
        if not hasattr(obj, self.name):
            value = self.loader(obj)
            setattr(obj, self.name, value)
        return getattr(obj, self.name)

class APIClient:
    @LazyProperty
    def expensive_data(self):
        # Only loaded when first accessed
        return self.fetch_from_api()
```

## Design Patterns with Descriptors

### 1. Registry Pattern
```python
class RegisteredField:
    registry = {}
    
    def __set_name__(self, owner, name):
        self.name = name
        if owner not in self.registry:
            self.registry[owner] = []
        self.registry[owner].append(name)
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, f'_{self.name}', None)
    
    def __set__(self, obj, value):
        setattr(obj, f'_{self.name}', value)

class Model:
    name = RegisteredField()
    value = RegisteredField()
    
    @classmethod
    def get_fields(cls):
        return RegisteredField.registry.get(cls, [])
```

### 2. Observer Pattern
```python
class ObservableAttribute:
    def __init__(self):
        self.observers = []
    
    def __set_name__(self, owner, name):
        self.name = f'_{name}'
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)
    
    def __set__(self, obj, value):
        old_value = getattr(obj, self.name, None)
        setattr(obj, self.name, value)
        
        for observer in self.observers:
            observer(obj, old_value, value)
    
    def add_observer(self, callback):
        self.observers.append(callback)

class Model:
    data = ObservableAttribute()

# model.data.add_observer(lambda obj, old, new: print(f"Changed: {old} -> {new}"))
```

## Error-Prone Patterns to Avoid

### 1. Storing Data on Descriptor Instance
```python
# BAD: Shared state between instances
class BadDescriptor:
    def __init__(self):
        self.value = None  # WRONG: shared between all instances
    
    def __get__(self, obj, objtype=None):
        return self.value
    
    def __set__(self, obj, value):
        self.value = value

# GOOD: Store on instance
class GoodDescriptor:
    def __set_name__(self, owner, name):
        self.name = f'_{name}'
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)
    
    def __set__(self, obj, value):
        setattr(obj, self.name, value)
```

### 2. Forgetting to Handle None Object
```python
# BAD: Breaks introspection
class BadDescriptor:
    def __get__(self, obj, objtype=None):
        return obj._value  # AttributeError when obj is None

# GOOD: Handle class-level access
class GoodDescriptor:
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self  # Return descriptor itself
        return obj._value
```

## Decision Matrix

| Use Case | Descriptor | Property | Dataclass | External Library |
|----------|------------|----------|-----------|------------------|
| Single class validation | ❌ | ✅ | ✅ | ❌ |
| Reusable validation | ✅ | ❌ | ❌ | ✅ |
| Complex computed properties | ✅ | ✅ | ❌ | ❌ |
| Type checking | ❌ | ❌ | ❌ | ✅ |
| Framework development | ✅ | ❌ | ❌ | ❌ |
| Simple data storage | ❌ | ❌ | ✅ | ❌ |

## Bottom Line

**Use descriptors when:**
- Building frameworks or libraries
- Need reusable attribute behavior across classes
- Complex validation/transformation logic
- Advanced attribute access patterns

**Use properties when:**
- Single class attribute management
- Simple validation or computation
- Pythonic getter/setter patterns

**Use dataclasses when:**
- Simple data storage
- Type hints are sufficient
- No complex behavior needed

**Community wisdom**: Descriptors are powerful but complex. Most developers should stick to properties and dataclasses. Write descriptors only when you need the reusability across multiple classes.