# Safety Guard Plugin

Prevents Claude from executing destructive file operations and supply chain attacks.

## What it blocks

### File Operations

| Command | Reason |
|---------|--------|
| `rm -rf` (outside /tmp) | Catastrophic file deletion |
| `find ... -delete` | Mass file deletion |
| `shred` | Unrecoverable file destruction |
| `truncate` | Destroys file contents |

### Environment Files

| Pattern | Reason |
|---------|--------|
| `.env` | May contain secrets |
| `.env.local`, `.env.production`, etc. | May contain secrets |

**Allowed:** `.env.example`, `.env.sample`, `.env.template`, `.env.dist`

### Supply Chain Attacks

| Pattern | Reason |
|---------|--------|
| `curl ... \| bash` | Remote code execution |
| `wget ... \| sh` | Remote code execution |
| `bash -c "rm -rf ..."` | Bypass attempt |

## What it allows

- `rm -rf /tmp/...` - Temp directory cleanup
- `rm -rf $TMPDIR/...` - Temp directory cleanup
- `.env.example` - Template files (no secrets)

## Installation

```bash
claude plugin add ./plugins/safety-guard
```

## Note on protect-env

This plugin provides enhanced .env protection compared to `protect-env`:
- Allows `.env.example`, `.env.sample`, `.env.template`
- Can be used alongside or instead of `protect-env`

## Requirements

- cchooks library (installed automatically via uv)
