---
id: WEB-011
task_path: projects/topvnsport-web/tasks/WEB-011-fix-duplicate-cors-headers-gateway.md
project: topvnsport-web
result_ref: fe0ac70
executor: @coordinator
reviewer: "@gpt-5.6-sol"
status: passed
issued: 2026-07-25
verdict: pass
verdict_date: 2026-07-25
---

# Phiếu Review: WEB-011 — Storefront không lấy được data PMI: header CORS bị NHÂN ĐÔI (gateway + app cùng thêm) → browser chặn

- Dự án: topvnsport-web (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-web/tasks/WEB-011-fix-duplicate-cors-headers-gateway.md`
- Result-ref: fe0ac70
- Executor: @coordinator
- Reviewer: @gpt-5.6-sol
- Ngày phát phiếu: 2026-07-25

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [ ] **AC1**: Trên prod, mỗi response qua gateway có **đúng 1** header `Access-Control-Allow-Origin`. Verify:
  ```bash
  for u in "http://api-pmi.topvnsport.com/public/products?limit=1" "http://api-oms.topvnsport.com/api/sms/send-otp" "http://api-wms.topvnsport.com/public/stock?sku_codes=test"; do
    n=$(curl -sS -o /dev/null -D- --max-time 12 -H "Origin: http://topvnsport.com" "$u" | grep -ic "access-control-allow-origin")
    echo "$n  $u"   # phải = 1
  done
  ```
- [ ] **AC2**: Storefront (`http://topvnsport.com`) load được product list + product detail (data từ PMI hiển thị). Kiểm bằng browser thật hoặc bằng việc AC1 = 1 cho tất cả origin storefront.
- [ ] **AC3**: Luồng OTP Zalo từ storefront **vẫn chạy** sau khi gỡ gateway CORS (OMS app CORS đã có storefront origin từ `9ef2e42`, không cần thêm). `OPTIONS`/`POST /api/sms/send-otp` với `Origin: http://topvnsport.com` trả đúng 1 header CORS.
- [ ] **AC4**: Preflight `OPTIONS` cho các endpoint public vẫn trả CORS đúng (1 header) và status 2xx.
- [ ] **AC5**: Gỡ CORS khỏi gateway ở **cả** `locations.prod.conf` và `locations.conf` (dev không lệch prod, tránh tái diễn).
- [ ] **AC6**: Không đổi bất kỳ file nào trong `web/` (frontend không phải nguyên nhân).
- [ ] **AC7**: Test frontend hiện có vẫn xanh; nếu thêm test thì nên là test đếm-header-CORS ở tầng e2e/smoke (unit test JS khó chạm CORS).

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: web/src/__tests__/m2_1_forensic.test.ts, web/src/tests/challenger_m2_2_empirical.test.ts
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (xác nhận reviewer @gpt-5.6-sol ≠ executor @coordinator)

## Test gợi ý chạy trong repo code
- `web/src/__tests__/m2_1_forensic.test.ts`
- `web/src/tests/challenger_m2_2_empirical.test.ts`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict WEB-011 <pass|changes> --reviewer @gpt-5.6-sol [--commit <hash>] [--notes "..."]`
