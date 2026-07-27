---
title: "Spawn Patterns"
type: guide
tags: [dispatch, cli, agents, control-tower]
updated: 2026-07-24
---

# Spawn Patterns

CLI spawn commands for each tool — ready to copy-paste with placeholders.

## Executor prompt phải yêu cầu commit

Prompt `Execute task at <path>` trần trụi là **không đủ**. Ngày 2026-07-27, cả
3/3 executor của batch CTV2-088/095/102 hoàn thành và test xanh nhưng KHÔNG ai
commit — `git log` đứng yên, 674 dòng thay đổi của 3 task trộn chung trong một
working tree bẩn, không task nào có `result_ref` để phát `/review-order`.

Đây đúng là gap G4: `_parse_result_ref` chạy `git rev-parse HEAD` sau khi CLI
kết thúc, executor không commit thì nó trả về baseline → review diff rỗng →
verdict pass giả. Prompt executor vì vậy PHẢI kèm:

1. commit **chỉ** những file của task này (không đụng thay đổi dở dang của task chạy song song);
2. in commit hash ở dòng cuối theo dạng `RESULT_REF: <hash>`.

`scripts/ct-dispatch.py::build_prompt` đã nhúng sẵn yêu cầu này cho
`--role execute`.

**Không bao giờ chạy hai executor commit đồng thời trên cùng một working tree** —
chúng sẽ đua nhau trên `.git/index.lock`. Chạy tuần tự.

## Variables

- `<repo_root>` — from PROJECT REGISTRY in index.md
- `<model>` — from agent roster (`knowledge/agents/@<agent-id>.md`)
- `<task_path>` — absolute path to task file
- `<role>` — "Execute" or "Review"

## Claude Code

```bash
cd <repo_root> && claude --model <model> --effort <effort> -p "<role> task at <task_path>" --dangerously-skip-permissions < /dev/null
```

**Models:** claude-sonnet-5, claude-opus-5, claude-opus-4-5-20251101
**Effort:** low, medium, high — qua flag `--effort`. Bỏ flag = chạy ở effort
mặc định của CLI, KHÔNG phải effort ghi trong agent profile.

> Bài học 2026-07-27: `@claude-opus-5-medium` được spawn bằng
> `claude --model claude-opus-5` không kèm `--effort`, nên review chạy ở effort
> mặc định chứ không phải `medium` như profile khai. Effort trong
> `knowledge/agents/*.md` chỉ có tác dụng khi lệnh spawn thực sự truyền nó.

## Agy (Antigravity/Gemini)

```bash
cd <repo_root> && agy --model <model> --effort <effort> --print "<role> task at <task_path>" --dangerously-skip-permissions < /dev/null
```

**Flags:** `--model` (model name), `--effort` (low/medium/high), `--print` (prompt)

> `agy --help` liệt kê **cả** `--agent` lẫn `--model`, nên không suy ra được từ binary.
> Chốt 2026-07-27 (user): dùng `--model`. Guide trước đó ghi `--agent` là sai, và vì
> `ct-dispatch.py` tự validate lệnh với guide này nên nó đã từ chối dispatch mọi agent
> gemini/antigravity cho tới khi được sửa.
**Models:** gemini-2.5-flash, gemini-2.5-pro, gemini-3.6-flash
**Note:** Always add `< /dev/null` to prevent stdin hang

## Codex (OpenAI)

```bash
cd <repo_root> && codex exec -m <model> -c model_reasoning_effort=<effort> --dangerously-bypass-approvals-and-sandbox "<role> task at <task_path>"
```

Note: prompt is positional argument (at the end), NOT `-p` (that's `--profile`).

**Models:** gpt-5.6-luna, gpt-5.6-sol
**Effort:** low, medium, high (via `-c model_reasoning_effort=<effort>`)
**Tiers:** @gpt-5.6-luna-high = gpt-5.6-luna + effort=high

## Example

Task: `/home/lupca/projects/control-tower/projects/marketing-video-agent/tasks/MVA-001-simplify-architecture.md`
Agent: @gpt-5.6-luna-high
Repo: `/data/projects/marketing-video-agent`

```bash
cd /data/projects/marketing-video-agent && codex exec -m gpt-5.6-luna -c model_reasoning_effort=high --dangerously-bypass-approvals-and-sandbox "Execute task at /home/lupca/projects/control-tower/projects/marketing-video-agent/tasks/MVA-001-simplify-architecture.md"
```
