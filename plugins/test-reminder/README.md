# test-reminder

Remind to add tests when Claude Code creates new Python files.

## What it does

This PostToolUse hook checks if a corresponding test file exists when a new Python module is created. If no test file is found, it prints a reminder.

## Installation

```bash
/plugin install test-reminder
```

## Behavior

When a new `.py` file is written:
1. Skips test files (`test_*.py`), `__init__.py`, and `conftest.py`
2. Skips files already in `tests/` or `test/` directories
3. Looks for a corresponding `test_<module>.py` in common locations
4. Prints a reminder if no test file exists

## Checked locations

For a file `mymodule.py`, looks for tests in:
- Same directory: `test_mymodule.py`
- Subdirectory: `tests/test_mymodule.py`
- Parent tests directory: `../tests/test_mymodule.py`
