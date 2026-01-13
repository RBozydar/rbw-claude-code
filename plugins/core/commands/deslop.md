---
name: deslop
description: Remove AI-generated code slop from a branch. Use when cleaning up AI-generated code, removing unnecessary comments, defensive checks, or type casts. Checks diff against main and fixes style inconsistencies.
argument-hint: "[optional: base branch, defaults to main]"
---

# Remove AI Code Slop

Check the diff against main and remove all AI-generated slop introduced in this branch.

## Process

1. Get the diff against main:
   ```bash
   git diff main...HEAD
   ```

2. Review each changed file for slop patterns (see below)

3. Remove identified slop while preserving legitimate changes

4. Report a 1-3 sentence summary of what was changed

## What to Remove

### Unnecessary Comments

Remove comments that:
- State the obvious (e.g., `x = x + 1  # increment x`)
- Restate the function name in a docstring
- A human developer wouldn't add
- Are inconsistent with the rest of the file

**Keep** comments that explain WHY, not WHAT.

### Defensive Over-engineering

Remove:
- Extra defensive checks for scenarios that can't happen
- Try/catch blocks that are abnormal for that area of the codebase
- Validation in internal code that's already validated at boundaries

**Keep** defensive code that matches the existing codebase style.

### Type Workarounds

Remove:
- Casts to `any` or `Any` that work around type issues
- `# type: ignore` comments without justification

**Fix** the underlying type issue instead of hiding it.

### Inline Imports (Python)

Move inline imports to the top of the file with other imports:

```python
# Bad
def process():
    from utils import helper  # Move this
    return helper()

# Good
from utils import helper

def process():
    return helper()
```

### Style Inconsistencies

Remove or fix:
- Quote style that doesn't match the file (single vs double)
- Formatting that differs from the rest of the file
- Docstrings added to files that don't use them
- Type hints in files that don't have them elsewhere

## What to Keep

- Comments that explain complex logic or business rules
- Defensive code that matches existing patterns in the codebase
- Type hints that are consistent with the file's style
- Changes that are directly related to the task

## Output Format

After making changes, provide a brief summary:

```
Deslop complete:
- Removed 3 redundant comments in src/api/handlers.py
- Removed unnecessary try/except in src/services/order.py
- Moved 2 inline imports to top of file in src/utils/parser.py
```

If no slop found:

```
No slop detected in the current branch diff.
```

## Tips

- Focus on changes introduced in THIS branch, not pre-existing issues
- Don't refactor unrelated code
- Keep changes minimal and focused
- When in doubt, match the existing file style
