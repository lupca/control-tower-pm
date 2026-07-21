---
name: report
description: Quét toàn bộ projects/*.md, đếm task Done/Total và cập nhật bảng tiến độ trong index.md. Kích hoạt khi user gõ /report hoặc hỏi về tiến độ tổng thể các dự án.
allowed-tools: Read, Edit, Glob, Grep
---

## Report — cập nhật tiến độ vào index.md

### Quy trình

1. Liệt kê tất cả file trong `projects/*.md` (Glob).
2. Với mỗi file, đếm số dòng task cấp cao nhất (`- [ ]` / `- [x]` không thụt lề — sub-task thụt lề không tính riêng để tránh trùng lặp, chỉ đếm task cha). Tính Done = số `- [x]` cấp cao nhất, Total = Done + số `- [ ]` cấp cao nhất.
3. Cập nhật bảng "BẢN ĐỒ TIẾN ĐỘ DỰ ÁN" trong `index.md` (mục 3): cột Tiến độ (Done/Total), và Trạng thái (🔄 Đang chạy nếu còn task chưa xong, ✅ Hoàn tất nếu Done == Total > 0, ⏳ Tạm dừng nếu Total == 0).
4. Cập nhật "Thời gian cập nhật cuối" (mục 1) theo thời điểm hiện tại.
5. Ghi một entry vào `log.md` (COLLABORATIVE): tóm tắt số liệu đã cập nhật cho từng dự án.
6. Hiển thị bảng tiến độ mới cho user ngay trong chat, không chỉ ghi vào file.

### Lưu ý
- `/report` chỉ đọc và tổng hợp số liệu — không được tự ý sửa nội dung task (không đánh dấu `- [x]` thay user, không xóa task).
- Nếu phát hiện task đã tồn tại từ lâu (task cha có ngày `📅` quá hạn) và vẫn `- [ ]`, có thể nêu ra như một ghi chú cảnh báo trong phần báo cáo cho user, nhưng không tự sửa.
