# Modern Python Testing Best Practices for 2025

## Testing Layer Architecture

Modern Python applications should implement a clear testing pyramid with distinct layers that serve different purposes and have different characteristics.

### Testing Layers Defined

#### Unit Tests
- **Purpose**: Test individual functions, classes, or methods in complete isolation
- **Scope**: Single component/function
- **Dependencies**: All external dependencies mocked (database, APIs, file system, other services)
- **Speed**: Very fast (milliseconds)
- **Quantity**: Highest number of tests (70-80% of test suite)

```python
import pytest
from unittest.mock import Mock, patch
from tract.services.user_service import UserService

@patch('tract.repositories.user_repository.UserRepository.save')
@patch('tract.services.email_service.EmailService.send_welcome_email')
def test_user_registration_unit(mock_email, mock_save):
    """Unit test - all dependencies mocked."""
    # Arrange
    mock_save.return_value = True
    mock_email.return_value = True
    user_service = UserService()
    
    # Act
    result = user_service.register_user("test@example.com", "John Doe")
    
    # Assert
    assert result.success is True
    mock_save.assert_called_once()
    mock_email.assert_called_once()
```

#### Integration Tests
- **Purpose**: Test how multiple components within your codebase work together
- **Scope**: Multiple internal components/modules
- **Dependencies**: External dependencies mocked, internal dependencies real
- **Speed**: Medium (seconds)
- **Quantity**: Medium number of tests (15-25% of test suite)

```python
import pytest
from unittest.mock import patch
from tract.services.user_service import UserService
from tract.repositories.user_repository import UserRepository

@patch('tract.external.email_api.send_email')  # External API mocked
@patch('tract.external.credit_check.verify_user')  # External service mocked
def test_user_service_repository_integration(mock_credit, mock_email):
    """Integration test - internal components real, external mocked."""
    # Arrange
    mock_email.return_value = {"status": "sent"}
    mock_credit.return_value = {"approved": True}
    
    # Real internal components working together
    user_repo = UserRepository()
    user_service = UserService(user_repo)
    
    # Act
    result = user_service.register_user_with_verification("test@example.com", "John Doe")
    
    # Assert
    assert result.user_id is not None
    assert result.verification_sent is True
    # Verify internal component interactions
    saved_user = user_repo.find_by_email("test@example.com")
    assert saved_user is not None
```

#### End-to-End Tests
- **Purpose**: Test complete user workflows from start to finish
- **Scope**: Full application stack
- **Dependencies**: Zero mocking - real database, real external services
- **Speed**: Slow (minutes)
- **Quantity**: Smallest number of tests (5-15% of test suite)

```python
import pytest
from tract.app import create_app
from tract.database import get_db_connection

@pytest.mark.e2e
def test_complete_user_registration_workflow():
    """E2E test - no mocking, real everything."""
    # Setup real test environment
    app = create_app(environment="test")
    
    with app.test_client() as client:
        # Act - simulate real user workflow
        response = client.post('/api/users/register', json={
            "email": "real.test@example.com",
            "name": "Real User"
        })
        
        # Assert - verify real database state
        assert response.status_code == 201
        
        # Check real database
        with get_db_connection() as db:
            user = db.execute(
                "SELECT * FROM users WHERE email = ?", 
                ("real.test@example.com",)
            ).fetchone()
            assert user is not None
            
        # Verify real email was sent (check email service logs/queue)
        # This might involve checking actual email service APIs
```

## Project Structure

```
tests/
├── unit/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_services/
│   │   ├── __init__.py
│   │   ├── test_user_service.py
│   │   └── test_auth_service.py
│   └── test_utils/
│       ├── __init__.py
│       └── test_validators.py
├── integration/
│   ├── __init__.py
│   ├── test_service_repository_interactions.py
│   ├── test_internal_api_flows.py
│   └── test_cross_module_workflows.py
├── e2e/
│   ├── __init__.py
│   ├── test_user_registration_flow.py
│   └── test_complete_business_workflows.py
├── conftest.py
└── __init__.py
```

