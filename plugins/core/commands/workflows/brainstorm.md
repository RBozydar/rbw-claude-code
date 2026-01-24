---
name: workflows:brainstorm
description: Explore requirements and approaches through collaborative dialogue before planning implementation
argument-hint: "[feature idea or problem to explore]"
---

# Brainstorm a Feature or Improvement

**Note: The current year is 2026.** Use this when dating brainstorm documents.

Brainstorming helps answer **WHAT** to build through collaborative dialogue. It precedes `/workflows:plan`, which answers **HOW** to build it.

**Process knowledge:** Load the `brainstorming` skill for detailed question techniques, approach exploration patterns, and YAGNI principles.

## Feature Description

<feature_description> #$ARGUMENTS </feature_description>

**If the feature description above is empty, ask the user:** "What would you like to explore? Please describe the feature, problem, or improvement you're thinking about."

Do not proceed until you have a feature description from the user.

## Execution Flow

### Phase 0: Assess Requirements Clarity

Evaluate whether brainstorming is needed based on the feature description.

**Clear requirements indicators:**
- Specific acceptance criteria provided
- Referenced existing patterns to follow
- Described exact expected behavior
- Constrained, well-defined scope

**If requirements are already clear:**
Use **AskUserQuestion tool** to suggest: "Your requirements seem detailed enough to proceed directly to planning. Should I run `/workflows:plan` instead, or would you like to explore the idea further?"

### Phase 0.5: Problem Analysis (When Applicable)

If the feature description is a **problem statement** (contains words like "broken", "failing", "doesn't work", "bug", "issue"):

Run problem-analysis-agent to identify root cause:
- Task problem-analysis-agent("Analyze: <feature_description>")

Use the validated root cause to inform the rest of brainstorming. This ensures we solve the RIGHT problem.

### Phase 1: Understand the Idea

#### 1.1 Contextual Research (Parallel)

Run these research agents in parallel using TaskList:

1. **Always run:**
   - Task repo-research-analyst("Existing patterns for: <topic>")
   - Task learnings-researcher("Past solutions involving: <domain>")

2. **Run conditionally:**
   - Task framework-docs-researcher("<library>") - When feature involves specific frameworks
   - Task best-practices-researcher("<capability> best practices") - When entering unfamiliar domain

Create TaskList entries for parallel execution:
- TaskCreate for each research agent
- Execute in parallel, collect results
- Synthesize findings before proceeding to dialogue

#### 1.2 Collaborative Dialogue

Use the **AskUserQuestion tool** to ask questions **one at a time**.

**Guidelines (see `brainstorming` skill for detailed techniques):**
- Prefer multiple choice when natural options exist
- Start broad (purpose, users) then narrow (constraints, edge cases)
- Validate assumptions explicitly
- Ask about success criteria

**Exit condition:** Continue until the idea is clear OR user says "proceed"

### Phase 2: Explore Approaches

#### 2.1 Domain-Specific Analysis

Based on the feature domain, invoke the appropriate specialist agent:

| Domain Signal | Agent to Invoke |
|---------------|-----------------|
| API, endpoints, REST, GraphQL | Task api-design-brainstormer |
| Schema, database, models, tables | Task data-model-brainstormer |
| State, cache, sync, real-time | Task state-management-brainstormer |
| Auth, security, permissions, RBAC | Task security-brainstormer |

Run the relevant domain agent before proposing approaches.

#### 2.2 Alternative Perspectives (Required)

Always get external perspectives to avoid blind spots. Run in parallel:

1. **Gemini Perspective:**
   - Task gemini-brainstorm("Evaluate approaches for: <feature_description>")
   - Surfaces options from a different LLM's reasoning

2. **Devil's Advocate:**
   - Task devils-advocate-brainstormer("Challenge: <emerging_approach>")
   - Actively seeks flaws, risks, and overlooked alternatives

Both perspectives are required. Different models and contrarian framing catch blind spots that a single perspective misses.

#### 2.3 Approach Synthesis

