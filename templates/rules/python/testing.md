# Python Testing Standards

Rules for comprehensive testing with pytest.

## Test-Driven Development

Design the interface and test cases mentally before implementation. Output tests alongside implementation.

## Framework

Use pytest as the testing framework with these extensions:
- `pytest-cov` for coverage
- `pytest-asyncio` for async tests
- `pytest-mock` for mocking

## Test Structure

```python
def test_function_name_describes_behavior():
    # Arrange
    input_data = create_test_data()

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_value
```

## Naming

Test functions should describe the behavior being tested:

```python
# Good - describes behavior
def test_user_creation_with_valid_email_succeeds():
def test_order_total_includes_tax():
def test_empty_cart_returns_zero():

# Bad - vague
def test_user():
def test_order():
def test_cart():
```

## Fixtures

Use `conftest.py` for shared fixtures:

```python
# conftest.py
import pytest

@pytest.fixture
def db_session():
    session = create_test_session()
    yield session
    session.rollback()

@pytest.fixture
def sample_user(db_session):
    return create_user(db_session, name="Test User")
```

## Async Tests

Mark async tests and use `AsyncMock`:

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_async_function():
    mock_service = AsyncMock()
    mock_service.fetch.return_value = {"data": "test"}

    result = await function_under_test(mock_service)

    assert result == expected
    mock_service.fetch.assert_awaited_once()
```

## Mocking

Use pytest-mock for cleaner mocking:

```python
def test_with_mock(mocker):
    mock_api = mocker.patch("module.api_client")
    mock_api.get.return_value = {"status": "ok"}

    result = function_that_uses_api()

    assert result["status"] == "ok"
```

## Test Independence

Tests MUST be independent:
- No shared mutable state
- Each test sets up its own data
- Order of execution should not matter

## Coverage

Aim for high coverage while avoiding testing implementation details:
- Test behavior, not implementation
- Test edge cases and error scenarios
- Don't test getters/setters or trivial code

## What to Test

- All error scenarios and edge cases
- Boundary conditions
- Happy path AND failure paths
- Integration points (with mocks)

## What NOT to Test

- Private methods directly (test through public API)
- Framework code
- Trivial getters/setters
- Implementation details that may change
