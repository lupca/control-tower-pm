API Gửi tin
Lưu ý
Quyền cần có: Gửi tin qua số điện thoại

HTTP request
URL: https://business.openapi.zalo.me/message/template
Method: POST
Content Type: application/json
Response Type: application/json
Example request
curl --location 'https://business.openapi.zalo.me/message/template' \
--header 'Content-Type: application/json' \
--header 'access_token: your_access_token' \
--data '{
    "phone": "84987654321",
    "template_id": "7895417a7d3f9461cd2e",
    "template_data": {
        "ky": "1",
        "thang": "4/2020",
        "start_date": "20/03/2020",
        "end_date": "20/04/2020",
        "customer": "Nguyễn Thị Hoàng Anh",
        "cid": "PE010299485",
        "address": "VNG Campus, TP.HCM",
        "amount": "100",
        "total": "100000",
     },
    "tracking_id":"tracking_id"
}'

Tham số header
Tham số	Kiểu dữ liệu	Tính bắt buộc	Mô tả
access_token	string	yes	Đoạn mã cần truyền vào để xác minh quyền sử dụng API. Xem thêm tài liệu tham khảo
Cấu trúc body của request
Tham số	Kiểu dữ liệu	Tính bắt buộc	Mô tả
phone	string	yes	SĐT của người nhận.
Lưu ý: SĐT phải được liên kết với tài khoản Zalo và được viết ở định dạng chuẩn hóa theo mã quốc gia. (VD: SĐT 0987654321 viết theo định dạng chuẩn hóa của Việt Nam là 84987654321 hoặc +84987654321)
template_id	string	yes	ID của template muốn sử dụng.
template_id sẽ được phía Zalo cung cấp riêng cho từng đối tác.
template_data	JSON object	yes	Các thuộc tính của template mà đối tác đã đăng ký với Zalo.
Lưu ý: Cấu trúc template_data được quy định riêng ứng với từng template.
sending_mode	string	no	Chế độ gửi
Giá trị	Tên chế độ gửi	Mô tả
1 (Default)	Gửi thường	Tin qua SĐT được gửi theo cơ chế thông thường
3	Gửi vượt hạn mức	Cơ chế cho phép OA gửi tin qua SĐT tag 3 vượt hạn mức
Lưu ý: Chế độ Gửi vượt hạn mức (sending_mode = 3) chỉ áp dụng cho các OA được whitelist. Vui lòng liên hệ đội ngũ CSKH của Zalo Cloud qua support@zalo.solutions hoặc kênh hỗ trợ vận hành tin qua SĐT
tracking_id	string	yes	Mã số đánh dấu lần gọi API của đối tác, do đối tác định nghĩa. Đối tác có thể dùng tracking_id để đối soát mà không phụ thuộc vào message_id của Zalo cung cấp.
Lưu ý: Zalo khuyến khích sử dụng tham số có độ dài tối đa 48 ký tự và không chứa kí tự đặc biệt.
Ghi chú: API gửi tin qua SĐT có hỗ trợ mã hoá AES/CBC/PKCS5Padding. Chi tiết sẽ được trao đổi cụ thể trong lúc thực thi tích hợp nếu doanh nghiệp có yêu cầu.

Example respond
{
    "error": 0,
    "message": "Success",
    "data": {
           "msg_id": "a4d0243feee163bd3af2",
             "sent_time": "1626926349402",
             "sending_mode": "1",
             "quota": {
                "dailyQuota": "500",
                "remainingQuota": "499"
             }
    }
}

Cấu trúc thuộc tính data
Thuộc tính	Kiểu dữ liệu	Mô tả
msg_id	string	ID của tin qua SĐT.
sent_time	string	Thời gian gửi tin qua SĐT (định dạng timestamp).
sending_mode	string	Bao gồm giá trị:
1: tin qua SĐT được gửi theo cơ chế thông thường
3: tin qua SĐT được gửi theo cơ chế vượt hạn mức
quota	object	Thông tin quota tin qua SĐT của OA.
Cấu trúc thuộc tính data.quota
Thuộc tính	Kiểu dữ liệu	Mô tả
dailyQuota	string	Số lượng tin của OA được gửi qua SĐT trong 1 ngày.
Lưu ý: Hạn mức gửi tin qua SĐT mỗi ngày của OA sẽ tự động được điều chỉnh dựa theo chất lượng và nhu cầu gửi. Xem thêm chi tiết về cơ chế đánh giá chất lượng và quyền lợi gửi tin qua SĐT tại đây.
remainingQuota	string	Số lượng tin OA được gửi qua SĐT trong ngày còn lại.

