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

1. **Read Plan and Import Tasks**

   - Read the work document completely
   - **Extract `task_list_id` from YAML frontmatter** (if present)
   - Review any references or links provided in the plan
   - If anything is unclear or ambiguous, ask clarifying questions now
   - Get user approval to proceed
   - **Do not skip this** - better to ask questions now than build the wrong thing

   **If plan has `task_list_id`:**
   ```
   skill: import-tasks [task_list_id from frontmatter]
   ```
   This imports tasks from the planning session into your current session, preserving descriptions and dependencies.

   **If plan has no `task_list_id`:** Tasks will be created in Step 3 (backward compatibility with older plans)

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

3. **Create Task List** (if not imported from plan)

   **Skip this step if you imported tasks using the `import-tasks` skill in Step 1.**

   For plans without a `task_list_id`, use **TaskCreate** to break the plan into actionable tasks:

   ```
   # Create tasks for each major work item
   TaskCreate: "Implement user model" (activeForm: "Implementing user model")
   TaskCreate: "Add authentication service" (activeForm: "Adding auth service")
   TaskCreate: "Write integration tests" (activeForm: "Writing tests")

   # Set up dependencies with TaskUpdate
   TaskUpdate: task #3 addBlockedBy [#1, #2]  # Tests depend on model + service
   ```

   **Task best practices:**
   - Include dependencies between tasks using `addBlockedBy`/`addBlocks`
   - Prioritize based on what needs to be done first
   - Include testing and quality check tasks
   - Keep tasks specific and completable
   - Use `activeForm` for clear progress indication (present continuous: "Implementing...")

4. **Parallel Execution with Subagents** (Optional - for large plans)

   For large plans with independent work streams, spawn subagents to work in parallel on the same TaskList:

   ```bash
   # Get the current TaskList ID
   task_list_id=$(ls -t ~/.claude/tasks/ | head -1)
   echo "TaskList ID: $task_list_id"
   ```

   **Spawning coordinated subagents:**

   ```
   # For Python projects - use python-coder agent
   Task(python-coder): "Work on tasks #2 and #3. Import from TaskList $task_list_id first."

   # For other projects - use general-purpose agent
   Task(general-purpose): "Work on tasks #4 and #5. Import from TaskList $task_list_id first."
   ```

   **Key coordination patterns:**
   - Subagents import the TaskList using `skill: import-tasks [id]`
   - When one agent completes a task, others can see unblocked work
   - Use `TaskUpdate` with `addBlockedBy` to prevent race conditions
   - Subagents should claim tasks with `TaskUpdate: status=in_progress` before starting

   **Language-specific agent selection:**
   | Project Type | Agent to Use |
   |--------------|--------------|
   | Python (Django, FastAPI, Flask) | `python-coder` |
   | TypeScript/JavaScript | `general-purpose` |
   | Mixed/Other | `general-purpose` |

### Phase 2: Execute

1. **Task Execution Loop**

   Use **TaskList** to see available work, then execute each task:

   ```
   while (TaskList shows pending tasks):
     # 1. Check for available (unblocked) tasks
     TaskList  # Shows tasks with status and blockers

     # 2. Claim and start the next available task
     TaskUpdate: task #{id} status=in_progress

     # 3. Execute the task
     - Read any referenced files from the plan
     - Look for similar patterns in codebase
     - Implement following existing conventions
     - Write tests for new functionality
     - Run tests after changes

     # 4. Complete the task
     TaskUpdate: task #{id} status=completed

     # 5. Update plan document
     - Mark off the corresponding checkbox in the plan file ([ ] → [x])
     - Evaluate for incremental commit (see below)
   ```

   **Task status workflow:** `pending` → `in_progress` → `completed`

   **IMPORTANT**: Always update the original plan document by checking off completed items. Use the Edit tool to change `- [ ]` to `- [x]` for each task you finish. This keeps the plan as a living document showing progress and ensures no checkboxes are left unchecked.

