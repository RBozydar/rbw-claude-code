# Safety Guard Plugin

Prevents Claude from executing destructive file operations and supply chain attacks.

## What it blocks

### File Destruction

| Command | Reason |
|---------|--------|
| `rm -rf` (outside /tmp) | Catastrophic file deletion |
| `shred` | Unrecoverable file destruction |
| `truncate` | Destroys file contents |

### find Command Patterns

| Command | Reason |
|---------|--------|
| `find ... -delete` | Mass file deletion |
| `find ... -exec rm` | Mass file deletion via exec |
| `find ... -execdir rm` | Mass file deletion via execdir |
| `find ... -exec shred` | Mass file destruction |
| `find ... -exec chmod 000` | Removes all permissions |
| `find ... -exec mv ... /dev/null` | Destroys files |

### xargs Piping Patterns

| Command | Reason |
|---------|--------|
| `... \| xargs rm` | Mass file deletion |
| `... \| xargs shred` | Mass file destruction |
| `... \| xargs chmod 000` | Removes all permissions |
| `... \| xargs rm -rf` | Catastrophic file deletion |

### chmod Dangerous Patterns

| Command | Reason |
|---------|--------|
| `chmod 000` | Removes all permissions |
| `chmod 777 ... .ssh` | Security risk on SSH files |
| `chmod 777 ... .env` | Security risk on env files |
| `chmod -R 000` | Recursive permission removal |

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
| `bash -c "git reset --hard ..."` | Bypass attempt |
| `bash -c "git push --force ..."` | Bypass attempt |

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
