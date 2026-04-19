---
name: {{SKILL_NAME}}
description: Use this skill when {{specific trigger phrases, file types, systems, or failure modes}}. Do not use it for {{similar requests that should route elsewhere}}.
---

# {{Skill Title}}

## Overview

{{1-3 sentences explaining the non-obvious capability this skill gives Claude. Focus on the delta from default behavior.}}

## Trigger Examples

Use this skill for requests like:
- "{{example request that should trigger}}"
- "{{another request that should trigger}}"
- "{{request mentioning key file type, system, or failure mode}}"

Do not use it for:
- "{{similar request that should NOT trigger}}"
- "{{adjacent task better handled by another skill}}"

## Skill Category

{{Primary category only: library/API reference, verification, data analysis, business automation, scaffolding/templates, code quality, CI/CD, runbook, infrastructure ops}}

## Workflow / Decision Structure

{{Describe the main workflow in direct, imperative language. Prefer constraints and decision points over brittle step-by-step micromanagement unless safety or correctness requires a fixed sequence.}}

## Bundled Resources

List every bundled resource and when to use it:
- `scripts/...` - {{deterministic helper or verifier}}
- `references/...` - {{detailed docs loaded on demand}}
- `templates/...` - {{reusable output structure}}
- `assets/...` - {{boilerplate or sample materials}}
- `config.json` - {{install-specific constants, only if needed}}
- `evals/skill-evals.yaml` - repeated trigger and negative-trigger eval cases

Delete lines for resources this skill does not ship.

## Gotchas

Add real, specific failure patterns:
- Situation: {{what goes wrong}}
- Wrong instinct: {{common but incorrect move}}
- Correct approach: {{what Claude should do instead}}
- How to verify the fix: {{observable proof}}

Include at least one gotcha based on actual failures or known footguns.

## Verification

Explain how to prove the skill worked:
1. Preconditions: {{required setup or inputs}}
2. Action: {{what to run or inspect}}
3. Assertion: {{observable proof or expected state}}
4. Failure interpretation: {{what a failed check likely means}}

## Success Criteria

This skill is complete when:
- [ ] It triggers for the intended requests
- [ ] It avoids triggering for adjacent requests that belong elsewhere
- [ ] Bundled resources are referenced correctly
- [ ] Common failure cases are captured in Gotchas
- [ ] Verification is explicit and repeatable

## Progressive Disclosure Notes

Keep SKILL.md lean.
Move long API details, schemas, examples, and policy text into `references/`.
Put repeated helper logic into `scripts/`.
Put reusable output structures into `templates/`.
Point to those files explicitly so Claude can load them only when needed.

## Iteration Notes

Improve this skill after real use:
- add new trigger examples when phrasing drifts
- add negative cases when the skill over-triggers
- add scripts when Claude keeps rewriting helper logic
- extend `evals/skill-evals.yaml` with regressions and edge cases
- retire the skill if evals pass reliably without it
