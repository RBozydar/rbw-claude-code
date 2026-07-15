---
name: orchestrate-implementation
description: Orchestrate delegated implementation through proportional planning, risk-based review, exact-candidate approval, and safe delivery.
---

# Orchestrate Implementation

Run a gated relay around a **vertical slice**. Main owns product decisions, routing, the ledger, and final authorization. A persistent worker owns implementation. Reviewers approve affected axes. An integrator or publisher owns delivery. Main remains an adviser and does not become the code author.

At the start, tell the user: `Ensure this main thread uses GPT-5.6 Sol at high or greater reasoning.` Treat role models as defaults that main may override.

## 1. Frame the product contract

Read `references/gates.md` sections **Product contract**, **Boundary audit**, **Local-plan boundary**, **Minimal execution handoff**, **Scope signals**, and **Specification review**.

Treat the plan as a decision document, not software written in prose. Capture the outcome, critical invariants, acceptance examples, non-goals, risk, compatibility boundaries, and likely scope. Keep mutable SHAs, branch state, publication mechanics, and live validation evidence in the handoff or ledger. Keep plan/task artifacts local and outside every delivery commit and PR.

Inspect the repository and user-owned dirty state. For stateful work, map configuration consumers, persistent transitions, input classes, transaction ownership, and time provenance before freezing. Split independently useful persistence, operations, and presentation slices. When uncertain mechanics dominate the design, delegate one falsifiable disposable prototype and feed its evidence back into the contract; do not turn the prototype into production implicitly.

Use a fresh context-free contract reviewer for a new high-risk contract or a semantic redesign. Use a targeted review for a normal slice or a change confined to one risk axis. Resolve product `SPEC_GAP`s, then record `SPEC_FROZEN` with the product-plan revision/hash.

Completion criterion: product behavior is implementable and observable; unresolved questions are either explicit implementation discretion or routed decisions; the ledger records the local plan hash, contract, risk, scope signals, and dirty baseline.

## 2. Open the external ledger

Copy `assets/run-ledger-template.md` to `$CODEX_HOME/orchestration-runs/<main-thread-id>/<UTC timestamp>-<task-slug>.md`. Request write approval when required. Prefer durable thread output over `/tmp`.

Make main the sole ledger writer. Keep one current-state summary and an append-only checkpoint log. Record only state changes, decisions, current candidate/approval facts, scope signals, delivery state, and residual risks; link to actor evidence instead of copying histories or validation transcripts. Keep orchestration ledgers out of the repository.

Completion criterion: the ledger exists, distinguishes stable product decisions from mutable execution state, and preserves the repository baseline.

## 3. Choose actors and dispatch the worker

Read `references/protocol.md` sections **Actor selection**, **Thread bootstrap**, **Messages**, and **Checkpoints**.

Use main-thread subagents for bounded read-only investigation, synthesis, or review. Use `fork_turns="none"` when independence matters. Use a separate persistent thread/worktree for implementation, a writing prototype, long-running repair, integration, or authenticated publication. Reuse the same worker for its revisions and the same reviewer for narrow closure checks.

Preflight the worker checkout/worktree, branch identity, clean state, and required project configuration before dispatch. Dispatch one implementation worker with the product contract and a minimal handoff: local plan reference/hash, work branch, target branch, discovered starting SHA, hard boundaries, required validation, and delivery policy. Mark plan/task paths immutable and delivery-excluded. Record the worker identity before continuing.

Completion criterion: one persistent worker owns the isolated implementation branch; bounded supporting work has the smallest sufficient context and no competing writer.

## 4. Gate critical red tests when risk warrants it

Read `references/gates.md` section **Critical red-test gate**.

For high-risk behavior without a trusted oracle, ask the worker for a small set of critical black-box red tests before production edits. Cover the dangerous invariants, not every transport permutation. Treat test paths, matrix breadth, and test LoC as scope signals. If the red suite approaches or exceeds the expected implementation, enter `SCOPE_REVIEW` before expanding it. Build exhaustive matrices alongside implementation unless the contract genuinely requires them first.

Use an independent targeted test reviewer. Continue with the same reviewer for narrow fixes to its findings. A new public invariant or materially different behavior returns to specification review; a private implementation seam does not automatically rewrite the product plan.

