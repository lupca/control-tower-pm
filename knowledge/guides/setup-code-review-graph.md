# Setup code-review-graph cho project mới

> Guide cho agent khi onboard project mới vào control-tower

## Prerequisites

```bash
# Check if installed
which code-review-graph || echo "NOT INSTALLED"

# Install if needed
pip install code-review-graph
# hoặc
pipx install code-review-graph
```

---

## Quick Setup (one-liner)

```bash
~/projects/control-tower/templates/code-review-graph/setup.sh <project_root>
```

Script này chạy tất cả steps bên dưới. Hoặc làm thủ công từng bước.

---

## Tổng quan các bước

| Step | Mục đích | Tạo ra |
|------|----------|--------|
| 0 | Check Git | — |
| 1 | Auto Install | `.mcp.json` |
| 2 | Build Graph | `.code-review-graph/` |
| 3 | Copy Skills + Hooks | `.claude/skills/`, `.claude/settings.json` |
| 4 | Update CLAUDE.md | Section hướng dẫn dùng MCP tools |
| 5 | Test | Verify everything works |

---

## Step 0 — Check Git (BẮT BUỘC)

code-review-graph **yêu cầu git repo** để track files (`git ls-files`).

```bash
cd <project_root>
git status
```

### Nếu KHÔNG có git:

```bash
# ⚠️ HỎI USER TRƯỚC KHI INIT GIT
# "Project chưa có git. Có muốn init git repository không? [y/n]"

git init
git add .
git commit -m "Initial commit"
```

**Lưu ý:** 
- Không tự ý init git mà không hỏi user
- Nếu user từ chối → code-review-graph không hoạt động được, báo lại user

### Nếu CÓ git nhưng chưa có commit:

```bash
# Check
git log --oneline -1 2>/dev/null || echo "NO COMMITS"

# Nếu no commits:
git add .
git commit -m "Initial commit"
```

---

## Step 1 — Auto Install (RECOMMENDED)

```bash
cd <project_root>
code-review-graph install
```

Lệnh này tự động:
- Detect tất cả CLI tools (Claude Code, Codex, Antigravity, Cursor, etc.)
- Tạo `.mcp.json` với config đúng
- Cài hooks nếu platform hỗ trợ
- Inject instructions vào platform rules

### Target specific platform:

```bash
code-review-graph install --platform claude-code
code-review-graph install --platform codex
code-review-graph install --platform gemini-cli  # antigravity
code-review-graph install --platform cursor
```

---

## Step 2 — Build Graph

```bash
code-review-graph build
```

- Initial build: ~10 giây cho 500 files
- Subsequent updates: < 2 giây (incremental)

### Verify:

```bash
code-review-graph status
# Output: Files: X, Nodes: Y, Edges: Z

ls -la .code-review-graph/
# Phải có: graph.db, và các files khác
```

---

## Step 3 — Copy Skills + Hooks

Templates nằm trong `control-tower/templates/code-review-graph/`.

### 3a. Claude Code (`.claude/`)

```bash
cd <project_root>

# Copy skills (4 skills: debug-issue, explore-codebase, refactor-safely, review-changes)
mkdir -p .claude/skills
cp -r ~/projects/control-tower/templates/code-review-graph/.claude/skills/* .claude/skills/

# Copy settings.json (hooks auto-update graph on Edit/Write)
# Nếu đã có settings.json, merge hooks vào file hiện tại
cp ~/projects/control-tower/templates/code-review-graph/.claude/settings.json .claude/settings.json
```

### 3b. Codex / Antigravity (`.agents/`)

```bash
cd <project_root>
PROJECT_ROOT="$(pwd)"

# Copy skills + rules
mkdir -p .agents/{rules,skills}
cp -r ~/projects/control-tower/templates/code-review-graph/.agents/skills/* .agents/skills/
cp ~/projects/control-tower/templates/code-review-graph/.agents/rules/* .agents/rules/

# Copy MCP config + hooks (replace placeholder with actual path)
sed "s|__PROJECT_ROOT__|$PROJECT_ROOT|g" \
    ~/projects/control-tower/templates/code-review-graph/.agents/mcp_config.json > .agents/mcp_config.json

sed "s|__PROJECT_ROOT__|$PROJECT_ROOT|g" \
    ~/projects/control-tower/templates/code-review-graph/.agents/hooks.json > .agents/hooks.json
```

### Verify:

```bash
# Claude Code
ls .claude/skills/
# Output: debug-issue  explore-codebase  refactor-safely  review-changes

# Codex/Antigravity
ls .agents/
# Output: hooks.json  mcp_config.json  rules  skills
```

### Các skills có sẵn (cả 2 platforms):

| Skill | Mô tả |
|-------|-------|
| `debug-issue` | Debug issues bằng graph navigation |
| `explore-codebase` | Khám phá codebase qua architecture overview |
| `refactor-safely` | Refactor với dependency analysis |
| `review-changes` | Code review với risk scoring |

---

## Step 4 — Update CLAUDE.md

Thêm section hướng dẫn dùng MCP tools vào `CLAUDE.md`:

```bash
# Append snippet vào CLAUDE.md
cat ~/projects/control-tower/templates/code-review-graph/CLAUDE.md.snippet >> CLAUDE.md
```

**Hoặc copy nội dung sau vào cuối CLAUDE.md:**

