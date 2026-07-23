# HÒM THƯ YÊU CẦU CHỜ PHÂN LOẠI (inbox.md)

Nơi lưu trữ các ghi chú thô, ý tưởng, hoặc feedback từ User. Gõ `/ingest` để Agent tự động phân loại những yêu cầu này thành các task chi tiết trong thư mục `projects/`.

---

## Ý TƯỞNG & YÊU CẦU MỚI:

1.  *Ghi chú (2026-07-21):* Cần làm thêm phần xuất hóa đơn VAT tự động khi khách hàng hoàn tất checkout trên hệ thống OMS. Cái này có vẻ sẽ đụng tới file `invoice_service.py` và cần viết thêm test trong `test_invoice.py`. Ưu tiên trung bình thôi, deadline khoảng 15-08-2026.
2.  *Ghi chú (2026-07-21):* Sửa lỗi variant không load được hình ảnh khi kích thước file ảnh quá lớn (lỗi nén ảnh phía frontend). Cái này ưu tiên cao, ảnh hưởng trực tiếp tới chuyển đổi bán hàng.
3.  *Ghi chú (2026-07-23):* [control-tower-web] Lỗi giao diện dashboard: (a) Trang chi tiết một số project (vd: PMI) không lấy được data. (b) Kanban board không lấy được task của một số project. (c) Giao diện kanban bị kéo dài khi có nhiều task — cần giới hạn chiều cao cột và cho phép scroll (overflow-y).
4.  *Ghi chú (2026-07-23):* CD pipeline production deploy fail. Alembic migration `c9a2d4b80123` fail — `OCI runtime exec failed: exec failed: unable to start container process... found in $PATH: unknown`. Health checks [4/5] — `api-pmi` 200 OK nhưng `api-oms` 502. Process completed with exit code 1. Đây là nguyên nhân WMS-002 fix không được deploy lên prod (WEB-004). Project: topvnsport. Ưu tiên urgent.

