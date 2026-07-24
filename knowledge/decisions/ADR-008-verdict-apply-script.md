---
type: decision
scope: general
created: 2026-07-24
updated: 2026-07-24
tags: [control-tower, tooling, verdict, automation, tokens]
related: [[ADR-007-report-stats-script]]
---

# ADR-008: Script hoá phần cơ khí của `/verdict`

## Context

Sau [[ADR-007-report-stats-script]] (script hoá `/report`), rà lại các skill còn lại (`dispatch`, `review-order`, `verdict`, bỏ qua `/lint` theo yêu cầu User) để tìm nơi tốn token thủ công nhiều nhất. `/verdict` là nặng nhất: mỗi lần `pass`/`changes` phải tick checkbox AC/DoD ở **2 file** (review sheet + task gốc), sửa nhiều field frontmatter ở cả 2 file, cộng dồn 1 dòng + **tính lại toàn bộ bảng Summary Statistics** trong `knowledge/metrics/prediction-accuracy.md` (bài toán đếm/aggregate giống hệt `/report`), tăng `rejections:` counter, rồi mới gọi `update-agent-stats.sh` (đã script hoá từ trước). `/verdict` cũng được gọi thường xuyên nhất trong 6 macro (mỗi lần đóng/reopen task).

Khi rà `knowledge/metrics/prediction-accuracy.md` phát hiện 3 dòng cũ (MVA-002/003/004) sai schema (5 cột thay vì 9 cột chuẩn) — bằng chứng cho thấy ghi tay dễ trôi format.

## Decision

Thêm `scripts/ct-verdict-apply.py <task-id> <pass|changes> --reviewer @id [--commit <hash>] [--notes "..."] [--causal-root-cause ... --causal-mechanism ... --causal-counterfactual ... --causal-pattern-id ...]`.

Script tự làm toàn bộ phần cơ khí sau khi được gọi:
- Re-validate độc lập (không tin caller): `status:` phải là `in-review`, `--reviewer` phải khác `executor:` — sai thì refuse, exit 1, không đụng file nào.
- `pass`: tick toàn bộ `- [ ]` → `- [x]` trong task; set `status: done`/`reviewer:`/`result_ref:`/`updated:`; cập nhật frontmatter review sheet (`status/verdict/verdict_date`); nếu có đủ causal fields thì append `## Causal Analysis`, và nếu có `--causal-pattern-id` khớp pattern có sẵn thì tăng `Past Instances` trong `knowledge/patterns/_index.md`; append + tính lại `knowledge/metrics/prediction-accuracy.md` (bỏ qua an toàn các dòng sai schema, không sửa/xoá chúng); gọi `update-agent-stats.sh` cho cả executor lẫn reviewer.
- `changes`: append `## Findings từ reviewer` (mỗi note thành 1 dòng `- [ ]`); tăng `rejections:`; set `status: changes-requested`; cùng phần prediction-accuracy + agent-stats như trên; trả `reviewer_rotation_alert: true` khi `rejections >= 2`.

**Vẫn ở lại với coordinator (LLM)**, script không đụng tới:
- Đọc `state/mode.md` + Gate confirmation (stop/continue theo mode).
- Refuse four-eyes *trước User* (script refuse là lớp phòng thủ thứ 2, không thay thế bước hỏi/xác nhận).
- Nội dung causal analysis (root_cause/mechanism/counterfactual) — LLM phải hỏi User, chỉ truyền text qua flag.
- Đề xuất pattern MỚI (phải COLLABORATIVE, không tự tạo) — script chỉ tăng counter cho pattern đã tồn tại.
- Ghi `log.md` (cần "Giải trình" tường thuật).

Công thức `Match?` khi ghi dòng mới vào `prediction-accuracy.md`: `high`/`medium` kỳ vọng `pass`, `low` kỳ vọng `changes` — suy ra trực tiếp từ định nghĩa scoring đã ghi ở `## 1. Overview` của chính file đó, không phải suy đoán tuỳ tiện.

`/verdict` SKILL.md cập nhật: Step 4a/4b gọi script sau khi Gate + causal-analysis (nếu cần) đã được xác nhận/thu thập; đọc JSON trả về để biết còn việc gì cần làm tay (log.md, thông báo User, đề xuất pattern mới nếu không match).