```markdown
<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes_tool` or `query_graph_tool` instead of Grep
- **Understanding impact**: `get_impact_radius_tool` instead of manually tracing imports
- **Code review**: `detect_changes_tool` + `get_review_context_tool` instead of reading entire files
- **Finding relationships**: `query_graph_tool` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview_tool` + `list_communities_tool`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
| ------ | ---------- |
| `detect_changes_tool` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context_tool` | Need source snippets for review — token-efficient |
| `get_impact_radius_tool` | Understanding blast radius of a change |
| `get_affected_flows_tool` | Finding which execution paths are impacted |
| `query_graph_tool` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes_tool` | Finding functions/classes by name or keyword |
| `get_architecture_overview_tool` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes_tool` for code review.
3. Use `get_affected_flows_tool` to understand impact.
4. Use `query_graph_tool` pattern="tests_for" to check coverage.
```

---

## Step 5 — Test MCP Tools

Trong CLI (claude/codex/agy):

```
Build the code review graph for this project
```

Hoặc test trực tiếp:

```bash
code-review-graph query "main entry point"
code-review-graph detect-changes --brief
```

Test skills (trong Claude Code):

```
/explore-codebase
/review-changes
```

---

## Manual Setup (nếu auto install fail)

### Tạo .mcp.json manually:

```json
{
  "mcpServers": {
    "code-review-graph": {
      "command": "code-review-graph",
      "args": ["serve"],
      "cwd": "<ABSOLUTE_PATH_TO_PROJECT>",
      "type": "stdio"
    }
  }
}
```

**Hoặc** nếu dùng venv:

```json
{
  "mcpServers": {
    "code-review-graph": {
      "command": "/home/lupca/.local/share/code-review-graph-venv/bin/python3",
      "args": ["-m", "code_review_graph", "serve"],
      "cwd": "<ABSOLUTE_PATH_TO_PROJECT>",
      "type": "stdio"
    }
  }
}
```

---

## CLI Compatibility

| CLI | MCP Support | Install Command | Notes |
|-----|-------------|-----------------|-------|
| **Claude Code** | Native | `--platform claude-code` | Reads `.mcp.json` auto |
| **Antigravity (agy)** | Native | `--platform gemini-cli` | Reads `.mcp.json` auto |
| **Codex (OpenAI)** | Via flag | `--platform codex` | Needs `--mcp-config .mcp.json` |
| **Cursor** | Native | `--platform cursor` | Reads `.mcp.json` auto |
| **Windsurf** | Native | `--platform windsurf` | Reads `.mcp.json` auto |

### Spawn với MCP (từ control-tower):

```bash
# Claude Code
cd <repo> && claude -m <model> -p "..." --dangerously-skip-permissions

# Antigravity
cd <repo> && agy -m <model> -p "..."

# Codex (cần --mcp-config)
cd <repo> && codex exec -m <model> --mcp-config .mcp.json --dangerously-bypass-approvals-and-sandbox "..."
```

---

## Watch Mode (auto-update graph)

### Option 1: CLI watch

```bash
code-review-graph watch
# Runs in foreground, Ctrl+C to stop
```

### Option 2: Daemon (background, multi-repo)

```bash
# Register repos
crg-daemon add ~/project-a --alias proj-a
crg-daemon add ~/project-b

# Start daemon
crg-daemon start

# Check status
crg-daemon status
```

---

## Ignore Files

Tạo `.code-review-graphignore` tại project root:

```
generated/**
*.generated.ts
vendor/**
node_modules/**
dist/**
build/**
```

**Note:** Git-ignored files đã tự động bị skip. File này chỉ cần cho tracked files muốn exclude.

---

## Troubleshooting

### "Not a git repository"

```bash
# Solution: init git
git init && git add . && git commit -m "Initial commit"
```

### "Server not found" / MCP connection failed

```bash
# Check .mcp.json exists
cat .mcp.json

# Check cwd is absolute path
grep "cwd" .mcp.json

# Test serve manually
code-review-graph serve
```

### "Graph empty" / No nodes

```bash
# Check có source files
git ls-files | head -20

# Check language support
code-review-graph status

# Rebuild
code-review-graph build --force
```

### "Permission denied"

```bash
# Check executable
which code-review-graph
chmod +x $(which code-review-graph)
```

### Codex không thấy MCP tools

```bash
# Phải có --mcp-config flag
codex exec -m gpt-5.6-luna --mcp-config .mcp.json "..."
```

---

## Uninstall

```bash
# Preview (không xóa gì)
code-review-graph uninstall --dry-run

# Uninstall with confirmation
code-review-graph uninstall

# Uninstall without prompt
code-review-graph uninstall --yes

# Keep graph data, only remove integrations
code-review-graph uninstall --keep-data
```

---

## Quick Checklist

**Cơ bản:**
- [ ] Git repo tồn tại (`git status` OK)
- [ ] Có ít nhất 1 commit (`git log` OK)
- [ ] `code-review-graph install` chạy OK
- [ ] `code-review-graph build` chạy OK
- [ ] `code-review-graph status` shows nodes > 0
- [ ] `.mcp.json` tồn tại tại project root

**Claude Code (`.claude/`):**
- [ ] `.claude/skills/` có 4 thư mục (debug-issue, explore-codebase, refactor-safely, review-changes)
- [ ] `.claude/settings.json` có hooks PostToolUse và SessionStart
- [ ] `CLAUDE.md` có section "MCP Tools: code-review-graph"

**Codex/Antigravity (`.agents/`):**
- [ ] `.agents/skills/` có 4 thư mục
- [ ] `.agents/rules/code-review-graph.md` tồn tại
- [ ] `.agents/mcp_config.json` có absolute path đúng
- [ ] `.agents/hooks.json` có absolute path đúng

**Test:**
- [ ] `code-review-graph query "main"` returns results
- [ ] `/explore-codebase` skill works in Claude Code
- [ ] Codex với `--mcp-config .agents/mcp_config.json` thấy MCP tools
