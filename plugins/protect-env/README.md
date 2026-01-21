# Protect Env Plugin

Prevents Claude from reading `.env` files that may contain secrets.

## What it does

This plugin blocks any attempt to read environment files via:

- **Read tool** - Direct file reading
- **Bash commands** - `cat`, `head`, `tail`, `less`, `more`, `sed`, `awk`, `grep`, etc.
- **Grep tool** - Searching inside .env files
- **Input redirection** - `< .env`
- **File operations** - `cp`, `mv`, `scp`, `rsync` with .env as source

### Protected file patterns

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

When Claude tries to access an env file via any method:

```
Blocking: Access to '.env' is blocked. Environment files may contain
secrets and should not be read by AI assistants.
```

### Blocked commands (examples)

```bash
cat .env                    # Blocked
head -5 .env.local          # Blocked
tail .env.production        # Blocked
less .env                   # Blocked
grep API_KEY .env           # Blocked
sed -n '1p' .env            # Blocked
awk '{print $1}' .env       # Blocked
source .env                 # Blocked
. .env                      # Blocked
cp .env .env.backup         # Blocked
< .env xargs echo           # Blocked
```

### Allowed commands (examples)

```bash
ls -la .env                 # Allowed (listing, not reading)
rm .env                     # Allowed (deleting, not reading)
touch .env                  # Allowed (creating empty file)
echo "KEY=val" > .env       # Allowed (writing, not reading)
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
