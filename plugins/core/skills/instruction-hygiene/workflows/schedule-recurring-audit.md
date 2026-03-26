# Workflow: Schedule a Recurring Setup Audit

<required_reading>
Read these files first:
1. `references/five-filters.md`
2. `templates/weekly-audit-prompt.md`
</required_reading>

<process>
## Step 1: Choose the delivery format

Offer one of these outputs:
1. a reusable audit prompt the user can paste manually
2. a scheduled-task prompt for environments that support recurring tasks
3. both

## Step 2: Keep the recurring task read-only by default

The recurring audit should inspect and report. It should not edit files automatically unless the user explicitly wants autonomous rewriting.

Default report contents:
- what to cut
- why each item was flagged
- conflicts between files
- rough counts of passed vs flagged rules
- suggested cleaned root file changes

## Step 3: Generate the prompt

Base the generated prompt on the template, adjusting:
- file locations
- tool-specific wording
- recurrence cadence (weekly is the default)
- report destination if the environment supports delivery targets

## Step 4: Recommend a cadence

Use weekly by default for active setups. For slower-moving projects, recommend biweekly or monthly.

## Step 5: Remind the user how to act on reports

The recurring task should produce reports. The user or agent should review the report, then trim in batches and validate on common tasks rather than auto-deleting every flagged rule.
</process>

<success_criteria>
Scheduling work is complete when:
- The user has a reusable or scheduled audit prompt
- The prompt uses the five filters
- The task is read-only unless the user explicitly requested otherwise
- The cadence matches the user's maintenance needs
</success_criteria>
