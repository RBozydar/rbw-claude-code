---
name: brainstorming
description: This skill should be used before implementing features, building components, or making changes when requirements need clarification. It guides exploring user intent, approaches, and design decisions before planning. Triggers on "let's brainstorm", "help me think through", "what should we build", "explore approaches", ambiguous feature requests, or when multiple valid interpretations exist.
---

# Brainstorming

Clarify **WHAT** to build before diving into **HOW** to build it.

## When to Use

**Brainstorm when:**
- Requirements are unclear or ambiguous
- Multiple approaches could solve the problem
- Trade-offs need exploration
- Feature scope needs refinement

**Skip when:**
- Requirements include acceptance criteria
- Task is a straightforward bug fix
- User says "just do it" or provides a detailed spec
- User references a specific existing pattern

## Core Process

### Phase 0: Assess Requirement Clarity

Before diving into questions, assess whether brainstorming is needed.

**Clear requirements signals:** specific acceptance criteria, referenced patterns, exact expected behavior, constrained scope.

**Brainstorming needed signals:** vague terms ("make it better"), multiple interpretations, undiscussed trade-offs.

If requirements are clear, suggest proceeding directly to planning or implementation.

### Phase 1: Understand the Idea

Ask questions **one at a time** to understand intent. Avoid overwhelming with multiple questions.

**Question techniques:**
1. **Prefer multiple choice** -- "Should notifications be: (a) email, (b) in-app, or (c) both?"
2. **Start broad, then narrow** -- core purpose → users → constraints
3. **Validate assumptions explicitly** -- "Assuming users are logged in. Correct?"
4. **Ask about success criteria early** -- "How will success be measured?"

**Key topics:** Purpose/motivation, Users/context, Constraints/timeline, Success criteria, Edge cases, Existing patterns in the codebase.

**Exit condition:** Continue until the idea is clear OR user says "proceed."

### Phase 2: Explore Approaches

Propose 2-3 concrete approaches:

```markdown
### Approach A: [Name]
[2-3 sentence description]

**Pros:** [Benefits]
**Cons:** [Drawbacks]
**Best when:** [Circumstances]
```

Lead with a recommendation. Be honest about trade-offs. Consider YAGNI -- simpler is usually better.

### Phase 3: Capture the Design

Summarize key decisions:

```markdown
---
date: YYYY-MM-DD
topic: <kebab-case-topic>
---

# <Topic Title>

## What We're Building
[1-2 paragraphs]

## Why This Approach
[Approaches considered and rationale]

## Key Decisions
- [Decision]: [Rationale]

## Open Questions
- [Unresolved questions]

## Next Steps
→ `/workflows:plan` for implementation details
```

**Output location:** `docs/brainstorms/YYYY-MM-DD-<topic>-brainstorm.md`

### Phase 4: Handoff

Present options:
1. **Proceed to planning** -- run `/workflows:plan`
2. **Refine further** -- continue exploring
3. **Done for now** -- return later

## YAGNI Principles

- Do not design for hypothetical future requirements
- Choose the simplest approach that solves the stated problem
- Prefer boring, proven patterns over clever solutions
- Defer decisions that do not need to be made now

## Incremental Validation

Keep sections short (200-300 words max). After each section, pause to validate: "Does this match what you had in mind?" This prevents wasted effort on misaligned designs.

## Exploration vs Convergence

**Exploration mode (divergent):** Generate many options without judgment. Use when requirements are unclear or early in brainstorming. Challenge assumptions, consider radical alternatives. Use the `gemini-brainstorm` agent for external perspectives and the `devils-advocate-brainstormer` agent to stress-test emerging ideas.

**Convergence mode (focused):** Narrow to a decision. Use when options are clear and trade-offs understood. Compare against success criteria, apply constraints as filters.

Always confirm mode transitions with the user.

## Anti-Patterns

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| Asking 5 questions at once | Ask one at a time |
| Jumping to implementation | Stay focused on WHAT, not HOW |
| Overly complex solutions | Start simple, add complexity only if needed |
| Ignoring codebase patterns | Research what exists first |
| Assumptions without validation | State and confirm assumptions |
| Lengthy design documents | Keep concise -- details go in the plan |
| Skipping success criteria | Ask early how success will be measured |
| Anchoring on first solution | Present 2-3 options before recommending |

## Integration with Planning

Brainstorming answers **WHAT** -- requirements, chosen approach, key decisions.
Planning answers **HOW** -- implementation steps, code patterns, testing strategy.

When brainstorm output exists, `/workflows:plan` should detect it and use it as input.
