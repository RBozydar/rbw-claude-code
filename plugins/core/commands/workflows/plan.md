---
name: workflows:plan
description: Transform feature descriptions into well-structured project plans following conventions
argument-hint: "[feature description, bug report, or improvement idea]"
---

# Create a plan for a new feature or bug fix

## Introduction

**Note: The current year is 2026.** Use this when dating plans and searching for recent documentation.

Transform feature descriptions, bug reports, or improvement ideas into well-structured markdown files issues that follow project conventions and best practices. This command provides flexible detail levels to match your needs.

## Feature Description

<feature_description> #$ARGUMENTS </feature_description>

**If the feature description above is empty, ask the user:** "What would you like to plan? Please describe the feature, bug fix, or improvement you have in mind."

Do not proceed until you have a clear feature description from the user.

## Main Tasks

### 0. Idea Refinement

**Check for brainstorm output first:**

Before asking questions, look for recent brainstorm documents in `docs/brainstorms/` that match this feature:

```bash
ls -la docs/brainstorms/*.md 2>/dev/null | head -10
```

**Relevance criteria:** A brainstorm is relevant if:
- The topic (from filename or YAML frontmatter) semantically matches the feature description
- Created within the last 14 days
- If multiple candidates match, use the most recent one

**If a relevant brainstorm exists:**
1. Read the brainstorm document
2. Announce: "Found brainstorm from [date]: [topic]. Using as context for planning."
3. Extract key decisions, chosen approach, and open questions
4. **Skip the idea refinement questions below** - the brainstorm already answered WHAT to build
5. Use brainstorm decisions as input to the research phase

**If multiple brainstorms could match:**
Use **AskUserQuestion tool** to ask which brainstorm to use, or whether to proceed without one.

**If no brainstorm found (or not relevant), run idea refinement:**

Refine the idea through collaborative dialogue using the **AskUserQuestion tool**:

- Ask questions one at a time to understand the idea fully
- Prefer multiple choice questions when natural options exist
- Focus on understanding: purpose, constraints and success criteria
- Continue until the idea is clear OR user says "proceed"

**Get alternative perspectives:**

Run gemini-brainstorm in parallel during refinement to get architectural perspectives from a different LLM:

- Task gemini-brainstorm(feature_description) - Alternative architectural perspectives

**Gather signals for research decision.** During refinement, note:

- **User's familiarity**: Do they know the codebase patterns? Are they pointing to examples?
- **User's intent**: Speed vs thoroughness? Exploration vs execution?
- **Topic risk**: Security, payments, external APIs warrant more caution
- **Uncertainty level**: Is the approach clear or open-ended?

**Skip option:** If the feature description is already detailed, offer:
"Your description is clear. Should I proceed with research, or would you like to refine it further?"

### 1. Local Research (Always Runs - Parallel)

<thinking>
First, I need to understand the project's conventions, existing patterns, and any documented learnings. This is fast and local - it informs whether external research is needed.
</thinking>

Run these agents **in parallel** to gather local context:

- Task repo-research-analyst(feature_description)
- Task learnings-researcher(feature_description)

**What to look for:**
- **Repo research:** existing patterns, CLAUDE.md guidance, technology familiarity, pattern consistency
- **Learnings:** documented solutions in `docs/solutions/` that might apply (gotchas, patterns, lessons learned)

**Reference Collection:**

- [ ] Document all research findings with specific file paths (e.g., `app/services/example_service.rb:42`)
- [ ] **Include relevant institutional learnings** from `docs/solutions/` (key insights, gotchas to avoid)
- [ ] Create a reference list of similar issues or PRs (e.g., `#123`, `#456`)
- [ ] Note any team conventions discovered in `CLAUDE.md` or team documentation

These findings inform the next step.

### 1.5. Research Decision

Based on signals from Step 0 and findings from Step 1, decide whether external research is needed.

**High-risk topics → always research.** Security, payments, external APIs, data privacy. The cost of missing something is too high. This takes precedence over speed signals.

