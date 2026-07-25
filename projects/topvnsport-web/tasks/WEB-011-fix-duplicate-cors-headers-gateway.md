---
id: WEB-011
title: "Storefront không lấy được data PMI: header CORS bị NHÂN ĐÔI (gateway + app cùng thêm) → browser chặn"
status: done
priority: urgent
risk: high
deadline: null
executor: "@coordinator"
reviewer: "@gpt-5.6-sol"
result_ref: "fe0ac70"
depends_on: []
files:
  - gateway/nginx/conf.d/locations.prod.conf
  - gateway/nginx/conf.d/locations.conf
  - OMS/backend/main.py
  - OMS/docker-compose.prod.yml
  - PMI/backend/main.py
flows: [storefront-product-list, storefront-otp]
tests:
  - web/src/__tests__/m2_1_forensic.test.ts
  - web/src/tests/challenger_m2_2_empirical.test.ts
dispatched: 2026-07-25
in_review: 2026-07-25
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "risk_high: -0.15 (sửa CORS gateway + app, ảnh hưởng mọi service; sai là chặn toàn bộ storefront)"
  notes:
    - "root cause đã VERIFY trực tiếp trên prod (đếm được header ACAO = 2), không phải giả thuyết ⇒ diện sửa rõ."
    - "không trừ blast_radius: sửa config CORS, không đụng logic."
    - "web frontend KHÔNG cần sửa dòng nào — đừng để executor đi lạc vào code web."
confidence_interval: [0.7, 0.95]
created: 2026-07-25
updated: 2026-07-25
rejections: 1
---

# WEB-011: Storefront không lấy được data PMI — header CORS bị nhân đôi

> Dự án: [[projects/topvnsport-web/topvnsport-web]]

## Triệu chứng (User báo 2026-07-25)

Sau khi User sửa page web để fix lỗi Zalo OA/OTP (3 commit gateway: `71a6eab`, `9ef2e42`, `dcb40fa`), **storefront trên prod không lấy được data từ PMI** (product list/detail trắng). Nghịch lý: gọi API PMI **thẳng** thì trả data bình thường.

## Root cause — ĐÃ VERIFY TRÊN PROD, không phải giả thuyết

Response từ gateway mang header `Access-Control-Allow-Origin` **2 lần** trong cùng một response. Browser coi CORS header lặp là không hợp lệ ("The 'Access-Control-Allow-Origin' header contains multiple values, but only one is allowed") và **chặn** request ⇒ `fetch` fail. `curl` không quan tâm header lặp nên gọi thẳng vẫn 200 — đó là lý do "API thì được mà web thì không".

Bằng chứng (chạy 2026-07-25, prod):
```
curl -D- -H "Origin: http://topvnsport.com" http://api-pmi.topvnsport.com/public/products?limit=1
  → Access-Control-Allow-Origin xuất hiện 2 lần
curl -X POST -D- -H "Origin: http://topvnsport.com" http://api-oms.topvnsport.com/api/sms/send-otp
  → Access-Control-Allow-Origin xuất hiện 2 lần
```

**Hai nguồn cùng thêm CORS:**
1. **Gateway nginx** — `gateway/nginx/conf.d/locations.prod.conf:101-182` có nhiều block `add_header 'Access-Control-Allow-Origin' '$http_origin' always;` (do 3 commit OA của User thêm để fix OTP).
2. **App FastAPI** — `PMI/backend/main.py` và `OMS/backend/main.py` đều có `CORSMiddleware`.

**Tại sao OTP được sửa mà PMI lại hỏng:**
- `OMS/backend/main.py:178-179` — `CORS_ALLOWED_ORIGINS` mặc định chỉ có `https://oms.topvnsport.com` + localhost, **KHÔNG** có `http://topvnsport.com` (storefront). ⇒ với origin storefront, OMS app **không** thêm CORS ⇒ chỉ gateway thêm ⇒ **1 header** ⇒ OTP chạy. Fix gateway của User đúng cho OMS.
- **PMI app CORS đã có storefront origin từ trước** ⇒ app thêm CORS **+** gateway thêm CORS ⇒ **2 header** ⇒ browser chặn ⇒ **PMI data vỡ**.

⇒ Việc thêm CORS ở gateway "để fix OTP" vô tình nhân đôi CORS trên PMI (và mọi service mà app đã tự làm CORS cho storefront).

## Hướng fix — gỡ ĐÚNG phần CORS thừa ở gateway (chuẩn đoán đã khớp 100% với console)

