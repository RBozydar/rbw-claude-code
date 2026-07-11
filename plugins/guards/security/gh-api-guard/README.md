# gh-api-guard

A Claude Code hook plugin that allows read-only GitHub CLI operations while
requiring manual approval for explicit mutations.

## Behavior

The guard parses actual `gh` invocations, including compound commands and
commands nested in `bash -c`, `sh -c`, `zsh -c`, or `eval`.

It allows:

- `gh api` REST requests whose effective method is `GET` or `HEAD`
- GraphQL queries supplied through a `query=` field
- Read-only `gh` commands such as `gh pr view` and `gh ruleset view`

It blocks:

- REST requests whose effective method is `POST`, `PUT`, `PATCH`, or `DELETE`
- GraphQL mutations and opaque GraphQL input/query files
- Destructive CLI operations such as PR merges, repository deletion, secret
  changes, workflow cancellation, and ruleset creation/deletion

GitHub CLI changes the default REST method from `GET` to `POST` when field or
input flags are supplied. The guard accounts for this behavior and also
recognizes `-X`, `--method`, and `--method=...` overrides.

## Examples

### Allowed

```bash
gh pr view 5 --json comments --jq '.comments | length'
gh api 'repos/owner/repo/pulls/5/comments?per_page=100' --jq 'length'
gh api graphql -f 'query=query { viewer { login } }'
gh api repos/owner/repo/issues -X GET -f state=open
gh ruleset view 123
```

### Blocked

```bash
gh api repos/owner/repo/issues/5/comments -f body='comment'
gh api repos/owner/repo -X DELETE
gh api graphql -f 'query=mutation { ... }'
gh pr merge 5
gh ruleset delete 123
```

## Installation

Add the plugin to your Claude Code configuration through the repository's
marketplace entry.
