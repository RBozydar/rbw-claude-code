# rbw-claude-code

A Claude Code plugin marketplace for Python development with AI-powered code review, workflow automation, and productivity tools.

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add RBozydar/rbw-claude-code
```

Then browse and install plugins:

```bash
/plugin menu
```

## Available Plugins

### AI-Powered Development

| Plugin | Description |
|--------|-------------|
| [core](plugins/core) | Universal AI development tools: 14 agents, 13 commands, 6 skills for code review, research, and workflow automation |
| [python-backend](plugins/python-backend) | Python-specific tools: 5 reviewers (including Gemini), 2 commands for pytest and type checking |

### Automation Hooks

| Plugin | Description |
|--------|-------------|
| [enforce-uv](plugins/enforce-uv) | Block bare python/pip/pytest commands, enforce uv usage |
| [conventional-commits](plugins/conventional-commits) | Validate git commit messages follow conventional format |
| [python-format](plugins/python-format) | Auto-format Python files with ruff after edits |
| [python-typecheck](plugins/python-typecheck) | Run type checking after Python file edits |
| [test-reminder](plugins/test-reminder) | Remind to add tests when creating new Python files |

### Security Hooks

| Plugin | Description |
|--------|-------------|
| [protect-env](plugins/protect-env) | Block reading .env files to protect secrets |
| [git-safety-guard](plugins/git-safety-guard) | Block destructive git commands (reset --hard, push --force, etc.) |
| [safety-guard](plugins/safety-guard) | Block destructive file ops, supply chain attacks, and .env reading |

## Core Plugin

The `core` plugin provides language-agnostic AI-powered development tools:

### Workflow Commands
- `/workflows:plan` - Transform features into structured plans
- `/workflows:work` - Execute work plans efficiently
- `/workflows:review` - Multi-agent code reviews with parallel analysis
- `/workflows:compound` - Document solved problems for knowledge compounding

### Review Agents
- `code-simplicity-reviewer` - Reviews for unnecessary complexity
- `security-sentinel` - Security vulnerability analysis
- `performance-oracle` - Performance analysis
- `architecture-strategist` - System design review
- `pattern-recognition-specialist` - Pattern/anti-pattern detection
- `agent-native-reviewer` - Ensures features are agent-accessible
- `data-migration-expert` - Database migration validation

### Research Agents
- `framework-docs-researcher` - Framework documentation lookup
- `git-history-analyzer` - Git history analysis
- `repo-research-analyst` - Repository analysis
- `best-practices-researcher` - Industry best practices

### Skills
- `compound-docs` - Document solved problems
- `git-worktree` - Manage Git worktrees
- `file-todos` - File-based todo tracking
- `create-agent-skills` - Create Claude Code skills
- `agent-native-architecture` - Build prompt-native AI agents
- `skill-creator` - Create new skills

## Python Backend Plugin

The `python-backend` plugin extends core with Python-specific capabilities:

### Review Agents
- `kieran-python-reviewer` - High-quality Python code review
- `skeptical-simplicity-reviewer` - Anti-overengineering critique
- `ml-expert-reviewer` - ML/DS/LLM specialized review
- `gemini-brainstorm` - Second opinion from Gemini
- `gemini-reviewer` - Alternative code review from Gemini

### Commands
- `/pytest-runner` - Smart pytest execution with failure analysis
- `/type-check` - Intelligent type checking with mypy/pyright

## Hook Plugins

### enforce-uv
Ensures Claude Code uses `uv` for all Python operations. Blocks bare `python`, `pip`, `pytest` commands.

### conventional-commits
Validates commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) specification.

### python-format
Runs `uvx ruff format` automatically after any Python file edit.

### python-typecheck
Runs `uvx pyright` automatically after any Python file edit.

### test-reminder
Reminds you to add tests when creating new Python modules.

### protect-env
Blocks reading `.env` files to prevent exposing secrets to AI.

### git-safety-guard
Blocks destructive git commands that could cause data loss:
- `git reset --hard`, `git reset --merge`
- `git push --force`, `git push -f`
- `git checkout -- <files>`, `git restore <files>`
- `git clean -f`, `git branch -D`
- `git stash drop`, `git stash clear`
- `git reflog expire`, `git filter-branch`

Allows safe alternatives: `git checkout -b`, `git push --force-with-lease`, `git clean -n`.

### safety-guard
Blocks destructive file operations and supply chain attacks:
- `rm -rf` outside temp directories
- `find -delete`, `shred`, `truncate`
- `curl | bash`, `wget | sh` (supply chain attacks)
- `bash -c` with destructive commands (bypass detection)
- Reading `.env` files (allows `.env.example`, `.env.sample`, `.env.template`)

## Requirements

- Claude Code with plugin support
- `uv` installed for Python-related plugins
- GitHub CLI (`gh`) for PR operations
- Gemini CLI for Gemini agents (optional)

## License

MIT
