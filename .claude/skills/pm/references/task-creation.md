# Task Creation — Spec Gate

Áp dụng khi User giao một yêu cầu mới qua `/pm`. Mục tiêu: tạo 1 file task riêng đầy đủ `files:`/AC/`tests:`/`flows:` (cú pháp frontmatter ở `AGENTS.md` mục 2.1), **không được ghi task nếu chưa gọi graph**.

## Các bước (theo bảng trong `AGENTS.md` mục 6.1)

Tất cả tool dưới đây bắt buộc kèm `repo_root=<tuyệt đối, tra từ index.md mục 2>`; dùng `detail_level="minimal"` khi tool hỗ trợ.

1. `get_minimal_context_tool(task="<mô tả task>", repo_root=...)` — định hướng trước, tránh dò mù.
2. `semantic_search_nodes_tool(query="<từ khóa từ mô tả task>", repo_root=..., detail_level="minimal")` — tìm đúng file/symbol thật. Nếu kết quả cho thấy tính năng **đã tồn tại** (có test pass, có schema constraint...), DỪNG LẠI, báo User rằng yêu cầu có thể đã được implement — đừng tạo task giả cho việc đã xong (xem ví dụ thực tế: `PMI-001` — "thêm validation cost/tax cho variant" từng bị phát hiện đã tồn tại sẵn trong topvnsport).
3. `get_impact_radius_tool(changed_files=[...path tìm được ở bước 2...], repo_root=..., detail_level="minimal")` → điền `files:`.
   - Nếu số file trong blast radius > **8**, KHÔNG viết 1 task lớn — đề xuất chẻ thành nhiều task nhỏ hơn (mỗi task 1 PR), trình bày phương án chẻ cho User trước khi viết bất kỳ task nào.
4. `query_graph_tool(pattern="tests_for", target=<file/symbol từ bước 3>, repo_root=..., detail_level="minimal")` → điền `tests:` (test đã có).
   - **Tham số đúng là `pattern`/`target`, KHÔNG có tham số `edge`.** Gọi sai sẽ lỗi ngay.
5. `get_knowledge_gaps_tool(repo_root=...)` — nếu vùng ảnh hưởng chạm hotspot chưa cover, thêm sub-task:
   `- [ ] Viết test cho <symbol/file> (hiện chưa có coverage — knowledge gap) — test đề xuất: <file test đề xuất>`
6. `get_hub_nodes_tool(top_n=50, repo_root=...)` và `get_bridge_nodes_tool(top_n=50, repo_root=...)` — nếu bất kỳ node nào trong `files:` trùng danh sách trả về → gắn `risk: high` trong frontmatter.
7. `get_affected_flows_tool(changed_files=[...], repo_root=...)` → điền `flows:`.

## Viết task

- Chuyển mọi path tuyệt đối graph trả về thành path **repo-relative** (cắt tiền tố `repo_root`). Không bao giờ ghi path đoán mò — nếu graph không xác nhận được, ghi `*(path chưa xác nhận qua graph)*` thay vì bịa.
- Đọc `<tên>.md` (file trùng tên folder project) → lấy `task_prefix` + `next_task_id`. ID = `<task_prefix>-<NNN>` (NNN = `next_task_id`, zero-pad 3 chữ số). Slug = kebab-case từ title (tối đa 40 ký tự ASCII).
- Tạo file `projects/<tên>/tasks/<ID>-<slug>.md` với frontmatter + body chuẩn (`AGENTS.md` mục 2.1), `status: todo`. Body PHẢI có dòng backlink `> Dự án: [[projects/<tên>/<tên>]]` ngay dưới tiêu đề H1 (wikilink thật, không phải path text — để Obsidian Graph vẽ được cạnh nối; không cần alias vì tên file đã trùng `<tên>`). KHÔNG điền `executor:`/`reviewer:`/`result_ref:` — các field này chỉ điền ở giai đoạn sau (Plan Gate/dispatch, review-order, verdict).
- Tăng `next_task_id` trong `<tên>.md` lên 1 sau khi tạo file xong.
- Thêm 1 dòng vào mục `## Tasks` của `<tên>.md`: `- [[<ID>-<slug>]] — <title> (todo)`. Nếu `<tên>.md` chưa có mục `## Tasks`, tạo mới (đặt trước mục "Quy tắc phê duyệt riêng"). Không bắt buộc phải làm hoàn hảo ở bước này — `/report` sẽ tự regenerate lại toàn bộ mục này mỗi lần chạy nên sai sót nhỏ sẽ tự sửa.
- Nếu task chạm `schemas/`, `models.py`, hoặc thư mục migration → RESTRICTED tự động (`AGENTS.md` mục 1 & 4), gắn `risk: high` và nêu rõ trong task.
- Để trống mục `## Plan` trong body — sẽ điền ở Plan Gate (xem `task-execution.md`), không điền trước.

## Đóng Spec Gate

1. Ghi 1 entry vào `log.md` (`operation: pm-create`, format `AGENTS.md` mục 7).
2. Hiển thị task vừa viết cho User, dừng lại chờ duyệt phạm vi & AC. **Không** tự chuyển sang Plan Gate — cần User xác nhận rõ ràng.