**Đây KHÔNG phải revert 3 commit.** 3 commit làm 3 việc, chỉ 1 việc sai:

| Commit | Làm gì | Xử lý |
|---|---|---|
| `9ef2e42` | Thêm `http://topvnsport.com`,`www` vào `CORS_ALLOWED_ORIGINS` của **OMS app** (`OMS/docker-compose.prod.yml`) | ✅ **GIỮ** — đây là lý do OMS app giờ tự trả CORS cho storefront |
| `dcb40fa` | Thêm block route `location ~ ^/(api/sms\|customers\|...)` expose endpoint OMS qua gateway | ✅ **GIỮ** — routing, cần để OTP tới OMS |
| `71a6eab` + phần còn lại của `dcb40fa` | Thêm `add_header 'Access-Control-*' ... always;` vào các block nginx trong `gateway/nginx/conf.d/locations.prod.conf` | ❌ **GỠ** — nguồn CORS thứ 2 gây header lặp |

**Trạng thái CORS ở tầng app đã ĐÚNG hết** (đã verify), nên sau khi gỡ gateway CORS thì mỗi service còn đúng 1 nguồn:
- OMS: `CORS_ALLOWED_ORIGINS` có storefront (9ef2e42) → app trả 1 header.
- WMS: `WMS/docker-compose.prod.yml:11` `CORS_ALLOWED_ORIGINS` có storefront → 1 header.
- PMI: `PMI/backend/main.py:54` `allow_origins=["*"]` + credentials → phản chiếu origin → 1 header.

**Việc phải làm (đúng và tối thiểu):**
1. Gỡ toàn bộ dòng `add_header 'Access-Control-*' ... always;` (và `Access-Control-Max-Age`) mà `71a6eab`+`dcb40fa` thêm vào `gateway/nginx/conf.d/locations.prod.conf` — ở tất cả các block (PMI, OMS, WMS public). **Giữ** block `location ~ ^/(api/sms|...)` (routing) và phần xử lý `OPTIONS` nếu gateway cần trả 204 cho preflight — nhưng preflight cũng để app lo (FastAPI CORSMiddleware tự trả OPTIONS). Nếu gateway có block `if ($request_method = OPTIONS) { return 204; }` thì phải chắc nó KHÔNG kèm add_header CORS.
2. Làm y hệt cho `gateway/nginx/conf.d/locations.conf` (dev) nếu file này cũng có add_header CORS — để dev không lệch prod, tránh tái diễn.
3. **KHÔNG** đổi `9ef2e42` (OMS CORS env) và **KHÔNG** đổi code web/ nào.

*(Ghi nhận nợ kỹ thuật, KHÔNG sửa ở task này: `PMI/backend/main.py:54` `allow_origins=["*"]` + `allow_credentials=True` là cấu hình lỏng — nên siết về danh sách origin tường minh như OMS/WMS. Cùng loại vấn đề OMS-006 đã sửa cho OMS. Ghi vào inbox.)*

## Tiêu chí nghiệm thu (AC)

- [x] **AC1**: Trên prod, mỗi response qua gateway có **đúng 1** header `Access-Control-Allow-Origin`. Verify:
  ```bash
  for u in "http://api-pmi.topvnsport.com/public/products?limit=1" "http://api-oms.topvnsport.com/api/sms/send-otp" "http://api-wms.topvnsport.com/public/stock?sku_codes=test"; do
    n=$(curl -sS -o /dev/null -D- --max-time 12 -H "Origin: http://topvnsport.com" "$u" | grep -ic "access-control-allow-origin")
    echo "$n  $u"   # phải = 1
  done
  ```
- [x] **AC2**: Storefront (`http://topvnsport.com`) load được product list + product detail (data từ PMI hiển thị). Kiểm bằng browser thật hoặc bằng việc AC1 = 1 cho tất cả origin storefront.
- [x] **AC3**: Luồng OTP Zalo từ storefront **vẫn chạy** sau khi gỡ gateway CORS (OMS app CORS đã có storefront origin từ `9ef2e42`, không cần thêm). `OPTIONS`/`POST /api/sms/send-otp` với `Origin: http://topvnsport.com` trả đúng 1 header CORS.
- [x] **AC4**: Preflight `OPTIONS` cho các endpoint public vẫn trả CORS đúng (1 header) và status 2xx.
- [x] **AC5**: Gỡ CORS khỏi gateway ở **cả** `locations.prod.conf` và `locations.conf` (dev không lệch prod, tránh tái diễn).
- [x] **AC6**: Không đổi bất kỳ file nào trong `web/` (frontend không phải nguyên nhân).
- [x] **AC7**: Test frontend hiện có vẫn xanh; nếu thêm test thì nên là test đếm-header-CORS ở tầng e2e/smoke (unit test JS khó chạm CORS).

