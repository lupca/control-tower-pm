---
id: CT-012
title: "Mô hình A — Điều phối agent EXECUTE + REVIEW qua CLI (agy / claude / codex / copilot)"
status: done
priority: high
risk: high
deadline: null
executor: "@claude-opus-4.5"
reviewer: "@agy-cli"
result_ref: "control-tower@main (ADR-003 + design doc)"
depends_on: [CT-002, CT-007, CT-009]
files:
  - AGENTS.md §1 (bảng phân quyền PLAN/EXECUTE/REVIEW/COORDINATE)
  - AGENTS.md §4 (2 Gate + handoff)
  - knowledge/decisions/ADR-003-model-a-cli-agent-orchestration.md (mới — bắt buộc theo Project Gate)
  - CLAUDE.md (mô tả "Model B (current)" → thêm Model A opt-in)
  - .claude/skills/ (skill điều phối CLI mới, nếu chốt design)
flows: []
tests: []
dispatched: 2026-07-22
in_review: 2026-07-22
created: 2026-07-22
updated: 2026-07-22T19:55
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

- **Executor** = một CLI agent viết code, ví dụ: `agy` cli, `claude` cli, `codex` cli, `github copilot` cli.
- **Reviewer** = một CLI agent **KHÁC** đọc diff + chạy test (khuyến khích chạy `/code-review` của repo đích).
- control-tower chuyển từ "bảng handoff thụ động" → "orchestrator chủ động spawn agent", nhưng **vẫn giữ nguyên** four-eyes (`AGENTS.md` §1) và 2 Gate (§4).

Đây là **thay đổi vai trò nền tảng** so với Model B (đảo ngược invariant "control-tower NEVER writes code / NEVER runs tests"), nên phải là **opt-in song song** với Model B, không thay thế mặc định, và bắt buộc có ADR-003.

## Tiêu chí nghiệm thu (AC)

> AC ở đây là tiêu chí cho **bản thiết kế + ADR** (task này là spec/TODO), không phải cho code chạy được.

- [ ] AC1: ADR-003 (`knowledge/decisions/ADR-003-model-a-cli-agent-orchestration.md`) mô tả rõ Model A vs Model B: khi nào dùng cái nào, và khẳng định Model A là **opt-in**, Model B vẫn là mặc định — không âm thầm thay invariant của `AGENTS.md` §1.
- [ ] AC2: Thiết kế nêu cụ thể **cách gọi từng CLI ở chế độ non-interactive/headless** để làm executor (ít nhất `agy` cli, `claude` cli, `codex` cli, `github copilot` cli): lệnh, cách truyền AC/Plan của task làm prompt, cwd = `repo_root` lấy từ PROJECT REGISTRY (`index.md`), cách thu `result_ref` (branch/commit/PR) trả về.
- [ ] AC3: Thiết kế **bảo toàn four-eyes**: reviewer CLI phải khác executor CLI (ví dụ exec=`claude` cli → review=`copilot` cli), map rõ ràng vào `executor:`/`reviewer:` của task; `/verdict pass` vẫn từ chối khi `reviewer == executor`.
- [ ] AC4: Thiết kế nêu **ranh giới an toàn**: 2 Gate (§4) vẫn mandatory trước khi spawn executor; không auto-commit/auto-merge nếu chưa có `/verdict pass` + xác nhận người (nhất quán với §19.2 no-auto-commit của CT-009); ghi audit `log.md` (§7) cho mỗi lần spawn agent.
- [ ] AC5: Thiết kế chỉ ra **điểm tích hợp với hạ tầng paradigm-shift sẵn có**: dùng Reputation (CT-002) để chọn CLI-agent nào cho task nào, đặt trong khung Goal-Conditioned Autonomy (CT-007) và Auto-Remediation TNR (CT-009); liệt kê skill/thay đổi AGENTS.md cần có (chưa cần code).

## Plan

> Spec Gate đã được User duyệt (2026-07-22). Đây là kế hoạch **thiết kế** (deliverable = bản design + ADR-003), KHÔNG phải viết code sản phẩm. Sau khi User duyệt Plan này → `status: ready` → chọn `executor:` → `dispatched`.

### Step 1 — Khảo sát chế độ headless của các CLI (→ AC2)
Với từng CLI (`agy` cli, `claude` cli, `codex` cli, `github copilot` cli), xác định: lệnh chạy non-interactive (print/headless mode), cách truyền prompt (AC + Plan của task), cách set cwd = `repo_root` (lấy từ PROJECT REGISTRY `index.md`), exit code, và cách đọc `result_ref` trả về (branch/commit/PR). Ghi thành bảng so sánh trong design doc. Không cần chạy thật ở bước này — chỉ tra tài liệu/`--help`.

### Step 2 — Viết ADR-003 (→ AC1)
`knowledge/decisions/ADR-003-model-a-cli-agent-orchestration.md`: nêu Context (Model B invariant "control-tower NEVER writes code"), Decision (Model A là nhánh **opt-in song song**, Model B vẫn mặc định), Consequences, và tiêu chí "khi nào chọn Model A vs Model B". Bắt buộc theo Project Gate của control-tower.

### Step 3 — Thiết kế cơ chế orchestration + four-eyes (→ AC3)
Mô tả luồng: từ `status: dispatched`, control-tower spawn executor CLI trong `repo_root` với AC/Plan làm prompt → nhận `result_ref` → spawn **reviewer CLI khác** chạy `/code-review` của repo đích → map kết quả vào `/verdict`. Khẳng định `executor:`/`reviewer:` luôn là 2 CLI khác nhau; `/verdict pass` vẫn refuse khi `reviewer == executor`.

### Step 4 — Thiết kế ranh giới an toàn + audit (→ AC4)
Chốt các bất biến giữ nguyên: 2 Gate (§4) vẫn mandatory **trước** khi spawn executor; không auto-commit/auto-merge khi chưa `/verdict pass` + xác nhận người (nhất quán §19.2); mỗi lần spawn agent ghi 1 entry `log.md` (§7). Liệt kê các failure mode (CLI treo, sửa ngoài scope, tự commit) + cách chặn.

### Step 5 — Liệt kê điểm tích hợp & thay đổi cần có (→ AC5)
Chỉ ra (design-only, chưa code): dùng Reputation (CT-002) để chọn CLI-agent; đặt trong khung CT-007/CT-009; và danh sách thay đổi `AGENTS.md` §1/§4 + `CLAUDE.md` + skill điều phối mới sẽ phải làm ở các task kế tiếp.

### Step 6 — Đóng gói để review
Gom Step 1–5 thành design doc + ADR-003, đối chiếu đủ 5 AC, rồi handoff cho reviewer độc lập qua `/review-order` (reviewer ≠ executor). control-tower KHÔNG tự duyệt design của mình.

## Sub-tasks

- [ ] Khảo sát chế độ headless của `agy` cli, `claude` cli, `codex` cli, `github copilot` cli (lệnh, prompt, exit code, cách lấy commit/branch)
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
