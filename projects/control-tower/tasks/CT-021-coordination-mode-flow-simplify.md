---
id: CT-021
title: "Coordination mode + đơn giản hóa task flow"
status: done
priority: medium
risk: normal
deadline: null
executor: "@gpt-5.6-sol"
reviewer: "@antigravity-3.1-pro"
result_ref: "ca2384b"
depends_on: []
files:
  - AGENTS.md
  - state/mode.md
  - .claude/skills/mode/mode.md
  - .claude/skills/pm/pm.md
  - .claude/skills/dispatch/dispatch.md
  - .claude/skills/review-order/review-order.md
  - .claude/skills/verdict/verdict.md
flows: []
tests: []
dispatched: 2026-07-23
in_review: 2026-07-23
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "meta-project, Markdown only — low blast radius (-0.0)"
    - "no code tests applicable (-0.0)"
    - "similar CT tasks (paradigm shifts) had high success rate (-0.0)"
    - "touches core AGENTS.md rules (-0.1)"
created: 2026-07-23
updated: 2026-07-23
closed: 2026-07-23
assigned_reviewer: "@antigravity-3.1-pro"
---

# CT-021: Coordination mode + đơn giản hóa task flow

> Dự án: [[projects/control-tower/control-tower]]

## Tiêu chí nghiệm thu (AC)

### Phần 1 — Coordination Mode
- [x] 3 levels định nghĩa trong AGENTS.md §4: `plan-only`, `supervised` (default), `bypass`
- [x] Skill `/mode <level>` hoạt động: ghi state vào `state/mode.md`, log vào `log.md`
- [x] `/mode` không có arg → hiển thị mode hiện tại
- [x] Protected actions (luôn hỏi dù bypass): delete task/project, bulk update >3 tasks
- [x] Hard rule (refuse, không prompt): reviewer==executor

### Phần 2 — Skill chạy single-invocation trong auto mode
- [x] Skills có gate (`/pm`, `/dispatch`, `/review-order`, `/verdict`) check mode tại mỗi gate
- [x] Supervised mode: STOP tại gate, chờ user confirm (multi-turn như hiện tại)
- [x] Bypass mode: continue ngay, không STOP (single-turn chạy hết)
- [x] **Actions (side effects) luôn chạy đầy đủ dù mode nào**: log.md, update agent stats, record prediction, etc.
- [x] Gate = checkpoint quyết định stop/continue, không phải cắt flow

### Phần 3 — Đơn giản hóa state machine
- [x] Bỏ state `ready` khỏi AGENTS.md §2.3
- [x] State machine mới: `todo → dispatched → in-review → done` (+ `changes-requested`)
- [x] Tách rõ trong §4: States (trạng thái task) vs Gates (checkpoints)
- [x] Bảng mode behavior cho từng gate trong §4

## Verification

- `grep -r "ready" AGENTS.md` → không còn `ready` như một status độc lập
- `cat state/mode.md` → file tồn tại với format YAML hợp lệ
- `ls .claude/skills/mode/` → skill tồn tại
- `grep "state/mode.md" .claude/skills/*/*.md` → các skill có gate đều check mode
- Test bypass mode: `/mode bypass` → `/pm` chạy Spec→Plan→Dispatch trong 1 turn
- Test side effects: sau `/verdict pass` trong bypass mode → verify agent stats updated

## Plan

### 1. Update AGENTS.md §2.3 — State machine
- Xóa `ready` khỏi diagram và mô tả
- State machine mới: `todo → dispatched → in-review → done` (+ `changes-requested` loop)
- Update mô tả từng state cho khớp

### 2. Update AGENTS.md §4 — Modes + Gates
- Tách rõ **States** (trạng thái task) vs **Gates** (checkpoints)
- Thêm bảng 3 modes:
  ```
  | Mode | Gates behavior | Protected |
  | plan-only | Block dispatch/verdict | n/a |
  | supervised | Prompt tại mỗi gate | Prompt |
  | bypass | Auto-approve, single-turn | Prompt |
  ```
- Định nghĩa Protected actions: delete task/project, bulk >3
- Hard rule: reviewer==executor → refuse (không phải mode-dependent)

### 3. Tạo state/mode.md
- Path: `state/mode.md`
- Format: `mode: supervised` (YAML đơn giản)
- Default: `supervised`

### 4. Tạo skill /mode
- Path: `.claude/skills/mode/SKILL.md`
- `/mode` → show current mode
- `/mode <level>` → validate level, update `state/mode.md`, log to `log.md`
- Levels: `plan-only`, `supervised`, `bypass`

### 5. Refactor skills với gate check
Mỗi skill thêm helper function `check_gate(gate_name)`:
```
1. Read state/mode.md
2. If plan-only + gate is dispatch/verdict → block
3. If bypass → log "auto-approved: <gate_name>", return true
4. If supervised → prompt, return user response
```

**5a. /pm** — 2 gates (Spec, Plan) + dispatch
- Sau Spec Gate actions → check_gate("spec")
- Sau Plan Gate actions → check_gate("plan") 
- Sau Dispatch actions → done
- Bypass mode: chạy hết trong 1 turn

**5b. /dispatch** — 1 gate
- check_gate("dispatch") trước spawn command

**5c. /review-order** — 1 gate
- check_gate("review-order") trước tạo review sheet

**5d. /verdict** — 1 gate + protected check
- check_gate("verdict") 
- Protected actions (delete) → luôn prompt dù bypass

## Sub-tasks

- [x] Update AGENTS.md §2.3: bỏ `ready`, state machine 4 trạng thái
- [x] Update AGENTS.md §4: định nghĩa 3 modes (plan-only, supervised, bypass) + bảng behavior + protected actions + tách States vs Gates
- [x] Tạo `state/mode.md` với default `supervised`
- [x] Tạo skill `/mode` trong `.claude/skills/mode/`
- [x] Refactor `/pm`: internal loop qua stages, check mode tại mỗi gate, continue nếu bypass
- [x] Refactor `/dispatch`: check mode, continue nếu bypass
- [x] Refactor `/review-order`: check mode, continue nếu bypass
- [x] Refactor `/verdict`: check mode (trừ protected actions), ensure side effects luôn chạy
