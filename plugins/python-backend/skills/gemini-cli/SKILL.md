---
name: gemini-cli
description: This skill teaches proper Gemini CLI usage patterns. Use stdin piping instead of shell variable gymnastics. Covers code review, plan review, and general prompts.
---

# Gemini CLI Usage Guide

This skill ensures clean, readable Gemini CLI invocations without shell gymnastics.

## Core Principle

**Always pipe content via stdin. Never use heredocs or shell variable assignment.**

```bash
# GOOD - Clean and readable
cat file.md | gemini --sandbox -o text "Review this for issues"

# BAD - Shell gymnastics
CONTENT=$(cat file.md)
gemini --sandbox "$(cat <<'EOF'
Review this:
$CONTENT
EOF
)"
```

## Command Structure

```bash
<content-source> | gemini [options] "prompt"
```

### Required Options

| Option | Purpose |
|--------|---------|
| `--sandbox` or `-s` | Always use - prevents code modifications |
| `-o text` or `--output-format text` | Plain text output |
| `-m MODEL` or `--model MODEL` | Model selection |

### Available Models

| Model | Use Case |
|-------|----------|
| `gemini-3-pro-preview` | Default, best quality |
| `gemini-3-flash-preview` | Faster, cheaper |

## Common Patterns

### Review a Plan/Spec File

```bash
cat plans/my-feature.md | gemini --sandbox -o text -m gemini-3-pro-preview \
  "Review this plan for architectural issues, missing requirements, and risks"
```

### Review Git Diff

```bash
# Unstaged changes
git diff | gemini --sandbox -o text "Review this diff for bugs and security issues"

# Staged changes
git diff --cached | gemini --sandbox -o text "Review these staged changes"

# Branch vs main
git diff main...HEAD | gemini --sandbox -o text "Review all changes on this branch"
```

### Review a Code File

```bash
cat src/module.py | gemini --sandbox -o text "Check this code for N+1 queries and security issues"
```

### Multiple Files

```bash
cat src/models.py src/views.py | gemini --sandbox -o text "Review these related files for consistency"
```

### With Focus Areas

```bash
git diff | gemini --sandbox -o text "Review this diff focusing on:
1. SQL injection vulnerabilities
2. Missing error handling
3. Performance issues"
```

## Wrapper Script

For convenience, use the wrapper script at `scripts/gemini-review.sh`:

```bash
# Review a plan
scripts/gemini-review.sh --plan plans/my-feature.md

# Review diff
scripts/gemini-review.sh --diff --staged

# Review file with custom prompt
scripts/gemini-review.sh --file src/api.py "Check for security issues"

# With focus areas
scripts/gemini-review.sh --diff --focus "security,performance"

# With different model
scripts/gemini-review.sh --plan plans/big-feature.md --model gemini-3-flash-preview
```

## What NOT to Do

### Never Use Heredocs

```bash
# BAD
gemini --sandbox "$(cat <<'EOF'
Your prompt here
EOF
)"
```

### Never Assign to Variables First

```bash
# BAD
DIFF=$(git diff)
PLAN=$(cat plan.md)
gemini --sandbox "$DIFF $PLAN"
```

### Never Use Deprecated -p Flag

```bash
# BAD - deprecated
gemini -p "prompt" --sandbox

# GOOD - positional prompt
gemini --sandbox "prompt"
```

### Never Skip Sandbox Mode

```bash
# BAD - no sandbox
gemini "Review this code"

# GOOD - always sandbox
gemini --sandbox "Review this code"
```

## Integration with Agents

When using gemini from Claude Code agents:

1. **Always use stdin piping** - readable and clean
2. **Always use `--sandbox`** - safety first
3. **Use `-o text`** - plain text for parsing
4. **Use appropriate model** - pro for quality, flash for speed

Example agent invocation:

```bash
git diff --cached | gemini --sandbox -o text -m gemini-3-pro-preview \
  "You are a senior code reviewer. Review this diff for:
1. Bugs and logic errors
2. Security vulnerabilities
3. Performance issues
Provide specific file:line references."
```

## Error Handling

### No Input

If you see "No input provided via stdin", ensure you're piping content:

```bash
# Wrong - no pipe
gemini --sandbox "Review this"

# Right - with content
echo "hello" | gemini --sandbox "Review this"
cat file.md | gemini --sandbox "Review this"
```

### Large Files

For very large files, consider:

1. Review specific sections
2. Use flash model for speed
3. Summarize before detailed review

```bash
# Review just the first 500 lines
head -500 large-file.py | gemini --sandbox -o text "Review this code section"
```

## Quick Reference

| Task | Command |
|------|---------|
| Review plan | `cat plan.md \| gemini --sandbox -o text "Review for issues"` |
| Review unstaged diff | `git diff \| gemini --sandbox -o text "Review for bugs"` |
| Review staged diff | `git diff --cached \| gemini --sandbox -o text "Review"` |
| Review file | `cat file.py \| gemini --sandbox -o text "Check security"` |
| Review branch | `git diff main...HEAD \| gemini --sandbox -o text "Review"` |