## Consequences

- Giảm mạnh số Edit call + rủi ro tick sai/thiếu checkbox, quên field, hay làm sai công thức Summary Statistics mỗi lần đóng task.
- Phát hiện được các dòng sai schema cũ trong `prediction-accuracy.md` mà không tự sửa (không phải phạm vi `/verdict`) — nếu muốn dọn, cần một lần sửa tay riêng hoặc qua `/lint`.
- Test bằng sandbox riêng (`/tmp/.../verdict-test`, không đụng file thật) trước khi coi là an toàn dùng cho task thật — 6 kịch bản: pass (có/không review sheet, có causal+pattern bump), changes (rejections tăng + rotation alert), refuse four-eyes, refuse sai status, và bỏ qua an toàn dòng malformed.
- Nếu sau này cần parse frontmatter tương tự ở skill khác, nên tái dùng các hàm `fm_get`/`fm_set`/`split_frontmatter` ở đây thay vì viết lại.

### Hardening Update (CT-024)

Cải tiến 4 điểm độ bền và ngữ nghĩa cho `scripts/ct-verdict-apply.py`:
1. **Cờ `--dry-run`**: Cho phép chạy kiểm tra toàn bộ logic trên task thật và trả về JSON dự kiến mà không ghi bất kỳ file nào (`"dry_run": true`).
2. **Tính `In Interval?` độc lập**: Parse `confidence_interval: [lo, hi]` từ task frontmatter. Quy đổi outcome thực tế: `pass` → 1.0, `changes` → 0.0. Đánh giá `✅` nếu `lo <= outcome <= hi`, `❌` nếu nằm ngoài khoảng, `—` nếu task không khai báo confidence interval.
3. **Tick checkbox đúng phạm vi (AC Scoped Ticking)**: Chỉ tick `- [ ]` → `- [x]` trong section `## Tiêu chí nghiệm thu (AC)` (từ heading AC đến heading `##` kế tiếp), không tick tràn lan toàn bộ body task.
4. **Ghi atomic (Atomic Writes)**: Gom toàn bộ file mutation (task, review sheet, prediction accuracy, pattern index) và chỉ ghi khi tất cả phép tính thành công qua temp-file + rename. Nếu script phụ `update-agent-stats.sh` lỗi, ghi nhận vào JSON kết quả nhưng không làm hỏng dữ liệu cốt lõi đã ghi.

### Re-verdict & Edge Cases Hardening (CT-026)

Cải tiến 4 điểm xử lý re-verdict và edge cases fence/CRLF cho `scripts/ct-verdict-apply.py`:
1. **Re-verdict idempotent (Prediction Accuracy)**: `prepare_prediction_accuracy` cập nhật in-place dòng hiện có trong `prediction-accuracy.md` nếu task đã từng có verdict trước đó (thay vì append dòng mới). Đảm bảo mỗi task có đúng 1 dòng phản ánh kết quả cuối cùng, đồng thời tính lại bảng Summary Statistics chính xác.
2. **Không double-count executed (Agent Profile Stats)**: Re-verdict không tăng `total_tasks_executed` của executor. Phân biệt first-verdict vs re-verdict bằng cách kiểm tra sự tồn tại của task trong `prediction-accuracy.md` (`is_reverdict`). Nếu là re-verdict, điều chỉnh `success_rate` và `recent_trend` theo kết quả mới nhất mà không tăng số task đã thực hiện.
3. **Fence boundary matching đúng marker (AC Checkbox Scanning)**: `tick_ac_checkboxes` theo dõi marker mở fence (` ``` ` hoặc `~~~`) và chỉ đóng fence khi gặp ĐÚNG marker đã mở. Tránh trường hợp code fence lồng nhau có marker khác chứa dòng `##` gây kết thúc sớm section AC.
4. **Hỗ trợ CRLF line endings**: `split_frontmatter` và các hàm đọc file tự động normalize `\r\n` thành `\n` trước khi parse frontmatter/body, giúp xử lý các task file có định dạng dòng CRLF (Windows) không bị lỗi parsing.

## Status

Accepted
