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

**Deep Code Quality Reviewers (run for thorough reviews):**
7. Task baseline-code-reviewer(PR content) - 17 atomic code smell categories
8. Task coherence-reviewer(PR content) - Repetition, naming consistency, zombie code
9. Task drift-reviewer(PR content) - Module structure, cross-file comprehension, abstraction opportunities

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
- Task ml-expert-reviewer(PR content) - If ML/DS/LLM code detected (notebooks, model code, prompts)

**Detection for ML/DS code:**
- `*.ipynb` files present
- Imports of: torch, tensorflow, sklearn, pandas, numpy, transformers, openai, anthropic
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

</conditional_agents>

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

### 5. Findings Synthesis and Todo Creation Using file-todos Skill

<critical_requirement> ALL findings MUST be stored in the todos/ directory using the file-todos skill. Create todo files immediately after synthesis - do NOT present findings for user approval first. Use the skill for structured todo management. </critical_requirement>

#### Step 1: Synthesize All Findings

<thinking>
Consolidate all agent reports into a categorized list of findings.
Remove duplicates, prioritize by severity and impact.
</thinking>

<synthesis_tasks>

- [ ] Collect findings from all parallel agents
- [ ] Categorize by type: security, performance, architecture, quality, etc.
- [ ] Assign severity levels: P1 CRITICAL, P2 IMPORTANT, P3 NICE-TO-HAVE
- [ ] Remove duplicate or overlapping findings
- [ ] Estimate effort for each finding (Small/Medium/Large)

</synthesis_tasks>

#### Step 2: Create Todo Files Using file-todos Skill

<critical_instruction> Use the file-todos skill to create todo files for ALL findings immediately. Do NOT present findings one-by-one asking for user approval. Create all todo files in parallel using the skill, then summarize results to user. </critical_instruction>

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

#### Step 3: Summary Report

After creating all todo files, present comprehensive summary:

```markdown
## Code Review Complete

**Review Target:** PR #XXXX - [PR Title] **Branch:** [branch-name]

### Findings Summary:

- **Total Findings:** [X]
- **P1 CRITICAL:** [count] - BLOCKS MERGE
- **P2 IMPORTANT:** [count] - Should Fix
- **P3 NICE-TO-HAVE:** [count] - Enhancements

### Created Todo Files:

**P1 - Critical (BLOCKS MERGE):**

- `001-pending-p1-{finding}.md` - {description}
- `002-pending-p1-{finding}.md` - {description}

**P2 - Important:**

- `003-pending-p2-{finding}.md` - {description}
- `004-pending-p2-{finding}.md` - {description}

**P3 - Nice-to-Have:**

- `005-pending-p3-{finding}.md` - {description}

### Review Agents Used:

**Core:**
- code-simplicity-reviewer
- security-sentinel
- performance-oracle
- architecture-strategist
- pattern-recognition-specialist
- agent-native-reviewer

**Deep Quality (if run):**
- baseline-code-reviewer
- coherence-reviewer
- drift-reviewer

**Language-Specific:**
- [language-specific agents used]

### Next Steps:

1. **Address P1 Findings**: CRITICAL - must be fixed before merge
2. **Triage All Todos**: `ls todos/*-pending-*.md` or `/triage`
3. **Work on Approved Todos**: `/resolve_todo_parallel`
```

### Important: P1 Findings Block Merge

Any **P1 (CRITICAL)** findings must be addressed before merging the PR. Present these prominently and ensure they're resolved before accepting the PR.
