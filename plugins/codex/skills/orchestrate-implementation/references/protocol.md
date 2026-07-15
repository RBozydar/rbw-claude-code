# Orchestration Protocol

Read only the sections named by `SKILL.md` at the phase that names them.

## States

Contract and orchestration:

- `CONTRACT_REVIEW`
- `PROTOTYPING`
- `SPEC_APPROVED`
- `SPEC_FROZEN`
- `SPEC_GAP`
- `SCOPE_REVIEW`
- `STOP_AND_REPLAN`
- `ORCHESTRATION_BLOCKED`
- `STALLED`
- `DONE`
- `STOPPED`

Worker:

- `IMPLEMENTING`
- `WAITING_FOR_MAIN`
- `RED_TESTS_READY`
- `RED_TESTS_APPROVED`
- `READY_FOR_REVIEW`
- `REVISING`
- `APPROVAL_STALE`
- `READY_FOR_INTEGRATION`
- `PUBLISHING_PR`
- `MONITORING_PR`
- `ADDRESSING_PR_FEEDBACK`
- `READY_FOR_HUMAN_REVIEW`
- `READY_EXCEPT_BASELINE_CI`
- `DONE`

Review and diagnosis:

- `REVIEWING`
- `CHANGES_REQUESTED`
- `REVIEW_APPROVED`
- `DIAGNOSING`
- `DIAGNOSIS_READY`
- `DIAGNOSIS_INCONCLUSIVE`

Local integration:

- `INTEGRATING_LOCAL`
- `MERGED_LOCAL`
- `RECONCILING_PROJECT_STATE`

Only main emits `SPEC_FROZEN` and `MARK_DONE`. Only the worker emits `READY_FOR_REVIEW`. Only a reviewer emits approval. Infrastructure failures enter `ORCHESTRATION_BLOCKED`; public-contract failures enter `STOP_AND_REPLAN`; accumulated scope signals enter `SCOPE_REVIEW`.

## Actor selection

### Main

Main owns product decisions, scope arbitration, finding classification, the ledger, routing, and final authorization. Main processes structured checkpoints and targeted disputed evidence. It does not write product code, own a candidate branch, perform code-producing integration, reread completed histories, or synchronously babysit long-running actors.

### Main-thread subagent

Use a subagent for bounded read-only work that should return in one result:

- repository investigation or option comparison;
- one-axis review or contract interpretation;
- session/metrics analysis;
- diagnosis of a specific finding;
- synthesis of raw reviewer or PR evidence.

Use `fork_turns="none"` for independent review and pass only the exact artifact, snapshot, and question. A subagent does not own a durable branch, authenticated remote state, or a multi-cycle implementation.

### Separate persistent thread

Use a separate thread/worktree for:

- implementation or any sustained code/test writing;
- a disposable prototype that writes code;
- migration, recovery, or long-running repair;
- candidate integration;
- authenticated publication and PR monitoring;
- a reviewer that genuinely needs continuity across multiple substantial cycles.

Keep one worker for the life of its candidate. Send revisions back to it instead of spawning replacements. Keep publication monitoring in a smaller publisher context and notify main only on state changes.

### Reviewer continuity

Use the same reviewer to verify narrow closure of its own findings. Use a fresh targeted reviewer when one semantic axis changes. Use a fresh context-free reviewer after decomposition, architectural redesign, or cross-axis contract change. Main owns this routing; worker-internal review does not duplicate the independent stack.

## Thread bootstrap

### Worker

Before dispatch, prove the intended checkout/worktree can read required instruction and project configuration, has the expected branch/base, and preserves the dirty baseline. Include the product contract and minimal execution handoff: local plan path/hash, work/target branches, discovered starting SHA, hard boundaries, validation, delivery policy, dirty baseline, and message schema. Identify every plan/task path as immutable and delivery-excluded.

Make the worker the sole candidate writer. It owns implementation, tests, candidate commits, scoped fixes, and validation. It may integrate or publish when selected. Create one worker goal spanning execution through main-authorized `DONE` when goal tools are available.

### Prototype

Give a writing prototype one falsifiable mechanism question, disposable branch/worktree, strict scope, and required evidence. Its output is evidence, not an implicitly approved production base.

### Reviewers

Give reviewers the exact artifact and affected axis. A fresh reviewer receives repository facts without worker conclusions. A continuing reviewer receives only its prior findings plus the revised artifact and closure evidence. Do not create fresh generic Standards/Spec pairs for each narrow candidate revision.

### Integrator and publisher

Give the actor the exact approved candidate SHA, destination, dirty baseline, permitted Git/remote operations, required post-operation checks, and main/worker IDs. Use Luna Medium for authenticated GitHub operations. A publisher changes remote state only; code feedback returns to the worker.

## Messages

### Checkpoint envelope

```text
STATE: <state>
TASK: <task reference>
CONTRACT_HASH: <hash>
SNAPSHOT: <candidate or target SHA, or n/a>
EVIDENCE: <paths, commands, results, URLs>
COUNTERS: <attempts, questions, review rounds, scope reviews>
NEXT: <expected actor/action>
```

Use this envelope for state changes, not routine polling.

### Worker needs a decision

```text
STATE: WAITING_FOR_MAIN
BLOCKING: <yes|no>
QUESTION: <one concrete question>
OPTIONS: <choices and consequences>
RECOMMENDATION: <one recommendation>
```

### Scope review

