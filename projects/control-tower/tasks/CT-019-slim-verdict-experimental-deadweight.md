---
id: CT-019
title: "Tách experimental dead weight khỏi /verdict core flow"
status: dispatched
priority: high
risk: normal
deadline: null
executor: "@antigravity"
reviewer: null
result_ref: null
depends_on: []
files:
  - .claude/skills/verdict/SKILL.md
  - AGENTS-EXPERIMENTAL.md
  - .claude/skills/pm/SKILL.md
  - .claude/skills/pm/references/task-creation.md
  - .claude/skills/lint/SKILL.md
  - .claude/skills/review-order/SKILL.md
  - .claude/skills/goal/SKILL.md
flows: [verdict-pass, verdict-changes]
tests: []
dispatched: 2026-07-23
in_review: null
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "blast_radius: 7 (-0.0)"
    - "hub_bridge: false (-0.0)"
    - "no_tests: true — meta-project, no code tests (-0.1)"
    - "content_only: markdown refactor, no logic change (-0.0)"
    - "bonus: reduces token cost for all future sessions (+0.05)"
confidence_interval: [0.75, 0.95]
created: 2026-07-23
updated: 2026-07-23
---

# CT-019: Tách experimental dead weight khỏi /verdict core flow

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh

Nghiên cứu thực tế trên toàn bộ codebase (2026-07-23) cho thấy:

| Tính năng | § | Dữ liệu thật | Kết luận |
|:---|:---|:---|:---|
| Agent Reputation | §12 | 17 agent profiles, script chạy mỗi verdict | ✅ Đang dùng 100% |
| LLM-Modulo Verifier | §15 | `verifier-rules.yaml` tồn tại, MVA-001 có `## Verifier Results` | 🟡 Đã dùng thử |
| Confidence Calibration | §16 | 14 task có `confidence_interval:`, chưa auto-adjust gate | 🟡 Ghi field nhưng chưa tự động |
| Causal Analysis / Pattern | §13 | 4 pattern file — tất cả `Past Instances: (none yet)` | 🔴 Template rỗng |
| Cross-Repo Intelligence | §14 | `cross-repo/_index.md`: `*(none yet)*` | 🔴 0% sử dụng |
| Goal Autonomy | §17 | Không có file `GOAL-*.md` nào tồn tại | 🔴 0% sử dụng |
| Stigmergic Coordination | §18 | `events.jsonl` không tồn tại | 🔴 0% sử dụng |
| Auto-Remediation (TNR) | §19 | Không task nào có `tnr_spec:` hay `auto_remediated: true` | 🔴 0% sử dụng |
| Vericoding (Formal Spec) | §20 | Không task nào có `formal_spec:` (trừ CT-010 — task tự mô tả nó) | 🔴 0% sử dụng |

**Vấn đề:** `/verdict` SKILL.md (91 dòng) xử lý edge cases cho 12 concerns, trong đó 6 tính năng chưa từng trigger. Mỗi lần gọi `/verdict`, agent phải đọc toàn bộ + tham chiếu `AGENTS-EXPERIMENTAL.md` (~4K tokens). Tính chung các skill khác cũng reference file này → lãng phí token trên mọi session.

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1:** `AGENTS-EXPERIMENTAL.md` giữ nguyên nội dung làm tài liệu lưu trữ (archive) — không skill nào reference tới nữa.
- [ ] **AC2:** `/verdict` SKILL.md được rút gọn (≤ 55 dòng) — chỉ giữ core steps:
  1. Kiểm tra four-eyes (reviewer ≠ executor)
  2. Pass: cập nhật review sheet → tick AC → `status: done` → ghi `log.md` → chạy `update-agent-stats.sh` → ghi prediction accuracy
  3. Changes: cập nhật review sheet → thêm `## Findings` → `status: changes-requested` → ghi `log.md` → chạy `update-agent-stats.sh` → ghi prediction accuracy
  4. §13 (causal analysis) giữ inline nhưng rút gọn — chỉ trigger khi `risk: high`
  5. Xóa hẳn: §14 (cross-repo), §17 (goal escalation), §18 (stigmergic), §19 (auto-remediation/TNR), §20 (vericoding/formal spec) — 0% usage
  6. §16 (confidence interval) xóa khỏi verdict — chỉ `/pm` cần
- [ ] **AC3:** Các skill khác (`/pm`, `/lint`, `/review-order`, `/goal`) xóa reference tới `AGENTS-EXPERIMENTAL.md` cho các tính năng dormant (§14, §17, §18, §19, §20). Giữ reference cho §12, §13, §15, §16 nếu skill đó thực sự dùng.
- [ ] **AC4:** `AGENTS.md` header "Detail files" cập nhật ghi chú rằng `AGENTS-EXPERIMENTAL.md` là archive, không còn load mặc định.
- [ ] **AC5:** Không mất thông tin — `AGENTS-EXPERIMENTAL.md` giữ nguyên 271 dòng làm archive.

## Verification

- `wc -l .claude/skills/verdict/SKILL.md` → ≤ 55 dòng (từ 91)
- `wc -l AGENTS-EXPERIMENTAL.md` → giữ nguyên 271 dòng (archive, không sửa)
- `grep -c "AGENTS-EXPERIMENTAL.md" .claude/skills/verdict/SKILL.md` → 0 (không còn reference)
- `grep -r "§14\|§17\|§18\|§19\|§20" .claude/skills/verdict/SKILL.md` → 0 (xóa hẳn dormant features)
- `grep -c "§13" .claude/skills/verdict/SKILL.md` → ≥ 1 (causal analysis giữ inline, rút gọn)

## Plan

**Hướng B — Đơn giản hóa triệt để.** Không tạo thư mục mới. Không dùng "conditional load" (AI không tự biết load). Bật/tắt = có/không ghi trong SKILL.md.

### Nguyên tắc
1. `AGENTS-EXPERIMENTAL.md` giữ nguyên → archive (tài liệu lưu trữ, không skill nào trỏ tới)
2. `/verdict` SKILL.md xóa hẳn 5 tính năng dormant (§14, §17, §18, §19, §20), rút gọn §13, xóa §16
3. Các skill khác: xóa reference dormant, giữ reference cho tính năng đang dùng (§12, §15)
4. Muốn kích hoạt lại tính năng dormant trong tương lai → con người thêm lại instruction vào SKILL.md

### Thứ tự thực hiện
1. Sửa `.claude/skills/verdict/SKILL.md` — rút gọn từ 91 → ≤ 55 dòng
2. Sửa các skill khác — xóa reference dormant
3. Sửa `AGENTS.md` header — đánh dấu archive
4. Verify bằng các lệnh ở mục Verification

## Sub-tasks

- [x] Rút gọn `/verdict` SKILL.md: xóa §14, §17, §18, §19, §20; rút gọn §13; xóa §16 → 91 → 52 dòng ✅
- [x] Xóa reference dormant trong `/pm`, `/lint`, `/review-order`, `/goal` skills ✅
- [x] Cập nhật `AGENTS.md` header "Detail files" → đánh dấu archive ✅
- [x] Verify bằng các lệnh ở mục Verification ✅
