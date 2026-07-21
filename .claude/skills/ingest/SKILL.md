---
name: ingest
description: Đọc toàn bộ ghi chú thô trong inbox.md, phân loại từng ghi chú về đúng dự án và làm giàu bằng code-review-graph trước khi ghi vào projects/*.md, rồi xóa khỏi inbox. Kích hoạt khi user gõ /ingest.
allowed-tools: Read, Edit, Write, Grep, Glob, mcp__code-review-graph__get_minimal_context, mcp__code-review-graph__get_impact_radius_tool, mcp__code-review-graph__query_graph_tool, mcp__code-review-graph__semantic_search_nodes_tool
---

## Ingest — phân loại inbox.md thành task chính thức

### Quy trình

1. Đọc `AGENTS.md` và `index.md` mục 2 (PROJECT REGISTRY) nếu chưa đọc trong phiên.
2. Đọc toàn bộ `inbox.md`. Với mỗi ghi chú thô:
   a. Xác định dự án đích (dựa vào từ khóa: OMS/đơn hàng/hóa đơn → `topvnsport-oms`; PMI/variant/sản phẩm → `topvnsport-pmi`; nếu không rõ, hỏi user thay vì đoán).
   b. Tra `repo_root` của dự án đó trong PROJECT REGISTRY.
   c. Áp dụng đúng quy trình graph ở `AGENTS.md` mục 2.2 (giống skill `/pm`): `get_minimal_context` → `get_impact_radius_tool` → `query_graph_tool(tests_for)`, luôn kèm `repo_root` và `detail_level="minimal"`, để xác nhận path thật thay cho path đoán mò ghi trong ghi chú thô.
   d. Viết task (kèm sub-task nếu cần) vào file `projects/<task-file>` tương ứng theo cú pháp chuẩn.
3. Sau khi tất cả ghi chú đã được chuyển thành task, xóa các mục đã xử lý khỏi `inbox.md` (giữ lại mục nào chưa xử lý được, vd thiếu thông tin — không xóa, hỏi user).
4. Ghi một entry tổng hợp vào `log.md` (COLLABORATIVE) liệt kê: bao nhiêu ghi chú đã ingest, ghi chú nào chuyển về dự án nào.
5. Báo cáo ngắn gọn cho user: đã tạo bao nhiêu task, ở file nào, và path graph đã xác nhận khác gì so với ghi chú gốc (nếu có sai lệch đáng chú ý).

### Lưu ý
- `/ingest` không tự đánh dấu task là `- [x]` và không tự sửa code — chỉ chuyển ghi chú thô thành task có cấu trúc.
- Nếu một ghi chú không đủ thông tin để xác định dự án hoặc mô tả quá mơ hồ, giữ nguyên trong `inbox.md` và hỏi user thay vì đoán.
