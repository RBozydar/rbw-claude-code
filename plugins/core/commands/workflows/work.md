---
name: workflows:work
description: Execute work plans efficiently while maintaining quality and finishing features
argument-hint: "[plan file, specification, or todo file path]"
---

# Work Plan Execution Command

Execute a work plan efficiently while maintaining quality and finishing features.

## Introduction

This command takes a work document (plan, specification, or todo file) and executes it systematically. The focus is on **shipping complete features** by understanding requirements quickly, following existing patterns, and maintaining quality throughout.

## Input Document

<input_document> #$ARGUMENTS </input_document>

## Execution Workflow

### Phase 1: Quick Start

1. **Read Plan and Clarify**

   - Read the work document completely
   - Review any references or links provided in the plan
   - If anything is unclear or ambiguous, ask clarifying questions now
   - Get user approval to proceed
   - **Do not skip this** - better to ask questions now than build the wrong thing

2. **Setup Environment**

   Choose your work style:

   **Option A: Live work on current branch**
   ```bash
   git checkout main && git pull origin main
   git checkout -b feature-branch-name
   ```

   **Option B: Parallel work with worktree (recommended for parallel development)**
   ```bash
   # Ask user first: "Work in parallel with worktree or on current branch?"
   # If worktree:
   skill: git-worktree
   # The skill will create a new branch from main in an isolated worktree
   ```

   **Recommendation**: Use worktree if:
   - You want to work on multiple features simultaneously
   - You want to keep main clean while experimenting
   - You plan to switch between branches frequently

   Use live branch if:
   - You're working on a single feature
   - You prefer staying in the main repository

3. **Create Todo List**
   - Use TodoWrite to break plan into actionable tasks
   - Include dependencies between tasks
   - Prioritize based on what needs to be done first
   - Include testing and quality check tasks
   - Keep tasks specific and completable

### Phase 2: Execute

1. **Task Execution Loop**

   For each task in priority order:

   ```
   while (tasks remain):
     - Mark task as in_progress in TodoWrite
     - Read any referenced files from the plan
     - Look for similar patterns in codebase
     - Implement following existing conventions
     - Write tests for new functionality
     - Run tests after changes
     - Mark task as completed
   ```

2. **Follow Existing Patterns**

   - The plan should reference similar code - read those files first
   - Match naming conventions exactly
   - Reuse existing components where possible
   - Follow project coding standards (see CLAUDE.md)
   - When in doubt, grep for similar implementations

3. **Use Specialized Coding Agents**

   When implementing code, delegate to the appropriate specialized coding agent with full context:

   **For Python projects:**
   Use the `python-coder` agent via Task tool. Provide comprehensive context so the agent doesn't have to figure things out:

   **Required context to include:**
   - What to implement (specific task from the plan)
   - Where to implement it (file paths, module location)
   - Related files to reference (existing patterns to follow)
   - Expected interfaces/signatures (function names, class structure)
   - Dependencies to use (libraries, internal modules)
   - Any constraints or requirements from the plan

   **Example with full context:**
   ```
   Task(python-coder): "Implement UserAuthService in src/services/auth.py

   Context:
   - Follow pattern from src/services/email.py (async service with dependency injection)
   - Use httpx for async HTTP calls to the OAuth provider
   - Inject DatabaseAdapter via __init__ (don't instantiate)
   - Must implement: authenticate(token: str) -> User | None
   - Use Pydantic for User model validation
   - Add tests in tests/services/test_auth.py following test_email.py pattern"
   ```

   **Bad example (lacks context):**
   ```
   Task(python-coder): "Implement authentication"  # Agent has to guess everything
   ```

   The agent enforces SOLID principles, asyncio patterns, and production-quality standards automatically - you just need to tell it WHAT to build and WHERE.

4. **Test Continuously**

   - Run relevant tests after each significant change
   - Don't wait until the end to test
   - Fix failures immediately
   - Add new tests for new functionality

   **Test Commands by Language:**
   - Python: `pytest`, `uv run pytest`, or `poetry run pytest`
   - JavaScript/TypeScript: `npm test`, `yarn test`, or `pnpm test`
   - Go: `go test ./...`
   - Generic: Check `package.json`, `pyproject.toml`, `Makefile`, or CI config for test commands

5. **Figma Design Sync** (if applicable)

   For UI work with Figma designs:

   - Implement components following design specs
   - Use figma-design-sync agent iteratively to compare
   - Fix visual differences identified
   - Repeat until implementation matches design

