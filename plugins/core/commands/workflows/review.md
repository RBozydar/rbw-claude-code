---
name: workflows:review
description: Perform exhaustive code reviews using multi-agent analysis, ultra-thinking, and worktrees
argument-hint: "[PR number, GitHub URL, branch name, or latest]"
---

# Review Command

<command_purpose> Perform exhaustive code reviews using multi-agent analysis, ultra-thinking, and Git worktrees for deep local inspection. </command_purpose>

## Introduction

<role>Senior Code Review Architect with expertise in security, performance, architecture, and quality assurance</role>

## Prerequisites

<requirements>
- Git repository with GitHub CLI (`gh`) installed and authenticated
- Clean main/master branch
- Proper permissions to create worktrees and access the repository
- For document reviews: Path to a markdown file or document
</requirements>

## Main Tasks

### 1. Determine Review Target & Setup (ALWAYS FIRST)

<review_target> #$ARGUMENTS </review_target>

<thinking>
First, I need to determine the review target type and set up the code for analysis.
</thinking>

#### Immediate Actions:

<task_list>

- [ ] Determine review type: PR number (numeric), GitHub URL, file path (.md), or empty (current branch)
- [ ] Check current git branch
- [ ] If ALREADY on the PR branch → proceed with analysis on current branch
- [ ] If DIFFERENT branch → offer to use worktree: "Use git-worktree skill for isolated Call `skill: git-worktree` with branch name
- [ ] Fetch PR metadata using `gh pr view --json` for title, body, files, linked issues
- [ ] Set up language-specific analysis tools
- [ ] Prepare security scanning environment
- [ ] Make sure we are on the branch we are reviewing. Use gh pr checkout to switch to the branch or manually checkout the branch.

Ensure that the code is ready for analysis (either in worktree or on current branch). ONLY then proceed to the next step.

</task_list>

#### Parallel Agents to review the PR:

<parallel_tasks>

Run ALL or most of these agents at the same time:

**Core Reviewers (always run):**
1. Task code-simplicity-reviewer(PR content) - YAGNI, severity taxonomy, temporal contamination
2. Task architecture-strategist(PR content)
3. Task pattern-recognition-specialist(PR content) - Coherence patterns, duplication thresholds
4. Task security-sentinel(PR content)
5. Task performance-oracle(PR content)
6. Task agent-native-reviewer(PR content) - Verify new features are agent-accessible
7. Task baseline-code-reviewer(PR content) - 17 atomic code smell categories
8. Task slop-detector(PR content) - AI-generated code patterns: unnecessary comments, defensive over-engineering, type workarounds

**Deep Code Quality Reviewers (run for thorough reviews):**
1. Task coherence-reviewer(PR content) - Repetition, naming consistency, zombie code
2. Task drift-reviewer(PR content) - Module structure, cross-file comprehension, abstraction opportunities

**Research Agents:**
10. Task git-history-analyzer(PR content)
11. Task best-practices-researcher(PR content)

</parallel_tasks>

#### Language-Specific Agents (Run if applicable):

<language_agents>

These agents are run based on the programming language detected in the PR:

**If PR contains Python files (*.py, pyproject.toml, requirements.txt):**
- Task kieran-python-reviewer(PR content) - Python code review with type hints, Pythonic patterns
- Task skeptical-simplicity-reviewer(PR content) - Anti-overengineering critique
- Task ml-expert-reviewer(PR content) - If ML/DS/LLM code detected (notebooks, model code, prompts, dealing with LLMs)

**Detection for ML/DS code:**
- `*.ipynb` files present
- Imports of: torch, tensorflow, sklearn, pandas, numpy, transformers, openai, anthropic, litellm
- Files in directories named: models/, ml/, ai/, llm/, data/

</language_agents>

#### Conditional Agents (Run if applicable):

<conditional_agents>

These agents are run ONLY when the PR matches specific criteria. Check the PR files list to determine if they apply:

**If PR contains database migrations or data transformations:**

- Task data-migration-expert(PR content) - Validates ID mappings, checks for swapped values, verifies rollback safety

**When to run migration agents:**
- PR includes files matching `alembic/versions/*.py`, `migrations/*.py`, `**/migrate/*.py`
- PR modifies columns that store IDs, enums, or mappings
- PR includes data backfill scripts
- PR changes how data is read/written (e.g., changing from FK to string column)
- PR title/body mentions: migration, backfill, data transformation, ID mapping

**What these agents check:**
- `data-migration-expert`: Verifies hard-coded mappings match production reality (prevents swapped IDs), checks for orphaned associations, validates dual-write patterns

**If PR is a significant refactor or technical debt cleanup:**

- Task refactor-analyst-agent(PR content) - 11-dimension analysis, philosophy validation, tiered recommendations

