# Orchestration Run

- Run/task/main thread: `<run ID / task / main ID>`
- Repository/start: `<path / ref / SHA>`
- Current state: `<state>`
- Plan contract: `<local path / revision / hash; delivery-excluded>`
- Risk and hard boundaries: `<risk / user-owned state / side effects>`
- Scope disposition: `<signals / split-prototype-simplify-exception decision>`

## Current handoff

- Work branch / target branch / starting SHA: `<values>`
- Worker / reviewers / publisher: `<IDs and model/effort>`
- Delivery policy: `<local or PR; remote/base; merge authority>`
- Required checks: `<commands or behavioral gates>`
- Dirty baseline: `<owned paths or clean>`
- Current candidate: `<base / SHA / changed paths / clean>`
- Current approvals: `<axis / SHA / stale reason>`
- Blocking state or next action: `<one current fact>`

## Checkpoint log

Append one row only when state, snapshot, decision, approval, or delivery changes. Point to actor evidence; do not copy transcripts or validation logs.

| UTC | Actor/turn | State | Spec/candidate | Counters | Decision or evidence pointer / next |
|---|---|---|---|---|---|

## Open findings and decisions

Keep only unresolved or still-relevant items. Remove closed detail after its disposition is captured in the checkpoint log.

| Axis/class/severity | Current evidence | Disposition/owner |
|---|---|---|

## Delivery and completion

- PR or local result: `<URL / head / base / target SHA>`
- Required-check state: `<green | pending | READY_EXCEPT_BASELINE_CI evidence>`
- Final approvals: `<axes / exact SHA>`
- Local plan reconciliation: `<path/hash/status; uncommitted>`
- Residual risks: `<items or none>`
- Final outcome: `<DONE | STOPPED | READY_EXCEPT_BASELINE_CI>`

## Efficiency signals

- Semantic revisions / scope reviews / implementation attempts: `<counts>`
- Red snapshots / production reviews / PR feedback batches: `<counts>`
- Production and test paths/lines: `<counts>`
- Unchanged-state polls / history rereads / blocked events: `<counts>`
- Input/cache/output tokens and estimated cost: `<values if available>`
- Key elapsed observations: `<dispatch/candidate/review/delivery; never gates>`
