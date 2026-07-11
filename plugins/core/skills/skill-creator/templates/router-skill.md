---
name: {{SKILL_NAME}}
description: Use this skill when {{task family, systems, file types, or failure modes}}. Do not use it for {{similar tasks that should route elsewhere}}.
---

# {{Skill Title}}

## Overview

{{1-3 sentences explaining the shared capability across the workflows in this skill and why this needs routing rather than a single flat instruction set.}}

## Essential Principles

These rules apply across all workflows:
1. {{Shared principle that must not be skipped}}
2. {{Safety, correctness, or quality guardrail}}
3. {{Constraint that keeps the skill focused}}

## Trigger Examples

Use this skill for requests like:
- "{{request that should route to workflow A}}"
- "{{request that should route to workflow B}}"
- "{{request that should route to workflow C}}"

Do not use it for:
- "{{similar request that belongs to another skill}}"
- "{{request too broad or unrelated for this router}}"

## Intake and Routing

If the user intent is ambiguous, ask one focused intake question to determine the workflow.
If intent is already clear from the request, route directly without asking.

Example routing table:

| Signal | Workflow | Read next |
|--------|----------|-----------|
| {{keyword set A}} | Workflow A | `workflows/{{workflow-a}}.md` |
| {{keyword set B}} | Workflow B | `workflows/{{workflow-b}}.md` |
| {{keyword set C}} | Workflow C | `workflows/{{workflow-c}}.md` |

Route to the closest workflow, then adapt within that workflow. Do not force brittle step ordering unless the workflow is safety-critical.

## Bundled Resources

- `workflows/...` - workflow-specific procedures and decision trees
- `references/...` - detailed domain knowledge loaded on demand
- `templates/...` - reusable output structures
- `scripts/...` - deterministic helpers or verifiers
- `evals/skill-evals.yaml` - repeated trigger and routing eval cases

Delete lines for resources this skill does not ship.

## Domain Knowledge Index

Summarize what lives in `references/`:
- `references/{{reference-1}}.md` - {{purpose}}
- `references/{{reference-2}}.md` - {{purpose}}

## Workflow Index

Summarize what lives in `workflows/`:
- `workflows/{{workflow-a}}.md` - {{when to use it}}
- `workflows/{{workflow-b}}.md` - {{when to use it}}
- `workflows/{{workflow-c}}.md` - {{when to use it}}

## Gotchas

Capture real routing and execution failures:
- Situation: {{ambiguous phrasing or misroute}}
- Wrong instinct: {{common incorrect routing choice}}
- Correct approach: {{how to disambiguate or route correctly}}
- How to verify the fix: {{observable proof}}

Add workflow-specific footguns here only if they affect more than one workflow; otherwise put them in the workflow file.

## Verification

Explain how to verify both routing and outcome:
1. Trigger check: {{how to confirm the right workflow was selected}}
2. Action check: {{how to confirm the workflow executed correctly}}
3. Negative check: {{how to confirm unrelated prompts do not route here}}
4. Evidence: {{logs, files, screenshots, assertions, or other proof}}

## Success Criteria

A well-executed {{SKILL_NAME}} skill:
- [ ] Routes requests to the right workflow consistently
- [ ] Avoids hijacking adjacent requests
- [ ] Keeps shared principles in SKILL.md and details in workflow/reference files
- [ ] Documents cross-workflow failure modes in Gotchas
- [ ] Has repeatable eval coverage for trigger and routing behavior

## Progressive Disclosure Notes

Keep SKILL.md focused on shared principles, routing, and resource discovery.
Move workflow detail into `workflows/`.
Move dense knowledge into `references/`.
Point to files explicitly so Claude can load only what it needs.

## Iteration Notes

Improve this router over time:
- add new trigger phrases when user language shifts
- add negative cases when the skill hijacks nearby requests
- split workflows when a single route becomes overloaded
- extend `evals/skill-evals.yaml` with routing regressions and edge cases
- remove workflows that no longer add value