Sự kiện người dùng nhận tin qua SĐT
Khi Official Account gửi tin nhắn cho người dùng và tin nhắn đã đến thiết bị người dùng, hệ thống Zalo sẽ gửi đến Webhook Url của ứng dụng một HTTP request như sau

Lưu ý
Quyền cần có: Nhận sự kiện gửi tin qua SĐT

Lưu ý
Thời điểm user nhận tin nhắn là giá trị của trường delivery_time, không phải thời điểm webhook nhận event hay giá trị của trường timestamp

URL: webhook URL của ứng dụng
Method: POST
Content Type: application/json
Header X-ZEvent-Signature: mac = sha256(appId + data + timeStamp + OAsecretKey), với data là chuỗi json trả về dưới đây.
Header X-ZEvent-Server: ZNS
Example request
{
  "sender": {
    "id": "2893352839501541173"
  },
  "recipient": {
    "id": "84123456789"
  },
  "event_name": "user_received_message",
  "message": {
    "delivery_time": "1602960467432",
    "msg_id": "15a0cc0bbb13bd4ce403",
    "tracking_id": "tracking_id"
  },
  "app_id": "2074138120372622546",
  "timestamp": "1602560967477"
}

Cấu trúc thuộc tính data
Thuộc tính	Kiểu dữ liệu	Mô tả
sender.id	string	ID của Official Account gửi tin
recipient.id	string	Số điện thoại người dùng nhận tin

Lưu ý: Số điện thoại sẽ có dạng mã hóa SHA-256 nếu đối tác gửi tin qua SĐT sử dụng hash phone.
event_name	string	Tên sự kiện

Giá trị nhận về: user_received_message
message.delivery_time	string	Thời gian thiết bị của người dùng nhận được tin qua SĐT
message.msg_id	string	ID của tin qua SĐT
message.tracking_id	string	Mã số đánh dấu lần gọi API của đối tác, do đối tác định nghĩa.
app_id	string	ID của ứng dụng gửi tin (ứng dụng mà OA đã cấp quyền)
timestamp	string	Thời điểm gửi sự kiện


Nếu cần cung cấp thì hỏi lại tôi.
https://developers.zalo.me/docs/zbs-template-message/gui-tin-template-qua-sdt/api-truy-xuat-thong-tin-gui-tin-qua-sdt/api-lay-thong-tin-trang-thai-gui-tin-qua-sdt

Sự kiện journey được tính phí
Khi có sự kiện tin nhắn journey đầu tiên thuộc chuỗi hành trình (journey) được gửi thành công đến thiết bị người dùng và journey bắt đầu được tính phí, hệ thống Zalo sẽ gửi đến Webhook Url của ứng dụng một HTTP request như sau.
https://developers.zalo.me/docs/zbs-template-message/gui-tin-template-qua-sdt/webhook-gui-tin-qua-sdt/su-kien-thay-doi-ve-han-muc-gui-tin-qua-sdt

Sự kiện journey hết hạn
Khi có sự kiện một journey hết hạn và chưa từng được sử dụng, hệ thống Zalo sẽ gửi đến Webhook Url của ứng dụng một HTTP request như sau.
https://developers.zalo.me/docs/zbs-template-message/gui-tin-template-qua-sdt/webhook-gui-tin-qua-sdt/su-kien-journey-het-han
Sự kiện thay đổi về hạn mức gửi tin qua SĐT
Khi có sự kiện thay đổi về hạn mức gửi tin của OA được phát sinh theo hệ thống đánh giá hoặc theo đề xuất thay đổi từ khách hàng, hệ thống Zalo sẽ gửi đến Webhook Url của ứng dụng một HTTP request như sau.
https://developers.zalo.me/docs/zbs-template-message/gui-tin-template-qua-sdt/webhook-gui-tin-qua-sdt/su-kien-journey-duoc-tinh-phi

API Lấy thông tin trạng thái gửi tin qua SĐT
API cho phép đối tác truy xuất trạng thái gửi tin qua SĐT.
https://developers.zalo.me/docs/zbs-template-message/gui-tin-template-qua-sdt/webhook-gui-tin-qua-sdt/su-kien-nguoi-dung-nhan-tin-qua-sdt