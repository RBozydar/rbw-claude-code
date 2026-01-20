#!/usr/bin/env bash
# gemini-review.sh - Clean wrapper for gemini code/plan reviews
#
# Usage:
#   gemini-review.sh --plan FILE [--model MODEL] [--focus "areas"]
#   gemini-review.sh --diff [--staged] [--model MODEL] [--focus "areas"]
#   gemini-review.sh --file FILE "prompt" [--model MODEL]
#
# Examples:
#   gemini-review.sh --plan plans/my-feature.md
#   gemini-review.sh --diff --staged
#   gemini-review.sh --file src/module.py "Check for security issues"

set -euo pipefail

# Defaults
MODEL="gemini-3-pro-preview"
MODE=""
FILE=""
PROMPT=""
FOCUS=""
STAGED=""

usage() {
    cat <<'EOF'
Usage: gemini-review.sh [options] [prompt]

Modes (pick one):
  --plan FILE      Review a plan/specification file
  --diff           Review git diff (unstaged by default)
  --file FILE      Review a specific file with custom prompt

Options:
  --staged         With --diff, review staged changes only
  --model MODEL    Model to use (default: gemini-3-pro-preview)
  --focus "areas"  Focus areas for review
  -h, --help       Show this help

Examples:
  gemini-review.sh --plan plans/feat-auth.md
  gemini-review.sh --diff --staged --focus "security,performance"
  gemini-review.sh --file src/api.py "Check for N+1 queries"
EOF
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --plan)
            MODE="plan"
            FILE="$2"
            shift 2
            ;;
        --diff)
            MODE="diff"
            shift
            ;;
        --file)
            MODE="file"
            FILE="$2"
            shift 2
            ;;
        --staged)
            STAGED="--cached"
            shift
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --focus)
            FOCUS="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            # Remaining args are the prompt
            PROMPT="$*"
            break
            ;;
    esac
done

if [[ -z "$MODE" ]]; then
    echo "Error: Must specify --plan, --diff, or --file" >&2
    usage
fi

# Build focus instruction if provided
FOCUS_INSTRUCTION=""
if [[ -n "$FOCUS" ]]; then
    FOCUS_INSTRUCTION="Focus especially on: $FOCUS."
fi

case "$MODE" in
    plan)
        if [[ ! -f "$FILE" ]]; then
            echo "Error: Plan file not found: $FILE" >&2
            exit 1
        fi
        cat "$FILE" | gemini --sandbox -o text -m "$MODEL" "You are a senior software architect reviewing a plan/specification.

Review this plan for:
1. Architectural soundness
2. Missing requirements or edge cases
3. Implementation risks
4. Scalability concerns
5. Unclear specifications
6. Security considerations

$FOCUS_INSTRUCTION

Provide specific, actionable feedback."
        ;;

    diff)
        DIFF_CMD="git diff $STAGED"
        DIFF_OUTPUT=$($DIFF_CMD)

        if [[ -z "$DIFF_OUTPUT" ]]; then
            echo "No changes to review" >&2
            exit 0
        fi

        echo "$DIFF_OUTPUT" | gemini --sandbox -o text -m "$MODEL" "You are a senior code reviewer. Review this diff for:
1. Bugs and logic errors
2. Security vulnerabilities
3. Performance issues
4. Code quality and maintainability
5. Missing error handling

$FOCUS_INSTRUCTION

Provide specific file:line references for each issue."
        ;;

    file)
        if [[ ! -f "$FILE" ]]; then
            echo "Error: File not found: $FILE" >&2
            exit 1
        fi

        if [[ -z "$PROMPT" ]]; then
            PROMPT="Review this code for issues, bugs, and improvements."
        fi

        cat "$FILE" | gemini --sandbox -o text -m "$MODEL" "$PROMPT $FOCUS_INSTRUCTION"
        ;;
esac
