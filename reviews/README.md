# reviews/

Chứa phiếu review (`<task-slug>-review.md`) do skill `/review-order` sinh ra khi một task chuyển sang `status: in-review`. Mỗi phiếu tự chứa Acceptance Criteria, Definition of Done, test gợi ý, result-ref (branch/commit/PR của executor), và câu hỏi rủi ro từ `code-review-graph` (tĩnh, read-only).

Reviewer độc lập (khác `👷 executor` của task) đọc phiếu này, tự đọc diff + chạy test trong repo code đích (khuyến khích dùng `/code-review` của repo đó), rồi báo kết quả lại qua `/verdict` (xem `AGENTS.md` mục 4, 8).

control-tower không tự tạo/xóa phiếu ngoài luồng `/review-order` — không sửa tay file trong thư mục này trừ khi cần đính chính thông tin.
