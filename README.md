# rbw-claude-code

A Claude Code plugin marketplace for Python development with AI-powered code
review, workflow automation, and productivity tools.

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add RBozydar/rbw-claude-code
```

Then browse and install plugins:

```bash
/plugin menu
```

### Poetry Users

If you use Poetry instead of uv for package management, install from the `poetry-variant` branch:

```bash
/plugin marketplace add RBozydar/rbw-claude-code#poetry-variant
```

This variant includes `enforce-poetry` instead of `enforce-uv`, suggesting `poetry run` and `poetry add` commands.

### Hook Setup (Required Workaround)

Due to a [known Claude Code bug](https://github.com/anthropics/claude-code/issues/16288),
plugin hooks are matched but not executed. Until this is fixed upstream, you need to
manually configure hooks in your settings.

Navigate to the marketplace directory:

```bash
cd ~/.claude/plugins/RBozydar/rbw-claude-code
```

Run the setup script:

```bash
# Global hooks (apply to all projects) - default
./scripts/setup-hooks.sh

# Or project-specific hooks (run from within your project)
./scripts/setup-hooks.sh --project
```

To verify hooks are active:

```bash
/hooks
```

You should see the configured hooks listed (enforce-uv, conventional-commits, etc.).

#### Auto-Sync Detection

Once hooks are installed, a `SessionStart` hook automatically checks if your
configured hooks are in sync with available plugin hooks. If hooks change
(e.g., after updating the marketplace), you'll see a warning at session start:

```text
====================================================
  rbw-claude-code: Hooks are out of sync!
====================================================

  Plugin hooks have changed. Run to update:

    ./scripts/setup-hooks.sh --project

====================================================
```

You can also manually check sync status:

```bash
./scripts/setup-hooks.sh --check           # Check global hooks
./scripts/setup-hooks.sh --check --project # Check project hooks
```

## Available Plugins

### AI-Powered Development

| Plugin | Description |
|--------|-------------|
| [core](plugins/core) | Universal AI development tools: 14 agents, 13 commands, 6 skills |
| [python-backend](plugins/python-backend) | Python-specific tools: 5 reviewers, 2 commands |

### Automation Hooks

| Plugin | Description |
|--------|-------------|
| [enforce-uv](plugins/enforce-uv) | Block bare python/pip/pytest commands, enforce uv |
| [conventional-commits](plugins/conventional-commits) | Validate conventional commit format |
| [python-format](plugins/python-format) | Auto-format Python files with ruff after edits |
| [python-typecheck](plugins/python-typecheck) | Run type checking after Python file edits |
| [test-reminder](plugins/test-reminder) | Remind to add tests when creating new Python files |

### Security Hooks

| Plugin | Description |
|--------|-------------|
| [protect-env](plugins/protect-env) | Block reading .env files to protect secrets |
| [git-safety-guard](plugins/git-safety-guard) | Block destructive git commands |
| [safety-guard](plugins/safety-guard) | Block destructive file ops and supply chain attacks |

## Core Plugin

The `core` plugin provides language-agnostic AI-powered development tools:

### Workflow Commands

- `/workflows:plan` - Transform features into structured plans
- `/workflows:work` - Execute work plans efficiently
- `/workflows:review` - Multi-agent code reviews with parallel analysis
- `/workflows:compound` - Document solved problems for knowledge compounding

### Code Review Agents

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

| Skill Name | Description |
|------------|-------------|
| `core:agent-native-architecture` | Build AI agents using prompt-native architecture |
| `core:compound-docs` | Capture solved problems as categorized documentation |
| `core:create-agent-skills` | Expert guidance for creating Claude Code skills |
| `core:file-todos` | File-based todo tracking in todos/ directory |
| `core:git-ship` | Complete git workflow: commit, push, PR, CI, merge |
| `core:git-worktree` | Manage Git worktrees for parallel development |
| `core:skill-creator` | Guide for creating effective skills |

## Python Backend Plugin

The `python-backend` plugin extends core with Python-specific capabilities:

### Python Review Agents

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

Ensures Claude Code uses `uv` for all Python operations.
Blocks bare `python`, `pip`, `pytest` commands.

### conventional-commits

Validates commit messages follow
[Conventional Commits](https://www.conventionalcommits.org/) specification.

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

Allows safe alternatives: `git checkout -b`, `git push --force-with-lease`,
`git clean -n`.

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
