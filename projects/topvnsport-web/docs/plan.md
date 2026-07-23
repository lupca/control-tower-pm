# Kế Hoạch Triển Khai Zalo OTP (ZBS Template Message) 

Tài liệu này cung cấp bản đặc tả kỹ thuật và kế hoạch thực thi chi tiết dành cho Đội ngũ Phát triển (Developers) nhằm tích hợp tính năng gửi Zalo OTP vào nền tảng Website, thay thế hoàn toàn hệ thống SMS OTP truyền thống.

sdt test: 0382426669
5XozDvtflGWH6hirbEwz3nqUiZAKy_zxI4R-8TZHyK0aL88MeTtKRd9hjpRszy9q8sE7CFZevrey4eC7jfA6H6S1u0syfhrgCGl49UQglLi_ADqIuw6UHHqjdHdftvDD7bYJCCR-qqOTMDrmwzodJtjE-WkyjRf9TqNAFf3tnKHUPRyaj-VxK5vpcH7NnEXlFogo0CRVwZq_R9TcxPdeCX8svbxeWeib9oEATAw7zabCBgD_bDloDdPsbdsaXCb1HW2iDSlnycWUNuObcj7BQ7uXcX21bCLkSJAa3et2uZT1UU5sXSgN05Czad-NozyfOZ25PeYH_YPHEFuRtycHOIbfbHZbnUDl1qZcBSpRw44VK9G4Z-N2EKiulSCt3f_nkG0

## User Review Required

> [!IMPORTANT]
> **Yêu cầu Xác nhận từ Product Owner:** 
> Việc gỡ bỏ hoàn toàn SMS và chỉ sử dụng Zalo OTP đồng nghĩa với việc: Nếu người dùng không sử dụng Zalo, hoặc số điện thoại chưa liên kết Zalo, họ sẽ **không thể nhận được OTP và không thể hoàn tất mua hàng**. Hãy đảm bảo quyết định này phù hợp với chiến lược tập khách hàng của dự án.
> Ngoài ra, hệ thống Zalo quy định access token chỉ có hiệu lực 25 giờ. Plan này sẽ tích hợp `apscheduler` để tự động refresh token ngầm mỗi 20 tiếng. Xin xác nhận việc thêm thư viện `apscheduler` là hợp lệ.

## Proposed Changes

Kế hoạch thay đổi tập trung vào **OMS Backend**, loại bỏ hoàn toàn `sms_service.py` hiện tại.

### 1. Cập nhật Thư viện & Biến cấu hình
#### [MODIFY] [requirements.txt](file:///home/lupca/projects/topvnsport/OMS/backend/requirements.txt)
- Thêm thư viện `apscheduler==3.10.4` để hỗ trợ Background Cron Jobs.

#### Cơ sở dữ liệu (Bảng SystemConfig)
Đảm bảo đã insert các record sau vào bảng `SystemConfig` trước khi chạy luồng:
- `zalo_app_id`
- `zalo_secret_key`
- `zalo_access_token`
- `zalo_refresh_token`
- `zalo_template_id`
- *(Gỡ bỏ `speed_sms_token`)*

### 2. Xây dựng Zalo Service API
#### [NEW] [zalo_service.py](file:///home/lupca/projects/topvnsport/OMS/backend/services/zalo_service.py)
- **Tạo hàm `send_zalo_otp`**:
  - Endpoint: `POST https://business.openapi.zalo.me/message/template`
  - Headers: `access_token` lấy từ cấu hình.
  - Xử lý số điện thoại: Sử dụng `utils.phone_helper.normalize_phone` để đưa về định dạng `84xxxxxxxxx` (bắt buộc của Zalo, không có dấu `+`).
  - Trả về cấu trúc rõ ràng: Thành công hoặc Thất bại kèm mã lỗi (đặc biệt lưu ý các mã lỗi Zalo: `-118` tài khoản không tồn tại, `-115` hết quota, `-108` sai định dạng).
- **Tạo hàm `refresh_zalo_token`**:
  - Endpoint: `POST https://oauth.zaloapp.com/v4/oa/access_token`
  - Truyền `app_id`, `secret_key`, `grant_type=refresh_token`, và `refresh_token` hiện tại.
  - Phản hồi từ Zalo sẽ cấp 1 `access_token` và 1 `refresh_token` mới.

#### [DELETE] [sms_service.py](file:///home/lupca/projects/topvnsport/OMS/backend/services/sms_service.py)
- Xóa hoàn toàn file này.

### 3. Cập nhật Luồng OTP Chính & Tự động hoá Token
#### [MODIFY] [main.py](file:///home/lupca/projects/topvnsport/OMS/backend/main.py)
- **Tích hợp Zalo OTP trong API `/api/sms/send-otp`**:
  - Xóa đoạn fetch `speed_sms_token`. Lấy `zalo_access_token` và `zalo_template_id` từ `SystemConfig`.
  - Thay thế hàm gọi `services.sms_service.send_speed_sms` thành `services.zalo_service.send_zalo_otp`.
  - **Xử lý Exception**: Nếu Zalo trả về thất bại (do SĐT không có Zalo, hoặc lỗi khác), trực tiếp `raise HTTPException(status_code=400, detail="Không thể gửi Zalo OTP. Vui lòng đảm bảo SĐT đã đăng ký Zalo.")` để báo lỗi hiển thị lên Frontend. (Không Fallback).
- **Thiết lập Cron Job Tự động Refresh Token**:
  - Sử dụng `@app.on_event("startup")`. Khởi tạo `BackgroundScheduler` của `apscheduler`.
  - Đăng ký job chạy mỗi 20 giờ. Job sẽ:
    1. Fetch `zalo_refresh_token` từ `SystemConfig`.
    2. Gọi `zalo_service.refresh_zalo_token`.
    3. Update `SystemConfig` với `access_token` và `refresh_token` mới.
