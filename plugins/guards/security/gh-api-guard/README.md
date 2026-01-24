# gh-api-guard

A Claude Code hook plugin that allows only safe `gh api` commands while blocking
potentially dangerous operations.

## Purpose

The `gh api` command is powerful but can perform destructive operations like
deleting repositories, force merging PRs, or modifying settings. This plugin
creates a safelist of allowed read-only operations (primarily PR comment
fetching) while requiring manual approval for everything else.

## Allowed Operations

The following `gh api` endpoints are auto-allowed:

| Endpoint Pattern | Description |
|------------------|-------------|
| `repos/{owner}/{repo}/pulls/{num}/comments` | Fetch inline PR comments |
| `repos/{owner}/{repo}/issues/{num}/comments` | Fetch issue/PR general comments |
| `repos/{owner}/{repo}/pulls/{num}/reviews` | Fetch PR reviews |
| `repos/{owner}/{repo}/pulls/{num}/reviews/{id}/comments` | Fetch specific review comments |

## Blocked Operations

- Any endpoint using `POST`, `PUT`, `PATCH`, or `DELETE` methods
- Any endpoint not in the allowed list

## Examples

### Allowed

```bash
# Fetch inline PR comments
gh api repos/owner/repo/pulls/35/comments

# Fetch with jq filtering
gh api repos/owner/repo/pulls/35/comments --jq '.[] | .body'

# Fetch issue comments
gh api repos/owner/repo/issues/35/comments

# Fetch PR reviews
gh api repos/owner/repo/pulls/35/reviews
```

### Blocked (requires manual approval)

```bash
# POST request to create a comment
gh api repos/owner/repo/pulls/35/comments -X POST -f body="comment"

# DELETE request
gh api repos/owner/repo -X DELETE

# Unlisted endpoint
gh api repos/owner/repo/collaborators
```

## Customization

To allow additional safe endpoints, edit `hooks/check-gh-api.py` and add
patterns to the `ALLOWED_PATTERNS` list:

```python
ALLOWED_PATTERNS = [
    # Existing patterns...
    r"^repos/[^/]+/[^/]+/pulls/\d+/comments$",
    # Add your pattern here:
    r"^repos/[^/]+/[^/]+/pulls/\d+/files$",  # Allow fetching PR files
]
```

## Installation

Add to your `.claude/settings.json`:

```json
{
  "plugins": ["./plugins/gh-api-guard"]
}
```

Or install from the marketplace.
