#!/bin/bash
# Setup code-review-graph for a project
# Usage: ./setup.sh <project_root> [--claude-only] [--codex-only]

set -e

PROJECT_ROOT="${1:-.}"
TEMPLATE_DIR="$(dirname "$0")"
SETUP_CLAUDE=true
SETUP_CODEX=true

# Parse flags
for arg in "$@"; do
    case $arg in
        --claude-only) SETUP_CODEX=false ;;
        --codex-only) SETUP_CLAUDE=false ;;
    esac
done

cd "$PROJECT_ROOT"
PROJECT_ROOT_ABS="$(pwd)"

echo "=== Step 0: Check git ==="
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "ERROR: Not a git repository. Run: git init && git add . && git commit -m 'Initial'"
    exit 1
fi
echo "✓ Git repo OK"

echo ""
echo "=== Step 1: Install MCP config ==="
if command -v code-review-graph >/dev/null 2>&1; then
    code-review-graph install
else
    echo "WARNING: code-review-graph not installed. Run: pipx install code-review-graph"
fi

echo ""
echo "=== Step 2: Build graph ==="
if command -v code-review-graph >/dev/null 2>&1; then
    code-review-graph build
    code-review-graph status
fi

echo ""
echo "=== Step 3a: Copy Claude Code config ==="
if [ "$SETUP_CLAUDE" = true ]; then
    mkdir -p .claude/skills
    cp -r "$TEMPLATE_DIR/.claude/skills/"* .claude/skills/
    echo "✓ Copied 4 skills to .claude/skills/"

    if [ -f .claude/settings.json ]; then
        echo "WARNING: .claude/settings.json exists. Merge hooks manually from:"
        echo "  $TEMPLATE_DIR/.claude/settings.json"
    else
        cp "$TEMPLATE_DIR/.claude/settings.json" .claude/settings.json
        echo "✓ Created .claude/settings.json with hooks"
    fi
else
    echo "SKIPPED (--codex-only)"
fi

echo ""
echo "=== Step 3b: Copy Codex/Antigravity config ==="
if [ "$SETUP_CODEX" = true ]; then
    mkdir -p .agents/{rules,skills}
    cp -r "$TEMPLATE_DIR/.agents/skills/"* .agents/skills/
    cp "$TEMPLATE_DIR/.agents/rules/"* .agents/rules/
    echo "✓ Copied skills + rules to .agents/"

    # Copy and replace __PROJECT_ROOT__ placeholder
    if [ -f .agents/mcp_config.json ]; then
        echo "WARNING: .agents/mcp_config.json exists. Merge manually from:"
        echo "  $TEMPLATE_DIR/.agents/mcp_config.json"
    else
        sed "s|__PROJECT_ROOT__|$PROJECT_ROOT_ABS|g" "$TEMPLATE_DIR/.agents/mcp_config.json" > .agents/mcp_config.json
        echo "✓ Created .agents/mcp_config.json"
    fi

    if [ -f .agents/hooks.json ]; then
        echo "WARNING: .agents/hooks.json exists. Merge manually from:"
        echo "  $TEMPLATE_DIR/.agents/hooks.json"
    else
        sed "s|__PROJECT_ROOT__|$PROJECT_ROOT_ABS|g" "$TEMPLATE_DIR/.agents/hooks.json" > .agents/hooks.json
        echo "✓ Created .agents/hooks.json"
    fi
else
    echo "SKIPPED (--claude-only)"
fi

echo ""
echo "=== Step 4: Update CLAUDE.md ==="
if [ -f CLAUDE.md ]; then
    if grep -q "code-review-graph MCP tools" CLAUDE.md; then
        echo "CLAUDE.md already has code-review-graph section"
    else
        cat "$TEMPLATE_DIR/CLAUDE.md.snippet" >> CLAUDE.md
        echo "✓ Appended MCP tools section to CLAUDE.md"
    fi
else
    echo "WARNING: CLAUDE.md not found. Create it first, then run:"
    echo "  cat $TEMPLATE_DIR/CLAUDE.md.snippet >> CLAUDE.md"
fi

echo ""
echo "=== Done! ==="
echo "Test with: code-review-graph query 'main'"
echo ""
echo "Platforms configured:"
[ "$SETUP_CLAUDE" = true ] && echo "  ✓ Claude Code (.claude/)"
[ "$SETUP_CODEX" = true ] && echo "  ✓ Codex/Antigravity (.agents/)"