## Pytest Configuration

### pyproject.toml Configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--tb=short",
    "--cov=tract",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
]

markers = [
    "unit: marks tests as unit tests (fast, isolated, all dependencies mocked)",
    "integration: marks tests as integration tests (medium speed, internal components real, external mocked)",
    "e2e: marks tests as end-to-end tests (slow, no mocking, real everything)",
    "slow: marks tests as slow running (> 1 second)",
    "requires_db: marks tests that require database connection",
    "requires_network: marks tests that require network access",
]

filterwarnings = [
    "error",
    "ignore::UserWarning",
    "ignore::DeprecationWarning",
]
```

### Running Different Test Layers

```bash
# Run only unit tests (fast feedback during development)
uv run pytest tests/unit -m unit

# Run only integration tests
uv run pytest tests/integration -m integration

# Run only e2e tests
uv run pytest tests/e2e -m e2e

# Run all except e2e (for CI fast pipeline)
uv run pytest -m "not e2e"

# Run all tests
uv run pytest

# Run tests in parallel (for faster execution)
uv run pytest -n auto
```

## Modern Fixture Patterns

### Session-Scoped Fixtures for Expensive Setup

```python
# conftest.py
import pytest
from typing import Generator
from tract.database import Database
from tract.config import TestConfig

@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    """Session-wide test configuration."""
    return TestConfig(
        database_url="sqlite:///:memory:",
        environment="test"
    )

@pytest.fixture(scope="session")
def database(test_config: TestConfig) -> Generator[Database, None, None]:
    """Session-scoped database connection for integration tests."""
    db = Database(test_config.database_url)
    db.create_tables()
    yield db
    db.close()

@pytest.fixture(scope="function")
def clean_database(database: Database) -> Generator[Database, None, None]:
    """Function-scoped clean database state."""
    yield database
    database.clear_all_tables()
```

### Type-Annotated Fixtures

```python
from typing import Generator, Protocol
import pytest

class MockEmailService(Protocol):
    def send_email(self, to: str, subject: str, body: str) -> bool: ...

@pytest.fixture
def mock_email_service() -> Generator[MockEmailService, None, None]:
    """Type-annotated mock email service."""
    mock = Mock(spec=MockEmailService)
    mock.send_email.return_value = True
    yield mock
```

### Parametrized Test Cases with Type Safety

```python
from dataclasses import dataclass
from typing import Any
import pytest

@dataclass
class ValidationTestCase:
    input_value: str
    expected_result: bool
    expected_error: type[Exception] | None
    description: str

@pytest.mark.parametrize("test_case", [
    ValidationTestCase("valid@email.com", True, None, "valid email"),
    ValidationTestCase("invalid-email", False, ValueError, "invalid format"),
    ValidationTestCase("", False, ValueError, "empty email"),
], ids=lambda tc: tc.description)
def test_email_validation(test_case: ValidationTestCase):
    """Type-safe parametrized testing."""
    if test_case.expected_error:
        with pytest.raises(test_case.expected_error):
            validate_email(test_case.input_value)
    else:
        result = validate_email(test_case.input_value)
        assert result == test_case.expected_result
```

## Test Data Management

### Factory Pattern for Test Data

```python
from dataclasses import dataclass
from typing import Any
import uuid

@dataclass
class UserFactory:
    @staticmethod
    def create_user(**overrides: Any) -> dict[str, Any]:
        """Create test user data with optional overrides."""
        defaults = {
            "id": str(uuid.uuid4()),
            "email": f"test{uuid.uuid4().hex[:8]}@example.com",
            "name": "Test User",
            "is_active": True,
        }
        return {**defaults, **overrides}

    @staticmethod
    def create_admin_user(**overrides: Any) -> dict[str, Any]:
        """Create admin user for testing."""
        admin_defaults = {
            "role": "admin",
            "permissions": ["read", "write", "admin"]
        }
        return UserFactory.create_user(**admin_defaults, **overrides)

