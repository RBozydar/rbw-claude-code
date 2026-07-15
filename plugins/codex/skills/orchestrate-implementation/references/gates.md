# Contract, Scope, Review, and Integration Gates

## Product contract

Freeze stable decisions only:

- outcome and user value;
- critical invariants and acceptance examples;
- explicit non-goals and compatibility boundaries;
- risk classification and reasons;
- likely production/test surfaces;
- hard external constraints such as dependency, migration, security, or side-effect policy;
- required validation by behavior or risk axis.

The plan is not the final software product. Leave private helper names, exhaustive test matrices, exact shell programs, live SHAs, PR polling, and publication mechanics to implementation, the handoff, or the ledger unless they are themselves public behavior or safety-critical.

Product changes use `SPEC_GAP -> STOP_AND_REPLAN -> SPEC_FROZEN`. Mutable execution-state changes do not rewrite the product contract.

## Boundary audit

Before freezing stateful work, map only the boundaries that can change observable behavior or safety:

- every runtime-policy source and production consumer;
- persistent enable, disable, restart, replacement, retry, and rollback transitions;
- absent, null, empty, malformed, unsupported, mixed, and valid-no-match inputs;
- transaction ownership and the mutation boundary;
- event time, execution time, source watermark, freshness, and historical-time meaning.

Use a compact table or a falsifiable prototype, not an expanded implementation script. If the audit reveals independently useful persistence, operations, and presentation outcomes, split them before dispatch. Record private mechanics as implementation discretion.

## Local-plan boundary

Plan and task files are local working artifacts:

- review and approve them locally;
- record their exact path and hash in the ledger;
- pass their contract to workers through the handoff or delegation message;
- keep them immutable to implementation workers;
- exclude them from candidate commits, integration commits, and PR diffs;
- reconcile their status locally after delivery and leave those edits uncommitted.

Do not create a separate plan PR. Do not bundle plan/task files into the implementation PR. When a tracked plan/task file is locally modified, treat it as user-owned dirty state and build the implementation branch from the clean target base without carrying that diff.

## Minimal execution handoff

Give the worker the smallest sufficient runtime envelope:

```text
PLAN: <local path / hash>
WORK_BRANCH: <branch>
TARGET_BRANCH: <branch>
STARTING_SHA: <discovered at dispatch>
HARD_BOUNDARIES: <paths, side effects, immutable user work>
REQUIRED_CHECKS: <commands or behavioral gates>
DELIVERY: <local or PR policy / publisher>
```

Record discovered candidate SHAs, hashes, dirty state, PR state, and actor IDs in the ledger. Do not embed them into the stable plan merely to make orchestration executable.

## Model policy

Main may override every role. Defaults:

| Role | Low/medium risk | High risk |
|---|---|---|
| Worker | Terra `max` | Sol `high` |
| General reviewer | Sol `high` | Sol `xhigh` |
| Contract/test reviewer | Sol `high` | Sol `xhigh` |
| Specialist reviewer | As needed | Sol `xhigh` |
| Diagnostic | Sol `xhigh`, then one `max` escalation | Same |
| Integrator | Worker or selected thread | Selected thread |
| Publisher | Luna `medium` | Luna `medium` |

Treat persistence, migration, security, permissions, destructive filesystem operations, and consequential business-contract changes as high risk unless main records a justified override.

Delegate authenticated GitHub reads and writes to Luna Medium unless the user explicitly selects another model. Reserve Sol for product decisions and reviews that need it.

## Scope signals

Use these together as diagnostic evidence, never as automatic rejection:

- a fourth semantic plan revision would begin;
- production paths, public interfaces, or state machines keep multiplying;
- one task spans store, service, CLI, API, export, migration, and documentation;
- one task combines independently useful persistence, operations, and presentation outcomes;
- test LoC or matrix breadth approaches or exceeds the size of the expected implementation;
- a red test needs a previously unidentified public seam;
- multiple plan-only delivery cycles occur before product code;
- the plan contains substantial Git, publication, preservation, or reconciliation machinery;
- reviewer findings move between subsystems instead of converging;
- a supposedly ready PR exposes another public-contract gap or release-blocker wave.

File, line, and test estimates are reviewability signals unless the user explicitly declares a hard limit. Exceeding an estimate triggers a scope decision; it never justifies compressed code, weakened tests, suppressions, or omitted behavior.

Before a fourth semantic revision, main enters `SCOPE_REVIEW` and chooses one:

- split into independently useful vertical slices;
- prototype the uncertain mechanism;
- simplify the product contract;
- leave a private implementation choice to the worker;
- continue as one documented exception.

If that exception later needs a fifth semantic revision, default to split, prototype, or simplify. Continuing the whole slice requires explicit user authorization and a recorded reason it cannot deliver smaller useful outcomes.