Completion criterion: critical tests fail for the intended missing behavior and receive `RED_TESTS_APPROVED`, or the ledger records why a separate red gate is unnecessary.

## 5. Route questions and run scope resets

Answer `WAITING_FOR_MAIN` from evidence; use a focused read-only subagent for substantial investigation. Send the worker one actionable decision and checkpoint it.

Treat estimates as tripwires, not targets. When plan size, changed paths, test LoC, interface breadth, or review churn rises, decide whether the slice remains coherent instead of compressing legitimate work.

Before starting a fourth semantic plan revision, enter `SCOPE_REVIEW`. Ask whether the task should be split vertically, prototyped, simplified, granted implementation discretion, or continued as one justified exception. Record the decision before another revision. If a continued exception later needs a fifth semantic revision, split, prototype, or simplify by default; continuing the whole slice requires explicit user authorization.

Enter `STOP_AND_REPLAN` for confirmed scope expansion, a changed trust/state/schema contract, an unsafe new public invariant, or a user-defined hard boundary. Enter `ORCHESTRATION_BLOCKED` for infrastructure or permission failures. Preserve the existing worker and state.

Completion criterion: every question has a decision; every scope signal has an explicit disposition; revision four never begins by inertia.

## 6. Review the exact candidate proportionally

Read `references/gates.md` sections **Snapshot gate**, **Approval freshness**, **Finding classes**, and **Review axes**.

Require a clean unpublished candidate commit with explicit base/candidate SHAs, validation, changed paths, and risks. Plan/task paths must be absent from the candidate diff. Always bind final approval to the exact candidate.

Choose review context by change:

- continue the same reviewer for narrow closure, wording, metadata, branch, hash, or workflow corrections;
- use a fresh targeted reviewer for a semantic change confined to one axis;
- use a fresh context-free full review for decomposition, architectural redesign, or cross-axis semantic change;
- use fresh applicable code/specialist review for the final implementation candidate.

Main selects one proportionate independent review stack. Workers may self-review but do not create duplicate cold Standards/Spec reviewers unless main delegates them. Invalidate only affected approvals, except that the final candidate must always receive exact-SHA verification. Route findings by class and return introduced defects to the persistent worker.

Completion criterion: actionable introduced defects are zero; required affected axes approve the same clean candidate; every other finding has a disposition.

## 7. Escape stalled implementation loops

Read `references/protocol.md` section **Loop escape**. Diagnose after repeated identical failures or several no-progress cycles. Pause the worker and use a fresh read-only diagnostic against the latest contract and snapshot.

If diagnosis finds a product gap, return to scope/specification review. If it finds an implementation defect, send one revised strategy to the same worker. Escalate inconclusive diagnosis to the user rather than multiplying workers.

Completion criterion: retries stop long enough to produce an evidence-backed recovery decision.

## 8. Deliver the approved snapshot

For local delivery, read `references/gates.md` section **Local integration**. The worker or selected integrator verifies target state, integrates the exact candidate, reruns required gates, and reconciles local plan/task state without committing it.

For GitHub delivery, read `references/github.md` in full. A dedicated Luna Medium publisher owns every authenticated GitHub operation and event-driven monitoring in its smaller context. Main consumes state changes instead of polling or rereading thread histories. The publisher batches terminal review feedback for the current candidate; code feedback returns to the persistent worker and receives affected-axis review before republishing.

Completion criterion: the approved snapshot is locally integrated and reconciled, or its PR is ready for the contract-selected human/automated decision with green checks and no unresolved actionable feedback.

## 9. Authorize DONE

Read only missing or disputed evidence plus the final worker report. Verify final SHA, contract hash, affected-axis approvals, validation, scope disposition, dirty-state ownership, project-state reconciliation, and delivery outcome.

Send `MARK_DONE` only when required checks are green or the user explicitly changes the delivery contract. A candidate blocked solely by a proven pre-existing required check remains `READY_EXCEPT_BASELINE_CI`, not `DONE` or `READY_FOR_HUMAN_REVIEW`. Require the worker's final `DONE`, complete its goal, and report scope, validation, approvals, delivery state, untouched changes, residual risks, and efficiency signals.

Completion criterion: the delivered snapshot matches the product contract and execution handoff; worker, ledger, and user report agree.
