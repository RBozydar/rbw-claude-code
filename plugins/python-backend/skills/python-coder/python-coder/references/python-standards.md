# Python Development Standards Reference

## Design Principles

### Architectural Patterns
- **SOLID Principles:** Adhere strictly, specifically:
  - Single Responsibility: Classes and modules should have one reason to change.
  - Dependency Inversion: High-level modules should not import low-level modules; both should depend on abstractions (Protocols/ABC).
- **Dependency Injection:** Do not instantiate heavy dependencies (db adapters, http clients) inside classes. Pass them in via `__init__`.
- **Composition over Inheritance:** Avoid deep inheritance hierarchies.
- **Configuration:** Do not hardcode configurations. Use Pydantic `BaseSettings` or environment variables.

## Asyncio & Concurrency

### Structured Concurrency
Use `asyncio.TaskGroup` for managing task lifecycles.
- IF tasks depend on each other: Let exceptions propagate to cancel the group.
- IF tasks are independent: Wrap them in a "Firewall" (try/except) so the group remains active despite individual failures.

### Non-Blocking I/O
NEVER use blocking I/O calls (e.g., `time.sleep`, `requests`, standard file I/O) inside async functions.
- Use `asyncio.sleep` instead of `time.sleep`.
- Use `httpx` (async client) instead of `requests`.
- Use `aiofiles` for file operations if absolutely necessary, or offload to a thread.

### CPU-Bound Operations
Offload heavy CPU computations (numpy, image processing, heavy parsing) to a thread or process pool using `loop.run_in_executor`.

### Background Tasks
NEVER use "fire and forget" `create_task` without holding a reference.
- Bad: `asyncio.create_task(do_background_work())` (Variable is garbage collected, task may vanish).
- Good: Add background tasks to a `set` of strong references or use a `TaskGroup`.

### Synchronization
Use `asyncio.Lock`, `asyncio.Event`, etc., NOT `threading.Lock`.

### Context Managers
Prefer `async with` context managers for resource management (DB connections, sessions) to ensure cleanups happen even on cancellation.

## Asyncio Fault Tolerance

### The Firewall Pattern
When running tasks that must not impact siblings (e.g., processing independent events), use exception isolation.

NEVER let an exception bubble up from an independent background task:
- Wrap the task logic in a `try/except Exception` block.
- Log the error with stack trace (`logger.exception`).
- Return `None` (or a failure object) so the event loop perceives the task as "completed successfully" and doesn't cancel siblings.

```python
async def _safe_run(self, task_name: str, coro: Awaitable[T]) -> T | None:
    """Runs a coroutine safely, logging errors without crashing the group."""
    try:
        return await coro
    except Exception as e:
        logger.exception(f"Independent task '{task_name}' failed unexpectedly")
        return None  # Swallow exception so TaskGroup doesn't cancel others
```

Full example:

```python
import asyncio
import logging

logger = logging.getLogger(__name__)

async def independent_task(task_id: str):
    if task_id == "B":
        raise ValueError("Task B crashed!")
    await asyncio.sleep(1)
    logger.info(f"Task {task_id} completed")

async def safe_wrapper(task_id: str):
    """Acts as the firewall. The exception stops here."""
    try:
        await independent_task(task_id)
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e} - continuing other tasks.")

async def entry_point():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(safe_wrapper("A"))
        tg.create_task(safe_wrapper("B"))  # Fails safely
        tg.create_task(safe_wrapper("C"))

    logger.info("Entry point finished. Tasks A and C should have succeeded.")
```

## Error Handling

- NEVER use assertions in production code (only in tests)
- Catch `Exception`, not `BaseException`, for general error handling.
- Only catch `BaseException` at the absolute top-level entry point (main loop) for final logging before crash.

## Logging

Use standard logging library. Log messages should be structured where possible:
- Avoid f-strings in logger calls for aggregation tools
- Use: `logger.info("Processed %s", item_id)`
- Not: `logger.info(f"Processed {item_id}")`

## Input Validation

- ALWAYS use Pydantic for input validation despite small performance cost
- Define clear Pydantic models for all data structures
- Validate at boundaries (API endpoints, external data sources)

## Naming Conventions

Follow PEP 8 strictly:
- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_CASE` for constants
- NEVER override built-in names (`type`, `next`, `exit`, `list`, `dict`, etc.)
- Avoid variable shadowing
- Use descriptive, meaningful names

## Immutability

- Prefer immutable types whenever possible (`tuple` over `list`, `frozenset` over `set`)
- Use `Final` type hint for constants
- Design data structures to minimize mutation

## Default Arguments

NEVER use mutable default arguments:

```python
# Bad
def function(arg: list[int] = []) -> None:
    ...

# Good
def function(arg: list[int] | None = None) -> None:
    arg = arg or []
```

## Imports

- ALWAYS use absolute imports, never relative imports
- Organize imports in three sections (stdlib, third-party, local) separated by blank lines
- Use `from typing import ...` only for types missing in Python 3.11+

## Type Hints

- Provide type hints for ALL function parameters and return values
- Use modern syntax: `Type | None` instead of `Optional[Type]`
- Use `TypeVar` for generic types
- Define custom types in `types.py`
- Use `Protocol` for duck typing and structural subtyping

```python
from typing import Protocol, TypeVar

T = TypeVar('T', bound='Processable')

class Processable(Protocol):
    def process(self) -> None: ...
```

## Comments and Documentation

- Write self-documenting code that minimizes need for comments
- When comments are needed, explain WHY, not WHAT
- Use Google-style docstrings for all public APIs
- Document complex algorithms and business logic

## Testing (TDD Approach)

Design the interface and test cases mentally before writing the implementation:
- Write tests BEFORE implementation (Test-Driven Development)
- Use pytest as the testing framework
- Use pytest-cov for coverage reporting
- Write both unit tests and functional tests
- Test all error scenarios and edge cases
- Use proper fixtures and pytest-mock for mocking
- Aim for high test coverage while avoiding testing implementation details
- Ensure tests are independent and do not rely on shared mutable state
- Use `conftest.py` for shared fixtures
- Use `pytest-asyncio` for async tests
- Mark async tests with `@pytest.mark.asyncio`
- Verify that mocks for async functions are awaitable (`AsyncMock`)

## Prohibited Practices

| Practice | Alternative |
|----------|-------------|
| `eval()` / `exec()` | Structured parsing, AST module |
| `global` statements | Pass state via parameters, use classes |
| `print()` in production | Use `logger` |
| Bare `except:` | Catch specific exceptions |
| Blocking I/O in async | Use async libraries (`httpx`, `aiofiles`) |
| Calling async without `await` | Always `await` or explicitly schedule |
| `asyncio.run()` inside running loop | Use `await` directly |
| Mutable default arguments | Use `None` with conditional assignment |
| Relative imports | Use absolute imports |
| `Optional[X]` | Use `X | None` |
