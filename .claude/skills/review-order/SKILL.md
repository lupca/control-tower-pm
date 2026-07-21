---
name: review-order
description: Sinh phiếu review cho một task mà executor đã báo xong — gom AC, DoD, 🧪, result-ref, và câu hỏi rủi ro (từ graph, read-only) để giao reviewer độc lập (người/AI khác, khác executor). KHÔNG tự review, KHÔNG chạy test, KHÔNG đọc diff thực tế. Kích hoạt khi user gõ /review-order.
argument-hint: "<task path/ID> --ref <branch|commit|PR>"
allowed-tools: Read, Edit, Write, Grep, Glob, mcp__code-review-graph__get_suggested_questions_tool, mcp__code-review-graph__get_affected_flows_tool
---

## Review Order — phát phiếu review, không tự review

Bạn đang ở control-tower, KHÔNG phải repo code đích. Skill này **không đọc diff thực tế** của executor và **không chạy test** — nó chỉ tổng hợp thông tin đã có (task + graph tĩnh) thành một phiếu review tự chứa.

### Bước 1 — Định vị task

1. Đọc `AGENTS.md` (đặc biệt mục 1, 4, 5) và `index.md` mục 2 (PROJECT REGISTRY) nếu chưa đọc trong phiên.
2. Tìm task theo ID/path trong `$ARGUMENTS`: Glob `projects/*/tasks/<ID>-*.md` nếu User cho ID (vd `PMI-001`), hoặc theo path đầy đủ nếu User chỉ rõ.
3. Đọc frontmatter, kiểm tra `status:` hiện tại của task:
   - Nếu `status: dispatched` → hợp lệ, tiếp tục.
   - Nếu `status` khác (`todo`, `ready`, `in-review`, `done`, `changes-requested`) → dừng lại, báo User: task chưa sẵn sàng để phát phiếu review (vd chưa dispatch, hoặc đã đang review rồi), không tự ý đổi trạng thái.
4. Lấy `--ref <branch|commit|PR>` từ `$ARGUMENTS`. Nếu thiếu, hỏi User (không tự bịa result-ref).

### Bước 2 — Ghi result-ref, chuyển trạng thái

1. Ghi `result_ref: "<giá trị --ref>"` vào frontmatter.
2. Cập nhật `status: in-review`, `in_review: <ngày hôm nay>`, `updated: <ngày hôm nay>`.

### Bước 3 — Làm giàu câu hỏi rủi ro (read-only, tùy chọn)

Tra `repo_root` của dự án trong PROJECT REGISTRY, rồi (nếu graph khả dụng):

1. `get_suggested_questions_tool(repo_root=...)` — câu hỏi ưu tiên: bridge node thiếu test, hub node chưa cover, coupling bất ngờ.
2. `get_affected_flows_tool(changed_files=<danh sách files: ĐÃ GHI trong task từ Spec Gate>, repo_root=...)` — dùng lại danh sách file đã chốt lúc lập task, **không** tự đọc git diff mới của executor (ranh giới: đây là tĩnh, không phải review thật).

Nếu graph không trả về gì hữu ích hoặc lỗi, bỏ qua bước này — phiếu review vẫn hợp lệ chỉ với AC/DoD/test từ task.

### Bước 4 — Sinh phiếu review

Viết file `reviews/<ID>-review.md` (vd `PMI-001-review.md`):

```markdown
# Phiếu Review: <ID> — <title>

- Dự án: <tên dự án> (`<repo_root>`)
- Task gốc: `projects/<tên>/tasks/<ID>-<slug>.md`
- Result-ref: <branch/commit/PR từ --ref>
- Executor: <executor: của task>
- Ngày phát phiếu: <hôm nay>

## Acceptance Criteria cần verify
<copy nguyên khối "## Tiêu chí nghiệm thu (AC)" từ task>

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: <danh sách tests: từ task>
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ <executor>)

## Test gợi ý chạy trong repo code
<lệnh test theo CLAUDE.md/Project Gates của dự án đó, vd docker compose exec pytest ...>

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc bạn tự đọc diff)
<liệt kê kết quả get_suggested_questions_tool / get_affected_flows_tool nếu có>

## Gợi ý công cụ
Repo code đích có thể có sẵn skill `/code-review` (hoặc tương đương) — khuyến khích dùng để đọc diff + chạy test một cách có cấu trúc.

## Trả kết quả
Sau khi review xong, báo lại cho control-tower bằng lệnh:
`/verdict <ID> <pass|changes> --reviewer @<tên bạn> [--commit <hash>] [--notes "..."]`
```

### Bước 5 — Đóng bước

1. Ghi 1 entry vào `log.md` (`operation: review-order`, format `AGENTS.md` mục 7) — nêu rõ path phiếu review vừa sinh.
2. Báo User: phiếu đã sẵn tại `reviews/<ID>-review.md`, giao cho reviewer độc lập (**phải khác** `executor:` của task — nhắc lại rule four-eyes).

### Lỗi thường gặp cần tránh
- Tự ý review/chấm điểm AC ngay trong bước này — đó là việc của reviewer ngoài hệ, không phải `/review-order`.
- Tự đọc git diff/log của executor để "giúp" điền câu hỏi — chỉ dùng dữ liệu tĩnh đã ghi trong task hoặc graph không cần diff.
- Phát phiếu cho task chưa `dispatched` hoặc đã `in-review`/`done`.
