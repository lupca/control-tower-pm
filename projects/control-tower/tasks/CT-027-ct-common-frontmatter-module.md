---
id: CT-027
title: "Tách ct_common.py — module frontmatter dùng chung cho các script control-tower"
status: done
priority: medium
risk: normal
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
result_ref: "9ecd91d"
depends_on: []
dispatched: 2026-07-24
in_review: 2026-07-24
files:
  - scripts/ct_common.py
  - scripts/ct-report-stats.py
  - scripts/ct-verdict-apply.py
  - scripts/test_ct_verdict_apply.py
flows: [report, verdict-pass, verdict-changes]
tests:
  - scripts/test_ct_verdict_apply.py
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "refactor thuần, có test harness sẵn (-0.1)"
    - "đụng ct-verdict-apply.py — script mutate state thật, cần cẩn thận (-0.1)"
confidence_interval: [0.7, 0.9]
created: 2026-07-24
updated: 2026-07-24
rejections: 1
---

# CT-027: Tách ct_common.py — frontmatter helpers dùng chung

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh

`scripts/ct-report-stats.py` và `scripts/ct-verdict-apply.py` **lặp lại** logic parse/ghi YAML frontmatter (split_frontmatter, fm_get, fm_set, fm_get_inline_list, find_task_file, rebuild...). Tách ra 1 module chung để: (a) mọi script mới sau này (`ct-dispatch.py`, `ct-review-order.py`, `ct-lint.py` — [[CT-028-dispatch-review-order-scripts]]) dùng lại, ít code hơn; (b) sửa 1 chỗ, đúng mọi nơi. Làm TRƯỚC & riêng để dễ test (nền tảng cho CT-028).

## Tiêu chí nghiệm thu (AC)

- [x] **AC1:** Tạo `scripts/ct_common.py` gom các helper frontmatter/task dùng chung đang bị lặp ở 2 script: tối thiểu `split_frontmatter`, `rebuild`, `fm_get`, `fm_set`, `fm_get_inline_list`, `find_task_file` (+ `REPO_ROOT`/`FM_RE` nếu hợp lý). Có docstring ngắn mỗi hàm.
- [x] **AC2 (revised):** `ct-report-stats.py` import từ `ct_common` (bỏ bản copy) — CLI + JSON **byte-identical cho dữ liệu LF** (repo toàn LF: verified 0 diff read-only + --apply). **CRLF:** report giờ CRLF-tolerant (kế thừa `split_frontmatter` chung của ct_common) — đây là thay đổi **CÓ CHỦ ĐÍCH** (nới scope theo review CT-027 round 1): nhất quán với verdict (CT-026 AC4), fails-safe (parse thay vì trả MISSING). KHÔNG giữ parser LF-only riêng cho report vì sẽ phá đúng mục tiêu dedup của task này.
- [x] **AC3:** `ct-verdict-apply.py` import từ `ct_common` (bỏ bản copy) — hành vi/CLI KHÔNG đổi; `scripts/test_ct_verdict_apply.py` vẫn **10/10 pass**. Giữ nguyên defense-in-depth (status + four-eyes trước mọi ghi), transactional write, re-verdict idempotency, dry-run.
- [x] **AC4:** Không có duplicate frontmatter logic còn sót giữa 2 script (mỗi helper chung chỉ định nghĩa 1 lần, trong `ct_common.py`). Thêm 1-2 unit test cho `ct_common` (vd fm_get/fm_set round-trip, split_frontmatter CRLF).

## Notes

- **KHÔNG đổi CLI signature / JSON schema / hành vi** của 2 script — đây là refactor nội bộ thuần. Nếu import path cần `sys.path` thì làm gọn (2 script cùng thư mục `scripts/` với `ct_common.py` nên import trực tiếp được).
- `/report` và `/verdict` skill gọi 2 script này qua CLI → CLI giữ nguyên nên **không cần sửa skill, không cần ADR mới** (Project Gate chỉ trigger khi đổi skill/AGENTS).
- Nghiệm thu bằng sandbox /tmp cho phần verdict (KHÔNG chạy script mutate lên repo thật); report có thể chạy read-only trên repo thật (không --apply) để so JSON.
- Reviewer ≠ executor (four-eyes): executor @gpt-5.6-luna-high, reviewer @gpt-5.6-sol.

## Findings từ reviewer (round 1 — @gpt-5.6-sol, ref 9ecd91d)
- AC1/AC3/AC4 **pass**; LF data byte-identical (read-only + --apply); suite 10/10; defense-in-depth/transactional/idempotency/dry-run nguyên.
- [x] AC2 (CRLF): refactor làm report CRLF-tolerant (trước LF-only) → không byte-identical cho task CRLF. **Resolution:** nới scope — chấp nhận CRLF-tolerance có chủ đích (User duyệt; reviewer đã offer "change scope" là 1 lựa chọn hợp lệ). Code KHÔNG đổi (ref vẫn 9ecd91d); chỉ revise AC2. Re-review round 2 xác nhận.
