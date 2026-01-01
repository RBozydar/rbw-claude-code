# Core Plugin

Universal AI-powered development tools for code review, research, and workflow automation.

## What it does

This plugin provides language-agnostic agents, commands, and skills that work across any codebase. It's the foundation for AI-assisted development workflows.

## Installation

```bash
claude plugin add ./plugins/core
```

## Components

### Agents (14)

**Review Agents (7):**
- `code-simplicity-reviewer` - Reviews code for unnecessary complexity
- `security-sentinel` - Security vulnerability analysis
- `performance-oracle` - Performance analysis and optimization
- `architecture-strategist` - System architecture and design review
- `pattern-recognition-specialist` - Identifies code patterns and anti-patterns
- `agent-native-reviewer` - Ensures features are agent-accessible
- `data-migration-expert` - Database migration validation

**Research Agents (4):**
- `framework-docs-researcher` - Researches framework documentation via Context7
- `git-history-analyzer` - Analyzes git history for patterns
- `repo-research-analyst` - Deep repository analysis
- `best-practices-researcher` - Researches industry best practices

**Workflow Agents (3):**
- `spec-flow-analyzer` - Analyzes specification flows
- `bug-reproduction-validator` - Validates bug reproductions
- `pr-comment-resolver` - Resolves PR review comments

### Commands (13)

**Workflow Commands:**
- `/workflows:plan` - Transform features into structured plans
- `/workflows:work` - Execute work plans efficiently
- `/workflows:review` - Multi-agent code reviews
- `/workflows:compound` - Document solved problems

**Utility Commands:**
- `/resolve_pr_parallel` - Resolve PR comments in parallel
- `/resolve_parallel` - Resolve TODO comments in parallel
- `/resolve_todo_parallel` - Resolve CLI todos in parallel
- `/changelog` - Create changelogs from merges
- `/triage` - Triage findings for todo system
- `/generate_command` - Create new slash commands
- `/heal-skill` - Fix incorrect SKILL.md files
- `/create-agent-skill` - Create Claude Code skills
- `/plan_review` - Multi-agent plan review

### Skills (7)

- `agent-native-architecture` - Building AI agents with prompt-native patterns
- `create-agent-skills` - Guide for creating Claude Code skills
- `compound-docs` - Document solved problems for knowledge compounding
- `git-worktree` - Manage Git worktrees for isolated development
- `git-ship` - Complete git workflow: commit, push, PR, CI wait, merge
- `file-todos` - File-based todo tracking system
- `skill-creator` - Creating new Claude Code skills

### MCP Servers (1)

- `context7` - Framework documentation lookup (100+ frameworks)

## Usage

### Code Review

```bash
/workflows:review 123  # Review PR #123
/workflows:review      # Review current branch
```

### Planning

```bash
/workflows:plan "Add user authentication feature"
```

### Execution

```bash
/workflows:work plans/feature-auth.md
```

### Knowledge Compounding

```bash
/workflows:compound  # Document the problem you just solved
```

## Philosophy

Each unit of engineering work should make subsequent units easier—not harder. This plugin enables:

1. **Plan** - Transform ideas into structured, actionable plans
2. **Delegate** - Use specialized agents for different review perspectives
3. **Assess** - Multi-angle review with stakeholder considerations
4. **Codify** - Document solutions for future reference

## Requirements

- Claude Code CLI
- GitHub CLI (`gh`) for PR operations
- Git for version control operations
