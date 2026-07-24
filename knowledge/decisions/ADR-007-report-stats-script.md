---
type: decision
scope: general
created: 2026-07-24
updated: 2026-07-24
tags: [control-tower, tooling, report, automation, tokens]
related: [[ADR-006-coordination-modes-and-task-states]]
---

# ADR-007: Script hoá phần đếm/regenerate cơ khí của `/report`

## Context

`/report` yêu cầu: glob toàn bộ `projects/*/tasks/*.md`, đọc `status:` frontmatter từng file, đếm theo project, rồi viết lại bảng `## Tiến độ` + `## Tasks` trong từng `projects/<name>/<name>.md`. Chạy tay (Glob + Read từng file + tính nhẩm + nhiều lệnh Edit) tốn rất nhiều token cho một việc thuần cơ khí, không cần phán đoán — và dễ sai: một lần chạy `/report` thủ công đã đọc nhầm `status:` của CT-023 (đọc 2 lần ra 2 kết quả khác nhau do file đang được ghi đè giữa chừng).

Đã có tiền lệ script hoá phần cơ khí trong hệ thống: `scripts/update-agent-stats.sh` (được `/verdict` gọi trực tiếp để cập nhật stat agent) và `scripts/add-review-frontmatter.sh`. Nguyên tắc "control-tower không chứa product code" trong `CLAUDE.md` áp dụng cho code sản phẩm của dự án đích (topvnsport, marketing-video-agent...), không áp dụng cho tooling nội bộ giúp chính control-tower vận hành.

## Decision

Thêm `scripts/ct-report-stats.py`: quét `projects/*/tasks/*.md`, đếm `status:` theo project, và (với `--apply`) tự viết lại đúng 2 block `## Tiến độ` + `## Tasks` trong `projects/<name>/<name>.md` — theo format cố định đã dùng trước giờ (bảng 2 cột, danh sách `- [[slug]] — title (status)`, thứ tự trạng thái ưu tiên done/dispatched/in-review/changes-requested/todo).

Script **không đụng** vào: `status:`/nội dung của bất kỳ task file nào, `index.md`, `log.md`, hay `knowledge/_index.md`. Những phần đó vẫn cần phán đoán (ghi chú executor/reviewer, cảnh báo deadline trễ, tường thuật trong log) nên vẫn do coordinator (LLM) viết sau khi đọc JSON output của script.

`/report` (SKILL.md) cập nhật quy trình: bước 1-3 (glob + đếm + viết bảng Tiến độ/Tasks) chạy qua `python3 scripts/ct-report-stats.py --apply`, đọc JSON trả về (gồm `counts` mới và `old_counts` cũ) để biết đã đổi gì; các bước còn lại (regenerate index.md, knowledge/_index.md, log.md, báo cáo User) giữ nguyên như cũ, do coordinator thực hiện.

## Consequences

- Nhanh hơn nhiều, ít token hơn nhiều: 1 lệnh Bash thay vì Glob + đọc ~70 file + nhiều Edit. Không còn rủi ro đọc nhầm frontmatter do thao tác tay.
- Script là nguồn sự thật duy nhất cho format bảng — sửa format ở 1 chỗ thay vì phải nhớ đúng format mỗi lần Edit tay.
- Nếu sau này thêm skill khác cần parse frontmatter tương tự (vd. `/lint`), nên tái dùng hàm `parse_frontmatter`/`collect_tasks` trong file này thay vì viết script riêng trùng lặp.
- Vẫn phải review diff sau khi chạy `--apply` (giống mọi thay đổi khác) — script không tự commit.

## Status

Accepted
