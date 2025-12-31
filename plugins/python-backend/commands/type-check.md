---
name: type-check
description: Run mypy or pyright with incremental checking and error categorization
argument-hint: "[file path, module, or 'all']"
---

# Type Check Command

Run Python type checking with automatic tool detection, incremental analysis, and categorized error reporting.

## Usage

```bash
/type-check                    # Check all files
/type-check src/               # Check specific directory
/type-check src/services/      # Check module
/type-check --strict           # Run with strict mode
/type-check affected           # Check only changed files
```

## Arguments

<arguments> #$ARGUMENTS </arguments>

## Execution Flow

### 1. Detect Type Checker Configuration

<thinking>
First, determine which type checker is configured and how to run it.
</thinking>

**Check for configuration (priority order):**

1. **pyright** - `pyrightconfig.json` or `pyproject.toml [tool.pyright]`
2. **mypy** - `mypy.ini`, `.mypy.ini`, or `pyproject.toml [tool.mypy]`

**Detect runner:**
```bash
# Priority order
1. uvx pyright / uvx mypy    # If using uv
2. poetry run pyright/mypy   # If poetry.lock present
3. pyright / mypy            # Direct execution
```

### 2. Run Type Checker

**For pyright:**
```bash
pyright $ARGUMENTS
# or with JSON output for parsing
pyright --outputjson $ARGUMENTS
```

**For mypy:**
```bash
mypy $ARGUMENTS
# With useful defaults
mypy --show-error-codes --pretty $ARGUMENTS
```

**Incremental mode (default):**
- Use cached results for unchanged files
- Only recheck modified files and their dependents

**Strict mode (if requested):**
```bash
mypy --strict $ARGUMENTS
# or
pyright --strict $ARGUMENTS
```

### 3. Categorize Errors

Group errors by severity and type:

**Critical (must fix):**
- `error: Incompatible types` - Type mismatch in assignment/return
- `error: Argument of type X is not assignable` - Wrong function arguments
- `error: Missing return statement` - Incomplete function

**Important (should fix):**
- `error: Missing type annotation` - Untyped function/variable
- `error: Cannot determine type` - Inference failure
- `error: Unused "type: ignore"` - Stale suppression comments

**Warnings (consider fixing):**
- `note: Revealed type is` - Type information
- `error: Name X is not defined` - Possibly missing import
- `error: Module has no attribute` - API mismatch

### 4. Error Analysis

For each error, provide:

1. **Location:** `file.py:line:column`
2. **Error code:** `[assignment]`, `[arg-type]`, `[return-value]`
3. **Message:** What went wrong
4. **Suggestion:** How to fix it

**Common fixes:**

| Error | Likely Fix |
|-------|-----------|
| `Incompatible types in assignment` | Add explicit type annotation or cast |
| `Argument X has incompatible type` | Check function signature, add type annotation |
| `Missing return statement` | Add return or change return type to `None` |
| `Cannot find module` | Add `py.typed` marker or stub package |
| `has no attribute` | Check if Optional/None handling needed |

### 5. Summary Report

```markdown
## Type Check Results

**Status:** PASSED / FAILED
**Checker:** mypy 1.8.0 / pyright 1.1.350
**Files checked:** X
**Errors found:** Y

### Errors by Category:

**Critical (X errors):**
1. `src/services/user.py:45` - Incompatible return type
   - Expected: `User`
   - Got: `Optional[User]`
   - **Fix:** Handle None case or update return annotation

2. `src/api/routes.py:23` - Argument type mismatch
   - Parameter `user_id` expects `int`, got `str`
   - **Fix:** Convert with `int(user_id)` or update parameter type

**Important (Y errors):**
1. `src/models/order.py:12` - Missing type annotation
   - Function `process` has no return type
   - **Fix:** Add `-> OrderResult` or `-> None`

### Files with Most Errors:

| File | Errors |
|------|--------|
| src/services/payment.py | 8 |
| src/api/routes.py | 5 |
| src/models/user.py | 3 |

### Quick Fixes:

```python
# Add to src/services/user.py:45
def get_user(user_id: int) -> User | None:  # Changed from User
    ...

# Add to src/api/routes.py:23
user_id: int = int(request.args.get("user_id", 0))
```

### Next Steps:

1. Fix critical errors first (they may cause runtime issues)
2. Add missing type annotations to public APIs
3. Consider adding `# type: ignore[code]` for known issues
```

## Options

| Option | Description |
|--------|-------------|
| `affected` | Check only files changed since last commit |
| `--strict` | Enable strict mode (all optional checks) |
| `--no-cache` | Force full recheck |
| `--show-absolute-path` | Show full file paths |

## Configuration Tips

**Recommended pyproject.toml settings:**

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true

[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "strict"
reportMissingImports = true
reportMissingTypeStubs = false
```

## Troubleshooting

**"Cannot find module X":**
- Install type stubs: `pip install types-requests`
- Or add to mypy.ini: `ignore_missing_imports = True`
- Or add `py.typed` marker to your package

**"Type of X is Unknown":**
- Add explicit type annotation
- Check if library has type stubs available
- Use `cast()` if type is known but not inferred

**Too many errors on legacy code:**
- Start with `--ignore-missing-imports`
- Add type annotations incrementally
- Use `# type: ignore` sparingly with error codes
