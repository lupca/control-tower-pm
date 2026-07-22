---
id: CT-012
title: "Mô hình A — Điều phối agent EXECUTE + REVIEW qua CLI (agy / claude / copilot)"
status: todo
priority: high
risk: high
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: [CT-002, CT-007, CT-009]
files:
  - AGENTS.md §1 (bảng phân quyền PLAN/EXECUTE/REVIEW/COORDINATE)
  - AGENTS.md §4 (2 Gate + handoff)
  - knowledge/decisions/ADR-003-model-a-cli-agent-orchestration.md (mới — bắt buộc theo Project Gate)
  - CLAUDE.md (mô tả "Model B (current)" → thêm Model A opt-in)
  - .claude/skills/ (skill điều phối CLI mới, nếu chốt design)
flows: []
tests: []
dispatched: null
in_review: null
created: 2026-07-22
updated: 2026-07-22
tier: 3
paradigm_source: "Model A — control-tower as active CLI-agent orchestrator (đối lập Model B hiện tại)"
---

# CT-012: Mô hình A — Điều phối agent EXECUTE + REVIEW qua CLI

> Dự án: [[projects/control-tower/control-tower]]
>
> ⚠️ **Đây là task TODO / thiết kế (spec-only).** Chỉ tạo task để nắm ý tưởng, CHƯA implement. Phải qua Spec Gate → Plan Gate (`AGENTS.md` §4) và **có ADR-003 đi kèm** (Project Gate của control-tower: mọi thay đổi AGENTS.md phải có ADR) trước khi được dispatch.

## Bối cảnh (Context)

**Mô hình B (hiện tại — mặc định):** control-tower CHỈ `PLAN` + `COORDINATE`. Nó không bao giờ viết code, không đọc diff, không chạy test. `EXECUTE` (viết code) và `REVIEW` (đọc diff, chạy test) đều nằm **ngoài hệ** — do người hoặc một AI khác tự làm trong repo đích, độc lập với nhau (reviewer ≠ executor). control-tower chỉ phát phiếu (`/review-order`) và ghi kết quả (`/verdict`).

**Mô hình A (đề xuất trong task này):** control-tower **chủ động điều phối** `EXECUTE` và `REVIEW` bằng cách gọi các **coding-agent CLI** ở chế độ headless/non-interactive, ngay trong `repo_root` của dự án đích:

- **Executor** = một CLI agent viết code, ví dụ: `agy` cli, `claude` cli, `github copilot` cli.
- **Reviewer** = một CLI agent **KHÁC** đọc diff + chạy test (khuyến khích chạy `/code-review` của repo đích).
- control-tower chuyển từ "bảng handoff thụ động" → "orchestrator chủ động spawn agent", nhưng **vẫn giữ nguyên** four-eyes (`AGENTS.md` §1) và 2 Gate (§4).

Đây là **thay đổi vai trò nền tảng** so với Model B (đảo ngược invariant "control-tower NEVER writes code / NEVER runs tests"), nên phải là **opt-in song song** với Model B, không thay thế mặc định, và bắt buộc có ADR-003.

## Tiêu chí nghiệm thu (AC)

> AC ở đây là tiêu chí cho **bản thiết kế + ADR** (task này là spec/TODO), không phải cho code chạy được.

- [ ] AC1: ADR-003 (`knowledge/decisions/ADR-003-model-a-cli-agent-orchestration.md`) mô tả rõ Model A vs Model B: khi nào dùng cái nào, và khẳng định Model A là **opt-in**, Model B vẫn là mặc định — không âm thầm thay invariant của `AGENTS.md` §1.
- [ ] AC2: Thiết kế nêu cụ thể **cách gọi từng CLI ở chế độ non-interactive/headless** để làm executor (ít nhất `agy` cli, `claude` cli, `github copilot` cli): lệnh, cách truyền AC/Plan của task làm prompt, cwd = `repo_root` lấy từ PROJECT REGISTRY (`index.md`), cách thu `result_ref` (branch/commit/PR) trả về.
- [ ] AC3: Thiết kế **bảo toàn four-eyes**: reviewer CLI phải khác executor CLI (ví dụ exec=`claude` cli → review=`copilot` cli), map rõ ràng vào `executor:`/`reviewer:` của task; `/verdict pass` vẫn từ chối khi `reviewer == executor`.
- [ ] AC4: Thiết kế nêu **ranh giới an toàn**: 2 Gate (§4) vẫn mandatory trước khi spawn executor; không auto-commit/auto-merge nếu chưa có `/verdict pass` + xác nhận người (nhất quán với §19.2 no-auto-commit của CT-009); ghi audit `log.md` (§7) cho mỗi lần spawn agent.
- [ ] AC5: Thiết kế chỉ ra **điểm tích hợp với hạ tầng paradigm-shift sẵn có**: dùng Reputation (CT-002) để chọn CLI-agent nào cho task nào, đặt trong khung Goal-Conditioned Autonomy (CT-007) và Auto-Remediation TNR (CT-009); liệt kê skill/thay đổi AGENTS.md cần có (chưa cần code).

## Plan

*(Chưa điền — chờ Plan Gate. Task này mới ở Spec Gate: `status: todo`, đang chờ User duyệt scope & AC. Sau khi duyệt Spec sẽ điền `## Plan` cụ thể rồi mới chuyển `ready`/`dispatched`.)*

## Sub-tasks

- [ ] Khảo sát chế độ headless của `agy` cli, `claude` cli, `github copilot` cli (lệnh, prompt, exit code, cách lấy commit/branch)
- [ ] Viết ADR-003 (Model A opt-in vs Model B mặc định) — bắt buộc theo Project Gate
- [ ] Thiết kế cơ chế giữ four-eyes khi executor/reviewer đều là CLI agent
- [ ] Thiết kế ranh giới an toàn: gates vẫn mandatory, no-auto-commit, audit từng lần spawn
- [ ] Xác định thay đổi cần có ở `AGENTS.md` §1/§4 + `CLAUDE.md` + skill điều phối

## Research References

- [CLAUDE.md](../../../CLAUDE.md) — định nghĩa "Model B (current)"; Model A sẽ là nhánh opt-in song song.
- [AGENTS.md §1](../../../AGENTS.md) — bảng phân quyền hiện tại (PLAN/EXECUTE/REVIEW/COORDINATE) mà Model A sẽ nới ra.
- [[CT-002-reputation-system]] — chọn CLI-agent theo reputation.
- [[CT-007-goal-conditioned-autonomy]] — khung autonomy để đặt Model A vào.
- [[CT-009-auto-remediation-tnr]] — nguyên tắc no-auto-commit (§19.2) mà Model A phải tuân.
