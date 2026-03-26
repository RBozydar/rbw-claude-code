# Workflow: Run a Full Setup Audit

<required_reading>
Read these files first:
1. `references/five-filters.md`
</required_reading>

<process>
## Step 1: Locate the active instruction surface

Find the files that can influence behavior in the current project. Include as many of these as exist:
- `CLAUDE.md`
- nested `CLAUDE.md` files
- skill files in local skill directories
- context folders or docs explicitly used as prompt scaffolding
- related instruction files for other tools if they duplicate Claude guidance

List what was found before analyzing.

## Step 2: Read the setup end-to-end

Read the relevant files completely before giving recommendations.

As you read, extract each distinct rule or instruction into a review list. Shorten long passages into atomic rules so they can be scored consistently.

## Step 3: Score each rule with the five filters

For each rule, determine:
- passes all filters
- cut candidate
- rewrite candidate
- merge candidate
- conflict needing user decision

Track the source file for each rule so recommendations are actionable.

## Step 4: Produce the audit report

Use this structure:

```markdown
## Setup Audit Report

### Instruction Surface
- [file]
- [file]
- [file]

### Summary
- Total rules reviewed: X
- Passed cleanly: X
- Flagged for cutting: X
- Flagged for rewrite/merge: X
- Conflicts found: X

### Cut Candidates
- "[rule]" — [one-line reason]

### Rewrite or Merge Candidates
- "[rule]" — [why it should be rewritten or merged]

### Conflicts
- [rule/source] vs [rule/source] — [conflict description]

### Minimal Root File Recommendation
- What belongs in root `CLAUDE.md`
- What should move out or stay elsewhere
```

## Step 5: Offer next actions

After the report, offer:
1. Draft a trimmed root file
2. Draft exact deletions/rewrites across files
3. Generate a recurring audit prompt
4. Stop at the report
</process>

<success_criteria>
The audit is complete when:
- The active instruction surface was listed
- Relevant files were read fully
- Rules were scored with the five filters
- Cut, rewrite, merge, and conflict candidates were identified
- The user received a clear report plus next-step options
</success_criteria>