**Strong local context → skip external research.** Codebase has good patterns, CLAUDE.md has guidance, user knows what they want. External research adds little value.

**Uncertainty or unfamiliar territory → research.** User is exploring, codebase has no examples, new technology. External perspective is valuable.

**Get explicit user confirmation using AskUserQuestion tool:**

Present the research decision with options:
- **Option 1: Skip external research** - "Local context is strong, proceed to planning"
- **Option 2: Run external research** - "Research best practices and framework docs first"
- **Option 3: Research specific topic** - "Research only [specific area]"

Examples of what to present:
- "Your codebase has solid patterns for this. Skip external research and proceed to planning?"
- "This involves payment processing. I recommend researching current best practices first. Proceed with research?"

**Do not proceed until user confirms.**

### 1.5b. External Research (Conditional)

**Only run if user selected external research in Step 1.5.**

Run these agents in parallel:

- Task best-practices-researcher(feature_description)
- Task framework-docs-researcher(feature_description)

### 1.6. Consolidate Research

After all research steps complete, consolidate findings:

- Document relevant file paths from repo research (e.g., `app/services/example_service.rb:42`)
- **Include relevant institutional learnings** from `docs/solutions/` (key insights, gotchas to avoid)
- Note external documentation URLs and best practices (if external research was done)
- List related issues or PRs discovered
- Capture CLAUDE.md conventions

**Optional validation:** Briefly summarize findings and ask if anything looks off or missing before proceeding to planning.

### 2. Deep Analysis (For Complex Issues)

<thinking>
For complex problems, bugs, or refactoring tasks, run specialized analysis agents before planning.
</thinking>

**When to use these agents:**
- Bug reports or unexpected behavior → `problem-analysis-agent`
- Multiple valid approaches exist → `solution-design-agent`
- Refactoring or technical debt cleanup → `refactor-analyst-agent`
- Open-ended analytical questions (taxonomy, trade-offs, definitions) → `deepthink-agent`

**Problem Analysis (for bugs/issues):**

If the feature is actually a bug or complex issue where the root cause is unclear:

- Task problem-analysis-agent(feature_description) - Identifies WHY the problem occurs (not how to fix it)

Output: Root cause statement with evidence, confidence assessment, ready for solution design.

**Solution Design (when multiple approaches exist):**

If multiple valid solutions exist and choosing wrong has real cost:

- Task solution-design-agent(problem_statement_or_root_cause) - Generates diverse solutions from 7 perspectives

Output: Ranked solutions with trade-offs, failure conditions, and recommendation.

**Refactoring Analysis (for cleanup/refactor):**

If the plan involves refactoring or technical debt:

- Task refactor-analyst-agent(scope_description) - 11-dimension analysis of existing code

Output: Tiered recommendations (Critical/Recommended/Consider) with evidence.

**Deep Thinking (for open-ended analytical questions):**

If the feature requires answering questions like "What's the right way to classify X?" or "How should we balance A vs B?":

- Task deepthink-agent(analytical_question) - Structured multi-step reasoning with verification

Output: Structured answer based on question type (taxonomy, trade-off, definitional, evaluative, exploratory).

### 3. Issue Planning & Structure

<thinking>
Think like a product manager - what would make this issue clear and actionable? Consider multiple perspectives
</thinking>

**Title & Categorization:**

- [ ] Draft clear, searchable issue title using conventional format (e.g., `feat: Add user authentication`, `fix: Cart total calculation`)
- [ ] Determine issue type: enhancement, bug, refactor
- [ ] Convert title to filename: add today's date prefix, strip prefix colon, kebab-case, add `-plan` suffix
  - Example: `feat: Add User Authentication` → `2026-01-21-feat-add-user-authentication-plan.md`
  - Keep it descriptive (3-5 words after prefix) so plans are findable by context

**Stakeholder Analysis:**

- [ ] Identify who will be affected by this issue (end users, developers, operations)
- [ ] Consider implementation complexity and required expertise

