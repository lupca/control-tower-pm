---
id: CT-026
title: "ct-verdict-apply.py: idempotent re-verdict + mixed-fence/CRLF edge cases (follow-up CT-024)"
status: done
priority: medium
risk: normal
deadline: null
executor: "@antigravity"
reviewer: "@gpt-5.6-sol"
result_ref: "8304963"
depends_on: [CT-024]
dispatched: 2026-07-24
in_review: 2026-07-24
files:
  - scripts/ct-verdict-apply.py
  - scripts/test_ct_verdict_apply.py
  - knowledge/decisions/ADR-008-verdict-apply-script.md
flows: [verdict-pass, verdict-changes]
tests:
  - scripts/test_ct_verdict_apply.py
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "code khu trú 1 script, đã có test harness sẵn (CT-024) (-0.1)"
    - "no_tests suite CI, chỉ chạy tay/sandbox (-0.1)"
confidence_interval: [0.7, 0.9]
created: 2026-07-24
updated: 2026-07-24
rejections: 1
---

# CT-026: ct-verdict-apply.py — idempotent re-verdict + fence/CRLF edges

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh

Trong lúc chạy [[CT-024-harden-verdict-apply-script]] end-to-end (3 round review thật), lộ ra 4 điểm non-blocking phải fix riêng — 2 flaw **re-verdict** (nghiêm trọng hơn, buộc phải ghi verdict THỦ CÔNG ở round 2 + round 3 để không hỏng dữ liệu) và 2 edge case còn lại của AC3/frontmatter. Gộp vào 1 task follow-up thay vì kéo dài CT-024.

## Tiêu chí nghiệm thu (AC)

- [x] **AC1 (re-verdict idempotent — prediction-accuracy):** `update_prediction_accuracy` KHÔNG append dòng mới nếu đã có dòng cho `task_id` đó — thay vào đó **cập nhật dòng hiện có** thành kết quả mới nhất (verdict/Match/In-Interval). Một task bị reject rồi cuối cùng pass chỉ để lại **đúng 1 dòng** phản ánh outcome cuối. Test: verdict changes rồi verdict pass cùng task → 1 dòng, verdict=pass.
- [x] **AC2 (re-verdict không double-count executed):** re-verdict cùng một task KHÔNG tăng `total_tasks_executed` của executor lần nữa (task chỉ được execute 1 lần dù nhiều round review). Cân nhắc: chỉ gọi `update-agent-stats.sh` executor ở lần verdict ĐẦU cho task, hoặc truyền cờ để phân biệt first-verdict vs re-verdict. `success_rate` phản ánh outcome cuối, không phải mỗi round. Test: changes→pass cùng task → executed +1 tổng cộng, success_rate đúng.
- [x] **AC3 (F1 — mixed-marker fence):** `tick_ac_checkboxes` chỉ đóng fenced block bằng **đúng marker đã mở** (``` ``` ``` chỉ đóng bởi ``` ``` ```, `~~~` chỉ đóng bởi `~~~`) khi dò ranh giới section AC. Case hiện fails-closed: một ` ``` ` block chứa dòng `~~~` rồi `##` làm scan tưởng hết fence sớm → cắt section. Test: AC section có nested mixed-marker fence chứa `##`, checkbox AC sau đó vẫn được tick.
- [x] **AC4 (F2 — CRLF frontmatter, low):** `FM_RE`/`split_frontmatter` tolerate task file CRLF (`\r\n`) — hiện `FM_RE` yêu cầu `\n` literal nên task CRLF fail ngay ở `split_frontmatter`. Repo hiện toàn LF nên priority thấp; có thể normalize `\r\n`→`\n` khi đọc. Test: task CRLF xử lý được (hoặc quyết định won't-fix có ghi lý do).

## Notes

- Bằng chứng gốc: log.md các entry verdict CT-024 round 2/3 (ghi tay vì đúng 2 flaw AC1/AC2 này) + phiếu review `CT-024-review.md` (F1/F2 non-blocking findings của @claude-opus).
- Giữ nguyên toàn bộ hành vi đã pass ở CT-024 (dry-run, In-Interval độc lập, scoped tick single-marker, transactional write + OSError). Chỉ bổ sung.
- Nghiệm thu bằng sandbox /tmp (meta-project, không CI). Reviewer ≠ executor (four-eyes).
- AC1/AC2 ưu tiên cao nhất (ảnh hưởng tính đúng của metric + agent-stats khi có re-verdict); AC3 fails-closed hiếm; AC4 low.

## Findings từ reviewer (round 1 — @gpt-5.6-sol, ref df97eb3)
- [x] AC1 pass; AC3 pass (mixed tilde/backtick không đóng chéo, `##` trong fence không cắt section); AC4 pass (CRLF normalize OK).
- [x] **AC2 (blocking):** `prev_verdict` lấy từ dòng khớp task_id **ĐẦU tiên** (`ct-verdict-apply.py:218`) thay vì cuối → legacy `changes→pass` duplicate rồi `changes` mới thì `success_rate` sai. → **Fixed round 2 (8304963):** dùng dòng khớp CUỐI làm `prev_verdict` + regression test. @gpt-5.6-sol re-review PASS.

## Kết quả (round 2 — @gpt-5.6-sol, ref 8304963) → PASS
- 4/4 AC pass, suite 10/10. Đóng bằng CHÍNH `ct-verdict-apply.py` đã fix (validation end-to-end thật đầu tiên của công cụ trên task thật): `--dry-run` preview OK rồi chạy thật — tick đúng 4 AC (scoped), prediction-accuracy thêm 1 dòng CT-026 (không trùng, `is_reverdict:false` đúng vì execute lần đầu), agent-stats @antigravity executed→7 (success 1.0), @gpt-5.6-sol reviewed→12. Cả 2 flaw re-verdict mà CT-024 gặp giờ đã hết.
