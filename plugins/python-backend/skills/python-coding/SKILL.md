---
name: python-coding
description: This skill should be loaded when writing, reviewing, or refactoring Python code to apply strict coding standards directly in the current context without spawning a subagent. It provides comprehensive Python development standards covering SOLID principles, asyncio patterns, type hints, testing, and production-quality code.
---

# Python Coder Standards

Apply these standards when writing, reviewing, or refactoring Python code. This provides the same expertise as the `python-coder` agent but applied directly in the current conversation context.

## Quick Reference Checklist

Before providing any code or review, verify:

1. Absolute imports only
2. Modern type hints (`X | None`)
3. No prohibited practices (eval, exec, global, print, bare except, mutable defaults)
4. Pydantic validation at boundaries
5. No blocking I/O in async paths
6. `asyncio.TaskGroup` for structured concurrency
7. Google-style docstrings on public APIs
8. Structured logging (no f-strings in logger calls)
9. No assertions in production code
10. Immutable types preferred (tuple > list, frozenset > set)

See [references/python-standards.md](./references/python-standards.md) for full details on each item.

## Detailed Standards

For the complete standards reference covering all patterns, examples, and anti-patterns, load:

```
references/python-standards.md
```

This reference covers:
- **Design Principles** - SOLID, dependency injection, composition over inheritance
- **Asyncio & Concurrency** - TaskGroup, firewall pattern, non-blocking I/O, synchronization
- **Fault Tolerance** - Exception isolation for independent tasks
- **Error Handling** - Exception hierarchy, no assertions in production
- **Logging** - Structured logging patterns
- **Input Validation** - Pydantic models at boundaries
- **Naming & Immutability** - PEP 8, no built-in shadowing, immutable defaults
- **Imports & Type Hints** - Absolute imports, modern syntax, Protocols
- **Testing** - TDD with pytest, async testing patterns
- **Prohibited Practices** - Complete list of banned patterns with alternatives

## Output Guidelines

When writing code:
- Provide complete, runnable code with all imports
- Include type hints on all parameters and return values
- Add Google-style docstrings to public APIs
- Show example usage when helpful

When reviewing code:
- Reference specific violations from the standards
- Explain WHY each change is needed
- Provide corrected code
- Prioritize by severity
