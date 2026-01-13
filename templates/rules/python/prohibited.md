# Python Prohibited Practices

Practices that should NEVER appear in production Python code.

## Code Execution

NO `eval()` or `exec()` in source code:

```python
# NEVER do this
result = eval(user_input)
exec(dynamic_code)
```

## Global State

NO `global` statements (constants are OK):

```python
# Bad
def increment():
    global counter
    counter += 1

# Good - use class or pass as parameter
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1
```

## Print Statements

NO `print()` in production code. Use logging:

```python
# Bad
print(f"Processing {item}")

# Good
logger.info("Processing %s", item)
```

## Bare Except

NO bare `except:` clauses:

```python
# Bad
try:
    risky_operation()
except:
    pass

# Good - be specific
try:
    risky_operation()
except ValueError as e:
    logger.error("Invalid value: %s", e)
```

## Mutable Default Arguments

NEVER use mutable defaults:

```python
# Bad - shared mutable state
def append_to(item, target=[]):
    target.append(item)
    return target

# Good
def append_to(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

## Assertions in Production

NO assertions in production code (only in tests):

```python
# Bad - assertions can be disabled with -O
assert user.is_authenticated

# Good - explicit check
if not user.is_authenticated:
    raise AuthenticationError("User not authenticated")
```

## Relative Imports

ALWAYS use absolute imports:

```python
# Bad
from .utils import helper
from ..models import User

# Good
from mypackage.utils import helper
from mypackage.models import User
```

## Logging Anti-patterns

NO f-strings in logger calls (breaks log aggregation):

```python
# Bad
logger.info(f"Processing user {user_id}")

# Good - use % formatting
logger.info("Processing user %s", user_id)
```

## Blocking in Async

NO blocking calls in `async def` functions:

```python
# Bad
async def fetch_data():
    response = requests.get(url)  # BLOCKING!
    time.sleep(1)  # BLOCKING!

# Good
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    await asyncio.sleep(1)
```

## Quick Checklist

Before committing, verify:
- [ ] No `eval()` or `exec()`
- [ ] No `global` statements
- [ ] No `print()` statements
- [ ] No bare `except:`
- [ ] No mutable default arguments
- [ ] No assertions in production code
- [ ] All imports are absolute
- [ ] No f-strings in logger calls
- [ ] No blocking calls in async functions
