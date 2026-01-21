# Clean Code Execution Practices

Rules for executing code cleanly without shell gymnastics or ad-hoc scripts.

## No Inline Python Scripts

NEVER use `python -c "..."` or `uv run python -c "..."` to verify code:

```bash
# Bad - ad-hoc inline verification
uv run python -c "
from mymodule import MyClass
obj = MyClass()
print(obj.method())
"

# Good - write a proper test
# tests/test_mymodule.py
def test_myclass_method():
    obj = MyClass()
    assert obj.method() == expected_value
```

**Why:**
- Ad-hoc scripts aren't reusable or documented
- They bypass the test suite
- They require permission prompts
- For simple checks, just read and reason about the code

## Gemini CLI Usage

Use stdin piping instead of shell variable gymnastics:

```bash
# Bad - convoluted heredoc with variable expansion
CONTENT=$(cat file.md)
gemini --sandbox "$(cat <<EOF
Review this:
$CONTENT
EOF
)"

# Good - pipe content directly
cat file.md | gemini --sandbox "Review this plan for issues"

# Good - for git diffs
git diff | gemini --sandbox "Review this diff for bugs"

# Good - combine content sources
cat CLAUDE.md plans/feature.md | gemini --sandbox "Review with project context"
```

**Why:**
- Piping is cleaner and more readable
- No shell escaping issues
- No variable assignment overhead
- Standard Unix pattern

## When to Execute vs Reason

**Execute (write tests):**
- Complex logic verification
- Integration behavior
- Edge cases and error handling
- Anything that should be in the test suite

**Reason (don't execute):**
- "Is this dataclass frozen?" - read the code
- "Does this function exist?" - read/grep the code
- "Is the type annotation correct?" - read the code
- Simple structural questions

## Verification Checklist

Before running ad-hoc code, ask:

1. Should this be a test? If yes, write a test
2. Can I answer by reading the code? If yes, just read it
3. Is this a one-time exploration? Consider if the answer should be documented

## Quick Reference

| Task | Bad | Good |
|------|-----|------|
| Verify code works | `python -c "..."` | Write pytest test |
| Check syntax | `python -c "import mod"` | `uv run python -m py_compile mod.py` |
| Review with Gemini | `VAR=$(cat); gemini "...$VAR"` | `cat file \| gemini "..."` |
| Simple verification | Execute anything | Read and reason |
