# feat: Add Gemini Plan Reviewer to plan_review Command

**Date:** 2025-01-01
**Type:** Enhancement
**Status:** Draft

## Overview

Add a Gemini-based plan reviewer agent to the `/plan_review` command that provides alternative AI perspectives on plans and specifications, complementing Claude's review with a second opinion from Google Gemini.

## Problem Statement / Motivation

The current `/plan_review` command uses Claude-based agents (`@agent-code-simplicity-reviewer` and `@agent-architecture-strategist`) for reviewing plans. While effective, having a single AI perspective may miss issues that a different model would catch. Model diversity in code reviews (via `gemini-reviewer.md`) has already proven valuable for surfacing blind spots.

**Why this matters:**
- Different LLMs have different training data and reasoning patterns
- Gemini may catch architectural issues or ambiguities Claude misses
- Already proven pattern with `gemini-reviewer.md` and `gemini-brainstorm.md` in the codebase
- Provides users with higher confidence in plan quality through consensus validation

## Proposed Solution

Create a new agent `gemini-plan-reviewer.md` in `/plugins/python-backend/agents/external-llm/` that:
1. Uses the Gemini CLI to review plan/specification content
2. Is conditionally invoked by the `/plan_review` command when Gemini CLI is available
3. Follows established patterns from existing Gemini agents
4. Provides strategic feedback on plans, architecture, and specifications

### Agent Location Decision

**Chosen:** `/plugins/python-backend/agents/external-llm/gemini-plan-reviewer.md`

**Rationale:**
- Keeps all Gemini agents together (matches existing pattern)
- Cross-plugin dependency is acceptable (already happens with Python/ML agents in plan_review)
- Maintains separation of external LLM integrations in python-backend

## Technical Approach

### File Changes

#### 1. New File: `plugins/python-backend/agents/external-llm/gemini-plan-reviewer.md`

```markdown
---
name: gemini-plan-reviewer
description: Get alternative perspectives on plans and specifications from Google Gemini. Use when you want a second opinion from a different LLM on feature plans, architecture proposals, or project specifications.
tools: Bash, Read, Grep, Glob
---

# Gemini Plan Review Agent

You provide alternative AI perspectives on plans and specifications by invoking the Google Gemini CLI in sandbox mode.

## Purpose

- Offer a second opinion from a different LLM (Gemini) on plans and specifications
- Identify gaps, risks, or ambiguities Claude's review might miss
- Validate architectural decisions with diverse AI perspectives
- Surface blind spots in planning through model diversity

## Prerequisites

- Gemini CLI installed (`gemini --version` to verify)
- Google authentication configured

## Input

You receive:
- **Plan content:** A specification, feature plan, architecture proposal, or project plan
- **Model (optional):** Specific model to use (default: `gemini-3-pro-preview`)

### Available Models

| Model | Use Case | Cost |
|-------|----------|------|
| `gemini-3-flash-preview` | Fast plan reviews | Low |
| `gemini-3-pro-preview` | Latest Gemini 3 Pro | Medium |

Parse model from prompt if specified (e.g., "using flash, review..." or "model: gemini-3-pro-preview")

## Process

### 1. Gather Plan Context

First, read the plan content. If given a file path, read the file. Also gather relevant codebase context:
- Read CLAUDE.md for project conventions
- Identify relevant existing patterns in the codebase

### 2. Formulate the Gemini Prompt

Create a focused prompt that:
- Provides the full plan content
- Asks specific review questions
- Requests structured feedback

### 3. Execute Gemini CLI

Run Gemini in sandbox mode:

```bash
gemini --sandbox --output-format text --model <model> "$(cat <<'EOF'
You are a senior software architect reviewing a plan/specification.

Review this plan for:
1. Architectural soundness - Are the design decisions appropriate?
2. Missing requirements - What use cases or edge cases are not covered?
3. Implementation risks - What could go wrong during implementation?
4. Scalability concerns - Will this scale with growth?
5. Unclear specifications - What needs more detail or clarification?
6. Dependency risks - Are there risky external dependencies?
7. Security considerations - Any security gaps in the plan?

