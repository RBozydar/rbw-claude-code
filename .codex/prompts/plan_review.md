---
description: "Have multiple specialized agents review a plan in parallel"
argument-hint: "[plan file path or plan content]"
---

<!-- Generated from plugins/core/commands/plan_review.md -->
<!-- Do not edit by hand. Regenerate from the Claude command source. -->

Have `agent-code-simplicity-reviewer` agent `agent-architecture-strategist` agent review this plan in parallel.

For Python projects, also include:
- `agent-kieran-python-reviewer` agent
- `agent-skeptical-simplicity-reviewer` agent
- `agent-gemini-plan-reviewer` agent
For Python LLM/DS/ML projects also include:
- `agent-ml-expert-reviewer` agent

Run all applicable agents in parallel using the agent spawning. If Gemini CLI is not installed, skip the Gemini agent gracefully and continue with the other reviewers.
