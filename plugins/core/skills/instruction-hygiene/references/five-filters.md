# Five Filters for Instruction Hygiene

Use these filters on every rule, preference, convention, or warning found in the setup.

## 1. Default Behavior
Question: Is this something Claude already does reasonably well without being told?

Good candidates to cut:
- "Be concise"
- "Explain your reasoning clearly"
- "Use descriptive names"
- "Write clean code"

Keep only when the project requires a non-default behavior or unusually strict constraint.

## 2. Contradiction
Question: Does this conflict with another instruction somewhere else?

Common examples:
- one file says "be concise" while another says "always explain every technical term"
- one rule says "ask before making changes" while another says "act autonomously"
- one skill says "prefer uv" while another example uses bare `python`

When contradictions appear, preserve the sharper, more durable instruction and delete or rewrite the weaker one.

## 3. Duplication
Question: Is this already covered elsewhere?

Common examples:
- the same package-manager rule repeated in root `CLAUDE.md`, a skill, and a context file
- the same testing checklist repeated across multiple skills
- the same writing-style guidance duplicated in several instruction layers

Prefer a single authoritative location plus lightweight references.

## 4. Bandaid Rule
Question: Does this read like a patch for one frustrating past output instead of a stable policy?

Smells like:
- hyper-specific wording constraints
- rules beginning with "never again"
- instructions clearly tied to one previous failure mode
- one-off formatting preferences that are not broadly useful

These usually belong in the prompt for that task, not in the global setup.

## 5. Vagueness
Question: Would two different sessions interpret this differently?

Examples of vague rules:
- "be more natural"
- "use a good tone"
- "think harder"
- "be strategic"

If the intent is important, rewrite it into a concrete instruction with observable behavior. Otherwise remove it.

## Reporting Format
For each flagged rule, report:
- the exact rule or a short quote
- which filter(s) it failed
- one-line reason
- recommended action: cut, rewrite, merge, or keep

## Keep List Heuristics
Usually keep:
- project purpose and domain context
- package manager / build / test commands
- repository-specific workflows
- security constraints
- naming conventions with real downstream impact
- tool quirks and stable environment facts