Provide specific, actionable feedback with clear reasoning.

Plan to review:
<plan>
[PLAN CONTENT HERE]
</plan>
EOF
)"
```

**Important flags:**
- `--sandbox` - Prevents any code modifications
- `--output-format text` - Returns plain text
- `--model <model>` - Model to use (default: `gemini-2.5-pro`)

### 4. Parse and Report

Structure Gemini's feedback in a clear format.

## Output Format

```markdown
## Gemini Plan Review Results

**Plan:** [Plan title or file path]

**Model:** [model used] (via Gemini CLI)

### Summary
[High-level assessment of the plan - 2-3 sentences]

### Strengths Identified
- [What's good about this plan]
- [Well-thought-out aspects]

### Concerns & Risks

#### Critical
- **[Issue]** - [Description and why it's critical]

#### Important
- **[Issue]** - [Description]

#### Minor
- **[Suggestion]** - [Description]

### Missing Elements
- [Requirements or considerations not addressed]
- [Edge cases not covered]

### Questions for Clarification
- [Ambiguities that need resolution]
- [Unclear requirements]

### Gemini Verdict
[APPROVE / REQUEST CHANGES / NEEDS DISCUSSION]

### Key Insights
Perspectives that might not be in Claude's review:
- [Insight 1]
- [Insight 2]

### Raw Output
<details>
<summary>Full Gemini Response</summary>

[Complete unedited response]

</details>
```

## Error Handling

### CLI Not Found
```markdown
**Status:** Gemini CLI not available

To enable Gemini plan reviews:
1. Install Gemini CLI following official docs
2. Authenticate: `gemini` (follow prompts)

Plan review completed with Claude agents only.
```

### Authentication Failed
```markdown
**Status:** Gemini authentication required

Run: `gemini` and follow authentication prompts

Plan review completed with Claude agents only.
```

### Timeout
If Gemini takes too long (>2 minutes):
```markdown
**Status:** Gemini review timed out

The plan may be too large or complex. Consider:
1. Reviewing specific sections separately
2. Summarizing large sections first

Plan review completed with Claude agents only.
```

### Plan Too Large
If plan exceeds reasonable token limits:
1. Warn user about truncation
2. Send first ~40k tokens with note about truncation
3. Suggest reviewing sections separately if needed

## Safety Constraints

- **Always use `--sandbox`** - Prevents code modifications
- **Truncate large plans** - Don't overwhelm with huge content
- **No secrets in prompts** - Users should ensure plans don't contain credentials
- **Verify suggestions** - Gemini feedback is one perspective, not authoritative
```

#### 2. Update: `plugins/core/commands/plan_review.md`

**Current content:**
```markdown
---
name: plan_review
description: Have multiple specialized agents review a plan in parallel
argument-hint: "[plan file path or plan content]"
---

Have @agent-code-simplicity-reviewer @agent-architecture-strategist review this plan in parallel.

For Python projects, also include:
- @agent-kieran-python-reviewer
- @agent-skeptical-simplicity-reviewer
For LLM/DS/ML projects also include
- @agent-ml-expert-reviewer

Run all applicable agents in parallel using the Task tool.
```

**Updated content:**
```markdown
---
name: plan_review
description: Have multiple specialized agents review a plan in parallel
argument-hint: "[plan file path or plan content]"
---

Have @agent-code-simplicity-reviewer @agent-architecture-strategist review this plan in parallel.

For Python projects, also include:
- @agent-kieran-python-reviewer
- @agent-skeptical-simplicity-reviewer
For LLM/DS/ML projects also include:
- @agent-ml-expert-reviewer

If Gemini CLI is available (check with `gemini --version`), also include:
- @agent-gemini-plan-reviewer

Run all applicable agents in parallel using the Task tool. If Gemini CLI is not installed, skip the Gemini agent gracefully and continue with the other reviewers.
```

#### 3. Update: `plugins/python-backend/README.md`

Add to agents table:
```markdown
| gemini-plan-reviewer | Get alternative plan review perspectives from Google Gemini |
```

## Acceptance Criteria

### Functional Requirements

- [ ] New agent file created at `plugins/python-backend/agents/external-llm/gemini-plan-reviewer.md`
- [ ] Agent follows YAML frontmatter schema (name, description, tools)
- [ ] Agent uses Gemini CLI with `--sandbox` flag
- [ ] Agent provides structured output format matching other Gemini agents
- [ ] `plan_review.md` command updated to conditionally include Gemini agent
- [ ] Graceful degradation when Gemini CLI not available

### Non-Functional Requirements

- [ ] Agent fails gracefully with clear error messages
- [ ] Timeout handling for slow responses (2 minute limit)
- [ ] Large plan handling (truncation with warning)
- [ ] Documentation updated (README)

### Quality Gates

- [ ] Plugin validation passes: `claude plugin validate .`
- [ ] Manual testing with sample plan
- [ ] Error case testing (CLI not found, auth failure, timeout)

## Implementation Phases

### Phase 1: Core Agent Creation

**Tasks:**
1. Create `plugins/python-backend/agents/external-llm/gemini-plan-reviewer.md`
   - YAML frontmatter with name, description, tools
   - Purpose and prerequisites sections
   - Process workflow (gather context, formulate prompt, execute, report)
   - Output format template
   - Error handling section
   - Safety constraints

2. Validate plugin structure
   ```bash
   claude plugin validate .
   ```

### Phase 2: Command Integration

**Tasks:**
1. Update `plugins/core/commands/plan_review.md`
   - Add conditional Gemini agent inclusion
   - Add graceful skip instruction when CLI unavailable

2. Test command execution
   - With Gemini CLI available
   - Without Gemini CLI (graceful skip)

### Phase 3: Documentation & Testing

**Tasks:**
1. Update `plugins/python-backend/README.md`
   - Add agent to agents table

2. Manual testing
   - Review a sample plan with Gemini enabled
   - Verify error handling paths
   - Test timeout scenario

## Alternative Approaches Considered

### 1. Create agent in core plugin
**Rejected because:** Would break the pattern of keeping Gemini agents isolated in python-backend. Cross-plugin dependencies are already established.

### 2. Make Gemini agent always run (fail if not available)
**Rejected because:** Would break existing workflows for users without Gemini CLI. Graceful degradation is more user-friendly.

### 3. Create separate `/plan_review_gemini` command
**Rejected because:** Users would have to run two commands. Integration into existing command provides seamless experience.

### 4. Store Gemini as required dependency
**Rejected because:** Not all users need or want external LLM integration. Optional enhancement is the right approach.

## Dependencies & Prerequisites

### Required
- Existing plan_review.md command structure
- Existing Gemini agent patterns (gemini-reviewer.md, gemini-brainstorm.md)
- Plugin validation tooling

### Optional (for full functionality)
- Gemini CLI installed and authenticated
- Network connectivity for Gemini API

## Risk Analysis & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Gemini CLI not installed for most users | High | Low | Graceful skip, clear instructions |
| Gemini adds latency to plan review | Medium | Low | Parallel execution with other agents |
| Gemini gives conflicting advice vs Claude | Medium | Low | Frame as "alternative perspective" not authoritative |
| Large plans exceed token limits | Medium | Medium | Truncation with warning, suggest sectional review |
| API rate limits during heavy use | Low | Low | Users manage their own API usage |

## Future Considerations

Out of scope for v1, but potential enhancements:

1. **Comparative analysis** - Cross-reference Gemini findings with Claude agent findings to highlight consensus and conflicts
2. **Model selection flag** - Allow users to specify model via command argument
3. **Cost tracking** - Warn users about API usage patterns
4. **Secret scrubbing** - Automatic detection and redaction of sensitive data in plans

## Success Metrics

- Plan reviews include Gemini perspective when CLI available
- No failures for users without Gemini CLI
- Error messages are clear and actionable
- Output format is consistent with existing Gemini agents

## References

### Internal References
- `plugins/core/commands/plan_review.md:1-16` - Current plan_review command
- `plugins/python-backend/agents/external-llm/gemini-reviewer.md:1-234` - Gemini code review pattern
- `plugins/python-backend/agents/external-llm/gemini-brainstorm.md:1-181` - Gemini brainstorm pattern
- `plugins/core/agents/review/architecture-strategist.md:1-52` - Claude architecture review pattern

### External References
- Gemini CLI documentation
- Google Cloud authentication setup

## MVP Implementation

### `plugins/python-backend/agents/external-llm/gemini-plan-reviewer.md`

```markdown
---
name: gemini-plan-reviewer
description: Get alternative perspectives on plans and specifications from Google Gemini. Use when you want a second opinion from a different LLM on feature plans, architecture proposals, or project specifications.
tools: Bash, Read, Grep, Glob
---

# Gemini Plan Review Agent

You provide alternative AI perspectives on plans and specifications by invoking the Google Gemini CLI in sandbox mode.

## Purpose

- Offer a second opinion from Gemini on plans and specifications
- Identify gaps, risks, or ambiguities Claude's review might miss
- Surface blind spots through model diversity

## Prerequisites

- Gemini CLI installed (`gemini --version` to verify)
- Google authentication configured

## Input

You receive plan content (file path or inline) to review.

**Default model:** `gemini-2.5-pro`

Parse model from prompt if specified (e.g., "using flash, review...")

## Process

### 1. Read the Plan

If given a file path, read it. Gather relevant codebase context from CLAUDE.md.

### 2. Execute Gemini Review

```bash
PLAN_CONTENT="[plan content here]"

gemini --sandbox --output-format text --model gemini-2.5-pro "$(cat <<'EOF'
You are a senior software architect reviewing a plan/specification.

Review for:
1. Architectural soundness
2. Missing requirements or edge cases
3. Implementation risks
4. Scalability concerns
5. Unclear specifications
6. Security considerations

Provide specific, actionable feedback.

Plan:
$PLAN_CONTENT
EOF
)"
```

### 3. Report Results

## Output Format

```markdown
## Gemini Plan Review Results

**Model:** [model] (via Gemini CLI)

### Summary
[2-3 sentence assessment]

### Concerns & Risks

#### Critical
- **[Issue]** - [Why critical]

#### Important
- **[Issue]** - [Description]

### Missing Elements
- [Gaps identified]

### Questions for Clarification
- [Ambiguities]

### Gemini Verdict
[APPROVE / REQUEST CHANGES / NEEDS DISCUSSION]

### Key Insights
- [Unique perspectives]

### Raw Output
<details>
<summary>Full Response</summary>
[Complete response]
</details>
```

## Error Handling

### CLI Not Found
Report: "Gemini CLI not available. Plan review completed with Claude agents only."

### Timeout (>2 minutes)
Report: "Gemini review timed out. Plan review completed with Claude agents only."

## Safety

- Always use `--sandbox`
- Truncate large plans (~40k tokens max)
- Verify suggestions - Gemini feedback is one perspective
```

### Updated `plugins/core/commands/plan_review.md`

```markdown
---
name: plan_review
description: Have multiple specialized agents review a plan in parallel
argument-hint: "[plan file path or plan content]"
---

Have @agent-code-simplicity-reviewer @agent-architecture-strategist review this plan in parallel.

For Python projects, also include:
- @agent-kieran-python-reviewer
- @agent-skeptical-simplicity-reviewer
For LLM/DS/ML projects also include:
- @agent-ml-expert-reviewer

If Gemini CLI is available (check with `gemini --version`), also include:
- @agent-gemini-plan-reviewer

Run all applicable agents in parallel using the Task tool. If Gemini CLI is not installed, skip the Gemini agent gracefully and continue with the other reviewers.
```