## Specification review

Match independence to the change:

| Situation | Review context |
|---|---|
| New high-risk contract | Fresh context-free full review |
| Normal or one-axis contract | Targeted review |
| Narrow fix to a reviewer's findings | Same reviewer |
| Wording, formatting, actor, branch, SHA, preservation value, or delivery-only correction | Same reviewer or affected-axis check |
| One-axis semantic change | Fresh targeted specialist |
| Decomposition, architecture change, or cross-axis semantic rewrite | Fresh context-free full review |

A contract reviewer verifies observable acceptance, coherent invariants, non-goals, risk, vertical-slice boundaries, and compatibility with live repository state. It does not demand implementation details merely because they can be specified.

`SPEC_APPROVED` means the product decision is sufficient to implement safely. It does not mean every private helper, test fixture, or release command has been predetermined.

## Risk tripwires

Enter `STOP_AND_REPLAN` when evidence confirms:

- work crosses an explicit hard boundary or user-owned scope;
- risk materially increases into migration, persistence mutation, destructive operation, permission, secret, or trust-boundary work;
- a public state/schema/auth/compatibility invariant changes;
- an architectural finding makes the current vertical slice unsafe;
- the task can no longer satisfy its stated non-goals.

Use `SCOPE_REVIEW`, not automatic stop, for justified line/test growth, private implementation seams, or delivery-state drift. Record the evidence and decision either way.

## Critical red-test gate

Use this gate for high-risk behavior lacking a trusted oracle. Freeze a small set of black-box tests around the dangerous invariants, such as:

- no consequential write before authorization;
- approval executes reviewed stored intent rather than recomputing it;
- stale or failed execution rolls back coherently;
- concurrency has an explicit winner/loser outcome;
- authentication precedes protected parsing and mutation;
- migration and quarantine boundaries fail safely.

Do not require every renderer, limit permutation, and transport matrix before production work. Add exhaustive matrices alongside implementation unless they are necessary to establish the oracle. When red-test size approaches or exceeds expected production size, pause for `SCOPE_REVIEW`; treat this as evidence, not a hard limit.

The reviewer confirms intended red failure, black-box behavior, no production diff, and no scope redefinition. It requests only oracle-critical closure before production; broader coverage travels with implementation. Test LoC, function count, and surface breadth are scope signals rather than correctness limits.

## Snapshot gate

Review an implementation candidate only when:

- base and candidate SHAs are explicit;
- status is clean and untracked files are empty;
- changed paths fit the decided slice or have an explicit disposition;
- every local plan/task path is absent from the diff;
- claimed validation and residual risks are recorded.

Create a fresh exact-snapshot code review independent of the worker. Add fresh specialists only for applicable high-risk axes. Every approval identifies candidate SHA, contract revision, changed paths, validation, findings, and residual risks.

## Approval freshness

Invalidate approvals by affected axis:

- auth or trust-boundary changes invalidate security/transport review;
- transaction, migration, schema, or concurrency changes invalidate persistence review;
- observable behavior changes invalidate product/spec review;
- operations or deployment changes invalidate operations review;
- wording, metadata, branch, hash, and delivery-only corrections receive narrow closure review.

Every changed implementation candidate still receives final exact-SHA code verification. A candidate change does not automatically require a complete cold specification restart.

## Finding classes

- `INTRODUCED_DEFECT`: caused by the candidate; return to the persistent worker.
- `PRE_EXISTING_DEFECT`: existed at the starting SHA; separate it unless it blocks safe delivery.
- `SPEC_GAP`: missing or contradictory public behavior/invariant; return to specification or scope review.
- `OUT_OF_SCOPE_IMPROVEMENT`: useful but unnecessary; record separately.

Main arbitrates disputed classification before routing work.

## Review axes

Main selects the independent review stack. The worker may self-review but does not spawn duplicate cold Standards/Spec reviewers unless main delegates them. Every implementation receives one independent general/code review. Add only applicable specialist axes:

- product/specification and business invariants;
- persistence, migrations, transactions, idempotency, and recovery;
- security, permissions, secrets, trust boundaries, and unsafe input;
- operations, observability, deployment, rollback, and resource behavior.

Green tests are evidence, not approval. Reviewers inspect the diff and exercise their critical risks.

## Local integration

The selected worker or integrator:

1. verifies target branch/ref and dirty state;
2. stops on unsafe user-owned or competing writes;
3. integrates the exact approved candidate by the selected method;
4. records the resulting target SHA;
5. reruns required post-merge validation;
6. reconciles local plan/task status after delivery without staging or committing it;
7. verifies final status, validation, and document agreement.

Main arbitrates and verifies but performs no code-producing Git operation. Delivery remains complete only when committed code matches the locally reconciled plan, while plan/task edits remain uncommitted.
