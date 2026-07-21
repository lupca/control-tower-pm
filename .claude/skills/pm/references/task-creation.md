# Task Creation — Spec Gate

Áp dụng khi User giao một yêu cầu mới qua `/pm`. Mục tiêu: sinh ra một task đầy đủ `🔗`/`✅ AC`/`🧪`/`🌀` (cú pháp ở `AGENTS.md` mục 2.1), **không được ghi task nếu chưa gọi graph**.

## Các bước (theo bảng B1 trong `AGENTS.md` mục 5.1)

Tất cả tool dưới đây bắt buộc kèm `repo_root=<tuyệt đối, tra từ index.md mục 2>`; dùng `detail_level="minimal"` khi tool hỗ trợ.

1. `get_minimal_context_tool(task="<mô tả task>", repo_root=...)` — định hướng trước, tránh dò mù.
2. `semantic_search_nodes_tool(query="<từ khóa từ mô tả task>", repo_root=..., detail_level="minimal")` — tìm đúng file/symbol thật. Nếu kết quả cho thấy tính năng **đã tồn tại** (có test pass, có schema constraint...), DỪNG LẠI, báo User rằng yêu cầu có thể đã được implement — đừng tạo task giả cho việc đã xong (xem ví dụ thực tế: task "thêm validation cost/tax cho variant" từng bị phát hiện đã tồn tại sẵn trong topvnsport).
3. `get_impact_radius_tool(changed_files=[...path tìm được ở bước 2...], repo_root=..., detail_level="minimal")` → điền `🔗`.
   - Nếu số file trong blast radius > **8**, KHÔNG viết 1 task lớn — đề xuất chẻ thành nhiều task nhỏ hơn (mỗi task 1 PR), trình bày phương án chẻ cho User trước khi viết bất kỳ task nào.
4. `query_graph_tool(pattern="tests_for", target=<file/symbol từ bước 3>, repo_root=..., detail_level="minimal")` → điền `🧪` (test đã có).
   - **Tham số đúng là `pattern`/`target`, KHÔNG có tham số `edge`.** Gọi sai sẽ lỗi ngay.
5. `get_knowledge_gaps_tool(repo_root=...)` — nếu vùng ảnh hưởng chạm hotspot chưa cover, thêm sub-task:
   `- [ ] Viết test cho <symbol/file> (hiện chưa có coverage — knowledge gap) 🧪 <file test đề xuất>`
6. `get_hub_nodes_tool(top_n=50, repo_root=...)` và `get_bridge_nodes_tool(top_n=50, repo_root=...)` — nếu bất kỳ node nào trong `🔗` trùng danh sách trả về → gắn `⚠️high-risk` vào dòng task cha.
7. `get_affected_flows_tool(changed_files=[...], repo_root=...)` → điền `🌀 Luồng ảnh hưởng:`.

## Viết task

- Chuyển mọi path tuyệt đối graph trả về thành path **repo-relative** (cắt tiền tố `repo_root`). Không bao giờ ghi path đoán mò — nếu graph không xác nhận được, ghi `*(path chưa xác nhận qua graph)*` thay vì bịa.
- Viết task cha + sub-task theo đúng cú pháp `AGENTS.md` mục 2.1 vào `projects/<task-file>` (tra từ registry).
- Nếu task chạm `schemas/`, `models.py`, hoặc thư mục migration → RESTRICTED tự động (`AGENTS.md` mục 1 & 4), nêu rõ trong task.
- Để trống mục `▸ Plan:` — sẽ điền ở Plan Gate (xem `task-execution.md`), không điền trước.

## Đóng Spec Gate

1. Ghi 1 entry vào `log.md` (`operation: pm-create`, format `AGENTS.md` mục 6).
2. Hiển thị task vừa viết cho User, dừng lại chờ duyệt phạm vi & AC. **Không** tự chuyển sang Plan Gate — cần User xác nhận rõ ràng.
