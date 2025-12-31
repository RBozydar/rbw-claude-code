# Protect Env Plugin

Prevents Claude from reading `.env` files that may contain secrets.

## What it does

This plugin blocks any attempt to read environment files, including:
- `.env`
- `.env.local`
- `.env.production`
- `.env.development`
- Any file matching `.env.*`

## Installation

```bash
claude plugin add ./plugins/protect-env
```

## Behavior

When Claude tries to read an env file:

```
Blocking Read: Reading '.env' is blocked. Environment files may contain
secrets and should not be read by AI assistants.
```

## Why?

Environment files often contain:
- API keys
- Database credentials
- Secret tokens
- Production secrets

These should never be exposed to AI assistants or included in context.

## Requirements

- cchooks library (installed automatically via uv)
