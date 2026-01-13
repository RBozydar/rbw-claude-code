# Python Type Hints Standards

Rules for comprehensive and modern type annotations.

## Required Type Hints

Provide type hints for ALL:
- Function parameters
- Function return values
- Class attributes (when not obvious from `__init__`)

```python
def process_data(items: list[str], limit: int = 10) -> dict[str, int]:
    ...
```

## Modern Syntax

Use Python 3.10+ union syntax:

| Old (Avoid) | Modern (Use) |
|-------------|--------------|
| `Optional[str]` | `str \| None` |
| `Union[int, str]` | `int \| str` |
| `List[int]` | `list[int]` |
| `Dict[str, int]` | `dict[str, int]` |
| `Tuple[int, ...]` | `tuple[int, ...]` |

## Protocols for Duck Typing

Use `Protocol` instead of ABCs when you need structural subtyping:

```python
from typing import Protocol

class Processable(Protocol):
    def process(self) -> None: ...

def run(item: Processable) -> None:
    item.process()  # Works with any class that has process()
```

## TypeVar for Generics

```python
from typing import TypeVar

T = TypeVar('T', bound='BaseModel')

def clone(item: T) -> T:
    return item.model_copy()
```

## Custom Types

Define custom types in a `types.py` module:

```python
# types.py
from typing import TypeAlias

UserId: TypeAlias = str
Timestamp: TypeAlias = float
Config: TypeAlias = dict[str, str | int | bool]
```

## Final for Constants

```python
from typing import Final

MAX_RETRIES: Final = 3
API_URL: Final = "https://api.example.com"
```

## Avoid

- Don't use `Any` unless absolutely necessary
- Don't use `# type: ignore` without explanation
- Don't mix old and new syntax in the same file