**Content Planning:**

- [ ] Choose appropriate detail level based on issue complexity and audience
- [ ] List all necessary sections for the chosen template
- [ ] Gather supporting materials (error logs, screenshots, design mockups)
- [ ] Prepare code examples or reproduction steps if applicable, name the mock filenames in the lists

### 4. SpecFlow Analysis

After planning the issue structure, run SpecFlow Analyzer to validate and refine the feature specification:

- Task spec-flow-analyzer(feature_description, research_findings)

**SpecFlow Analyzer Output:**

- [ ] Review SpecFlow analysis results
- [ ] Incorporate any identified gaps or edge cases into the issue
- [ ] Update acceptance criteria based on SpecFlow findings

### 5. Create TaskList

After SpecFlow analysis, create the executable TaskList that will drive implementation:

1. **Create tasks from acceptance criteria:**

   ```
   # Create a task for each major work item identified
   TaskCreate: "Implement [component/feature]" (activeForm: "Implementing...")
   TaskCreate: "Add tests for [component]" (activeForm: "Testing...")
   TaskCreate: "Update documentation" (activeForm: "Documenting...")
   ```

2. **Set up dependencies:**

   ```
   # Tests depend on implementation
   TaskUpdate: task #2 addBlockedBy [#1]
   # Docs depend on tests passing
   TaskUpdate: task #3 addBlockedBy [#2]
   ```

3. **Get the TaskList ID:**

   ```bash
   task_list_id=$(ls -t ~/.claude/tasks/ | head -1)
   echo "TaskList ID: $task_list_id"
   ```

4. **Include TaskList ID in plan file** (see Output Format below)

**Task creation guidelines:**
- One task per logical unit of work (model, service, component, test suite)
- Include clear `activeForm` for progress visibility
- Set dependencies to prevent race conditions
- Keep tasks specific and completable in a single focused session

### 6. Choose Implementation Detail Level

Select how comprehensive you want the issue to be, simpler is mostly better.

#### 📄 MINIMAL (Quick Issue)

**Best for:** Simple bugs, small improvements, clear features

**Includes:**

- Problem statement or feature description
- Basic acceptance criteria
- Essential context only

**Structure:**

````markdown
---
title: [Issue Title]
type: [feat|fix|refactor]
date: YYYY-MM-DD
---

# [Issue Title]

[Brief problem/feature description]

## Acceptance Criteria

- [ ] Core requirement 1
- [ ] Core requirement 2

## Context

[Any critical information]

## MVP

### test.rb

```ruby
class Test
  def initialize
    @name = "test"
  end
end
```

## Code Changes (Unified Diff Format)

For non-trivial code changes, use unified diff format to specify exact locations:

```diff
--- a/path/to/file.py
+++ b/path/to/file.py
@@ -123,6 +123,15 @@ def existing_function(ctx):
   # Context lines (unchanged) serve as location anchors
   existing_code()

+  # WHY: Guard against race condition when messages arrive out-of-order
+  new_code()

   # More context to anchor the insertion point
   more_existing_code()
```

## References

- Related issue: #[issue_number]
- Documentation: [relevant_docs_url]

#### 📋 MORE (Standard Issue)

**Best for:** Most features, complex bugs, team collaboration

**Includes everything from MINIMAL plus:**

- Detailed background and motivation
- Technical considerations
- Success metrics
- Dependencies and risks
- Basic implementation suggestions

**Structure:**

```markdown
---
title: [Issue Title]
type: [feat|fix|refactor]
date: YYYY-MM-DD
---

# [Issue Title]

## Overview

[Comprehensive description]

## Problem Statement / Motivation

[Why this matters]

## Proposed Solution

[High-level approach]

## Technical Considerations

- Architecture impacts
- Performance implications
- Security considerations

## Acceptance Criteria

- [ ] Detailed requirement 1
- [ ] Detailed requirement 2
- [ ] Testing requirements

## Success Metrics

[How we measure success]

## Dependencies & Risks

[What could block or complicate this]

## References & Research

- Similar implementations: [file_path:line_number]
- Best practices: [documentation_url]
- Related PRs: #[pr_number]
```

