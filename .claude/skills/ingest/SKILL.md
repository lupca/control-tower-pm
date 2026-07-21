---
name: ingest
description: Đọc toàn bộ ghi chú thô trong inbox.md, phân loại từng ghi chú về đúng dự án và làm giàu bằng code-review-graph trước khi tạo task hoặc route thành knowledge — reconcile vào task tương tự đã có thay vì tạo trùng. Kích hoạt khi user gõ /ingest.
allowed-tools: Read, Edit, Write, Grep, Glob, mcp__code-review-graph__get_minimal_context_tool, mcp__code-review-graph__get_impact_radius_tool, mcp__code-review-graph__query_graph_tool, mcp__code-review-graph__semantic_search_nodes_tool
---

## Ingest — phân loại inbox.md thành task hoặc knowledge (reconcile, đừng append)

### Quy trình

1. Đọc `AGENTS.md` (đặc biệt mục 9 "Reconcile, đừng append" và mục 11 "Quản lý knowledge") và `index.md` mục 2 (PROJECT REGISTRY) nếu chưa đọc trong phiên.
2. Đọc toàn bộ `inbox.md`. Với mỗi ghi chú thô:
   a. **Phân loại task vs knowledge trước** (`AGENTS.md` mục 11.1): ghi chú actionable, có việc cần làm/deadline → task (bước b-d dưới đây). Ghi chú là domain knowledge/quyết định/quy ước, không cần hành động ngay → knowledge (bước e).
   b. Xác định dự án đích (từ khóa: OMS/đơn hàng/hóa đơn → `topvnsport-oms`; PMI/variant/sản phẩm → `topvnsport-pmi`; không rõ → hỏi User thay vì đoán).
   c. Tra `repo_root` của dự án đó trong PROJECT REGISTRY. **Glob `projects/<tên>/tasks/*.md`** — nếu đã có task tương tự (cùng file/symbol liên quan, hoặc cùng chủ đề nghiệp vụ), đọc frontmatter + body, **bổ sung/viết lại mạch lạc vào task đó** (thêm sub-task, cập nhật `files:`/AC/`tests:` nếu ghi chú mới có thông tin bổ sung, cập nhật `updated:`) — KHÔNG tạo task mới trùng lặp.
   d. Nếu chưa có task tương tự, áp dụng đúng quy trình graph như `.claude/skills/pm/references/task-creation.md`: `get_minimal_context_tool` → `semantic_search_nodes_tool`/`get_impact_radius_tool` → `query_graph_tool(pattern="tests_for", target=...)`, luôn kèm `repo_root` và `detail_level="minimal"`, để xác nhận path thật thay cho path đoán mò ghi trong ghi chú thô. Đọc `<tên>.md` (file trùng tên folder project) lấy `task_prefix`/`next_task_id`, tạo file `projects/<tên>/tasks/<ID>-<slug>.md` đúng cú pháp `AGENTS.md` mục 2.1 (có `files:`/AC/`tests:`, `status: todo`), tăng `next_task_id`.
   e. **Route knowledge** (`AGENTS.md` mục 11.5): tạo file trong `knowledge/<type>/` (scope=general, áp dụng nhiều dự án) hoặc `projects/<tên>/docs/` (scope=project cụ thể) với frontmatter chuẩn mục 11.3. KHÔNG tạo task giả cho nội dung không actionable này.
3. Sau khi một ghi chú đã được reconcile/tạo task/route knowledge xong → xóa mục đó khỏi `inbox.md`. Giữ lại mục nào chưa xử lý được (vd thiếu thông tin để xác định dự án, hoặc mơ hồ giữa task/knowledge) — không xóa, hỏi User.
4. Ghi một entry vào `log.md` (`operation: ingest`, format `AGENTS.md` mục 7) — liệt kê: bao nhiêu ghi chú đã ingest, ghi chú nào reconcile vào task có sẵn vs tạo task mới vs route thành knowledge.
5. Báo cáo ngắn gọn cho User: đã xử lý bao nhiêu ghi chú, task/knowledge nào được bổ sung vs tạo mới, path graph xác nhận khác gì so với ghi chú gốc (nếu có sai lệch đáng chú ý).

### Lưu ý
- `/ingest` không tự đánh dấu task `status: done` và không tự sửa code — chỉ chuyển ghi chú thô thành task có cấu trúc hoặc knowledge file, tuân theo Spec Gate như `/pm` cho task (dừng chờ duyệt, không tự chuyển sang Plan Gate).
- Ưu tiên reconcile hơn tạo mới: một backlog có nhiều task trùng lặp cùng một vấn đề khó review hơn một task được cập nhật liên tục.
- Không tự bịa nội dung domain/ADR — knowledge do User cung cấp/duyệt, `/ingest` chỉ route đúng chỗ và đúng frontmatter.
- Nếu một ghi chú không đủ thông tin để xác định dự án, không rõ task hay knowledge, hoặc mô tả quá mơ hồ, giữ nguyên trong `inbox.md` và hỏi User thay vì đoán.
