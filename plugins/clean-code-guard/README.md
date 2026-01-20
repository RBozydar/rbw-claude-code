# clean-code-guard

Hook plugin that blocks messy code execution patterns and nudges toward clean alternatives.

## What It Blocks

### 1. Multi-line `python -c` Scripts

```bash
# BLOCKED - Multi-line inline scripts
uv run python -c "
from mymodule import MyClass
obj = MyClass()
print(obj)
"

# ALLOWED - Simple one-liners
python -c "print('hello')"
```

**Why?** Inline scripts are:
- Not reusable
- Not part of the test suite
- Hard to read
- Require manual approval each time

**Instead:** Write proper tests in `tests/` and run with pytest.

### 2. Gemini with Heredocs/Variable Assignment

```bash
# BLOCKED - Heredoc pattern
gemini --sandbox "$(cat <<'EOF'
Review this:
$CONTENT
EOF
)"

# BLOCKED - Variable assignment pattern
CONTENT=$(cat file.md)
gemini --sandbox "$CONTENT"

# ALLOWED - Clean stdin piping
cat file.md | gemini --sandbox -o text "Review this"
git diff | gemini --sandbox -o text "Review this diff"
```

**Why?** Heredoc patterns are:
- Hard to read
- Prone to quoting issues
- Unnecessarily complex

**Instead:** Use stdin piping or the wrapper script:
```bash
scripts/gemini-review.sh --plan file.md
scripts/gemini-review.sh --diff
```

## Installation

Add to your project's `.claude/settings.json`:

```json
{
  "plugins": [
    "/path/to/rbw-claude-code/plugins/clean-code-guard"
  ]
}
```

## Related

- `templates/rules/clean-code-execution.md` - Rule template for CLAUDE.md
- `plugins/python-backend/skills/gemini-cli/SKILL.md` - Gemini CLI usage guide
- `scripts/gemini-review.sh` - Wrapper script for clean gemini invocations