6. **Track Progress**
   - Keep TodoWrite updated as you complete tasks
   - Note any blockers or unexpected discoveries
   - Create new tasks if scope expands
   - Keep user informed of major milestones

### Phase 3: Quality Check

1. **Run Core Quality Checks**

   Always run before submitting:

   **For Python projects:**
   ```bash
   # Run tests
   uv run pytest

   # Run linting
   uvx ruff check .

   # Run type checking
   mypy .  # or pyright
   ```

   **For other languages:**
   Check CLAUDE.md or project configuration for language-specific commands.

2. **Consider Reviewer Agents** (Optional)

   Use for complex, risky, or large changes:

   - **code-simplicity-reviewer**: Check for unnecessary complexity
   - **performance-oracle**: Check for performance issues
   - **security-sentinel**: Scan for security vulnerabilities
   - **kieran-python-reviewer**: Verify Python conventions (Python projects)
   - **skeptical-simplicity-reviewer**: Challenge over-engineering

   Run reviewers in parallel with Task tool:

   ```
   Task(code-simplicity-reviewer): "Review changes for simplicity"
   Task(kieran-python-reviewer): "Check Python conventions"
   ```

   Present findings to user and address critical issues.

3. **Final Validation**
   - All TodoWrite tasks marked completed
   - All tests pass
   - Linting passes
   - Code follows existing patterns
   - Figma designs match (if applicable)
   - No console errors or warnings

### Phase 4: Ship It

1. **Create Commit**

   ```bash
   git add .
   git status  # Review what's being committed
   git diff --staged  # Check the changes

   # Commit with conventional format
   git commit -m "$(cat <<'EOF'
   feat(scope): description of what and why

   Brief explanation if needed.

   Generated with Claude Code

   Co-Authored-By: Claude <noreply@anthropic.com>
   EOF
   )"
   ```

2. **Create Pull Request**

   ```bash
   git push -u origin feature-branch-name

   gh pr create --title "Feature: [Description]" --body "$(cat <<'EOF'
   ## Summary
   - What was built
   - Why it was needed
   - Key decisions made

   ## Testing
   - Tests added/modified
   - Manual testing performed

   ## Screenshots
   [If applicable]

   Generated with Claude Code
   EOF
   )"
   ```

3. **Notify User**
   - Summarize what was completed
   - Link to PR
   - Note any follow-up work needed
   - Suggest next steps if applicable

---

## Key Principles

### Start Fast, Execute Faster

- Get clarification once at the start, then execute
- Don't wait for perfect understanding - ask questions and move
- The goal is to **finish the feature**, not create perfect process

### The Plan is Your Guide

- Work documents should reference similar code and patterns
- Load those references and follow them
- Don't reinvent - match what exists

### Test As You Go

- Run tests after each change, not at the end
- Fix failures immediately
- Continuous testing prevents big surprises

### Quality is Built In

- Follow existing patterns
- Write tests for new code
- Run linting before pushing
- Use reviewer agents for complex/risky changes only

### Ship Complete Features

- Mark all tasks completed before moving on
- Don't leave features 80% done
- A finished feature that ships beats a perfect feature that doesn't

## Quality Checklist

Before creating PR, verify:

- [ ] All clarifying questions asked and answered
- [ ] All TodoWrite tasks marked completed
- [ ] Tests pass
- [ ] Linting passes
- [ ] Code follows existing patterns
- [ ] Figma designs match implementation (if applicable)
- [ ] Commit messages follow conventional format
- [ ] PR description includes summary and testing notes

## When to Use Reviewer Agents

**Don't use by default.** Use reviewer agents only when:

- Large refactor affecting many files (10+)
- Security-sensitive changes (authentication, permissions, data access)
- Performance-critical code paths
- Complex algorithms or business logic
- User explicitly requests thorough review

For most features: tests + linting + following patterns is sufficient.

## Common Pitfalls to Avoid

- **Analysis paralysis** - Don't overthink, read the plan and execute
- **Skipping clarifying questions** - Ask now, not after building wrong thing
- **Ignoring plan references** - The plan has links for a reason
- **Testing at the end** - Test continuously or suffer later
- **Forgetting TodoWrite** - Track progress or lose track of what's done
- **80% done syndrome** - Finish the feature, don't move on early
- **Over-reviewing simple changes** - Save reviewer agents for complex work
