# Python Architecture Standards

Rules for clean, maintainable Python architecture.

## SOLID Principles

### Single Responsibility

Classes and modules should have one reason to change:

```python
# Bad - does too much
class UserManager:
    def create_user(self): ...
    def send_email(self): ...
    def generate_report(self): ...

# Good - focused responsibility
class UserRepository:
    def create(self, user: User) -> User: ...

class EmailService:
    def send(self, to: str, message: str) -> None: ...
```

### Dependency Inversion

High-level modules should not import low-level modules. Both should depend on abstractions:

```python
from typing import Protocol

class Storage(Protocol):
    def save(self, data: bytes) -> str: ...

class FileStorage:
    def save(self, data: bytes) -> str: ...

class S3Storage:
    def save(self, data: bytes) -> str: ...

# High-level module depends on abstraction
class DocumentService:
    def __init__(self, storage: Storage):
        self._storage = storage
```

## Dependency Injection

Do not instantiate heavy dependencies inside classes. Pass them in:

```python
# Bad - hard to test, tightly coupled
class OrderService:
    def __init__(self):
        self.db = PostgresDatabase()
        self.cache = RedisCache()

# Good - dependencies injected
class OrderService:
    def __init__(self, db: Database, cache: Cache):
        self._db = db
        self._cache = cache
```

## Composition Over Inheritance

Avoid deep inheritance hierarchies. Prefer composition:

```python
# Bad - fragile inheritance
class Animal: ...
class Mammal(Animal): ...
class Dog(Mammal): ...
class SwimmingDog(Dog): ...

# Good - composition
class Dog:
    def __init__(self, swimmer: Swimmer | None = None):
        self._swimmer = swimmer
```

## Configuration

Do not hardcode configurations. Use Pydantic BaseSettings:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: str
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

## Naming Conventions (PEP 8)

| Type | Convention | Example |
|------|------------|---------|
| Functions | snake_case | `process_data()` |
| Variables | snake_case | `user_count` |
| Classes | PascalCase | `UserService` |
| Constants | UPPER_CASE | `MAX_RETRIES` |
| Private | _prefix | `_internal_state` |

## Reserved Names

NEVER override built-in names:
- `type`, `next`, `exit`, `list`, `dict`, `set`
- `id`, `input`, `open`, `file`, `filter`, `map`

## Immutability

Prefer immutable types when possible:
- `tuple` over `list` for fixed collections
- `frozenset` over `set` for fixed sets
- Design data structures to minimize mutation