- **Thêm Endpoint Webhook Zalo `/api/sms/zalo-webhook`**:
  - Lắng nghe event `user_received_message`.
  - Verify header `X-ZEvent-Signature` với HMAC SHA-256 (bằng `OA_SECRET_KEY`).
  - Nếu hợp lệ, cập nhật field `provider_status = "DELIVERED"` vào record `OtpVerification` tương ứng với SĐT.

### 4. Cập nhật Unit / E2E Tests
#### [MODIFY] [test_main.py](file:///home/lupca/projects/topvnsport/OMS/backend/test_main.py)
- Thay đổi fixture mock SMS thành `configure_zalo_otp`.
- Chỉnh sửa mock logic để patch `services.zalo_service.send_zalo_otp` thay vì sms_service.
- Đảm bảo các test case "Failed to send" verify đúng HTTP 400 và thông báo lỗi Zalo cho người dùng.

#### [MODIFY] [test_storefront_otp_flow.py](file:///home/lupca/projects/topvnsport/e2e_tests/tests/test_storefront_otp_flow.py)
- Kiểm tra E2E flow vẫn hoạt động trơn tru với API Test Endpoint (lấy OTP nội bộ để bypass bước thực sự nhận tin Zalo).

### 5. Đặc Tả Kiểm Thử (Test Specification)
Phần này định nghĩa chi tiết các test case cần được update hoặc thêm mới để bao phủ hoàn toàn (coverage) cho cả Backend và Frontend/E2E.

#### 5.1. Backend Unit & Integration Tests (`test_main.py` & `test_zalo.py`)
- **[Update] `test_send_otp_success`**: Mock `zalo_service.send_zalo_otp` trả về `{ "status": "success", "error_code": 0 }`. Kiểm tra API trả về HTTP 200, record `OtpVerification` được tạo với trạng thái `PENDING`.
- **[New] `test_send_zalo_otp_invalid_phone`**: Mock Zalo API trả về lỗi `-108`. Đảm bảo API trả về HTTP 400 kèm thông báo "Số điện thoại không hợp lệ."
- **[New] `test_send_zalo_otp_unregistered_zalo`**: Mock Zalo API trả về lỗi `-118` hoặc `-115`. Đảm bảo API trả về HTTP 400 kèm thông báo "Số điện thoại chưa đăng ký Zalo hoặc không thể nhận được tin nhắn Zalo lúc này."
- **[Update] `test_send_otp_rate_limit_and_lockout`**: Đảm bảo cơ chế giới hạn gửi (cooldown 60s, khóa sau 5 lần) vẫn hoạt động bình thường với luồng Zalo mới.
- **[New] `test_zalo_webhook_valid_signature`**: Gửi một POST request giả lập sự kiện `user_received_message` với header `X-ZEvent-Signature` hợp lệ (được băm từ `OA_SECRET_KEY` dùng cho test). Kiểm tra record `OtpVerification` được chuyển sang `DELIVERED`.
- **[New] `test_zalo_webhook_invalid_signature`**: Gửi Webhook request với signature sai. Hệ thống phải từ chối với HTTP 401/403 để đảm bảo bảo mật.
- **[New] `test_scheduled_token_refresh`**: (Test function) Gọi trực tiếp hàm refresh token của apscheduler (đã mock `httpx`), đảm bảo `SystemConfig` được cập nhật chính xác với `access_token` và `refresh_token` mới.

#### 5.2. Frontend & E2E Tests (Cypress/Playwright - `test_storefront_otp_flow.py`)
- **[Update] `test_storefront_checkout_otp_success`**: 
  - *Kịch bản*: Khách hàng thêm sản phẩm vào giỏ, nhập SĐT hợp lệ. Nhấn gửi OTP. Lấy OTP từ test-endpoint và xác nhận thành công.
  - *Kỳ vọng*: Flow hoàn tất, Order được tạo thành công trên hệ thống.
- **[New] `test_storefront_checkout_zalo_unregistered`**:
  - *Kịch bản*: Khách hàng nhập số điện thoại không có Zalo (trigger backend trả lỗi -118).
  - *Kỳ vọng*: Bảng mã OTP (`OtpModal.tsx`) không được hiện ra, thay vào đó hiển thị trực tiếp một Toast/Error text màu đỏ trên UI: "Số điện thoại chưa đăng ký Zalo...". Luồng checkout bị chặn lại.
- **[Update] `test_storefront_otp_cooldown_ui`**:
  - *Kịch bản*: Khách hàng nhấn gửi OTP liên tục.
  - *Kỳ vọng*: UI Frontend hiển thị đúng đếm ngược 60 giây và backend trả lỗi HTTP 429 nếu cố tình bypass UI.

## Verification Plan

### Automated Tests
Developer sau khi code xong cần chạy lại toàn bộ test:
```bash
# Unit Test Backend
cd /home/lupca/projects/topvnsport/OMS/backend
pytest test_main.py -k "otp"

# E2E Test
cd /home/lupca/projects/topvnsport/e2e_tests
pytest tests/test_storefront_otp_flow.py
```

### Manual Verification
1. Lấy thông tin OAuth 4.0 từ Zalo Developer Portal.
2. Insert vào DB PostgreSQL (bảng `system_configs`).
3. Mở luồng checkout trên giao diện Web, nhập số điện thoại chưa từng đăng ký Zalo -> Kiểm tra web báo lỗi đỏ chính xác.
4. Nhập số điện thoại thật của DEV -> Kiểm tra tin nhắn ZBS OTP bắn về điện thoại (qua OA) và có thể verify để tạo Order thành công.
