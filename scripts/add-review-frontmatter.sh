#!/bin/bash
# Add YAML frontmatter to review files that don't have it
# Usage: ./scripts/add-review-frontmatter.sh [--dry-run]

set -e

DRY_RUN=false
[[ "$1" == "--dry-run" ]] && DRY_RUN=true

REVIEW_FILES=$(find /home/lupca/projects/control-tower -path "*/reviews/*-review.md" -type f 2>/dev/null)

for file in $REVIEW_FILES; do
    # Check if already has frontmatter
    if head -1 "$file" | grep -q "^---$"; then
        echo "SKIP (already has frontmatter): $file"
        continue
    fi

    TASK_ID=$(basename "$file" | sed 's/-review\.md$//')
    PROJECT=$(echo "$file" | sed 's|.*/projects/\([^/]*\)/reviews/.*|\1|')

    # Simple grep + sed extraction
    TASK_PATH=$(grep -i "task" "$file" | head -1 | grep -oE 'projects/[^`\]]+' | head -1)

    # Result ref: try backtick format first, then parenthesis format
    RESULT_REF=$(grep -i "result" "$file" | head -1 | sed 's/.*`\([^`]*\)`.*/\1/')
    # If still has markdown cruft, try commit hash in parentheses
    if echo "$RESULT_REF" | grep -q "Result"; then
        RESULT_REF=$(grep -i "result" "$file" | head -1 | grep -oE 'commit [a-f0-9]+' | sed 's/commit //' | head -1)
    fi

    EXECUTOR=$(grep -i "executor" "$file" | head -1 | grep -oE '@[a-zA-Z0-9._-]+' | head -1)
    ISSUED_DATE=$(grep -iE "ngày|issued|date" "$file" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)

    # Defaults
    [[ -z "$TASK_PATH" ]] && TASK_PATH="projects/${PROJECT}/tasks/${TASK_ID}.md"
    [[ -z "$RESULT_REF" ]] && RESULT_REF="null"
    [[ -z "$EXECUTOR" ]] && EXECUTOR="null"
    [[ -z "$ISSUED_DATE" ]] && ISSUED_DATE=$(date +%Y-%m-%d)

    FRONTMATTER="---
id: ${TASK_ID}
task_path: ${TASK_PATH}
project: ${PROJECT}
result_ref: ${RESULT_REF}
executor: ${EXECUTOR}
reviewer: null
status: pending
issued: ${ISSUED_DATE}
verdict: null
verdict_date: null
---
"

    if $DRY_RUN; then
        echo "=== $file ==="
        echo "$FRONTMATTER"
    else
        TEMP_FILE=$(mktemp)
        echo "$FRONTMATTER" > "$TEMP_FILE"
        cat "$file" >> "$TEMP_FILE"
        mv "$TEMP_FILE" "$file"
        echo "UPDATED: $file"
    fi
done

echo ""
if $DRY_RUN; then
    echo "Dry run complete. Run without --dry-run to apply."
else
    echo "Done."
fi