Combine insights from:
- Phase 1 research
- Domain agent recommendations
- Gemini alternative perspectives
- Devil's advocate challenges

Propose **2-3 concrete approaches** based on research and conversation.

For each approach, provide:
- Brief description (2-3 sentences)
- Pros and cons
- When it's best suited

Lead with your recommendation and explain why. Apply YAGNI—prefer simpler solutions.

Use **AskUserQuestion tool** to ask which approach the user prefers.

### Phase 2.5: Deep Analysis (Complex Features Only)

For features with multiple viable approaches or significant trade-offs:

1. **Solution Design Exploration:**
   - Task solution-design-agent("Generate diverse solutions for: <chosen_direction>")
   - Explores 7 reasoning perspectives to avoid anchoring

2. **Deep Thinking (If Still Unclear):**
   - Task deepthink-agent("Analyze trade-offs: <options>")
   - Structured multi-step reasoning for complex decisions

Skip this phase for straightforward features.

### Phase 3: Capture the Design

Write a brainstorm document to `docs/brainstorms/YYYY-MM-DD-<topic>-brainstorm.md`.

Ensure `docs/brainstorms/` directory exists before writing.

**Document template:**

```markdown
---
date: YYYY-MM-DD
topic: <kebab-case-topic>
domain: [api|data-model|state-management|security|general]
agents-used: [list of agents invoked]
---

# <Topic Title>

## What We're Building
[Concise description—1-2 paragraphs max]

## Success Criteria
- [How we'll know this works - maps to test cases]
- [Measurable outcomes]

## Constraints
- [Technical limitations]
- [Timeline constraints]
- [Scope boundaries]

## Dependencies
- [External systems]
- [Libraries/frameworks]
- [Existing code that must be understood]

## Why This Approach
[Brief explanation of approaches considered and why this one was chosen]

## Key Decisions
- [Decision 1]: [Rationale]
- [Decision 2]: [Rationale]

## Alternative Perspectives
[Insights from Gemini or domain agents that influenced the decision]

## Open Questions
- [Any unresolved questions for the planning phase]

## Next Steps
→ `/workflows:plan` for implementation details
```

### Phase 4: Handoff

Use **AskUserQuestion tool** to present next steps:

**Question:** "Brainstorm captured. What would you like to do next?"

**Options:**
1. **Proceed to planning** - Run `/workflows:plan` (will auto-detect this brainstorm)
2. **Refine design further** - Continue exploring
3. **Done for now** - Return later

## Parallel Execution with TaskList

This workflow uses TaskList for efficient parallel processing:

### Research Phase (1.1)
```
TaskCreate("Research: repo patterns", ...)
TaskCreate("Research: past learnings", ...)
TaskCreate("Research: best practices", ...)  # conditional
```
Execute all research in parallel, wait for completion.

### Perspective Phase (2.2)
```
TaskCreate("Perspective: Gemini analysis", ...)
TaskCreate("Perspective: Devil's advocate", ...)
```
Run both perspective agents in parallel after domain analysis.

### When to Parallelize
- Multiple independent research agents
- Gemini + Devil's Advocate perspectives
- Never parallelize: user questions (must be sequential)

## Output Summary

When complete, display:

```
Brainstorm complete!

Document: docs/brainstorms/YYYY-MM-DD-<topic>-brainstorm.md

Key decisions:
- [Decision 1]
- [Decision 2]

Agents used: [list]

Next: Run `/workflows:plan` when ready to implement.
```

## Important Guidelines

- **Stay focused on WHAT, not HOW** - Implementation details belong in the plan
- **Ask one question at a time** - Don't overwhelm
- **Apply YAGNI** - Prefer simpler approaches
- **Keep outputs concise** - 200-300 words per section max
- **Use parallel agents** - Run independent research in parallel via TaskList
- **Match domain agents** - Invoke specialist agents based on feature domain
- **Always get alternative perspectives** - Run both Gemini and Devil's Advocate agents
- **Run problem-analysis first** - For problem statements, identify root cause before brainstorming solutions

NEVER CODE! Just explore and document decisions.
