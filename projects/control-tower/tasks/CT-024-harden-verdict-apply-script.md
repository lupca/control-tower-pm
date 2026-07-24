---
id: CT-024
title: "Harden ct-verdict-apply.py — dry-run, scoped ticks, độc lập In-Interval, ghi atomic"
status: done
priority: medium
risk: normal
deadline: null
executor: "@antigravity"
reviewer: "@claude-opus"
result_ref: "ea9897a"
depends_on: []
files:
  - scripts/ct-verdict-apply.py
  - scripts/test_ct_verdict_apply.py
  - .claude/skills/verdict/SKILL.md
  - knowledge/decisions/ADR-008-verdict-apply-script.md
flows: [verdict-pass, verdict-changes]
tests:
  - scripts/test_ct_verdict_apply.py
dispatched: 2026-07-24
in_review: 2026-07-24
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "code (không chỉ markdown) nhưng khu trú 1 file script (-0.1)"
    - "no_tests: meta-project, chỉ validate bằng sandbox thủ công (-0.1)"
confidence_interval: [0.7, 0.9]
created: 2026-07-24
updated: 2026-07-24
rejections: 2
---

# CT-024: Harden ct-verdict-apply.py — 4 điểm từ review

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh

Review phiên 2026-07-24 (sau khi merge ADR-008) tìm ra 4 điểm cần siết ở `scripts/ct-verdict-apply.py`. Script hiện đúng và có defense-in-depth (re-check `status: in-review` + four-eyes trước mọi lần ghi), đã qua 6 kịch bản sandbox — nhưng **chưa chạy trên task thật lần nào** và có vài chỗ ngữ nghĩa/độ bền cần cải thiện trước khi tin dùng rộng. Task này xử lý cả 4.

## Tiêu chí nghiệm thu (AC)

- [x] **AC1 (validate an toàn):** Thêm cờ `--dry-run` — script chạy hết logic trên **task thật**, in JSON kết quả dự kiến, nhưng **KHÔNG ghi** bất kỳ file nào (task, review sheet, prediction-accuracy, patterns, agent-stats). Cho phép xác nhận script "sống" trên dữ liệu thật mà không mutate state. Không bundle việc chạy `/verdict` thật lên WEB-005 (đó là đóng task thật, không phải test).
- [x] **AC2 (In-Interval độc lập):** Cột `In Interval?` trong `prediction-accuracy.md` tính độc lập, KHÔNG copy nguyên `Match?`. Quy tắc: parse `confidence_interval: [lo, hi]` từ frontmatter; với `pass` coi outcome ≈ 1.0, với `changes` coi outcome ≈ 0.0; `✅` nếu outcome nằm trong `[lo, hi]`, `❌` nếu ngoài, `—` nếu task không có `confidence_interval`. (Ghi rõ quy ước outcome→giá trị này vào §1 hoặc chú thích bảng của file metric.)
- [x] **AC3 (tick đúng phạm vi):** `pass` chỉ tick các checkbox `- [ ]` nằm trong section AC (`## Tiêu chí nghiệm thu (AC)` cho tới heading `##` kế tiếp), KHÔNG tick mù mọi `- [ ]` trong body (tránh tick nhầm checklist ở Plan/Notes). `checkboxes_ticked` trong JSON phản ánh đúng số đã tick.
- [x] **AC4 (ghi atomic):** Gom toàn bộ mutation, chỉ ghi khi tất cả bước tính toán thành công (hoặc ghi qua temp-file rồi `rename`), để lỗi giữa chừng không để lại state ghi dở (review sheet đã đổi nhưng task chưa, v.v.). Nếu một side-effect phụ (vd `update-agent-stats.sh`) fail thì báo trong JSON nhưng không làm hỏng các file lõi đã ghi nhất quán.

## Implementation