```text
STATE: SCOPE_REVIEW
SIGNALS: <revision count, surfaces, test/plan size, interface or workflow growth>
PRODUCT_GAPS: <remaining public decisions>
IMPLEMENTATION_DISCRETION: <questions the worker can own>
OPTIONS: <split | prototype | simplify | continue exception>
RECOMMENDATION: <one choice with evidence>
```

### Red tests

```text
STATE: RED_TESTS_READY
TEST_SNAPSHOT: <SHA or deterministic diff hash>
TEST_PATHS: <paths>
CRITICAL_INVARIANTS: <mapped behaviors>
FAILURE_COMMANDS: <commands and outcomes>
EXPECTED_FAILURE: <missing behavior>
OBSERVED_FAILURE: <actual behavior>
PRODUCTION_DIFF: 0
SCOPE_SIGNALS: <test size/surfaces and disposition>
```

### Candidate review

```text
STATE: READY_FOR_REVIEW
BASE_SHA: <SHA>
CANDIDATE_SHA: <SHA>
SPEC_REVISION: <revision/hash>
WORKTREE_CLEAN: yes
CHANGED_PATHS: <paths>
LOCAL_PLAN_DIFF: 0
VALIDATION: <commands and outcomes>
RISKS: <known risks or none>
```

### Review finding

```text
STATE: CHANGES_REQUESTED
REVIEW_AXIS: <code|product-spec|persistence|security|operations>
REVIEWED_SHA: <SHA>
SPEC_REVISION: <revision/hash>
FINDINGS:
- [severity] [INTRODUCED_DEFECT|PRE_EXISTING_DEFECT|SPEC_GAP|OUT_OF_SCOPE_IMPROVEMENT] <evidence> — <impact and disposition>
INDEPENDENT_GATES: <commands and outcomes>
```

### Snapshot approval

```text
STATE: REVIEW_APPROVED
REVIEW_AXIS: <axis>
BASE_SHA: <SHA>
REVIEWED_SHA: <SHA>
SPEC_REVISION: <revision/hash>
WORKTREE_STATUS: clean
CHANGED_PATHS: <paths>
INDEPENDENT_GATES: <commands and outcomes>
ACTIONABLE_INTRODUCED_DEFECTS: 0
OTHER_FINDINGS: <dispositions or none>
RESIDUAL_RISKS: <risks or none>
```

### Diagnostic result

```text
STATE: DIAGNOSIS_READY|DIAGNOSIS_INCONCLUSIVE
FAILURE_CLASS: <specification|scope|strategy|environment|dependency|test-oracle|permissions|other>
ROOT_CAUSE: <evidence-backed cause or unknown>
WHY_LOOP_PERSISTED: <feedback gap or false assumption>
PROPOSED_CHANGE: <worker strategy, prototype, split, or contract change>
CONFIDENCE: <high|medium|low>
```

### Completion

```text
STATE: DONE
FINAL_SHA: <SHA>
SPEC_REVISION: <revision/hash>
RESULT: <outcome>
VALIDATION: <exact post-delivery checks>
APPROVALS: <axes and reviewed SHA>
DELIVERY: <local merge or PR>
UNTOUCHED_CHANGES: <paths/hunks or none>
RISKS: <residual risks or none>
METRICS: <reconciled counters and efficiency signals>
```

## Checkpoints

Record state changes in the external ledger with source actor, snapshot, local plan hash, counters, and an evidence pointer. Store the latest processed message/cursor per persistent thread. Keep one current-state summary plus an append-only checkpoint log; do not copy actor transcripts or repeat superseded validation.

Use targeted reads only for missing or disputed evidence. After one explicit wait returns without a state change, stop polling and rely on the actor, publisher monitor, automation wake, or the user's next resume. Give long-running tool calls a sufficient initial yield so a routine completion does not require another model turn. Deduplicate checkpoints by source message/turn ID.

## Loop escape

Pause after two substantially identical failures or several implementation/review cycles with no measurable acceptance progress. Keep the existing worker and create one fresh read-only diagnostic against the current contract and candidate.

Route the result:

- implementation defect -> one revised strategy to the same worker;
- test-oracle problem -> targeted test/spec decision;
- public contract or scope problem -> `SCOPE_REVIEW` or `STOP_AND_REPLAN`;
- environment/permission problem -> `ORCHESTRATION_BLOCKED`;
- inconclusive -> one independent escalation, then user decision.

Before a fourth semantic plan revision, run `SCOPE_REVIEW` even when findings differ. If a continued exception then needs a fifth semantic revision, split, prototype, or simplify unless the user explicitly authorizes another whole-slice revision. Revision count remains a diagnostic trigger rather than a quality verdict.

## Orchestration blocked

Use `ORCHESTRATION_BLOCKED` for task-service, capacity, quota, host, worktree, permission, thread, or remote-state failures. Record the failed operation, actor IDs, retry evidence, and next safe action. Preserve the original worker and candidate. After one bootstrap/configuration failure, repair or change the execution environment before dispatching another worker; do not repeat the same failing bootstrap.

## Metrics

Track signals useful for improving the process:

- semantic plan revisions and scope reviews;
- product gaps versus implementation-detail findings;
- worker implementation/revision attempts;
- review rounds and stale axes;
- red-test size, surfaces, and revisions;
- changed production/test paths and lines;
- subagent versus persistent-thread turns;
- polling/automation wakes and unchanged-state polls;
- input, cached-input, output tokens, and estimated cost when available;
- dispatch-to-candidate, review-to-approval, and delivery elapsed time as observations, never gates.

Include reconciled signals in the final report so later runs can compare process quality without turning estimates into hard limits.
