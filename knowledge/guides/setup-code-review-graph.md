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

## Step 3 — Test MCP Tools

Trong CLI (claude/codex/agy):

```
Build the code review graph for this project
```

Hoặc test trực tiếp:

```bash
code-review-graph query "main entry point"
code-review-graph detect-changes --brief
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

- [ ] Git repo tồn tại (`git status` OK)
- [ ] Có ít nhất 1 commit (`git log` OK)
- [ ] `code-review-graph install` chạy OK
- [ ] `code-review-graph build` chạy OK
- [ ] `code-review-graph status` shows nodes > 0
- [ ] `.mcp.json` tồn tại tại project root
- [ ] Test query: `code-review-graph query "main"`
