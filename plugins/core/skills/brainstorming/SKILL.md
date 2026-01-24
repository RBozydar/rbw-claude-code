---
name: brainstorming
description: This skill should be used before implementing features, building components, or making changes. It guides exploring user intent, approaches, and design decisions before planning. Triggers on "let's brainstorm", "help me think through", "what should we build", "explore approaches", ambiguous feature requests, or when the user's request has multiple valid interpretations that need clarification.
---

# Brainstorming

This skill provides detailed process knowledge for effective brainstorming sessions that clarify **WHAT** to build before diving into **HOW** to build it.

## When to Use This Skill

Brainstorming is valuable when:
- Requirements are unclear or ambiguous
- Multiple approaches could solve the problem
- Trade-offs need to be explored with the user
- The user hasn't fully articulated what they want
- The feature scope needs refinement

Brainstorming can be skipped when:
- Requirements are explicit and detailed
- The user knows exactly what they want
- The task is a straightforward bug fix or well-defined change

### Explicit Skip Signals
- User says "just do it" or "proceed"
- Requirements include acceptance criteria
- User references a specific existing pattern
- Task is a bug fix with clear reproduction steps
- User provides a detailed spec or design document

## Core Process

### Phase 0: Assess Requirement Clarity

Before diving into questions, assess whether brainstorming is needed.

**Signals that requirements are clear:**
- User provided specific acceptance criteria
- User referenced existing patterns to follow
- User described exact behavior expected
- Scope is constrained and well-defined

**Signals that brainstorming is needed:**
- User used vague terms ("make it better", "add something like")
- Multiple reasonable interpretations exist
- Trade-offs haven't been discussed
- User seems unsure about the approach

If requirements are clear, suggest: "Your requirements seem clear. Consider proceeding directly to planning or implementation."

### Phase 1: Understand the Idea

Ask questions **one at a time** to understand the user's intent. Avoid overwhelming with multiple questions.

**Question Techniques:**

1. **Prefer multiple choice when natural options exist**
   - Good: "Should the notification be: (a) email only, (b) in-app only, or (c) both?"
   - Avoid: "How should users be notified?"

2. **Start broad, then narrow**
   - First: What is the core purpose?
   - Then: Who are the users?
   - Finally: What constraints exist?

3. **Validate assumptions explicitly**
   - "I'm assuming users will be logged in. Is that correct?"

4. **Ask about success criteria early**
   - "How will you know this feature is working well?"

**Key Topics to Explore:**

| Topic | Example Questions |
|-------|-------------------|
| Purpose | What problem does this solve? What's the motivation? |
| Users | Who uses this? What's their context? |
| Constraints | Any technical limitations? Timeline? Dependencies? |
| Success | How will you measure success? What's the happy path? |
| Edge Cases | What shouldn't happen? Any error states to consider? |
| Existing Patterns | Are there similar features in the codebase to follow? |

**Exit Condition:** Continue until the idea is clear OR user says "proceed" or "let's move on"

### Phase 2: Explore Approaches

After understanding the idea, propose 2-3 concrete approaches.

**Structure for Each Approach:**

```markdown
### Approach A: [Name]

[2-3 sentence description]

**Pros:**
- [Benefit 1]
- [Benefit 2]

**Cons:**
- [Drawback 1]
- [Drawback 2]

**Best when:** [Circumstances where this approach shines]
```

**Guidelines:**
- Lead with a recommendation and explain why
- Be honest about trade-offs
- Consider YAGNI—simpler is usually better
- Reference codebase patterns when relevant

### Phase 3: Capture the Design

Summarize key decisions in a structured format.

**Design Doc Structure:**

```markdown
---
date: YYYY-MM-DD
topic: <kebab-case-topic>
---

# <Topic Title>

## What We're Building
[Concise description—1-2 paragraphs max]

## Why This Approach
[Brief explanation of approaches considered and why this one was chosen]

## Key Decisions
- [Decision 1]: [Rationale]
- [Decision 2]: [Rationale]

## Open Questions
- [Any unresolved questions for the planning phase]

## Next Steps
→ `/workflows:plan` for implementation details
```

**Output Location:** `docs/brainstorms/YYYY-MM-DD-<topic>-brainstorm.md`

### Phase 4: Handoff

Present clear options for what to do next:

1. **Proceed to planning** → Run `/workflows:plan`
2. **Refine further** → Continue exploring the design
3. **Done for now** → User will return later

## YAGNI Principles

During brainstorming, actively resist complexity:

- **Don't design for hypothetical future requirements**
- **Choose the simplest approach that solves the stated problem**
- **Prefer boring, proven patterns over clever solutions**
- **Ask "Do we really need this?" when complexity emerges**
- **Defer decisions that don't need to be made now**

## Incremental Validation

Keep sections short—200-300 words maximum. After each section of output, pause to validate understanding:

- "Does this match what you had in mind?"
- "Any adjustments before we continue?"
- "Is this the direction you want to go?"

This prevents wasted effort on misaligned designs.

## Exploration vs Convergence

Brainstorming has two distinct modes:

### Exploration Mode (Divergent)
- Goal: Generate many options without judgment
- When: Early in brainstorming, unclear requirements, new domains
- Techniques:
  - "What else could we do?"
  - Challenge assumptions
  - Consider radical alternatives
  - Use Gemini for external perspectives
  - Run Devil's Advocate to stress-test emerging ideas

### Convergence Mode (Focused)
- Goal: Narrow to a decision
- When: Options are clear, trade-offs understood
- Techniques:
  - Compare against success criteria
  - Apply constraints as filters
  - Use weighted decision matrices for complex choices

### Mode Transitions
- Signal exploration → convergence: "We have enough options. Let's evaluate."
- Signal convergence → exploration: "We're missing something. Let's step back."
- Always confirm mode transitions with the user

## Anti-Patterns to Avoid

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| Asking 5 questions at once | Ask one at a time |
| Jumping to implementation details | Stay focused on WHAT, not HOW |
| Proposing overly complex solutions | Start simple, add complexity only if needed |
| Ignoring existing codebase patterns | Research what exists first |
| Making assumptions without validating | State assumptions explicitly and confirm |
| Creating lengthy design documents | Keep it concise—details go in the plan |
| Proposing solutions before understanding constraints | Explore constraints early, before generating options |
| Skipping success criteria discussion | Ask "How will you know this is working?" early |
| Not validating with external perspectives | Use Gemini, Devil's Advocate, or team input for alternative viewpoints |
| Anchoring on first solution without exploring alternatives | Always present 2-3 options before recommending |
| Mixing exploration and convergence phases | Keep modes distinct; signal transitions explicitly |
| Not checking for existing solutions | Search learnings, past brainstorms, and codebase patterns first |

## Integration with Planning

Brainstorming answers **WHAT** to build:
- Requirements and acceptance criteria
- Chosen approach and rationale
- Key decisions and trade-offs

Planning answers **HOW** to build it:
- Implementation steps and file changes
- Technical details and code patterns
- Testing strategy and verification

When brainstorm output exists, `/workflows:plan` should detect it and use it as input, skipping its own idea refinement phase.