- Sửa `scripts/ct-verdict-apply.py`:
  - `--dry-run`: bọc mọi `path.write_text(...)` / `subprocess.run(update-agent-stats)` sau một guard `if not args.dry_run`, thu kết quả dự kiến vào JSON như thường; thêm `"dry_run": true` vào output.
  - `In Interval?`: thay dòng `in_interval = match_symbol if confidence_interval else "—"` bằng hàm parse `[lo, hi]` + so outcome (pass→1.0 / changes→0.0).
  - Tick: thay `tick_all_checkboxes(body)` (đang `body.replace("- [ ]", ...)`) bằng bản chỉ thao tác trong lát cắt section AC.
  - Atomic: tính trước (task_text_new, sheet_text_new, metric_text_new, ...), validate xong mới ghi lần lượt; cân nhắc temp+rename cho từng file.
- Cập nhật `.claude/skills/verdict/SKILL.md`: ghi chú `--dry-run` (khuyến nghị chạy dry-run 1 lần trước lần `pass` thật đầu tiên trên task thật).
- Cập nhật `ADR-008` (mục Consequences/Follow-up): 4 điểm hardening này + quy ước outcome→In-Interval. Không mở ADR mới — đây là tiến hoá của cùng quyết định.

## Notes

- Meta-project, không có graph/test suite → nghiệm thu bằng sandbox: tái tạo cây thư mục giả (task in-review + review sheet + prediction-accuracy + patterns) như ADR-008 đã làm, chạy `--dry-run` rồi chạy thật, `git diff` xác nhận đúng phạm vi. Reviewer ≠ executor (four-eyes).
- Không đổi hành vi defense-in-depth hiện có (status + four-eyes trước mọi ghi) — chỉ bổ sung.

## Findings từ reviewer (round 1 — @gpt-5.6-sol, ref 6006958)
- [x] AC3 (medium): tick_ac_checkboxes dùng substring replace → tick nhầm '- [ ]' trong ví dụ backtick. Fix round 2: line-anchored re.subn + skip code fence (edge case round 2 fix nốt ở round 3).
- [x] AC4a (high): ghi đa-file không rollback. → Fixed round 2: `transactional_write_all` temp+os.replace + rollback. Reviewer inject lỗi thật xác nhận rollback sạch.
- [x] AC4b (high): run_agent_stats không catch OSError. → Fixed round 2: catch → trả `{ran:false, error}` trong JSON. Verified.
- [x] Thiếu regression test → thêm `scripts/test_ct_verdict_apply.py` (4 test, pass).
- [x] AC1 + AC2 đã pass, giữ nguyên.

## Findings từ reviewer (round 2 — @gpt-5.6-sol, ref 74028a3)
- [x] AC3 (còn lại): hàm tìm ranh giới section AC (dò heading `##` kế tiếp) KHÔNG fence-aware — `##` trong fenced block bên trong section AC cắt section sớm. → Fixed round 3 (ea9897a): track fence state khi dò `## `; thêm test_ac3_fenced_code_with_heading_boundary (suite 5/5). @claude-opus verified independent.

## Kết quả (round 3 — @claude-opus, ref ea9897a) → PASS
- 4/4 AC verified pass; reviewer tự dựng edge case fence độc lập xác nhận fix đúng; test suite 5/5.
- **Deferred (non-blocking, ghi nợ):** F1 — mixed-marker nested fence (` ``` ` chứa `~~~` rồi `##`) vẫn cắt section sớm, nhưng **fails-closed** (bỏ sót tick, không corrupt), cực hiếm. F2 — task CRLF bị `FM_RE` reject upstream (repo toàn LF, không ảnh hưởng). Cả hai để follow-up cùng 2 flaw re-verdict của công cụ (append prediction-accuracy trùng, double-count executed khi re-verdict cùng task).
- Đóng bằng verdict thủ công (không chạy `ct-verdict-apply.py`) để né đúng 2 flaw re-verdict; prediction-accuracy sửa 1 dòng CT-024 (changes→pass), agent-stats @antigravity về 1.0 (CT-024 = success cuối cùng).