2. **Incremental Commits**

   After completing each task, evaluate whether to create an incremental commit:

   | Commit when... | Don't commit when... |
   |----------------|---------------------|
   | Logical unit complete (model, service, component) | Small part of a larger unit |
   | Tests pass + meaningful progress | Tests failing |
   | About to switch contexts (backend → frontend) | Purely scaffolding with no behavior |
   | About to attempt risky/uncertain changes | Would need a "WIP" commit message |

   **Heuristic:** "Can I write a commit message that describes a complete, valuable change? If yes, commit. If the message would be 'WIP' or 'partial X', wait."

   **Commit workflow:**
   ```bash
   # 1. Verify tests pass (use project's test command)
   # Examples: pytest, npm test, go test, etc.

   # 2. Stage only files related to this logical unit (not `git add .`)
   git add <files related to this logical unit>

   # 3. Commit with conventional message
   git commit -m "feat(scope): description of this unit"
   ```

   **Handling merge conflicts:** If conflicts arise during rebasing or merging, resolve them immediately. Incremental commits make conflict resolution easier since each commit is small and focused.

   **Note:** Incremental commits use clean conventional messages without attribution footers. The final Phase 4 commit/PR includes the full attribution.

3. **Follow Existing Patterns**

   - The plan should reference similar code - read those files first
   - Match naming conventions exactly
   - Reuse existing components where possible
   - Follow project coding standards (see CLAUDE.md)
   - When in doubt, grep for similar implementations

4. **Use Specialized Coding Agents**

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

5. **Test Continuously**

   - Run relevant tests after each significant change
   - Don't wait until the end to test
   - Fix failures immediately
   - Add new tests for new functionality

   **Test Commands by Language:**
   - Python: `pytest`, `poetry run pytest`, or `uv run pytest`
   - JavaScript/TypeScript: `npm test`, `yarn test`, or `pnpm test`
   - Go: `go test ./...`
   - Generic: Check `package.json`, `pyproject.toml`, `Makefile`, or CI config for test commands

6. **Figma Design Sync** (if applicable)

   For UI work with Figma designs:

   - Implement components following design specs
   - Use figma-design-sync agent iteratively to compare
   - Fix visual differences identified
   - Repeat until implementation matches design

7. **Track Progress**
   - Use **TaskList** to check overall progress
   - Use **TaskUpdate** to mark tasks completed or add blockers
   - Use **TaskCreate** to add new tasks if scope expands
   - Note any blockers with `TaskUpdate: addBlockedBy`
   - Keep user informed of major milestones

### Phase 3: Quality Check

1. **Run Core Quality Checks**

   Always run before submitting:

   **For Python projects:**
   ```bash
   # Run tests
   poetry run pytest

   # Run linting
   poetry run ruff check .

   # Run type checking
   mypy .  
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
   - **agent-native-reviewer**: Make sure the work done is agent compatible

   Run reviewers in parallel with Task tool:

   ```
   Task(code-simplicity-reviewer): "Review changes for simplicity"
   Task(kieran-python-reviewer): "Check Python conventions"
   ```

   Present findings to user and address critical issues.

3. **Final Validation**
   - All tasks marked completed (verify with `TaskList`)
   - All tests pass
   - Linting passes
   - Code follows existing patterns
   - Figma designs match (if applicable)
   - No console errors or warnings

4. **Pre-Ship Decision**

   After quality checks pass, use the **AskUserQuestion tool** to present options:

   **Question:** "Quality checks complete. Ready to ship?"

   **Options:**
   1. **Run `/workflows:review`** (Recommended for complex changes) - Multi-agent exhaustive review with ultra-thinking and worktrees
   2. **Ship it** - Proceed directly to commit and PR
   3. **Run specific reviewers** - Choose which reviewer agents to run

   Based on selection:
   - **`/workflows:review`** → Call the /workflows:review command for thorough multi-agent analysis
   - **Ship it** → Proceed to Phase 4
   - **Run specific reviewers** → Ask which reviewers to run (code-simplicity, security-sentinel, performance-oracle, etc.), run them, address findings, then return to this decision point

   **When to recommend `/workflows:review`:**
   - Changes touch 10+ files
   - Security-sensitive code (auth, permissions, data access)
   - Performance-critical paths
   - Complex business logic or algorithms
   - Significant refactoring

   For simpler changes, "Ship it" is usually sufficient since core quality checks already passed.

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
- [ ] All tasks marked completed (`TaskList` shows no pending tasks)
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
- **Forgetting to track tasks** - Use TaskList/TaskUpdate to track progress
- **80% done syndrome** - Finish the feature, don't move on early
- **Over-reviewing simple changes** - Save reviewer agents for complex work
- **Not using subagents for large plans** - Parallelize with shared TaskList for faster execution
