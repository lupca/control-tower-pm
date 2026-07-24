---
id: CT-027
task_path: projects/control-tower/tasks/CT-027-ct-common-frontmatter-module.md
project: control-tower
result_ref: 9ecd91d
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
status: passed
issued: 2026-07-24
verdict: pass
verdict_date: 2026-07-24
round: 2
---

## Round 2 (re-confirm sau khi nới scope — code KHÔNG đổi, ref vẫn 9ecd91d)
Round 1 = CHANGES: AC1/AC3/AC4 pass, LF byte-identical, suite 10/10, safety nguyên. AC2 chỉ fail vì report giờ CRLF-tolerant (trước LF-only) — không byte-identical cho task CRLF. **User đã duyệt nới scope**: chấp nhận CRLF-tolerance có chủ đích (nhất quán verdict/CT-026 AC4, fails-safe, repo toàn LF nên 0 tác động thật; giữ parser LF-only riêng sẽ phá mục tiêu dedup). AC2 đã revise trong task. **Chỉ cần xác nhận:** dưới AC2 (revised), deliverable 9ecd91d có pass không? (LF vẫn byte-identical + CRLF-tolerance là chủ đích ⇒ kỳ vọng pass). Không có commit mới.

# Phiếu Review: CT-027 — tách ct_common.py (frontmatter helpers dùng chung)

- Dự án: control-tower (`/home/lupca/projects/control-tower`) — meta-project
- Task gốc: `projects/control-tower/tasks/CT-027-ct-common-frontmatter-module.md`
- Result-ref: commit `9ecd91d` (branch `review/CT-027`) — diff so với `main`
- Executor: @gpt-5.6-luna-high
- Reviewer chỉ định: @gpt-5.6-sol (four-eyes: PHẢI ≠ @gpt-5.6-luna-high)
- Ngày phát phiếu: 2026-07-24

## Cách lấy diff (chỉ đọc)
```
cd /home/lupca/projects/control-tower
git diff main..9ecd91d -- scripts/ct_common.py scripts/ct-report-stats.py scripts/ct-verdict-apply.py scripts/test_ct_verdict_apply.py
```

## Acceptance Criteria cần verify
- [ ] **AC1:** `scripts/ct_common.py` tồn tại, gom `split_frontmatter`, `rebuild`, `fm_get`, `fm_set`, `fm_get_inline_list`, `find_task_file` (+ REPO_ROOT/FM_RE nếu có), mỗi hàm có docstring.
- [ ] **AC2:** `ct-report-stats.py` import từ `ct_common`, bỏ bản copy. CLI + JSON KHÔNG đổi — chạy `python3 scripts/ct-report-stats.py` (read-only) so JSON với `main` (byte-identical).
- [ ] **AC3:** `ct-verdict-apply.py` import từ `ct_common`, hành vi/CLI không đổi; `scripts/test_ct_verdict_apply.py` pass 10/10; giữ defense-in-depth (status+four-eyes trước mọi ghi), transactional write, re-verdict idempotency (1 dòng/task, không double-count executed), dry-run.
- [ ] **AC4:** Không còn duplicate frontmatter logic giữa 2 script (mỗi helper chung định nghĩa 1 lần trong ct_common). Có 1-2 unit test cho ct_common (fm_get/fm_set round-trip, split_frontmatter CRLF).

## Definition of Done
- [ ] Toàn bộ AC pass
- [ ] `scripts/test_ct_verdict_apply.py` xanh 100% (chạy thật trong /tmp)
- [ ] KHÔNG regression: mọi hành vi verdict/report giữ nguyên (refactor thuần, 0 đổi CLI/JSON/behavior)
- [ ] Reviewer ≠ executor (bạn @gpt-5.6-sol ≠ @gpt-5.6-luna-high)

## Kiểm tra rủi ro riêng
- Refactor dễ vô tình đổi hành vi: so JSON `ct-report-stats.py` (read-only) trước/sau = byte-identical? Chạy `git stash`/diff hoặc so với bản `main`.
- Verdict: chạy suite trong /tmp (KHÔNG chạy `ct-verdict-apply.py` thật lên repo — mutate agent-stats/prediction-accuracy). Xác nhận `--dry-run`, four-eyes-refuse, stale-status-refuse, transactional rollback vẫn đúng.
- Import: `ct_common` import gọn (cùng thư mục `scripts/`), không cần hack `sys.path` xấu.

## Review Toolchain
`cat .claude/review-toolchain.md` — không có → dùng /code-review mặc định + đọc script trực tiếp (meta-project markdown/python, không pytest CI).

## Trả kết quả
`/verdict CT-027 <pass|changes> --reviewer @gpt-5.6-sol [--commit 9ecd91d] [--notes "..."]`
