---
id: CT-021
task_path: projects/control-tower/tasks/CT-021-coordination-mode-flow-simplify.md
project: control-tower
result_ref: ca2384b
executor: "@gpt-5.6-sol"
reviewer: "@antigravity"
status: passed
issued: 2026-07-23
verdict: pass
verdict_date: 2026-07-23
---

# Phiếu Review: CT-021 — Coordination mode + đơn giản hóa task flow

- Dự án: control-tower (`/home/lupca/projects/control-tower`)
- Task gốc: `projects/control-tower/tasks/CT-021-coordination-mode-flow-simplify.md`
- Result-ref: ca2384b
- Executor: @gpt-5.6-sol
- Ngày phát phiếu: 2026-07-23

## Acceptance Criteria cần verify

### Phần 1 — Coordination Mode
- [ ] 3 levels định nghĩa trong AGENTS.md §4: `plan-only`, `supervised` (default), `bypass`
- [ ] Skill `/mode <level>` hoạt động: ghi state vào `state/mode.md`, log vào `log.md`
- [ ] `/mode` không có arg → hiển thị mode hiện tại
- [ ] Protected actions (luôn hỏi dù bypass): delete task/project, bulk update >3 tasks
- [ ] Hard rule (refuse, không prompt): reviewer==executor

### Phần 2 — Skill chạy single-invocation trong auto mode
- [ ] Skills có gate (`/pm`, `/dispatch`, `/review-order`, `/verdict`) check mode tại mỗi gate
- [ ] Supervised mode: STOP tại gate, chờ user confirm (multi-turn như hiện tại)
- [ ] Bypass mode: continue ngay, không STOP (single-turn chạy hết)
- [ ] **Actions (side effects) luôn chạy đầy đủ dù mode nào**: log.md, update agent stats, record prediction, etc.
- [ ] Gate = checkpoint quyết định stop/continue, không phải cắt flow

### Phần 3 — Đơn giản hóa state machine
- [ ] Bỏ state `ready` khỏi AGENTS.md §2.3
- [ ] State machine mới: `todo → dispatched → in-review → done` (+ `changes-requested`)
- [ ] Tách rõ trong §4: States (trạng thái task) vs Gates (checkpoints)
- [ ] Bảng mode behavior cho từng gate trong §4

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: *(meta-project, no code tests)*
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @gpt-5.6-sol)

## Verification commands
```bash
# Check ready state removed
grep -r "ready" AGENTS.md  # → không còn `ready` như một status độc lập

# Check mode file exists
cat state/mode.md  # → file tồn tại với format YAML hợp lệ

# Check mode skill exists
ls .claude/skills/mode/  # → skill tồn tại

# Check skills have gate check
grep "state/mode.md" .claude/skills/*/*.md  # → các skill có gate đều check mode
```

## Câu hỏi rủi ro
*(control-tower là meta-project, không có code-review-graph)*

- Các skill đã được refactor có đúng behavior tại mỗi mode không?
- ADR-006 có document đầy đủ design decisions không?
- `state/mode.md` có được tạo với default `supervised` không?

## Gợi ý công cụ
Đọc diff: `git show ca2384b` hoặc `git diff ca2384b^..ca2384b`

## Trả kết quả
Sau khi review xong, báo lại cho control-tower bằng lệnh:
`/verdict CT-021 <pass|changes> --reviewer @<tên bạn> --commit ca2384b [--notes "..."]`
