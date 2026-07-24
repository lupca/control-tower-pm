---
task_prefix: CT
next_task_id: 24
created: 2026-07-22
updated: 2026-07-23
---

# Control Tower (Meta-Project)

> Dự án quản lý chính hệ thống control-tower — nâng cấp quy trình, paradigm shifts, và self-improvement.

## Mô tả

Đây là meta-project: control-tower tự quản lý việc cải tiến chính nó. "Code" ở đây là các file Markdown (AGENTS.md, skills), configuration, và quy trình.

**repo_root:** `/home/lupca/projects/control-tower`

## Project Gates (Quy tắc phê duyệt riêng)

- Mọi thay đổi AGENTS.md hoặc skill phải có ADR đi kèm trong `knowledge/decisions/`
- Paradigm shift lớn (Tier 3) cần POC trước khi implement full

## Tiến độ
| Trạng thái | Số task |
|:---|---:|
| done | 22 |
| dispatched | 1 |
*(Cập nhật bởi `/report`)*

## References

- [AGENTS.md](../../AGENTS.md) — Rules of engagement
- [ADR-001-file-over-api](../../knowledge/decisions/ADR-001-file-over-api.md) — Founding decision
- [ADR-006-coordination-modes-and-task-states](../../knowledge/decisions/ADR-006-coordination-modes-and-task-states.md) — Coordination modes, Gates, and simplified task states
- [LLM-Modulo Framework (ICML 2024)](https://proceedings.mlr.press/v235/kambhampati24a.html)
- [STRATUS (NeurIPS 2025)](https://neurips.cc/virtual/2025/poster/116834)
- [Vericoding (Tegmark 2025)](https://arxiv.org/pdf/2509.22908)

## Tasks
*(Cập nhật bởi `/report` — mỗi lần chạy sẽ regenerate lại toàn bộ danh sách này từ `tasks/*.md`)*
- [[CT-001-pre-execution-prediction]] — Pre-Execution Prediction — Dự đoán task fail trước khi execute (done)
- [[CT-002-reputation-system]] — Reputation System — Track executor/reviewer performance (done)
- [[CT-003-causal-analysis]] — Causal Analysis — Hiểu WHY fix works, không chỉ THAT it works (done)
- [[CT-004-cross-repo-intelligence]] — Cross-Repository Intelligence — Learn patterns across repos (done)
- [[CT-005-llm-modulo-verifier]] — LLM-Modulo — Symbolic verifier cho LLM-generated plans (done)
- [[CT-006-confidence-calibration]] — Confidence Calibration — Know WHEN to escalate (done)
- [[CT-007-goal-conditioned-autonomy]] — Goal-Conditioned Autonomy — Từ task list sang goal pursuit (done)
- [[CT-008-stigmergic-coordination]] — Stigmergic Coordination — Agents coordinate qua shared artifacts (done)
- [[CT-009-auto-remediation-tnr]] — Auto-Remediation với TNR Safety — Closed-loop tự động (done)
- [[CT-010-vericoding-formal-proofs]] — Vericoding — Formal proofs thay vì testing (done)
- [[CT-011-review-paradigm-shift-batch]] — Independent Review — Paradigm Shift Batch (CT-004–CT-010) (done)
- [[CT-012-model-a-cli-agent-orchestration]] — Mô hình A — Điều phối agent EXECUTE + REVIEW qua CLI (agy / claude / codex / copilot) (done)
- [[CT-013-token-cost-automation-optimization]] — Đo baseline token cost của luồng manual (done)
- [[CT-014-fix-spawn-pattern-design]] — Sửa design doc spawn pattern: task file link + model tiering (done)
- [[CT-015-reorganize-agent-profiles]] — Tái cấu trúc agent profiles: tiering rõ ràng cho claude/antigravity/human (done)
- [[CT-016-terse-coordinator-mode]] — Coordinator terse mode: giảm output token, batch confirmations (done)
- [[CT-017-agent-roster-memory]] — Save agent roster + spawn patterns vào memory (done)
- [[CT-018-dispatch-skill]] — Tạo /dispatch skill — auto spawn CLI từ task + agent (done)
- [[CT-019-slim-verdict-experimental-deadweight]] — Tách experimental dead weight khỏi /verdict core flow (dispatched)
- [[CT-020-remove-agents-experimental]] — Xóa AGENTS-EXPERIMENTAL.md, archive dormant features (done)
- [[CT-021-coordination-mode-flow-simplify]] — Coordination mode + đơn giản hóa task flow (done)
- [[CT-022-reviewer-rotation]] — Reviewer Rotation — track rejections, enforce reviewer change (done)
- [[CT-023-ocr-review-toolchain]] — Tích hợp OCR vào review layer — review toolchain architecture (done)
