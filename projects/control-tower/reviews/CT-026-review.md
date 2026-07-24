---
id: CT-026
task_path: projects/control-tower/tasks/CT-026-verdict-apply-reverdict-and-fence-edges.md
project: control-tower
result_ref: df97eb3
executor: "@antigravity"
reviewer: "@gpt-5.6-sol"
status: passed
issued: 2026-07-24
verdict: pass
verdict_date: 2026-07-24
round: 2
---

## Round 2 (re-review sau fix AC2) — ref 8304963
Round 1 (`df97eb3`) = CHANGES: AC1/AC3/AC4 pass, chỉ AC2 fail (`prev_verdict` lấy dòng khớp ĐẦU thay vì CUỐI → legacy `changes→pass` duplicate rồi `changes` mới thì `success_rate` giữ 1.0, đúng 0.0). Executor fix ở `8304963`: dùng dòng khớp CUỐI làm prev_verdict + regression test (suite 10/10).

**Chỉ re-verify AC2** (AC1/AC3/AC4 đã pass round 1). Delta round 2:
```
git diff df97eb3..8304963 -- scripts/ct-verdict-apply.py scripts/test_ct_verdict_apply.py
```
Dựng lại chính case round-1: legacy duplicate `changes→pass` cùng task + executor stats, chạy verdict `changes` mới (sandbox /tmp) → xác nhận `success_rate` chỉnh đúng `pass→changes` (1.0→0.0) và duplicates gộp về 1 dòng `changes`. Xác nhận không regress case first-verdict pass (executed +1).

# Phiếu Review: CT-026 — verdict-apply re-verdict idempotency + fence/CRLF edges

- Dự án: control-tower (`/home/lupca/projects/control-tower`)
- Task gốc: `projects/control-tower/tasks/CT-026-verdict-apply-reverdict-and-fence-edges.md`
- Result-ref: commit `df97eb3` (branch `review/CT-026`) — diff so với `main`
- Executor: @antigravity
- Reviewer chỉ định: @gpt-5.6-sol (four-eyes: PHẢI ≠ @antigravity — xác nhận trước verdict)
- Ngày phát phiếu: 2026-07-24

## Bối cảnh
Follow-up của CT-024 — sửa 2 flaw re-verdict (buộc phải ghi verdict tay khi làm CT-024) + 2 edge case. Bạn (@gpt-5.6-sol) đã review CT-024 nên quen `ct-verdict-apply.py`.

## Cách lấy diff (chỉ đọc)
```
cd /home/lupca/projects/control-tower
git diff main..df97eb3 -- scripts/ct-verdict-apply.py scripts/test_ct_verdict_apply.py knowledge/decisions/ADR-008-verdict-apply-script.md
```

## Acceptance Criteria cần verify
- [ ] **AC1 (re-verdict idempotent — prediction-accuracy):** verdict lại cùng task_id → **cập nhật dòng hiện có** (không append dòng trùng); còn đúng 1 dòng phản ánh outcome cuối; stats recompute đúng. Test thật: changes rồi pass cùng task → 1 dòng verdict=pass, và dọn được dòng trùng cũ nếu có.
- [ ] **AC2 (không double-count executed):** re-verdict KHÔNG tăng `total_tasks_executed` lần nữa; `success_rate` theo outcome cuối. Test: changes→pass cùng task → executed +1 tổng, success_rate đúng (không phải mỗi round +1).
- [ ] **AC3 (mixed-marker fence):** fenced block chỉ đóng bằng đúng marker đã mở (` ``` ` vs `~~~`); nested mixed-marker fence chứa `##` không cắt section AC sớm. Test: dựng case này, checkbox AC sau fence vẫn tick.
- [ ] **AC4 (CRLF, low):** task file `\r\n` xử lý được ở `split_frontmatter`/`FM_RE` (normalize), hoặc won't-fix có lý do.

## Definition of Done
- [ ] Toàn bộ AC pass
- [ ] Test suite `scripts/test_ct_verdict_apply.py` xanh 100% (kỳ vọng 9 test); chạy thật trong /tmp
- [ ] Không regression: mọi hành vi CT-024 đã pass (dry-run, In-Interval độc lập, scoped tick single-marker, transactional write + OSError, defense-in-depth status/four-eyes) vẫn nguyên
- [ ] Reviewer ≠ executor (bạn ≠ @antigravity)

## Kiểm tra rủi ro riêng
- AC2 là điểm dễ sai nhất: cơ chế phân biệt first-verdict vs re-verdict là gì? Nếu dựa vào "task đã có dòng prediction-accuracy" thì task pass-ngay-lần-đầu có bị nhầm không? Kiểm tra: task mới toanh (chưa có dòng) pass lần đầu → executed PHẢI +1.
- AC1 dọn "dòng trùng cũ": có xoá nhầm dòng task khác không? Verify chỉ gộp theo đúng task_id.
- Chạy verdict THẬT trên sandbox /tmp (KHÔNG trên repo thật — sẽ mutate agent-stats/prediction-accuracy).

## Review Toolchain
`cat .claude/review-toolchain.md` — không có → dùng /code-review mặc định + đọc script trực tiếp (meta-project).

## Trả kết quả
`/verdict CT-026 <pass|changes> --reviewer @gpt-5.6-sol [--commit df97eb3] [--notes "..."]`
