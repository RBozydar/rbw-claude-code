# Workflow: Trim and Validate a Bloated Setup

<required_reading>
Read these files first:
1. `references/five-filters.md`
2. `workflows/run-setup-audit.md`
</required_reading>

<process>
## Step 1: Start from an audit, not intuition

If no audit exists yet, run the audit workflow first.

Do not begin editing until you have:
- the instruction surface
- a cut list
- any conflicts called out
- a sense of what must remain in root

## Step 2: Draft the leaner setup

Create a proposed cleaned version of the root `CLAUDE.md` that keeps only:
- project identity and durable context
- package manager / commands the agent truly needs
- stable workflow constraints
- security or policy constraints
- references to deeper docs when needed

Cut or relocate:
- generic quality advice
- duplicated reminders
- one-off bandaid rules
- vague tone/style nudges
- stale or contradictory content

## Step 3: Present edits before applying

Show the user:
- what you would delete
- what you would rewrite
- what you would keep
- the cleaned root file draft

If conflicts require a preference decision, stop and ask before editing.

## Step 4: Apply changes only with approval

Once approved, make the edits. Keep changes surgical and easy to review.

## Step 5: Validate on common tasks

Ask for or infer the user's 3 most common Claude tasks. Prefer realistic recurring tasks over edge cases.

Use the trimmed setup to evaluate whether outputs:
- stayed the same
- got better
- got worse in one specific way

If a regression appears, add back only the minimal rule needed to restore that behavior.

## Step 6: Summarize the minimum viable setup

Report:
- before/after file size or rule count if practical
- what was removed
- what survived and why
- what, if anything, had to be restored after validation
</process>

<success_criteria>
Trimming is complete when:
- A cleaned setup draft exists
- The user approved edits before file changes
- Dead-weight rules were removed or rewritten
- The setup was validated on common tasks or a concrete validation plan was provided
- Only the minimum necessary instructions remain
</success_criteria>