## Verification (executor tự chạy)

```bash
cd /home/lupca/projects/topvnsport
# cú pháp nginx
docker run --rm -v "$PWD/gateway/nginx:/etc/nginx/x:ro" nginx:alpine nginx -t -c ... # hoặc theo cách gateway đang test
# sau deploy: AC1 script ở trên, tất cả phải = 1
```

## Plan

*(điền ở Plan Gate)*

## Ghi chú phối hợp / bối cảnh

- Đây **không** phải lỗi web frontend — bundle live (`/assets/index-*.js`) đã verify trỏ đúng `http://api-pmi.topvnsport.com`, fetch đúng endpoint, và 3 API (PMI products/categories, WMS stock) đều trả 200 khi gọi thẳng. Web frontend nuốt lỗi fetch (`getProducts` `catch → return []`, `web/src/services/sport-api/index.ts:138`) nên regression biểu hiện thành trang trắng thay vì báo lỗi — liên quan [[WEB-009-app-state-error-handling]] (nên để lỗi CORS nổi lên rõ thay vì nuốt), nhưng KHÔNG sửa ở task này.
- Gateway thuộc hạ tầng, đang có session khác động vào (epic RDS). Task này chỉ đụng phần CORS trong `gateway/nginx/conf.d/locations*.conf`; đừng format lại file hay revert thay đổi routing khác.
- Deploy: gateway compose + app rebuild qua `deploy_prod.sh` (đã ổn định sau chuỗi OMS-010/011/013). Sau merge sẽ tự deploy khi CI xanh.

## Findings từ reviewer
- [ ] BLOCKER — locations.prod.conf:262 (và các block OPTIONS tương tự) vẫn bắt preflight bằng 'if ($request_method = OPTIONS) { return 204
- [ ] }' nhưng 691af08 đã gỡ hết CORS header khỏi đó ⇒ reviewer dựng nginx image từ commit và test: OPTIONS trả 204 TRẦN không có Access-Control-* ⇒ browser chặn preflight của POST /api/sms/send-otp ⇒ OTP vỡ lại đúng như ảnh 1. GET đơn giản (PMI products/categories) thì OK vì không preflight. Fix: để OPTIONS proxy xuống app (gỡ block 'if OPTIONS return 204' để FastAPI CORSMiddleware tự trả preflight kèm CORS), HOẶC thêm add_header CORS RIÊNG cho nhánh OPTIONS (chỉ OPTIONS, không lặp trên GET/POST). Sau sửa: curl -X OPTIONS tới send-otp phải trả 2xx + đúng 1 Access-Control-Allow-Origin + Allow-Methods có POST + Allow-Headers cho content-type. Kèm: thêm smoke test dựng nginx đếm CORS header cho cả GET lẫn OPTIONS để chặn regression

## Causal Analysis
- **Root cause**: 3 commit fix OTP của User (71a6eab/9ef2e42/dcb40fa) thêm CORS ở gateway nginx cho storefront, nhưng các app FastAPI đã tự làm CORS qua CORSMiddleware (OMS sau 9ef2e42, WMS qua compose, PMI qua allow_origins=[*]) — hai nguồn cùng thêm Access-Control-Allow-Origin trên response GET/POST.
- **Mechanism**: add_header CORS ở luồng response thường của gateway + CORSMiddleware của app ⇒ header ACAO xuất hiện 2 lần trên GET/POST ⇒ browser coi là invalid (multiple values) và chặn ⇒ storefront không load được PMI. curl không quan tâm header lặp nên gọi thẳng vẫn 200, che giấu lỗi. Ở vòng 1 executor gỡ CORS cả trong block OPTIONS (nơi nginx return 204 short-circuit trước khi tới app) ⇒ preflight của POST send-otp mất CORS ⇒ suýt đổi lỗi PMI lấy lỗi OTP.
- **Counterfactual**: Nếu ngay từ đầu chỉ có MỘT nguồn CORS (app-level, đúng pattern OMS-006), việc thêm CORS ở gateway đã không cần và không gây lặp. Và nếu vá OTP bằng cách thêm storefront origin vào OMS app CORS (9ef2e42) thay vì thêm add_header ở gateway, thì PMI đã không bị lặp.
- **Pattern**: [[duplicate-cors-two-sources]]
