---
id: CT-028
title: "ct-dispatch.py + ct-review-order.py — script hoá phần cơ khí của /dispatch và /review-order"
status: done
priority: medium
risk: normal
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
result_ref: "b8ba2e2"
depends_on: [CT-027]
dispatched: 2026-07-24
in_review: 2026-07-24
files:
  - scripts/ct-dispatch.py
  - scripts/ct-review-order.py
  - scripts/test_ct_dispatch_review.py
  - .claude/skills/dispatch/SKILL.md
  - .claude/skills/review-order/SKILL.md
  - knowledge/decisions/ADR-010-dispatch-review-order-scripts.md
flows: [dispatch, review-order]
tests:
  - scripts/test_ct_dispatch_review.py
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "2 script mới + sửa 2 skill + ADR — blast rộng hơn CT-027 (-0.15)"
    - "no CI, chỉ sandbox (-0.1)"
confidence_interval: [0.65, 0.85]
created: 2026-07-24
updated: 2026-07-25
rejections: 1
---

# CT-028: ct-dispatch.py + ct-review-order.py

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh

Vòng execute→review lặp nhiều nhất mỗi session; phần cơ khí (tra registry+roster dựng lệnh spawn; set frontmatter + sinh phiếu review) hiện làm tay tốn token. Script hoá cả hai, dùng chung `ct_common.py` ([[CT-027-ct-common-frontmatter-module]]). Gộp 2 script vào 1 task vì cùng nền tảng + cùng executor/reviewer.

## Tiêu chí nghiệm thu (AC)

- [x] **AC1 (ct-dispatch.py):** `python3 scripts/ct-dispatch.py <ID> [--role execute|review] [--reviewer @id] [--print-only]` — đọc task frontmatter (executor/reviewer), tra `repo_root` từ PROJECT REGISTRY (`index.md`) + `model`/CLI từ agent profile (`knowledge/agents/@<id>.md`) + spawn-patterns, **dựng đúng lệnh** `agy --model.. --print` / `codex exec -m.. -c model_reasoning_effort=..` / `claude --model.. -p` cho đúng agent. Mặc định in lệnh ra (`--print-only`); nếu không `--print-only` thì set `status: dispatched` + `executor:` vào task (KHÔNG tự chạy lệnh spawn — coordinator/User chạy).
- [x] **AC2 (ct-review-order.py):** `python3 scripts/ct-review-order.py <ID> --ref <hash> --reviewer @id` — **four-eyes: refuse nếu reviewer == executor**; set task frontmatter (status→in-review, result_ref, in_review/updated); sinh phiếu `projects/<proj>/reviews/<ID>-review.md` bằng cách copy khối "## Tiêu chí nghiệm thu (AC)" + DoD + `tests:` từ task. In JSON tóm tắt.
- [x] **AC3:** Cả 2 script dùng `ct_common.py` (không lặp lại frontmatter/registry parse). `--dry-run` cho ct-review-order (không ghi file, in JSON dự kiến) giống ct-verdict-apply.
- [x] **AC4:** Cập nhật `.claude/skills/dispatch/SKILL.md` + `review-order/SKILL.md` gọi script (giữ phần cần LLM: chọn executor, câu hỏi rủi ro từ graph, log.md narrative). Fallback thủ công nếu script lỗi. + `ADR-010` (Project Gate: sửa skill phải có ADR). + test sandbox `scripts/test_ct_dispatch_review.py`.

## Notes

- **Bắt đầu SAU khi CT-027 done** (dùng `ct_common`). depends_on: CT-027.
- ct-dispatch **không tự spawn** — chỉ dựng + in lệnh (an toàn; tránh tự chạy process ngoài ý muốn). Coordinator/User copy chạy.
- ct-review-order giữ four-eyes như một hard check (giống ct-verdict-apply).
- control-tower là meta-project không graph → phần "câu hỏi rủi ro từ code-review-graph" trong review-order để LLM/skip, không nhét vào script.
- Nghiệm thu sandbox /tmp. Reviewer ≠ executor: executor @gpt-5.6-luna-high, reviewer @gpt-5.6-sol.

## Findings từ reviewer (round 1 — @gpt-5.6-sol, ref 9bbf6f4)
- [x] AC3 (import ct_common) + AC4 (2 SKILL gọi script, giữ Tool Preflight CT-025, ADR-010) **pass**; command shapes agy/codex/claude đúng, default print không exec, 6/6 test sandbox pass.
- [x] **F1 (High, AC2): copy AC block không fence-aware** → Fixed round 2 (b8ba2e2): `section()` fence-aware, giữ đủ AC + nội dung fence. @gpt-5.6-sol verified.
- [x] **F2 (High, AC1): reviewer dispatch không four-eyes** → Fixed round 2: `--role review` hard refuse exit 1 khi reviewer==executor, zero output/state. Verified.
- [x] **F3 (Medium, AC1): prompt không shell-safe** → Fixed round 2: shlex.quote single-quote wrapping, `$()`/backtick vô hiệu. Injection test verified.

## Kết quả (round 2 — @gpt-5.6-sol, ref b8ba2e2) → PASS
- 4/4 AC pass, suite 9/9, 0 regression (Tool Preflight CT-025 giữ nguyên). Đóng qua ct-verdict-apply.py (dry-run → real). Hoàn tất script hoá vòng dispatch/review-order.
