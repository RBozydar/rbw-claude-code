# Clean Code Execution Patterns

Rules for executing code cleanly without shell gymnastics.

## Python Verification

**NEVER** use inline `python -c "..."` scripts to verify code works.

```python
# BAD - Requires permission, not reusable, clutters the session
uv run python -c "
from mymodule import MyClass
obj = MyClass()
print(obj)
"

# GOOD - Write a proper test
# tests/test_mymodule.py
def test_myclass_instantiation():
    obj = MyClass()
    assert obj is not None
```

### What to do instead:

1. **Write tests** - Add tests to the test suite and run with pytest
2. **Run existing tests** - If tests exist, run those
3. **Reason about code** - For simple checks ("is this frozen?"), read and verify without executing
4. **Use REPL** - If the project has a shell/REPL setup, use that

## External CLI Tools (gemini, etc.)

**NEVER** use shell variable assignment + heredocs to pass content:

```bash
# BAD - Shell gymnastics, hard to read, requires approval
CONTENT=$(cat file.md)
gemini --sandbox "$(cat <<'EOF'
Review this:
$CONTENT
EOF
)"

# GOOD - Pipe stdin directly
cat file.md | gemini --sandbox -o text "Review this plan for issues"

# GOOD - For git diffs
git diff | gemini --sandbox -o text "Review this diff for bugs"
```

## General Principles

1. **Use stdin/pipes** - Most CLI tools accept stdin; use it
2. **Write proper tests** - Don't verify with ad-hoc scripts
3. **Avoid variable juggling** - If you're assigning to a variable just to pass it, rethink
4. **Keep commands readable** - One-liners should be scannable

## Quick Reference

| Task | Bad | Good |
|------|-----|------|
| Verify Python code | `python -c "..."` | Write a test, run pytest |
| Review a file | `CONTENT=$(cat f); tool "$CONTENT"` | `cat f \| tool "prompt"` |
| Review git diff | `DIFF=$(git diff); tool "$DIFF"` | `git diff \| tool "prompt"` |
| Check if code works | Execute it | Read and reason about it |