#### 📚 A LOT (Comprehensive Issue)

**Best for:** Major features, architectural changes, complex integrations

**Includes everything from MORE plus:**

- Detailed implementation plan with phases
- Alternative approaches considered
- Extensive technical specifications
- Resource requirements and timeline
- Future considerations and extensibility
- Risk mitigation strategies
- Documentation requirements

**Structure:**

```markdown
---
title: [Issue Title]
type: [feat|fix|refactor]
date: YYYY-MM-DD
---

# [Issue Title]

## Overview

[Executive summary]

## Problem Statement

[Detailed problem analysis]

## Proposed Solution

[Comprehensive solution design]

## Technical Approach

### Architecture

[Detailed technical design]

### Implementation Phases

#### Phase 1: [Foundation]

- Tasks and deliverables
- Success criteria
- Estimated effort

#### Phase 2: [Core Implementation]

- Tasks and deliverables
- Success criteria
- Estimated effort

#### Phase 3: [Polish & Optimization]

- Tasks and deliverables
- Success criteria
- Estimated effort

## Alternative Approaches Considered

[Other solutions evaluated and why rejected]

## Acceptance Criteria

### Functional Requirements

- [ ] Detailed functional criteria

### Non-Functional Requirements

- [ ] Performance targets
- [ ] Security requirements
- [ ] Accessibility standards

### Quality Gates

- [ ] Test coverage requirements
- [ ] Documentation completeness
- [ ] Code review approval

## Success Metrics

[Detailed KPIs and measurement methods]

## Dependencies & Prerequisites

[Detailed dependency analysis]

## Risk Analysis & Mitigation

[Comprehensive risk assessment]

## Resource Requirements

[Team, time, infrastructure needs]

## Future Considerations

[Extensibility and long-term vision]

## Documentation Plan

[What docs need updating]

## References & Research

### Internal References

- Architecture decisions: [file_path:line_number]
- Similar features: [file_path:line_number]
- Configuration: [file_path:line_number]

### External References

- Framework documentation: [url]
- Best practices guide: [url]
- Industry standards: [url]

### Related Work

- Previous PRs: #[pr_numbers]
- Related issues: #[issue_numbers]
- Design documents: [links]
```

### 7. Issue Creation & Formatting

<thinking>
Apply best practices for clarity and actionability, making the issue easy to scan and understand
</thinking>

**Content Formatting:**

