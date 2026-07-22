#!/bin/bash
# Update agent profile stats after verdict
# Usage: ./scripts/update-agent-stats.sh <agent_id> <role> <verdict>
#   agent_id: @claude-sonnet-medium
#   role: executor | reviewer
#   verdict: pass | changes
#
# Updates:
#   - total_tasks_executed / total_tasks_reviewed
#   - success_rate (for executor only)
#   - last_active
#   - recent_trend

set -e

AGENT_ID="$1"
ROLE="$2"
VERDICT="$3"

if [[ -z "$AGENT_ID" || -z "$ROLE" || -z "$VERDICT" ]]; then
    echo "Usage: $0 <agent_id> <role> <verdict>"
    echo "  agent_id: @claude-sonnet-medium"
    echo "  role: executor | reviewer"
    echo "  verdict: pass | changes"
    exit 1
fi

# Remove @ prefix if present
AGENT_ID="${AGENT_ID#@}"
PROFILE="/home/lupca/projects/control-tower/knowledge/agents/@${AGENT_ID}.md"

if [[ ! -f "$PROFILE" ]]; then
    echo "WARNING: Agent profile not found: $PROFILE"
    echo "Creating minimal profile..."
    mkdir -p "$(dirname "$PROFILE")"
    cat > "$PROFILE" << EOF
---
agent_id: "@${AGENT_ID}"
type: ai
total_tasks_executed: 0
total_tasks_reviewed: 0
success_rate: 1.0
avg_review_rounds: 1.0
strengths: []
weaknesses: []
recent_trend: stable
last_active: $(date +%Y-%m-%d)
---

# @${AGENT_ID}

## Performance Summary
*Auto-generated. No historical data yet.*
EOF
fi

TODAY=$(date +%Y-%m-%d)

# Helper: get YAML field value
get_field() {
    grep "^$1:" "$PROFILE" | head -1 | sed "s/^$1: *//"
}

# Helper: set YAML field value (uses temp file to avoid sed -i permission issues)
set_field() {
    local field="$1"
    local value="$2"
    if grep -q "^${field}:" "$PROFILE"; then
        local tmp=$(mktemp)
        sed "s|^${field}:.*|${field}: ${value}|" "$PROFILE" > "$tmp" && mv "$tmp" "$PROFILE"
    fi
}

# Get current stats
EXECUTED=$(get_field "total_tasks_executed")
REVIEWED=$(get_field "total_tasks_reviewed")
SUCCESS_RATE=$(get_field "success_rate")
TREND=$(get_field "recent_trend")

# Default values
EXECUTED=${EXECUTED:-0}
REVIEWED=${REVIEWED:-0}
SUCCESS_RATE=${SUCCESS_RATE:-1.0}

if [[ "$ROLE" == "executor" ]]; then
    # Increment executed count
    NEW_EXECUTED=$((EXECUTED + 1))
    set_field "total_tasks_executed" "$NEW_EXECUTED"

    # Recalculate success rate
    if [[ "$VERDICT" == "pass" ]]; then
        # Calculate: (old_rate * old_count + 1) / new_count
        NEW_RATE=$(echo "scale=2; ($SUCCESS_RATE * $EXECUTED + 1) / $NEW_EXECUTED" | bc)
        NEW_TREND="improving"
    else
        # Calculate: (old_rate * old_count) / new_count
        NEW_RATE=$(echo "scale=2; ($SUCCESS_RATE * $EXECUTED) / $NEW_EXECUTED" | bc)
        NEW_TREND="declining"
    fi

    set_field "success_rate" "$NEW_RATE"
    set_field "recent_trend" "$NEW_TREND"

    echo "Updated executor @${AGENT_ID}: executed=$NEW_EXECUTED, success_rate=$NEW_RATE, trend=$NEW_TREND"

elif [[ "$ROLE" == "reviewer" ]]; then
    # Increment reviewed count
    NEW_REVIEWED=$((REVIEWED + 1))
    set_field "total_tasks_reviewed" "$NEW_REVIEWED"

    echo "Updated reviewer @${AGENT_ID}: reviewed=$NEW_REVIEWED"
fi

# Update last_active
set_field "last_active" "$TODAY"

echo "Agent profile updated: $PROFILE"
