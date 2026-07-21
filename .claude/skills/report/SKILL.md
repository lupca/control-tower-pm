---
name: report
description: Quét toàn bộ projects/*/tasks/*.md, đếm task theo status frontmatter, cập nhật <tên-dự-án>.md (file trùng tên folder project) + index.md, và cập nhật knowledge/_index.md. Kích hoạt khi user gõ /report hoặc hỏi về tiến độ tổng thể các dự án.
allowed-tools: Read, Edit, Glob, Grep
---

## Report — cập nhật tiến độ vào index.md + knowledge index

### Quy trình

1. Liệt kê tất cả file trong `projects/*/tasks/*.md` (Glob).
2. Với mỗi file, đọc `status:` từ frontmatter. Đếm theo từng dự án: `done`, `todo`, `ready`, `dispatched`, `in-review`, `changes-requested`. Total = tổng tất cả status.
3. Cập nhật bảng "Tiến độ" trong `projects/<tên>/<tên>.md` của từng dự án (số task theo từng status).
3b. **Regenerate mục `## Tasks`** trong mỗi `<tên>.md`: liệt kê lại toàn bộ `- [[<ID>-<slug>]] — <title> (<status>)` cho mọi file trong `tasks/*.md` (đọc `id`/`title`/`status` từ frontmatter). Đây là bước tự-heal — ghi đè toàn bộ mục này mỗi lần chạy, không phải append, để tự động phản ánh task mới do `/pm`/`/ingest` tạo hoặc task bị xoá. Wikilink `[[...]]` giữa `<tên>.md` và task là để Obsidian Graph view vẽ cạnh nối (xem `AGENTS.md` mục 2.1) — nếu thư mục `tasks/` rỗng, ghi `*(chưa có task nào)*`.
4. Cập nhật bảng "BẢN ĐỒ TIẾN ĐỘ DỰ ÁN" trong `index.md` (mục 3): cột Tiến độ (Done/Total), và Trạng thái (🔄 Đang chạy nếu còn task chưa xong, ✅ Hoàn tất nếu Done == Total > 0, ⏳ Tạm dừng nếu Total == 0).
5. Cập nhật "Thời gian cập nhật cuối" (mục 1) theo thời điểm hiện tại.
6. Glob `knowledge/**/*.md` + `projects/*/docs/*.md`, đọc `type:` từ frontmatter, group theo type. Cập nhật `knowledge/_index.md` (bảng cross-project theo `decisions/domains/conventions/research`, bảng per-project theo dự án) và bảng "KNOWLEDGE MAP" trong `index.md` (mục 6).
7. Ghi một entry vào `log.md` (COLLABORATIVE): tóm tắt số liệu đã cập nhật cho từng dự án + knowledge.
8. Hiển thị bảng tiến độ mới cho user ngay trong chat, không chỉ ghi vào file.

### Lưu ý
- `/report` chỉ đọc và tổng hợp số liệu — không được tự ý sửa nội dung task (không đổi `status:` thay user, không xóa task).
- Nếu phát hiện task đã tồn tại từ lâu (`deadline:` quá hạn) và vẫn chưa `done`, có thể nêu ra như một ghi chú cảnh báo trong phần báo cáo cho user, nhưng không tự sửa.
