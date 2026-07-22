---
task_prefix: CT
next_task_id: 14
created: 2026-07-22
updated: 2026-07-22
---

# Control Tower (Meta-Project)

> Dự án quản lý chính hệ thống control-tower — nâng cấp quy trình, paradigm shifts, và self-improvement.

## Mô tả

Đây là meta-project: control-tower tự quản lý việc cải tiến chính nó. "Code" ở đây là các file Markdown (AGENTS.md, skills), configuration, và quy trình.

**repo_root:** `/home/lupca/projects/control-tower`

## Project Gates (Quy tắc phê duyệt riêng)

- Mọi thay đổi AGENTS.md hoặc skill phải có ADR đi kèm trong `knowledge/decisions/`
- Paradigm shift lớn (Tier 3) cần POC trước khi implement full

## References

- [AGENTS.md](../../AGENTS.md) — Rules of engagement
- [ADR-001-file-over-api](../../knowledge/decisions/ADR-001-file-over-api.md) — Founding decision
- [LLM-Modulo Framework (ICML 2024)](https://proceedings.mlr.press/v235/kambhampati24a.html)
- [STRATUS (NeurIPS 2025)](https://neurips.cc/virtual/2025/poster/116834)
- [Vericoding (Tegmark 2025)](https://arxiv.org/pdf/2509.22908)

## Tasks

- [[CT-001-pre-execution-prediction]] ✅
- [[CT-002-reputation-system]] ✅
- [[CT-003-causal-analysis]] ✅
- [[CT-004-cross-repo-intelligence]] ✅ (self-reviewed, waived — see CT-011)
- [[CT-005-llm-modulo-verifier]] ✅ (self-reviewed, waived — see CT-011)
- [[CT-006-confidence-calibration]] ✅ (self-reviewed, waived — see CT-011)
- [[CT-007-goal-conditioned-autonomy]] ✅ POC (self-reviewed, waived — see CT-011)
- [[CT-008-stigmergic-coordination]] ✅ POC (self-reviewed, waived — see CT-011)
- [[CT-009-auto-remediation-tnr]] ✅ POC (self-reviewed, waived — see CT-011)
- [[CT-010-vericoding-formal-proofs]] ✅ (self-reviewed, waived — see CT-011)
- [[CT-011-review-paradigm-shift-batch]] ✅ (reviewer: @claude-4.5, independent — compensating control confirmed batch)
- [[CT-012-model-a-cli-agent-orchestration]] 📋 todo (Spec Gate — TODO thiết kế Mô hình A: điều phối EXECUTE/REVIEW qua CLI, cần ADR-003)
- [[CT-013-horizontal-scaling-bottlenecks]] 📋 todo (Spec Gate — nghiên cứu bottleneck horizontal scaling: log.md shared-write, next_task_id race, events.jsonl gap, archive, state duplication)
