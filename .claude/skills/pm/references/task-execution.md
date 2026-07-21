# Task Execution — Plan Gate → Dispatch

Áp dụng sau khi User đã duyệt Spec Gate (phạm vi + AC của task đã được xác nhận, `status: todo`).

## Plan Gate

1. Nghiên cứu sâu hơn codebase đích nếu cần (đọc source thật ở các file trong `files:`, không chỉ dựa vào graph) để viết kế hoạch code cụ thể — không chung chung.
2. Viết kế hoạch THẲNG vào mục `## Plan` của file task trong `projects/<tên>/tasks/<ID>-<slug>.md`: liệt kê thứ tự sửa file nào, hàm nào, migration nào (nếu có), theo đúng sub-task đã liệt kê ở Spec Gate.
3. Nếu trong lúc lập kế hoạch phát hiện cần chạm file **ngoài** `files:` đã duyệt → quay lại Spec Gate, không tự ý mở rộng phạm vi.
4. Ghi 1 entry vào `log.md` (`operation: plan`), cập nhật `updated:` trong frontmatter.
5. Dừng lại, hiển thị `## Plan` cho User, chờ duyệt.

## Sau khi Plan Gate được duyệt: chuyển `ready` rồi `dispatched`

**Đây là điểm control-tower dừng lại — KHÔNG tự viết code, KHÔNG tự chạy test, KHÔNG spawn subagent thực thi.** Việc code là hành động ngoài hệ (`AGENTS.md` mục 1, 4).

1. Cập nhật `status: ready` trong frontmatter của task.
2. Hỏi User: ai sẽ là `executor:` cho task này (người hoặc AI khác, trong repo code đích)?
3. Ghi `executor: "@tên"`, `status: dispatched`, `dispatched: <ngày hôm nay>`, `updated: <ngày hôm nay>` vào frontmatter.
4. Ghi 1 entry vào `log.md` (`operation: dispatch`) — tóm tắt: task nào, giao cho ai, phiếu giao việc (file task) đã tự chứa AC/`files:`/`tests:`/`## Plan`/DoD chưa cần công cụ gì thêm.
5. Báo cho User: task đã sẵn sàng giao cho executor — họ chỉ cần đường dẫn tới `projects/<tên>/tasks/<ID>-<slug>.md` (không cần quyền truy cập control-tower hay công cụ gì khác).
6. **Dừng lại hoàn toàn.** Khi executor báo xong (có `result_ref:`), User (hoặc chính executor) sẽ chạy `/review-order` — đó là bước tiếp theo, không phải một phần của `/pm`.

## Nếu task gắn `⚠️high-risk` hoặc chạm `schemas/`/`models.py`/migration

RESTRICTED (`AGENTS.md` mục 1 & 4): Plan Gate bắt buộc xác nhận rõ ràng bằng văn bản/chat của User trước khi chuyển `dispatched`, không được suy diễn im lặng.
