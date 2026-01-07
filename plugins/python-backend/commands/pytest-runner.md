---
name: pytest-runner
description: Run pytest with smart test discovery, parallel execution, and failure analysis
argument-hint: "[test path, marker, or 'affected' for changed files only]"
---

# Pytest Runner Command

Run pytest intelligently with automatic configuration detection, parallel execution, and actionable failure analysis.

## Usage

```bash
/pytest-runner                    # Run all tests
/pytest-runner tests/unit/        # Run specific directory
/pytest-runner -k "test_user"     # Run tests matching pattern
/pytest-runner affected           # Run tests for changed files only
/pytest-runner --coverage         # Run with coverage report
```

## Arguments

<arguments> #$ARGUMENTS </arguments>

## Execution Flow

### 1. Detect Test Configuration

<thinking>
First, determine how pytest is configured and how to run it.
</thinking>

**Check for configuration:**
- `pyproject.toml` - Look for `[tool.pytest.ini_options]`
- `pytest.ini` - Direct pytest config
- `setup.cfg` - Look for `[tool:pytest]`
- `conftest.py` - Test fixtures and plugins

**Detect test runner:**
```bash
# Priority order for running pytest
1. poetry run pytest    # If poetry.lock present
2. uv run pytest        # If uv.lock or pyproject.toml with uv
3. python -m pytest     # If virtual env active
4. pytest               # Fallback
```

### 2. Smart Test Discovery

**If argument is "affected":**
```bash
# Find changed Python files
git diff --name-only HEAD~1 | grep '\.py$'

# Map source files to test files
# src/services/user.py → tests/test_user.py, tests/services/test_user.py
# app/models/order.py → tests/models/test_order.py
```

**If no argument:**
```bash
# Discover test directories
tests/
test/
*_test.py
test_*.py
```

### 3. Run Tests

**Basic execution:**
```bash
# With verbose output and short traceback
pytest -v --tb=short $ARGUMENTS
```

**With parallel execution (if pytest-xdist installed):**
```bash
pytest -v --tb=short -n auto $ARGUMENTS
```

**With coverage (if requested):**
```bash
pytest -v --tb=short --cov=. --cov-report=term-missing $ARGUMENTS
```

### 4. Analyze Failures

If tests fail, provide actionable analysis:

**For each failing test:**
1. Show the failure location (file:line)
2. Extract the assertion message
3. Show relevant code context
4. Suggest likely causes:
   - Missing fixtures
   - Changed API signatures
   - Database/network dependencies
   - Import errors

**Group failures by type:**
- `AssertionError` - Logic failures
- `ImportError` - Module/dependency issues
- `TypeError/AttributeError` - Interface mismatches
- `ConnectionError` - External dependencies
- `fixture 'X' not found` - Missing test fixtures

### 5. Summary Report

```markdown
## Test Results

**Status:** PASSED / FAILED
**Duration:** Xs
**Tests:** X passed, Y failed, Z skipped

### Failures (if any):

1. `tests/test_user.py::test_create_user`
   - **Error:** AssertionError: expected 201, got 400
   - **Location:** tests/test_user.py:45
   - **Likely cause:** Validation logic changed in UserService

2. `tests/test_order.py::test_process_payment`
   - **Error:** ConnectionError: Cannot connect to payment API
   - **Likely cause:** External dependency - consider mocking

### Coverage (if requested):

| Module | Coverage |
|--------|----------|
| src/services | 85% |
| src/models | 92% |
| src/api | 78% |

**Missing coverage:** src/services/payment.py:45-67

### Next Steps:

1. Fix failing tests (run `/pytest-runner tests/test_user.py` to retest)
2. Add missing test coverage for payment.py
```

## Options

| Option | Description |
|--------|-------------|
| `affected` | Run tests only for files changed since last commit |
| `--coverage` | Include coverage report |
| `-k PATTERN` | Run tests matching pattern |
| `-x` | Stop on first failure |
| `--pdb` | Drop into debugger on failure |
| `-m MARKER` | Run tests with specific marker (e.g., `slow`, `integration`) |

## Integration with Workflow

After running tests:
- If all pass: Proceed with commit/PR
- If failures: Create todo items for each failure
- If coverage low: Suggest files needing tests

## Troubleshooting

**"No tests collected":**
- Check test file naming (`test_*.py` or `*_test.py`)
- Verify test functions start with `test_`
- Check for `__init__.py` in test directories if needed

**Import errors:**
- Ensure virtual environment is activated
- Check for circular imports
- Verify package is installed in editable mode (`pip install -e .`)

**Fixture not found:**
- Check `conftest.py` location
- Verify fixture scope
- Look for typos in fixture names
