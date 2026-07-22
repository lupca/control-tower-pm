# Setup code-review-graph cho project mới

> Guide cho agent khi onboard project mới vào control-tower

## Prerequisites

code-review-graph đã được cài global tại:
```
/home/lupca/.local/share/code-review-graph-venv/
```

## Step 1 — Tạo .mcp.json

Tại root của project mới, tạo file `.mcp.json`:

```json
{
  "mcpServers": {
    "code-review-graph": {
      "command": "/home/lupca/.local/share/code-review-graph-venv/bin/python3",
      "args": [
        "-m",
        "code_review_graph",
        "serve"
      ],
      "cwd": "<ABSOLUTE_PATH_TO_PROJECT>",
      "type": "stdio"
    }
  }
}
```

**Thay `<ABSOLUTE_PATH_TO_PROJECT>`** bằng đường dẫn tuyệt đối, ví dụ:
- `/home/lupca/projects/topvnsport`
- `/data/projects/marketing-video-agent`

## Step 2 — Build graph lần đầu

```bash
cd <project_root>
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph build
```

Hoặc từ bất kỳ CLI nào có MCP:
```
mcp__code-review-graph__build_or_update_graph_tool(repo_root="<absolute_path>")
```

## Step 3 — Verify

```bash
# Check graph exists
ls -la <project_root>/.code-review-graph/

# Test query
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph query "main entry point"
```

## CLI Compatibility

| CLI | MCP Support | Notes |
|-----|-------------|-------|
| **Claude Code** | Native | Reads `.mcp.json` automatically |
| **Antigravity (agy)** | Native | Reads `.mcp.json` automatically |
| **Codex (OpenAI)** | Partial | Needs `--mcp-config .mcp.json` flag |

### Codex spawn với MCP

```bash
codex exec -m gpt-5.6-luna --mcp-config .mcp.json "task prompt"
```

## Troubleshooting

### "Server not found"
- Check `.mcp.json` exists at project root
- Check `cwd` path is absolute và đúng
- Check venv exists: `ls /home/lupca/.local/share/code-review-graph-venv/`

### "Graph empty"
- Run build: `python3 -m code_review_graph build`
- Check project có code (không phải empty repo)

### "Permission denied"
- Check venv có execute permission: `chmod +x .../bin/python3`

## Template .mcp.json

Copy-paste ready:

```json
{
  "mcpServers": {
    "code-review-graph": {
      "command": "/home/lupca/.local/share/code-review-graph-venv/bin/python3",
      "args": ["-m", "code_review_graph", "serve"],
      "cwd": "/home/lupca/projects/YOUR_PROJECT_NAME",
      "type": "stdio"
    }
  }
}
```
