# gemini-model-guard

Block deprecated Gemini 2.x models and enforce Gemini 3 models only.

## Why

The Gemini 2.x models (gemini-2.5-pro, gemini-2.5-flash, etc.) are deprecated.
Always use the latest Gemini 3 models for better performance and features.

## Allowed Models

| Model | Use Case |
|-------|----------|
| `gemini-3-pro-preview` | Latest Gemini 3 Pro (recommended) |
| `gemini-3-flash-preview` | Fast, cost-effective |

## What Gets Blocked

Any `gemini` command using a model with "2" in the name:

```bash
# BLOCKED
gemini --model gemini-2.5-pro "prompt"
gemini --model gemini-2.5-flash-preview "prompt"
gemini -m gemini-2.5-pro "prompt"

# ALLOWED
gemini --model gemini-3-pro-preview "prompt"
gemini --model gemini-3-flash-preview "prompt"
gemini "prompt"  # Uses default model
```

## Installation

Add to your hooks setup:

```bash
./scripts/setup-hooks.sh
```
