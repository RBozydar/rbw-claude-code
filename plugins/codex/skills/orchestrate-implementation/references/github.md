# GitHub Delivery

## Authorization and ownership

Delegate every authenticated GitHub read or write to a dedicated Luna Medium publisher and run required `gh` commands outside the sandbox. Discover repository, parent/fork, and default branch before proposing destination. Explicit user policy selects push repository, base branch, merge authority, and publisher.

Default to a normal ready PR. Use a draft only when the user or repository workflow requires it.

## Publisher

Use a dedicated Luna Medium publisher. Give it the exact approved SHA, remote/head/base, PR title/body requirements, permitted remote operations, and main/worker IDs.

The publisher verifies approval freshness and confirms every local plan/task path is absent from the candidate diff. It then pushes the exact candidate, creates or updates the implementation PR, owns event-driven monitoring, and reports state changes. It does not publish plan-only PRs or implement feedback. Keep this monitoring out of the main orchestration context.

## Feedback and approval freshness

After each push, let configured checks and review sources reach terminal state, then collect and triage their feedback as one candidate-bound batch. Interrupt the batch only for an immediate high-severity safety event. Each audit checks:

- top-level comments;
- submitted reviews and review decision;
- inline comments and thread-resolution state;
- requested changes;
- required CI/check status;
- exact remote head and base;
- absence of local plan/task paths from the PR diff.

Use GraphQL when thread resolution matters. Save fetched feedback and the candidate-bound audit as local Markdown outside the delivery diff.

Classify feedback with the orchestration finding classes. Return introduced defects to the persistent worker. Route public-contract gaps to main. Record pre-existing and out-of-scope feedback separately.

After a candidate change, rerun final exact-SHA code verification and only the specialist axes affected by the change. Wording, metadata, branch, hash, or delivery-only corrections receive narrow closure review rather than a full cold specification restart.

Reply with evidence and resolve only satisfied threads.

## Monitoring and readiness

Prefer repository events, automation wakeups, or a publisher-owned monitor. Poll only when no event mechanism exists, use backoff, and keep unchanged-state polling inside the publisher's small context. Notify main only when state changes or a decision is required.

Any feedback, push, pending/failing check, requested change, or unresolved actionable thread resets readiness.

A PR is ready when, after the latest push:

- the remote head equals the approved candidate;
- all required checks are complete and green;
- actionable unresolved threads and comments are zero;
- requested changes are zero;
- required affected-axis approvals bind to the current head;
- mergeability and repository policy permit the selected next action.

Report `READY_FOR_HUMAN_REVIEW` or perform an explicitly authorized merge. If a required check remains red because of a proven pre-existing baseline failure, report `READY_EXCEPT_BASELINE_CI`; do not report `READY_FOR_HUMAN_REVIEW` or `DONE` until the required check is green or the user explicitly changes the delivery contract. Do not require arbitrary elapsed intervals or repeated clean polls when repository state already proves readiness.
