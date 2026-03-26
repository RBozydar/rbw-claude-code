---
name: gemini-cli
description: This skill should be used when invoking the Gemini CLI for code review, plan review, or any prompt-based task. It provides correct invocation patterns emphasizing stdin piping and @ syntax over shell variable gymnastics.
---

Ensure clean, readable Gemini CLI invocations without shell gymnastics.

## Core Principle

Always pipe content via stdin or use `@` syntax. Never use heredocs or shell variable assignment.

```bash
# CORRECT - Clean stdin pipe
cat file.md | gemini --sandbox -o text "Review this for issues"

# CORRECT - @ syntax for file references
gemini --sandbox -o text "Review this code" @src/module.py

# WRONG - Shell gymnastics
CONTENT=$(cat file.md)
gemini --sandbox "Review: $CONTENT"
```

## Command Structure

```bash
# Pipe content via stdin
<content-source> | gemini [options] "prompt"

# Reference files/folders directly
gemini [options] "prompt" @file.py @folder/
```

### Required Options

| Option | Purpose |
|--------|---------|
| `--sandbox` or `-s` | Required -- prevents code modifications |
| `-o text` | Plain text output (required for parsing) |
| `-m MODEL` | Model selection |

### Available Models

| Model | Use Case |
|-------|----------|
| `gemini-3-pro-preview` | Default, best quality |
| `gemini-3-flash-preview` | Faster, cheaper |

## Common Patterns

### File and Folder References with @

```bash
# Single file
gemini --sandbox -o text "Review this code" @src/module.py

# Multiple files
gemini --sandbox -o text "Check consistency" @src/models.py @src/views.py

# Entire folder
gemini --sandbox -o text "Review this module" @src/auth/

# Mix files and folders
gemini --sandbox -o text "Review the API" @src/api/ @tests/test_api.py
```

### Git Diff Review

```bash
# Unstaged changes
git diff | gemini --sandbox -o text "Review this diff for bugs and security issues"

# Staged changes
git diff --cached | gemini --sandbox -o text "Review these staged changes"

# Branch vs main
git diff main...HEAD | gemini --sandbox -o text "Review all changes on this branch"
```

### Focused Review with Prompt Detail

```bash
git diff | gemini --sandbox -o text "Review this diff focusing on:
1. SQL injection vulnerabilities
2. Missing error handling
3. Performance issues"
```

## Anti-Patterns

### Deprecated `-p` Flag

```bash
# WRONG - deprecated
gemini -p "prompt" --sandbox

# CORRECT - positional prompt
gemini --sandbox "prompt"
```

### Variable Assignment

```bash
# WRONG
DIFF=$(git diff)
gemini --sandbox "$DIFF"

# CORRECT
git diff | gemini --sandbox -o text "Review"
```

### Missing Sandbox

```bash
# WRONG - no sandbox
gemini "Review this code"

# CORRECT
gemini --sandbox "Review this code"
```

## Integration with Agents

When invoking gemini from Claude Code agents:

1. Always use stdin piping or `@` syntax
2. Always include `--sandbox`
3. Always include `-o text` for parseable output
4. Select model based on task: pro for quality, flash for speed

```bash
git diff --cached | gemini --sandbox -o text -m gemini-3-pro-preview \
  "Review this diff for bugs, security vulnerabilities, and performance issues.
Provide specific file:line references."
```

## Error Handling

The error "No input provided via stdin" indicates missing piped content. When using stdin mode, always pipe content before the gemini command. When referencing files directly, use `@` syntax instead.

For large files, review specific sections or use the flash model:

```bash
head -500 large-file.py | gemini --sandbox -o text "Review this code section"
```

## Quick Reference

| Task | Command |
|------|---------|
| Review plan | `gemini --sandbox -o text "Review for issues" @plan.md` |
| Review file | `gemini --sandbox -o text "Check security" @file.py` |
| Review folder | `gemini --sandbox -o text "Review module" @src/auth/` |
| Review unstaged diff | `git diff \| gemini --sandbox -o text "Review for bugs"` |
| Review staged diff | `git diff --cached \| gemini --sandbox -o text "Review"` |
| Review branch | `git diff main...HEAD \| gemini --sandbox -o text "Review"` |
