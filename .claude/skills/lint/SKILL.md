---
name: lint
description: Health-check toàn bộ backlog control-tower — phát hiện task hỏng, trễ, mồ côi, thiếu AC, link file chết, mâu thuẫn. Chạy định kỳ hoặc khi backlog có vẻ lệch. Kích hoạt khi user gõ /lint.
argument-hint: "[--project <tên>] (mặc định: tất cả)"
allowed-tools: Read, Glob, Grep, mcp__code-review-graph__query_graph_tool, mcp__code-review-graph__semantic_search_nodes_tool
---

## Lint — health-check backlog (vòng lặp thứ 3, giữ backlog không mục nát)

Chỉ đọc và báo cáo — **không tự sửa/xóa task** (thuộc RESTRICTED, xem `AGENTS.md` mục 1).

### Quy trình

1. Đọc `AGENTS.md` và `index.md` mục 2 (PROJECT REGISTRY) nếu chưa đọc trong phiên.
2. Xác định phạm vi: nếu có `--project <tên>` trong `$ARGUMENTS`, chỉ quét file task của dự án đó; nếu không, quét toàn bộ `projects/*.md`.
3. Với mỗi file trong phạm vi, chạy checklist sau và gom **Findings**:

   1. **Task trễ hạn**: `📅` < ngày hôm nay và task chưa `[x]` → liệt kê kèm số ngày trễ.
   2. **Thiếu AC / thiếu 🧪**: task cấp cao nhất (không phải sub-task) đang mở (`- [ ]`) mà không có khối `✅` hoặc `🧪` → cờ "task mơ hồ, cần regenerate qua `/pm`".
   3. **Link file chết**: với mỗi path trong `🔗`, gọi `query_graph_tool(pattern="file_summary", target=<path repo-relative>, repo_root=<repo_root của dự án>, detail_level="minimal")` (hoặc `semantic_search_nodes_tool` nếu cần đối chiếu theo tên) để kiểm tra file/symbol còn tồn tại trong graph; nếu không thấy → cờ "link chết, task có thể lỗi thời — path đã bị đổi tên/xóa".
   4. **Task mồ côi**: file task không xuất hiện trong PROJECT REGISTRY, hoặc dự án tương ứng không có `repo_root` hợp lệ (không phải path tuyệt đối, hoặc thư mục không tồn tại).
   5. **Mâu thuẫn**: 2 task (cùng file hoặc khác file) có cùng `🔗` trùng nhau nhưng mô tả có vẻ xung khắc (heuristic: đọc mô tả, không cần tool) → cờ để User xử lý thủ công.
   6. **Lệch trạng thái**: task đã `[x]` nhưng không tìm thấy entry `Commit:` tương ứng (khác `n/a`) trong `log.md` → cờ "đóng task nhưng thiếu bằng chứng commit".
   7. **Đề xuất dọn**: task có `📅` cách đây > 90 ngày và vẫn `- [ ]`, không có hoạt động log gần đây → gợi ý archive (không tự làm).

4. Xuất báo cáo dạng bảng "Findings" trong chat: cột Severity (🔴/🟡/🟢), Task (mô tả ngắn + file), Vấn đề, Đề xuất hành động.
5. Ghi 1 entry `lint` vào `log.md` theo format `AGENTS.md` mục 6 — tóm tắt số finding theo severity, không cần liệt kê hết trong log (chi tiết đã có trong chat).

### Lưu ý
- Nếu backlog sạch (không có finding nào), báo ngắn gọn "Backlog sạch, không phát hiện vấn đề" — vẫn ghi log để có dấu vết đã chạy `/lint`.
- Không đoán mò khi kiểm tra link chết — nếu graph tool trả lỗi hoặc không chắc, ghi rõ "chưa xác minh được" thay vì tự kết luận file còn tồn tại hay không.
