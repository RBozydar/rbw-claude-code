# Creating Slash Commands

Slash commands are custom commands users can invoke with `/command-name`.

## Quick Start

Create a markdown file in your plugin's `commands/` directory:

```bash
mkdir -p plugins/my-plugin/commands
```

Create `commands/my-command.md`:

```markdown
---
name: my-command
description: What this command does
arguments:
  - name: arg1
    description: First argument
    required: false
---

# My Command

Instructions for Claude when this command is invoked.

## What to do

1. Step one
2. Step two
3. Step three

## Arguments

The user may provide: $ARGUMENTS
```

## Command Frontmatter

```yaml
---
name: my-command          # Required: command name (without /)
description: Brief desc   # Required: shown in /help
arguments:                # Optional: document expected args
  - name: file
    description: File to process
    required: true
  - name: options
    description: Additional options
    required: false
---
```

## Command Body

The markdown body is the prompt given to Claude when the command runs.

Use `$ARGUMENTS` to reference user-provided arguments:

```markdown
The user wants to process: $ARGUMENTS

Do the following:
1. Read the file
2. Process it
3. Report results
```

## Examples

### Simple command

`commands/greet.md`:

```markdown
---
name: greet
description: Greet the user
---

Say hello to the user in a friendly way.
```

Usage: `/greet`

### Command with arguments

`commands/explain.md`:

```markdown
---
name: explain
description: Explain a file or concept
arguments:
  - name: target
    description: File path or concept to explain
    required: true
---

# Explain Command

Explain the following to the user: $ARGUMENTS

Be clear and concise. Use examples if helpful.
```

Usage: `/explain src/main.py`

### Complex workflow command

`commands/review.md`:

```markdown
---
name: review
description: Review code changes
arguments:
  - name: scope
    description: What to review (file, pr, or diff)
    required: false
---

# Code Review

Review the code changes specified by the user.

## Scope

$ARGUMENTS

If no scope provided, review staged changes (`git diff --cached`).

## Review Checklist

1. Check for bugs and logic errors
2. Verify error handling
3. Look for security issues
4. Assess code clarity
5. Suggest improvements

## Output Format

Provide feedback as:
- **Critical**: Must fix before merge
- **Suggestion**: Consider improving
- **Nitpick**: Minor style issues
```

## Registering Commands

Commands in the `commands/` directory are automatically discovered. No settings.json entry needed.

## Best Practices

1. **Clear names** - Use descriptive, action-oriented names
2. **Good descriptions** - Help users understand what the command does
3. **Document arguments** - Explain what input is expected
4. **Structured prompts** - Use headings and lists for clarity
5. **Include examples** - Show expected behavior in the prompt
