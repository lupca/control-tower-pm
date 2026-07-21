# Task Execution — Plan Gate → Code

Áp dụng sau khi User đã duyệt Spec Gate (phạm vi + AC của task đã được xác nhận).

## Plan Gate

1. Nghiên cứu sâu hơn codebase đích nếu cần (đọc source thật ở các file trong `🔗`, không chỉ dựa vào graph) để viết kế hoạch code cụ thể — không chung chung.
2. Viết kế hoạch THẲNG vào mục `▸ Plan:` của task trong `projects/<task-file>`: liệt kê thứ tự sửa file nào, hàm nào, migration nào (nếu có), theo đúng sub-task đã liệt kê ở Spec Gate.
3. Nếu trong lúc lập kế hoạch phát hiện cần chạm file **ngoài** `🔗` đã duyệt → quay lại Spec Gate, không tự ý mở rộng phạm vi.
4. Ghi 1 entry vào `log.md` (`operation: plan`).
5. Dừng lại, hiển thị `▸ Plan:` cho User, chờ duyệt. **Chưa được sửa dòng code nào của dự án đích trước khi User duyệt bước này.**

## Sau khi Plan Gate được duyệt: giao code

1. Việc sửa code là một hành động COLLABORATIVE riêng — chỉ bắt đầu khi User xác nhận rõ ràng (Y/N) sau khi thấy `▸ Plan:`.
2. Giao cho subagent/chính bạn thực thi đúng theo `▸ Plan:` đã duyệt — không tự thêm phạm vi mới giữa chừng.
3. Nếu task gắn `⚠️high-risk` hoặc chạm `schemas/`/`models.py`/migration (RESTRICTED — `AGENTS.md` mục 1 & 4): trước khi chạy `alembic revision --autogenerate` / `alembic upgrade head` hoặc bất kỳ migration nào, bắt buộc dừng và xin xác nhận bằng văn bản/chat của User riêng cho bước migrate, dù Plan Gate đã được duyệt.
4. Sau khi code xong, ghi 1 entry vào `log.md` (`operation: code`), rồi chuyển sang Code Gate — xem `task-finalization.md`. **Không** tự đánh dấu `- [x]` ở bước này.