# Usage in tests
def test_user_creation():
    user_data = UserFactory.create_user(name="Custom Name")
    user = create_user(user_data)
    assert user.name == "Custom Name"
```

## Async Testing Patterns

### Modern Async Test Support

```python
import pytest
import asyncio
from typing import AsyncGenerator

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async client fixture for testing async endpoints."""
    async with AsyncClient() as client:
        yield client

@pytest.mark.asyncio
async def test_async_user_creation(async_client: AsyncClient):
    """Test async endpoint with proper typing."""
    response = await async_client.post("/users", json={
        "email": "async@test.com",
        "name": "Async User"
    })
    assert response.status_code == 201
```

## Test Performance and Organization

### Performance Guidelines

1. **Unit tests should complete in < 100ms each**
2. **Integration tests should complete in < 5 seconds each**
3. **E2E tests can take longer but should be minimized**
4. **Use parallel execution for test suites > 1000 tests**

### Test Organization Best Practices

```python
class TestUserService:
    """Group related tests in classes for organization."""
    
    def test_create_user_success(self):
        """Test successful user creation."""
        pass
    
    def test_create_user_duplicate_email_fails(self):
        """Test that duplicate email creation fails."""
        pass
    
    def test_create_user_invalid_email_fails(self):
        """Test that invalid email fails validation."""
        pass

class TestUserServiceIntegration:
    """Separate class for integration tests."""
    
    @pytest.mark.integration
    def test_user_service_with_real_repository(self):
        """Test user service with real repository implementation."""
        pass
```

## Continuous Integration Test Strategy

### Multi-Stage Testing Pipeline

```yaml
# Example CI pipeline stages
stages:
  - name: "Fast Feedback"
    commands:
      - "uv run pytest tests/unit -m unit --maxfail=5"
    
  - name: "Integration Testing"
    commands:
      - "uv run pytest tests/integration -m integration"
    
  - name: "Full Test Suite"
    commands:
      - "uv run pytest tests/ --cov=tract --cov-fail-under=80"
    
  - name: "E2E Testing"
    commands:
      - "uv run pytest tests/e2e -m e2e"
    trigger: "main branch only"
```

## Key Testing Principles

1. **Test Pyramid**: Many unit tests, some integration tests, few E2E tests
2. **Fast Feedback**: Unit tests should provide immediate feedback during development
3. **Isolation**: Each test should be independent and able to run in any order
4. **Clarity**: Test names should clearly describe what they're testing
5. **Maintainability**: Tests should be as simple as possible while being comprehensive
6. **Type Safety**: Use type hints in test code for better IDE support and clarity

## Common Anti-Patterns to Avoid

### ❌ Testing Implementation Details
```python
# Bad - testing internal implementation
def test_user_service_calls_repository_method():
    user_service.create_user("test@example.com")
    assert user_service._repository.save.called  # Testing implementation
```

### ✅ Testing Behavior
```python
# Good - testing observable behavior
def test_user_service_creates_user_successfully():
    result = user_service.create_user("test@example.com")
    assert result.success is True
    assert result.user.email == "test@example.com"
```

### ❌ Mixing Test Layers
```python
# Bad - integration test with external dependencies
@pytest.mark.integration
def test_user_registration_with_real_email_api():
    # This should be E2E, not integration
    pass
```

### ✅ Proper Layer Separation
```python
# Good - integration test with mocked externals
@pytest.mark.integration
@patch('tract.external.email_service.send_email')
def test_user_registration_workflow(mock_email):
    # Tests internal component integration
    pass
```

This comprehensive testing strategy ensures robust, maintainable, and fast test suites that provide confidence in your Python applications while following modern 2025 best practices.