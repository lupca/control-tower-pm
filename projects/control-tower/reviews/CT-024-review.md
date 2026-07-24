---
id: CT-024
task_path: projects/control-tower/tasks/CT-024-harden-verdict-apply-script.md
project: control-tower
result_ref: ea9897a
executor: "@antigravity"
reviewer: "@claude-opus"
status: passed
issued: 2026-07-24
verdict: pass
verdict_date: 2026-07-24
round: 3
---

## ⚠️ Round 3 (re-review — ĐỔI REVIEWER theo rotation)

Lịch sử: Round 1 (`@gpt-5.6-sol`, `6006958`) CHANGES (AC3+AC4 fail). Round 2 (`@gpt-5.6-sol`, `74028a3`) CHANGES — AC4a/AC4b PASS (verified inject lỗi thật), chỉ còn AC3 edge case: dò ranh giới section AC không fence-aware. rejections=2 → **rotation: reviewer mới @claude-opus** (≠ @gpt-5.6-sol, ≠ executor @antigravity).

**Chỉ cần verify AC3 edge case còn lại** (AC1/AC2/AC4 đã pass, không đổi). Executor fix ở `ea9897a`. Xem delta round 3:
```
git diff 74028a3..ea9897a -- scripts/ct-verdict-apply.py
```
Fix tuyên bố: `tick_ac_checkboxes` track fence state (` ``` `/`~~~`) khi dò `## ` kế tiếp → `##` trong fenced block *bên trong* section AC không còn cắt section sớm; checkbox AC sau fence được tick đúng. Thêm test `test_ac3_fenced_code_with_heading_boundary` (suite 5/5).

**Cần làm:** dựng /tmp sandbox, chạy `scripts/test_ct_verdict_apply.py` xác nhận 5/5 pass; tự dựng 1 task có `##` trong fenced block giữa 2 AC checkbox, chạy verdict pass (sandbox) xác nhận checkbox sau fence được tick & `checkboxes_ticked` đúng. Fresh-eyes: soi lại toàn bộ `tick_ac_checkboxes` + `transactional_write_all` xem còn edge case nào không.

# Phiếu Review: CT-024 — Harden ct-verdict-apply.py (dry-run, scoped ticks, độc lập In-Interval, ghi atomic)

- Dự án: control-tower (`/home/lupca/projects/control-tower`)
- Task gốc: `projects/control-tower/tasks/CT-024-harden-verdict-apply-script.md`
- Result-ref: commit `6006958` (branch `review/CT-024`) — diff so với `main` (`f6136e0`)
- Executor: @antigravity
- Reviewer chỉ định: @gpt-5.6-sol (four-eyes: PHẢI ≠ @antigravity — xác nhận trước khi verdict)
- Ngày phát phiếu: 2026-07-24

## Cách lấy diff (chỉ đọc, không sửa)

```
cd /home/lupca/projects/control-tower
git diff main..6006958 -- scripts/ct-verdict-apply.py .claude/skills/verdict/SKILL.md \
  knowledge/decisions/ADR-008-verdict-apply-script.md knowledge/metrics/prediction-accuracy.md
```

Trọng tâm review là `scripts/ct-verdict-apply.py` (4 AC bên dưới). Lưu ý: `prediction-accuracy.md` trong diff còn chứa 1 phần sửa dữ liệu độc lập (backfill 3 dòng MVA sai schema) — KHÔNG thuộc AC CT-024, chỉ cần liếc để không nhầm; AC2 chỉ là phần quy ước `In Interval?` ở §1.

## Acceptance Criteria cần verify

- [ ] **AC1 (validate an toàn):** Thêm cờ `--dry-run` — script chạy hết logic trên **task thật**, in JSON kết quả dự kiến, nhưng **KHÔNG ghi** bất kỳ file nào (task, review sheet, prediction-accuracy, patterns, agent-stats). Cho phép xác nhận script "sống" trên dữ liệu thật mà không mutate state.
- [ ] **AC2 (In-Interval độc lập):** Cột `In Interval?` trong `prediction-accuracy.md` tính độc lập, KHÔNG copy nguyên `Match?`. Quy tắc: parse `confidence_interval: [lo, hi]`; `pass` → outcome ≈ 1.0, `changes` → outcome ≈ 0.0; `✅` nếu outcome trong `[lo, hi]`, `❌` nếu ngoài, `—` nếu không có `confidence_interval`. Quy ước này được ghi rõ vào §1/chú thích bảng của file metric.
- [ ] **AC3 (tick đúng phạm vi):** `pass` chỉ tick các checkbox `- [ ]` trong section AC (`## Tiêu chí nghiệm thu (AC)` tới heading `##` kế tiếp), KHÔNG tick mù mọi `- [ ]` trong body. `checkboxes_ticked` phản ánh đúng số đã tick.
- [ ] **AC4 (ghi atomic):** Gom toàn bộ mutation, chỉ ghi khi tất cả bước tính toán thành công (temp-file + `os.replace`), để lỗi giữa chừng không để lại state ghi dở. Side-effect phụ (`update-agent-stats.sh`) fail thì báo trong JSON nhưng không làm hỏng các file lõi đã ghi nhất quán.

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: (không có test suite — meta-project) → thay bằng nghiệm thu sandbox: dựng cây giả (task in-review + review sheet + prediction-accuracy + pattern index), chạy `--dry-run` rồi chạy thật, `git diff` xác nhận đúng phạm vi & atomic
- [ ] Không regression: defense-in-depth cũ (re-check `status: in-review` + four-eyes TRƯỚC mọi lần ghi) vẫn nguyên, 6 kịch bản sandbox gốc của ADR-008 vẫn pass
- [ ] Reviewer khác executor (bạn đang review, xác nhận bạn ≠ @antigravity)

## Kiểm tra rủi ro riêng của task này (từ review phiên trước)
- `--dry-run` phải bọc **mọi** điểm ghi: `path.write_text` cho task, review sheet, prediction-accuracy, pattern `_index.md`, VÀ `subprocess` gọi `update-agent-stats.sh`. Kiểm tra không sót đường ghi nào.
- Atomic: nếu một file ghi được rồi mà file sau lỗi → có rollback/không ghi dở không? Xác nhận thứ tự "tính hết → ghi hết" hoặc temp+rename cho từng file.
- Scoped tick: task có checkbox ngoài AC (vd trong Plan/Notes) → chạy thử `pass`, xác nhận chỉ AC được tick.
- In-Interval: thử task `changes` có `confidence_interval` low (vd MVA-001 `[0.1, 0.4]`, outcome 0.0 → phải `✅`) và task `pass` có CI không chứa 1.0 → phải `❌`, để chắc không phải copy `Match?`.

## Review Toolchain
Chạy review theo repo's toolchain:
  cat .claude/review-toolchain.md
Nếu file không tồn tại → dùng /code-review mặc định (control-tower là meta-project, không có toolchain file — dùng mặc định + đọc script Python trực tiếp).

## Trả kết quả
Sau khi review xong, báo lại cho control-tower bằng lệnh:
`/verdict CT-024 <pass|changes> --reviewer @gpt-5.6-sol [--commit <hash>] [--notes "..."]`
