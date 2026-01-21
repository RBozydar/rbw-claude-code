# clean-code-guard

Hook plugin that blocks messy code execution patterns and nudges toward clean alternatives.

## Escape Hatch

Add `# clean-code-guard: disable` comment to bypass all checks:

```bash
# clean-code-guard: disable
CONTENT=$(cat file.md); gemini "$CONTENT"  # Allowed with escape hatch
```

Use when you have a legitimate use case that the patterns incorrectly flag.

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

## Limitations

**Variable assignment pattern is intentionally broad:**
- May false-positive if a variable is assigned much earlier and gemini is called later with a different variable
- Use escape hatch if you encounter false positives

**Regex patterns have edge cases:**
- Non-greedy matching may not handle all nested quote scenarios
- Direct heredoc pattern may match literal strings containing the pattern

When in doubt, use the escape hatch and document why.

## Related

- `templates/rules/clean-execution.md` - Rule template for CLAUDE.md
- `plugins/python-backend/skills/gemini-cli/SKILL.md` - Gemini CLI usage guide
- `scripts/gemini-review.sh` - Wrapper script for clean gemini invocations
