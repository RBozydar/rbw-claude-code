---
name: plan_review
description: Have multiple specialized agents review a plan in parallel
argument-hint: "[plan file path or plan content]"
---

Have @agent-code-simplicity-reviewer @agent-architecture-strategist review this plan in parallel.

For Python projects, also include:
- @agent-kieran-python-reviewer
- @agent-skeptical-simplicity-reviewer
- @agent-gemini-plan-reviewer
For Python LLM/DS/ML projects also include:
- @agent-ml-expert-reviewer

Run all applicable agents in parallel using the Task tool. If Gemini CLI is not installed, skip the Gemini agent gracefully and continue with the other reviewers.
