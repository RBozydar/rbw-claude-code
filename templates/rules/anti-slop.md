# Anti-Slop Rule

Prevent AI-generated code patterns that reduce code quality.

## What is "Slop"?

Slop refers to unnecessary additions that AI assistants often introduce:
- Comments that state the obvious
- Defensive code for impossible scenarios
- Type casts to work around issues
- Style inconsistencies with existing code

## Patterns to Avoid

### Unnecessary Comments

Don't add comments that a human developer wouldn't add:

```python
# Bad - obvious from the code
x = x + 1  # Increment x by 1

# Bad - restating the function name
def get_user():
    """Get user."""  # Useless docstring
    ...

# Good - explains WHY, not WHAT
x = x + 1  # Compensate for zero-indexing in API response
```

### Defensive Over-engineering

Don't add checks for scenarios that can't happen:

```python
# Bad - over-defensive when caller is trusted
def process_order(order: Order) -> None:
    if order is None:
        raise ValueError("Order cannot be None")
    if not isinstance(order, Order):
        raise TypeError("Expected Order instance")
    # ... actual logic

# Good - trust validated inputs
def process_order(order: Order) -> None:
    # Pydantic already validated at boundary
    # ... actual logic
```

### Excessive Try/Catch

Don't wrap everything in try/except:

```python
# Bad - catching everything
try:
    result = simple_calculation(x, y)
except Exception:
    result = None

# Good - let errors propagate appropriately
result = simple_calculation(x, y)
```

### Type Casts to `any`

Don't use `Any` or `# type: ignore` to avoid fixing real issues:

```python
# Bad - hiding type errors
result: Any = problematic_function()
value = data["key"]  # type: ignore

# Good - fix the actual type issue
result: ExpectedType = properly_typed_function()
value: str = data.get("key", "")
```

### Inline Imports (Python)

Keep imports at the top of the file:

```python
# Bad - inline import
def process():
    from utils import helper  # Move to top
    return helper()

# Good - imports at top
from utils import helper

def process():
    return helper()
```

### Style Inconsistency

Match the existing file's style:

```python
# If file uses double quotes
message = "Hello"  # Good
message = 'Hello'  # Bad - inconsistent

# If file has no docstrings on private methods
def _helper(self):  # Good - match existing
    ...

def _helper(self):  # Bad - adding when others don't have
    """Helper function."""
    ...
```

## Before Committing

Check your diff against main:

```bash
git diff main...HEAD
```

Look for:
1. Comments that weren't in the original and don't add value
2. Try/except blocks around code that didn't have them
3. Type annotations that use `Any` or `# type: ignore`
4. Style changes unrelated to your actual task
5. Defensive checks in internal/trusted code paths

## Quick Checklist

- [ ] No obvious/redundant comments added
- [ ] No unnecessary try/except blocks
- [ ] No `Any` or `# type: ignore` added
- [ ] No inline imports (Python)
- [ ] Style matches existing file
- [ ] Changes are focused on the actual task
