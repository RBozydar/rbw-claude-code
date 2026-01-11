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

### Model Restrictions

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

### Introspection Commands

CLI introspection is blocked to prevent version discovery:

```bash
# BLOCKED
gemini --version
gemini -v
gemini --help
gemini -h
```

## Bypass Protection

This hook catches gemini invocations in many forms:

| Pattern | Example | Caught? |
|---------|---------|---------|
| Direct | `gemini -m gemini-2.5-pro` | ✅ |
| Piped input | `cat file \| gemini -m gemini-2.5-pro` | ✅ |
| Command chaining | `cd /tmp && gemini -m gemini-2.5-pro` | ✅ |
| Semicolon | `echo x; gemini -m gemini-2.5-pro` | ✅ |
| Newlines | `echo x`<br>`gemini -m gemini-2.5-pro` | ✅ |
| Subshells | `(gemini -m gemini-2.5-pro)` | ✅ |
| Command substitution | `$(gemini -m gemini-2.5-pro)` | ✅ |
| Backticks | `` `gemini -m gemini-2.5-pro` `` | ✅ |
| Brace grouping | `{ gemini -m gemini-2.5-pro; }` | ✅ |
| Absolute path | `/usr/bin/gemini -m gemini-2.5-pro` | ✅ |
| Relative path | `./gemini -m gemini-2.5-pro` | ✅ |
| Home path | `~/.local/bin/gemini -m gemini-2.5-pro` | ✅ |
| env wrapper | `env gemini -m gemini-2.5-pro` | ✅ |
| timeout wrapper | `timeout 60 gemini -m gemini-2.5-pro` | ✅ |
| nohup | `nohup gemini -m gemini-2.5-pro` | ✅ |
| exec | `exec gemini -m gemini-2.5-pro` | ✅ |
| time | `time gemini -m gemini-2.5-pro` | ✅ |
| nice/ionice | `nice gemini -m gemini-2.5-pro` | ✅ |
| Env var prefix | `VAR=x gemini -m gemini-2.5-pro` | ✅ |
| bash -c | `bash -c 'gemini -m gemini-2.5-pro'` | ✅ |
| sh -c | `sh -c 'gemini -m gemini-2.5-pro'` | ✅ |
| eval | `eval 'gemini -m gemini-2.5-pro'` | ✅ |
| xargs | `echo x \| xargs gemini -m gemini-2.5-pro` | ✅ |

## Defense in Depth

This plugin uses two hooks:

1. **PreToolUse** (primary): Blocks commands before execution
2. **PostToolUse** (fallback): Warns if Gemini 2.x output is detected after execution

## Known Limitations

These patterns **cannot** be detected:

- External scripts: `./script.sh` where script contains gemini calls
- Variable expansion: `cmd=gemini; $cmd -m gemini-2.5-pro`
- Heavy obfuscation: Base64 encoded commands, etc.

For external scripts, consider adding a Write hook to scan script contents.

## Installation

Add to your hooks setup:

```bash
./scripts/setup-hooks.sh
```