**When to run refactor agents:**
- PR title/body mentions: refactor, cleanup, technical debt, reorganize
- PR modifies file structure or moves code between modules
- PR changes 5+ files without adding new features
- PR simplifies or consolidates existing code

**What these agents check:**
- `refactor-analyst-agent`: Architecture, modules, abstraction opportunities, types, error handling, conditionals, naming, extraction, testability, modernization, readability

**If PR is a bug fix:**

- Task bug-reproduction-validator(PR content) - Validates the fix actually resolves the reported issue

**When to run bug validation:**
- PR title/body mentions: fix, bug, issue, resolve, closes #
- PR references a bug report or issue number
- PR description describes unexpected behavior being corrected

**What this agent checks:**
- `bug-reproduction-validator`: Attempts to reproduce the original bug, validates the fix addresses root cause, checks for regression potential

</conditional_agents>

#### Second Opinion (Optional - for high-stakes reviews):

<second_opinion>

For critical PRs or when you want diverse perspectives, get a second opinion from a different LLM:

**When to run:**
- Security-sensitive changes (authentication, authorization, data access)
- High-risk refactors affecting core functionality
- PRs that will be difficult to revert
- When Claude's review feels uncertain or incomplete

**Run:**
- Task gemini-reviewer(PR content) - Second opinion from Gemini to catch Claude's blind spots

**What this provides:**
- Different model's perspective on the same code
- Potential issues Claude might miss due to training differences
- Consensus validation (both models agree = higher confidence)
- Conflict identification (models disagree = needs human attention)

</second_opinion>

### 4. Ultra-Thinking Deep Dive Phases

<ultrathink_instruction> For each phase below, spend maximum cognitive effort. Think step by step. Consider all angles. Question assumptions. And bring all reviews in a synthesis to the user.</ultrathink_instruction>

<deliverable>
Complete system context map with component interactions
</deliverable>

#### Phase 3: Stakeholder Perspective Analysis

<thinking_prompt> ULTRA-THINK: Put yourself in each stakeholder's shoes. What matters to them? What are their pain points? </thinking_prompt>

<stakeholder_perspectives>

1. **Developer Perspective** <questions>

   - How easy is this to understand and modify?
   - Are the APIs intuitive?
   - Is debugging straightforward?
   - Can I test this easily? </questions>

2. **Operations Perspective** <questions>

   - How do I deploy this safely?
   - What metrics and logs are available?
   - How do I troubleshoot issues?
   - What are the resource requirements? </questions>

3. **End User Perspective** <questions>

   - Is the feature intuitive?
   - Are error messages helpful?
   - Is performance acceptable?
   - Does it solve my problem? </questions>

4. **Security Team Perspective** <questions>

   - What's the attack surface?
   - Are there compliance requirements?
   - How is data protected?
   - What are the audit capabilities? </questions>

5. **Business Perspective** <questions>
   - What's the ROI?
   - Are there legal/compliance risks?
   - How does this affect time-to-market?
   - What's the total cost of ownership? </questions> </stakeholder_perspectives>

#### Phase 4: Scenario Exploration

<thinking_prompt> ULTRA-THINK: Explore edge cases and failure scenarios. What could go wrong? How does the system behave under stress? </thinking_prompt>

<scenario_checklist>

- [ ] **Happy Path**: Normal operation with valid inputs
- [ ] **Invalid Inputs**: Null, empty, malformed data
- [ ] **Boundary Conditions**: Min/max values, empty collections
- [ ] **Concurrent Access**: Race conditions, deadlocks
- [ ] **Scale Testing**: 10x, 100x, 1000x normal load
- [ ] **Network Issues**: Timeouts, partial failures
- [ ] **Resource Exhaustion**: Memory, disk, connections
- [ ] **Security Attacks**: Injection, overflow, DoS
- [ ] **Data Corruption**: Partial writes, inconsistency
- [ ] **Cascading Failures**: Downstream service issues </scenario_checklist>

### 6. Multi-Angle Review Perspectives

#### Technical Excellence Angle

- Code craftsmanship evaluation
- Engineering best practices
- Technical documentation quality
- Tooling and automation assessment

#### Business Value Angle

- Feature completeness validation
- Performance impact on users
- Cost-benefit analysis
- Time-to-market considerations

#### Risk Management Angle

- Security risk assessment
- Operational risk evaluation
- Compliance risk verification
- Technical debt accumulation

#### Team Dynamics Angle

- Code review etiquette
- Knowledge sharing effectiveness
- Collaboration patterns
- Mentoring opportunities

### 4. Simplification and Minimalism Review

Run the Task code-simplicity-reviewer() to see if we can simplify the code.

### 5. Findings Synthesis, Documentation, and Execution Tracking

