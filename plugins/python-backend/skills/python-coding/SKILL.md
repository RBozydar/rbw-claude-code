---
name: python-coding
description: This skill provides comprehensive Python development standards covering SOLID principles, asyncio patterns, type hints, testing, and production-quality code. Load this skill when writing, reviewing, or refactoring Python code to apply strict coding standards directly in the current context without spawning a subagent.
---

# Python Coder Standards

Load these standards when writing, reviewing, or refactoring Python code. This provides the same expertise as the `python-coder` agent but applied directly in the current conversation context.

## When to Use

- Writing new Python modules, classes, or functions
- Reviewing Python code for quality and correctness
- Refactoring existing Python code
- Fixing bugs in Python codebases
- Designing async systems with proper concurrency patterns

## Core Principles

Write clean, concise, Pythonic code. Every line must serve a clear purpose. Never be overly verbose. Optimize for maintainability first, then performance.

## Quick Reference Checklist

Before providing any code or review, verify:

1. All imports are absolute (no relative imports)
2. All type hints present using modern syntax (`X | None` not `Optional[X]`)
3. No prohibited practices (eval, exec, global, print, bare except, mutable defaults)
4. Pydantic validation at all boundaries
5. No blocking I/O in async paths
6. `asyncio.TaskGroup` for structured concurrency
7. Google-style docstrings on public APIs
8. Structured logging (no f-strings in logger calls)
9. No assertions in production code
10. Immutable types preferred (tuple > list, frozenset > set)

## Detailed Standards

For the full standards reference covering all patterns, examples, and anti-patterns, load:

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