- [ ] Use clear, descriptive headings with proper hierarchy (##, ###)
- [ ] Include code examples in triple backticks with language syntax highlighting
- [ ] Add screenshots/mockups if UI-related (drag & drop or use image hosting)
- [ ] Use task lists (- [ ]) for trackable items that can be checked off
- [ ] Add collapsible sections for lengthy logs or optional details using `<details>` tags
- [ ] Apply appropriate emoji for visual scanning (🐛 bug, ✨ feature, 📚 docs, ♻️ refactor)

**Cross-Referencing:**

- [ ] Link to related issues/PRs using #number format
- [ ] Reference specific commits with SHA hashes when relevant
- [ ] Link to code using GitHub's permalink feature (press 'y' for permanent link)
- [ ] Mention relevant team members with @username if needed
- [ ] Add links to external resources with descriptive text

**Code & Examples:**

```markdown
# Good example with syntax highlighting and line references
```

```ruby
# app/services/user_service.rb:42
def process_user(user)

# Implementation here

end
```
````

# Collapsible error logs

<details>
<summary>Full error stacktrace</summary>

`Error details here...`

</details>

**AI-Era Considerations:**

- [ ] Account for accelerated development with AI pair programming
- [ ] Include prompts or instructions that worked well during research
- [ ] Note which AI tools were used for initial exploration (Claude, Copilot, etc.)
- [ ] Emphasize comprehensive testing given rapid implementation
- [ ] Document any AI-generated code that needs human review

### 8. Final Review & Submission

**Pre-submission Checklist:**

- [ ] Title is searchable and descriptive
- [ ] Labels accurately categorize the issue
- [ ] All template sections are complete
- [ ] Links and references are working
- [ ] Acceptance criteria are measurable
- [ ] Add names of files in pseudo code examples and todo lists
- [ ] Add an ERD mermaid diagram if applicable for new model changes

## Output Format

**Filename:** Use the date and kebab-case filename from Step 2 Title & Categorization.

```
docs/plans/YYYY-MM-DD-<type>-<descriptive-name>-plan.md
```
Examples:
- ✅ `docs/plans/2026-01-15-feat-user-authentication-flow-plan.md`
- ✅ `docs/plans/2026-02-03-fix-checkout-race-condition-plan.md`
- ✅ `docs/plans/2026-03-10-refactor-api-client-extraction-plan.md`
- ❌ `docs/plans/2026-01-15-feat-thing-plan.md` (not descriptive - what "thing"?)
- ❌ `docs/plans/2026-01-15-feat-new-feature-plan.md` (too vague - what feature?)
- ❌ `docs/plans/2026-01-15-feat: user auth-plan.md` (invalid characters - colon and space)
- ❌ `docs/plans/feat-user-auth-plan.md` (missing date prefix)

Write the plan to filename from Step 2 Title & Categorization with YAML frontmatter containing the TaskList ID:

```markdown
---
title: [Issue Title]
type: [feat|fix|refactor]
date: YYYY-MM-DD
task_list_id: [UUID from Step 5]
---

[Plan content...]
```

**TaskList section to include in plan:**

```markdown
## Tasks

Run `/workflows:work` with this plan to execute. Tasks are stored in `~/.claude/tasks/[task_list_id]/`.

To work on these tasks from another session:
```
skill: import-tasks [task_list_id]
```
```

## Post-Generation Options

After writing the plan file, use the **AskUserQuestion tool** to present these options:

**Question:** "Plan ready at `docs/plans/YYYY-MM-DD-<type>-<name>-plan.md`. What would you like to do next?"

**Options:**
1. **Open plan in editor** - Open the plan file for review
2. **Run `/deepen-plan`** - Enhance each section with parallel research agents (best practices, performance, edge cases)
3. **Run `/plan_review`** - Get feedback from reviewers (Kieran, Simplicity, etc.)
4. **Start `/workflows:work`** - Begin implementing this plan locally
5. **Start `/workflows:work` on remote** - Begin implementing in Claude Code on the web (use `&` to run in background)
6. **Parallel execution with subagents** - Spawn multiple agents to work on tasks in parallel
7. **Create Issue** - Create issue in project tracker (GitHub/Linear)
8. **Simplify** - Reduce detail level

Based on selection:
- **Open plan in editor** → Run `open docs/plans/<plan_filename>.md` to open the file in the user's default editor
- **`/deepen-plan`** → Call the /deepen-plan command with the plan file path to enhance with research
- **`/plan_review`** → Call the /plan_review command with the plan file path
- **`/workflows:work`** → Call the /workflows:work command with the plan file path
- **`/workflows:work` on remote** → Run `/workflows:work docs/plans/<plan_filename>.md &` to start work in background for Claude Code web
- **Parallel execution with subagents** → Spawn subagents with the TaskList ID:
  ```
  # For Python projects
  Task(python-coder): "Import tasks from [task_list_id] and work on tasks #1-3"

  # For other projects
  Task(general-purpose): "Import tasks from [task_list_id] and work on tasks #4-6"
  ```
- **Create Issue** → See "Issue Creation" section below
- **Simplify** → Ask "What should I simplify?" then regenerate simpler version
- **Other** (automatically provided) → Accept free text for rework or specific changes

Loop back to options after Simplify or Other changes until user selects `/workflows:work` or `/plan_review`.

## Issue Creation

When user selects "Create Issue", detect their project tracker from CLAUDE.md:

1. **Check for tracker preference** in user's CLAUDE.md (global or project):
   - Look for `project_tracker: github` or `project_tracker: linear`
   - Or look for mentions of "GitHub Issues" or "Linear" in their workflow section

2. **If GitHub:**
   ```bash
   # Extract title from plan filename (kebab-case to Title Case)
   # Read plan content for body
   gh issue create --title "feat: [Plan Title]" --body-file docs/plans/<plan_filename>.md
   ```

3. **If no tracker configured:**
   Ask user: "Which project tracker do you use? (GitHub/Linear/Other)"
   - Suggest adding `project_tracker: github` or `project_tracker: linear` to their CLAUDE.md

4. **After creation:**
   - Display the issue URL
   - Ask if they want to proceed to `/workflows:work` or `/plan_review`

NEVER CODE! Just research and write the plan.

---

## Appendix: Unified Diff Format for Code Changes

When the plan includes code changes, use unified diff format for precise specification.

### When to Use Diff Format

| Code Characteristic | Use Diff? | Reason |
| --- | --- | --- |
| Conditionals, loops, error handling | YES | Has branching logic |
| Multiple insertions same file | YES | >1 change location |
| Deletions or replacements | YES | Removing/changing existing code |
| Pure assignment/return (CRUD) | NO | Single statement, no branching |
| Boilerplate from template | NO | Developer can generate from pattern |

**Boundary test**: "Does developer need to see exact placement and context to implement correctly?"

### Diff Components

| Component | Authority | Purpose |
| --- | --- | --- |
| File path (`--- a/path/to/file.py`) | AUTHORITATIVE | Exact target file |
| Line numbers (`@@ -123,6 +123,15 @@`) | APPROXIMATE | May drift with earlier changes |
| Function context (`@@ ... @@ def func():`) | SCOPE HINT | Function containing the change |
| Context lines (unchanged) | AUTHORITATIVE ANCHORS | Match patterns to locate insertion |
| `+` lines | NEW CODE | Code to add, with WHY comments |
| `-` lines | REMOVED CODE | Code to delete |

### Comment Rules in Diffs

Comments in `+` lines explain **WHY**, not **WHAT**:

```diff
# CORRECT - explains WHY
+  # Polling chosen over webhooks: 30% webhook delivery failures observed
+  updates = poll_api(interval=30)

# INCORRECT - restates WHAT the code does
+  # Poll the API every 30 seconds
+  updates = poll_api(interval=30)
```

### Avoid Temporal Contamination

Comments must pass the "timeless present" test - no change-relative language:

| Contaminated | Clean |
| --- | --- |
| "Added mutex to fix race" | "Mutex serializes concurrent access" |
| "Changed to use batch API" | "Batch API reduces round-trips from N to 1" |
| "Unlike the old approach" | "Thread-safe: each goroutine gets independent state" |

### Location Directives: Forbidden

The diff structure handles location. Never put location directives in comments:

```diff
# WRONG - location directive in comment
+  # Insert this BEFORE the retry loop (line 716)
+  timestamp_guard()

# CORRECT - diff structure provides location
@@ -714,6 +714,10 @@ def put(self, ctx, tags):
   for tag in tags:
       subject = tag.subject

+      # Timestamp guard: prevent older data from overwriting newer
+      timestamp_guard()

       # Retry loop for Put operations
       for attempt in range(max_retries):
```

### Validation Checklist

Before finalizing code changes in a plan:
- [ ] File path is exact (not "auth files" but `src/auth/handler.py`)
- [ ] Context lines exist in target file (patterns match actual code)
- [ ] Comments explain WHY, not WHAT
- [ ] No location directives in comments
- [ ] No hidden baselines ("[adjective] compared to what?")
- [ ] 2-3 context lines for reliable anchoring