<critical_requirement> ALL findings MUST be stored in the todos/ directory using the file-todos skill AND tracked in TaskList for execution. Create todo files immediately after synthesis - do NOT present findings for user approval first. Use file-todos for detailed documentation and TaskList for execution tracking with `/workflows:work` integration. </critical_requirement>

#### Step 1: Synthesize All Findings

<thinking>
Consolidate all agent reports into a categorized list of findings.
Remove duplicates, prioritize by severity and impact.
</thinking>

<synthesis_tasks>

- [ ] Collect findings from all parallel agents
- [ ] Categorize by type: security, performance, architecture, quality, etc.
- [ ] Assign severity levels: 🔴 CRITICAL (P1), 🟡 IMPORTANT (P2), 🔵 NICE-TO-HAVE (P3)
- [ ] Remove duplicate or overlapping findings
- [ ] Estimate effort for each finding (Small/Medium/Large)

</synthesis_tasks>

#### Step 2: Create Todo Files Using file-todos Skill

<critical_instruction> Use the file-todos skill to create todo files for ALL findings immediately. Do NOT present findings one-by-one asking for user approval. Create all todo files in parallel using the skill, then summarize results to user. </critical_instruction>
**Implementation Options:**

**Option A: Direct File Creation (Fast)**

- Create todo files directly using Write tool
- All findings in parallel for speed
- Use standard template from `.claude/skills/file-todos/assets/todo-template.md`
- Follow naming convention: `{issue_id}-pending-{priority}-{description}.md`

**Option B: Sub-Agents in Parallel (Recommended for Scale)** For large PRs with 15+ findings, use sub-agents to create finding files in parallel:

```bash
# Launch multiple finding-creator agents in parallel
Task() - Create todos for first finding
Task() - Create todos for second finding
Task() - Create todos for third finding
etc. for each finding.
```

Sub-agents can:

- Process multiple findings simultaneously
- Write detailed todo files with all sections filled
- Organize findings by severity
- Create comprehensive Proposed Solutions
- Add acceptance criteria and work logs
- Complete much faster than sequential processing

**Execution Strategy:**

1. Synthesize all findings into categories (P1/P2/P3)
2. Group findings by severity
3. Launch 3 parallel sub-agents (one per severity level)
4. Each sub-agent creates its batch of todos using the file-todos skill
5. Consolidate results and present summary

**Process (Using file-todos Skill):**

1. For each finding:

   - Determine severity (P1/P2/P3)
   - Write detailed Problem Statement and Findings
   - Create 2-3 Proposed Solutions with pros/cons/effort/risk
   - Estimate effort (Small/Medium/Large)
   - Add acceptance criteria and work log

2. Use file-todos skill for structured todo management:

   ```bash
   skill: file-todos
   ```

   The skill provides:

   - Template location: `.claude/skills/file-todos/assets/todo-template.md`
   - Naming convention: `{issue_id}-{status}-{priority}-{description}.md`
   - YAML frontmatter structure: status, priority, issue_id, tags, dependencies
   - All required sections: Problem Statement, Findings, Solutions, etc.

3. Create todo files in parallel:

   ```bash
   {next_id}-pending-{priority}-{description}.md
   ```

4. Examples:

   ```
   001-pending-p1-path-traversal-vulnerability.md
   002-pending-p1-api-response-validation.md
   003-pending-p2-concurrency-limit.md
   004-pending-p3-unused-parameter.md
   ```

5. Follow template structure from file-todos skill: `.claude/skills/file-todos/assets/todo-template.md`

**Todo File Structure (from template):**

Each todo must include:

- **YAML frontmatter**: status, priority, issue_id, tags, dependencies
- **Problem Statement**: What's broken/missing, why it matters
- **Findings**: Discoveries from agents with evidence/location
- **Proposed Solutions**: 2-3 options, each with pros/cons/effort/risk
- **Recommended Action**: (Filled during triage, leave blank initially)
- **Technical Details**: Affected files, components, database changes
- **Acceptance Criteria**: Testable checklist items
- **Work Log**: Dated record with actions and learnings
- **Resources**: Links to PR, issues, documentation, similar patterns

**File naming convention:**

```
{issue_id}-{status}-{priority}-{description}.md

Examples:
- 001-pending-p1-security-vulnerability.md
- 002-pending-p2-performance-optimization.md
- 003-pending-p3-code-cleanup.md
```

**Status values:**

- `pending` - New findings, needs triage/decision
- `ready` - Approved by manager, ready to work
- `complete` - Work finished

**Priority values:**

- `p1` - Critical (blocks merge, security/data issues)
- `p2` - Important (should fix, architectural/performance)
- `p3` - Nice-to-have (enhancements, cleanup)

**Tagging:** Always add `code-review` tag, plus: `security`, `performance`, `architecture`, `python`, `quality`, etc.

