---
name: pm
description: Giao task mới hoặc chia nhỏ yêu cầu mơ hồ thành sub-task chi tiết cho một dự án đích, dùng code-review-graph để tìm blast radius và test liên quan trước khi ghi vào projects/*.md. Kích hoạt khi user gõ /pm hoặc nói về giao/quản lý/lên kế hoạch task cho một dự án cụ thể.
argument-hint: <mô tả task> [--project <tên dự án>]
allowed-tools: Read, Edit, Write, Grep, Glob, mcp__code-review-graph__get_minimal_context, mcp__code-review-graph__get_impact_radius_tool, mcp__code-review-graph__query_graph_tool, mcp__code-review-graph__semantic_search_nodes_tool, mcp__code-review-graph__get_architecture_overview_tool
---

## Project Manager — sinh task chi tiết bằng code-review-graph

Người dùng gọi: `/pm $ARGUMENTS`. Bạn đang chạy trong repo `control-tower`, KHÔNG phải repo đích.

### Quy trình (bám sát `AGENTS.md` mục 2.2 — không lặp lại logic, chỉ thực thi)

1. Đọc `AGENTS.md` (nếu chưa đọc trong phiên) để nắm Decision-Authority Matrix và cú pháp task chuẩn.
2. Đọc `index.md` mục 2 (PROJECT REGISTRY). Xác định dự án đích:
   - Nếu `$ARGUMENTS` có `--project <tên>`, dùng đúng tên đó để tra bảng.
   - Nếu không, suy luận dự án từ nội dung mô tả task (vd nhắc "variant", "PMI" → `topvnsport-pmi`; "đơn hàng", "OMS" → `topvnsport-oms`). Nếu không chắc, hỏi lại user.
   - Lấy `repo_root` tuyệt đối và `Task file` tương ứng từ bảng registry. Nếu dự án chưa có trong registry, dừng lại và báo user cần onboard trước (xem `AGENTS.md` mục 5).
3. Gọi `get_minimal_context(task="<mô tả task>", repo_root=<repo_root>)` trước tiên để định hướng.
4. Gọi `get_impact_radius_tool(..., repo_root=<repo_root>, detail_level="minimal")` trên các entity liên quan để tìm blast radius.
5. Gọi `query_graph_tool(pattern="tests_for", ..., repo_root=<repo_root>, detail_level="minimal")` để tìm test case liên quan tới các file/hàm bị ảnh hưởng.
6. Nếu cần tìm entity theo tên/keyword thay vì đường dẫn, dùng `semantic_search_nodes_tool(..., repo_root=<repo_root>)`.
7. Chuyển mọi path tuyệt đối graph trả về thành path **tương đối so với `repo_root`** (cắt tiền tố). Không bao giờ ghi path đoán mò vào task — nếu graph không xác nhận được một path, ghi rõ `*(path chưa xác nhận qua graph)*` thay vì bịa.
8. Viết task cha + sub-task thụt lề vào file dự án (`projects/<task-file>`) theo đúng cú pháp trong `AGENTS.md` mục 2.1, kèm 🔗 file liên quan và ghi chú blast radius/mức độ rủi ro khi có.
9. Ghi một entry vào `log.md` theo format ở `AGENTS.md` mục 3 — hành động này là **COLLABORATIVE**, không phải AUTONOMOUS.
10. Dừng lại, hiển thị task vừa viết cho user xem và chờ duyệt. **Không** tự động bắt đầu sửa code — việc bắt đầu code là một hành động COLLABORATIVE riêng, cần user xác nhận rõ ràng (Y/N) sau khi thấy task.

### Lỗi thường gặp cần tránh
- Quên truyền `repo_root` → graph tool sẽ auto-detect theo cwd của control-tower và trả kết quả sai/rỗng.
- Ghi path tuyệt đối vào `projects/*.md` (làm file khó đọc) thay vì path tương đối.
- Bỏ qua bước ghi `log.md`.
