---
name: ingest
description: Đọc toàn bộ ghi chú thô trong inbox.md, phân loại từng ghi chú về đúng dự án và làm giàu bằng code-review-graph trước khi ghi vào projects/*.md — reconcile vào task tương tự đã có thay vì tạo trùng. Kích hoạt khi user gõ /ingest.
allowed-tools: Read, Edit, Write, Grep, Glob, mcp__code-review-graph__get_minimal_context_tool, mcp__code-review-graph__get_impact_radius_tool, mcp__code-review-graph__query_graph_tool, mcp__code-review-graph__semantic_search_nodes_tool
---

## Ingest — phân loại inbox.md thành task chính thức (reconcile, đừng append)

### Quy trình

1. Đọc `AGENTS.md` (đặc biệt mục 9 "Reconcile, đừng append") và `index.md` mục 2 (PROJECT REGISTRY) nếu chưa đọc trong phiên.
2. Đọc toàn bộ `inbox.md`. Với mỗi ghi chú thô:
   a. Xác định dự án đích (từ khóa: OMS/đơn hàng/hóa đơn → `topvnsport-oms`; PMI/variant/sản phẩm → `topvnsport-pmi`; không rõ → hỏi User thay vì đoán).
   b. Tra `repo_root` của dự án đó trong PROJECT REGISTRY.
   c. **Đọc trước `projects/<task-file>` của dự án đó** — nếu đã có task tương tự (cùng file/symbol liên quan, hoặc cùng chủ đề nghiệp vụ), **bổ sung/viết lại mạch lạc vào task đó** (thêm sub-task, cập nhật `🔗`/`✅ AC`/`🧪` nếu ghi chú mới có thông tin bổ sung) — KHÔNG tạo task mới trùng lặp.
   d. Nếu chưa có task tương tự, áp dụng đúng quy trình graph như `.claude/skills/pm/references/task-creation.md`: `get_minimal_context_tool` → `semantic_search_nodes_tool`/`get_impact_radius_tool` → `query_graph_tool(pattern="tests_for", target=...)`, luôn kèm `repo_root` và `detail_level="minimal"`, để xác nhận path thật thay cho path đoán mò ghi trong ghi chú thô. Viết task mới đúng cú pháp `AGENTS.md` mục 2.1 (có `🔗`/`✅ AC`/`🧪`, `status: todo`).
3. Sau khi một ghi chú đã được reconcile/tạo task xong → xóa mục đó khỏi `inbox.md`. Giữ lại mục nào chưa xử lý được (vd thiếu thông tin để xác định dự án) — không xóa, hỏi User.
4. Ghi một entry vào `log.md` (`operation: ingest`, format `AGENTS.md` mục 7) — liệt kê: bao nhiêu ghi chú đã ingest, ghi chú nào reconcile vào task có sẵn vs tạo task mới.
5. Báo cáo ngắn gọn cho User: đã xử lý bao nhiêu ghi chú, task nào được bổ sung vs tạo mới, path graph xác nhận khác gì so với ghi chú gốc (nếu có sai lệch đáng chú ý).

### Lưu ý
- `/ingest` không tự đánh dấu task `- [x]` và không tự sửa code — chỉ chuyển ghi chú thô thành task có cấu trúc, tuân theo Spec Gate như `/pm` (dừng chờ duyệt, không tự chuyển sang Plan Gate).
- Ưu tiên reconcile hơn tạo mới: một backlog có nhiều task trùng lặp cùng một vấn đề khó review hơn một task được cập nhật liên tục.
- Nếu một ghi chú không đủ thông tin để xác định dự án hoặc mô tả quá mơ hồ, giữ nguyên trong `inbox.md` và hỏi User thay vì đoán.