#### Step 2.5: Create TaskList for Execution Tracking

After creating file-todos for documentation, create a TaskList for execution tracking. This enables `/workflows:work` integration and cross-session coordination.

**Why both file-todos AND TaskList?**
- **file-todos**: Detailed documentation (Problem Statement, Solutions, Work Log) - committed to repo
- **TaskList**: Execution tracking with dependencies and status - enables `/workflows:work`

**Create tasks from findings:**

```
# For each finding, create a task linking to its todo file
TaskCreate:
  subject: "Fix [finding description]"
  description: "Address [brief description]. See todos/[todo-filename].md for full context."
  activeForm: "Fixing [finding description]"
```

**Set up dependencies based on priority:**

```
# P1 findings should be completed first
# P2/P3 findings can be blocked by related P1 work

TaskUpdate: #[p2_task] addBlockedBy [#related_p1_task]
```

**Get TaskList ID for cross-session work:**

```bash
task_list_id=$(ls -t ~/.claude/tasks/ | head -1)
echo "TaskList ID: $task_list_id"
```

**Include in summary for `/workflows:work` integration.**

See `tasklist-conventions` skill for detailed patterns.

#### Step 3: Summary Report

After creating all todo files, present comprehensive summary:

```markdown
## ✅ Code Review Complete

**Review Target:** PR #XXXX - [PR Title] **Branch:** [branch-name]

### Findings Summary:

- **Total Findings:** [X]
- **🔴 CRITICAL (P1):** [count] - BLOCKS MERGE
- **🟡 IMPORTANT (P2):** [count] - Should Fix
- **🔵 NICE-TO-HAVE (P3):** [count] - Enhancements

### Created Todo Files:

**P1 - Critical (BLOCKS MERGE):**

- `001-pending-p1-{finding}.md` - {description}
- `002-pending-p1-{finding}.md` - {description}

**P2 - Important:**

- `003-pending-p2-{finding}.md` - {description}
- `004-pending-p2-{finding}.md` - {description}

**P3 - Nice-to-Have:**

- `005-pending-p3-{finding}.md` - {description}

### TaskList for Execution:

**TaskList ID:** `[task_list_id]`

Tasks created: [count]
- #1: Fix [P1 finding] (blocked by: none)
- #2: Fix [P1 finding] (blocked by: none)
- #3: Resolve [P2 finding] (blocked by: #1, #2)
- ...

**To work on findings:**
```bash
# In this session
/workflows:work

# In another session
skill: import-tasks [task_list_id]
```

### Review Agents Used:

**Core:**
- code-simplicity-reviewer
- security-sentinel
- performance-oracle
- architecture-strategist
- pattern-recognition-specialist
- agent-native-reviewer
- baseline-code-reviewer
- slop-detector

**Deep Quality (if run):**
- coherence-reviewer
- drift-reviewer

**Conditional (if applicable):**
- data-migration-expert (migrations)
- refactor-analyst-agent (refactors)
- bug-reproduction-validator (bug fixes)

**Second Opinion (if run):**
- gemini-reviewer

**Language-Specific:**
- [language-specific agents used]

### Next Steps:

1. **Address P1 Findings**: CRITICAL - must be fixed before merge

   - Review each P1 todo in detail
   - Implement fixes or request exemption
   - Verify fixes before merging PR

2. **Execute via TaskList** (Recommended):
   ```bash
   # Work through tasks with progress tracking
   /workflows:work

   # Or in another session, import tasks first
   skill: import-tasks [task_list_id]
   ```

3. **Triage All Todos** (Optional):
   ```bash
   ls todos/*-pending-*.md  # View all pending todos
   /triage                  # Use slash command for interactive triage
   ```

4. **Work on Approved Todos**:

   ```bash
   /resolve_todo_parallel  # Fix all approved items efficiently
   ```

5. **Track Progress**:
   - TaskList: Use `TaskList` to see status, `TaskUpdate` to mark complete
   - file-todos: Rename file when status changes: pending → ready → complete
   - Update Work Log as you work
   - Commit todos: `git add todos/ && git commit -m "refactor: add code review findings"`

### Severity Breakdown:

**🔴 P1 (Critical - Blocks Merge):**

- Security vulnerabilities
- Data corruption risks
- Breaking changes
- Critical architectural issues

**🟡 P2 (Important - Should Fix):**

- Performance issues
- Significant architectural concerns
- Major code quality problems
- Reliability issues

**🔵 P3 (Nice-to-Have):**

- Minor improvements
- Code cleanup
- Optimization opportunities
- Documentation updates

```

### Important: P1 Findings Block Merge

Any **🔴 P1 (CRITICAL)** findings must be addressed before merging the PR. Present these prominently and ensure they're resolved before accepting the PR.
