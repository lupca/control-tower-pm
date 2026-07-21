# Task Finalization — Code Gate & DoD

Áp dụng sau khi code cho task đã viết xong (theo `▸ Plan:` đã duyệt ở Plan Gate). Mục tiêu: chỉ đóng task (`- [x]`) khi đáp ứng đủ Definition of Done (`AGENTS.md` mục 3).

## Verify

1. `detect_changes_tool(repo_root=<repo_root của dự án>, detail_level="minimal")` — không truyền `changed_files` để tool tự phát hiện qua `git diff` trên working tree của dự án đích.
2. Đối chiếu kết quả với `🔗` + `▸ Plan:` đã duyệt:
   - Nếu code chạm file **ngoài phạm vi đã duyệt** → KHÔNG đóng task. Quay lại Plan Gate (`task-execution.md`), giải thích lý do mở rộng, chờ duyệt lại.
   - Nếu `detect_changes_tool` báo rủi ro mới chưa xử lý → KHÔNG đóng task, nêu rủi ro cho User.
3. Chạy test đã liệt kê ở `🧪` (theo đúng lệnh test của dự án đích, xem CLAUDE.md/Project Gates của dự án đó, thường là chạy trong Docker). Tất cả phải xanh 100%; nếu có test đỏ, KHÔNG đóng task, báo cho User biết test nào đỏ và lý do (nếu xác định được).
4. Kiểm tra không regression: các test khác trong cùng module/file vẫn xanh (không chỉ mỗi test mới thêm).

## Đóng task

Chỉ khi cả 4 bước Verify ở trên đều pass VÀ toàn bộ `✅ AC` của task đã thỏa:

1. Đánh dấu task cha và các sub-task liên quan thành `- [x]` trong `projects/<task-file>`.
2. Lấy commit hash thật của thay đổi vừa hoàn tất (`git log -1 --format=%H` trong repo đích, KHÔNG bịa hash).
3. Ghi 1 entry vào `log.md` (`operation: verify`, field `Commit:` = hash thật) theo format `AGENTS.md` mục 6.
4. Hiển thị tóm tắt cho User: AC nào đã pass, test nào đã chạy, commit hash. Đây vẫn là hành động COLLABORATIVE — nếu User phản hồi không đồng ý đóng task, hoàn tác đánh dấu `- [x]`.

## Khi không đủ điều kiện đóng task

Nếu bất kỳ điều kiện DoD nào không đạt: giữ nguyên `- [ ]`, ghi rõ trong `log.md` (`Trạng thái: Chờ duyệt` hoặc mô tả lý do chưa đóng được), và báo cho User biết cụ thể còn thiếu gì (AC nào chưa pass, test nào đỏ, file nào ngoài phạm vi...).
