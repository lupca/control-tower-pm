---
type: guide
title: "Setup crg-daemon auto-start"
created: 2026-07-24
updated: 2026-07-24
---

# Setup crg-daemon Auto-Start

`code-review-graph` daemon giữ graph luôn sync với code. Cần auto-start để không bị outdated.

## Prerequisites

- `code-review-graph` đã cài trong venv: `/home/lupca/.local/share/code-review-graph-venv/`
- Các repo đã được add vào watch list: `crg daemon add <repo> --alias <name>`

## Option 1: Systemd User Service (Recommended)

```bash
# 1. Tạo service file
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/crg-daemon.service << 'EOF'
[Unit]
Description=Code Review Graph Daemon
After=network.target

[Service]
ExecStart=/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph daemon start --foreground
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

# 2. Enable và start
systemctl --user daemon-reload
systemctl --user enable crg-daemon
systemctl --user start crg-daemon

# 3. Verify
systemctl --user status crg-daemon
```

**Ưu điểm:**
- Chạy ngay khi login, không cần mở terminal
- Tự restart nếu crash
- Quản lý bằng systemctl chuẩn

**Commands hữu ích:**
```bash
systemctl --user status crg-daemon   # Check status
systemctl --user restart crg-daemon  # Restart
journalctl --user -u crg-daemon -f   # Xem logs
```

## Option 2: Shell Profile

Thêm vào `~/.bashrc` hoặc `~/.zshrc`:

```bash
# Auto-start crg-daemon if not running
(pgrep -f "code_review_graph daemon" > /dev/null) || \
  /home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph daemon start &>/dev/null &
```

**Ưu điểm:** Đơn giản, không cần systemd
**Nhược điểm:** Chỉ start khi mở terminal

## Verify Daemon Running

```bash
# Check daemon status
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph daemon status

# Expected output:
# Daemon:  running (PID xxxxx)
# ...
#   Alias       Status    PID       Path
#   topvnsport  alive     xxxxx     /home/lupca/projects/topvnsport
#   mva         alive     xxxxx     /data/projects/marketing-video-agent
#   ctw         alive     xxxxx     /home/lupca/projects/control-tower-web
```

## Add New Repo to Watch

```bash
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph daemon add <repo_path> --alias <short_name>

# Example:
# daemon add /home/lupca/projects/new-project --alias newproj
```

## Troubleshooting

**Graph outdated sau khi code change:**
```bash
# Manual rebuild
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph build --repo <path>

# Check if synced
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph status --repo <path> --json | jq '{built_at_commit, current_sha}'
```

**Daemon không start:**
```bash
# Check logs
journalctl --user -u crg-daemon --no-pager -n 50

# Or daemon's own logs
ls ~/.code-review-graph/logs/
```
