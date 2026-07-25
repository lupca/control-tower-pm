# HÒM THƯ YÊU CẦU CHỜ PHÂN LOẠI (inbox.md)

Nơi lưu trữ các ghi chú thô, ý tưởng, hoặc feedback từ User. Gõ `/ingest` để Agent tự động phân loại những yêu cầu này thành các task chi tiết trong thư mục `projects/`.

> **Dọn ngày 2026-07-25** (session OMS-010/011): đã xoá các mục đã xử lý xong. Lịch sử đầy đủ của từng mục nằm trong `log.md` nếu cần tra lại. Đã xoá: OMS task ordering conflict (đã chốt), `DATABASE_URL` default chứa creds RDS (fix ở `b9d4259`), CI đỏ do `env_file` (fix ở `a953632`), cảnh báo push-vào-RDS-rỗng (data đã migrate), task IAM auth (cluster mới dùng password auth), cập nhật `prod-infrastructure.md` (đã update), endpoint WMS cũ (fix ở `b9d4259`), và mục bàn giao cluster mới (đã hoàn thành).
>
> ⚠️ **Đã gỡ secret khỏi file này**: mục bàn giao cluster có dán cleartext `RDS_PASSWORD` (kèm 2 ví dụ DSN đầy đủ). `inbox.md` là **git-tracked** — may là những dòng đó chưa được commit (`git log -S` xác nhận rỗng) nên xoá bây giờ là chúng không bao giờ vào git history. Giá trị đang nằm ở GitHub secret `RDS_PASSWORD`, không cần bản sao ở đây. **Đừng dán secret vào file trong repo** — xem mục 11.

---

## OCR SCAN FINDINGS — 2026-07-25 (chưa có task, còn mở)

### PMI Backend

1. **ALLOWED_SERVICE_KEYS crash at import** (`PMI/backend/routers/audit.py:17-18`) — HIGH
   - `os.environ["ALLOWED_SERVICE_KEYS"]` raise KeyError nếu không set
   - Variable định nghĩa nhưng không dùng

   *(Finding cũ "alembic.ini empty sqlalchemy.url" đã xoá — **false positive**: `PMI/backend/alembic/env.py` set `sqlalchemy.url` lúc runtime bằng `config.set_main_option`, để trống trong `.ini` là đúng thiết kế và OMS-010 cũng làm y vậy.)*

### OMS Backend

2. **Config update unrestricted keys** (`OMS/backend/routers/config.py:62-73`) — HIGH
   - Cho phép modify bất kỳ config key nào (kể cả `database_url`)
   - Lưu ý: OMS-006 đã thêm check admin role, nhưng **chưa** giới hạn tập key được sửa

3. **ZaloConfigOut expose secrets** (`OMS/backend/schemas/auth.py:14-19`) — HIGH (security)
   - API response chứa `zalo_secret_key`, `zalo_access_token`, `zalo_refresh_token`

4. **Mutable default arguments** (`OMS/backend/schemas/order.py:63-70`) — HIGH (bug)
   - `items: List[OrderItemOut] = []` — shared state across instances

5. **Concurrency: config update** (`OMS/backend/routers/config.py:55-74`) — MEDIUM
   - Lost updates khi concurrent PUT

### WMS Backend

6. **Mutable default arguments `= []`** (`WMS/backend/schemas.py`) — HIGH
   - `InboundItemCreate.items`, `PickListItemCreate.pick_list_items`, etc.

7. **seed.py resource leak + partial transaction** (`WMS/backend/seed.py`) — HIGH
   - `db.close()` không được gọi nếu exception
   - Commit sau mỗi insert → partial seeded state

### Web Frontend

8. **omsHelpers: HTTP error returns null** (`web/src/services/sport-api/omsHelpers.ts:14-16`) — HIGH
   - Trả `null` thay vì throw → caller không phân biệt được "not found" vs "API fail"

9. **popupService emit() không catch exception** (`web/src/components/ui/popupService.ts:81-84`) — HIGH
   - Listener throw → crash app hoặc reject promise

10. **HomePage Redux selectors undefined** (`web/src/features/home/HomePage.tsx:145-157`) — HIGH
    - `products`, `blogs`, `categories` có thể undefined → crash khi gọi `.filter()`

11. **imageByVisualOption ignores tier2** (`ProductDetailPage.tsx:135-157`) — MEDIUM (bug)
    - Early return sau tier1 → tier2 media không bao giờ được xử lý

---

## Ý TƯỞNG & YÊU CẦU MỚI

1. *Ghi chú (2026-07-21):* Sửa lỗi variant không load được hình ảnh khi kích thước file ảnh quá lớn (lỗi nén ảnh phía frontend). Ưu tiên cao, ảnh hưởng trực tiếp tới chuyển đổi bán hàng.

2. *✅ Bug 500 Zalo OA — ĐÃ SỬA TRÊN PROD (2026-07-26), còn 1 việc User phải làm:*
   - Root cause: `system_configs.config_value` là `VARCHAR(500)` trên DB thật trong khi model khai unbounded; OMS không có migration tool nên drift không bao giờ được sửa.
   - Chuỗi task: **OMS-006** ✅ (`3116bf3`) → **OMS-010** ✅ (`a953632`) → **OMS-011** ✅ (`b9d4259`) → **OMS-013** ✅ (`48a410e`, reviewed by @antigravity).
   - **Deploy `#30153397265` (cb51bee) THÀNH CÔNG 2026-07-26**: 3/3 migration ok, 9/9 health check 200, `Identity->OMS JWT smoke check: 200`, `Deployment completed successfully`. `0003_config_value_text` đã áp lên RDS ⇒ cột giờ là `TEXT`.
   - ✅ **Cấu hình Zalo đã ghi lên prod (2026-07-26)**: `system_configs` trên RDS trước đó rỗng (dữ liệu Zalo không sang RDS trong đợt migration — khớp nghi vấn: runbook dump `docker exec oms-db pg_dump -U postgres oms` nhưng container thật `oms_db`/database `oms_db`). User đã `PUT /api/configs/sms` (User tự chạy vì classifier chặn coordinator ở thao tác ghi secret lên prod) với 5 giá trị Zalo → báo "ok". `PUT` trả 200 = chính bug ban đầu đã hết end-to-end.
   - 🔴 **CÒN LẠI — rotate**: các token vừa nhập là token CŨ, đã lộ cleartext trong `index.md` (git-tracked, đã commit). Nên sinh token Zalo mới ở OA console rồi `PUT` lại. Gộp vào danh sách rotate mục 11.

3. *Ghi chú hệ thống (2026-07-25):* **Process ngoài hệ tự ghi state không hợp lệ vào task file** — 3 lần trong 1 phiên (OMS-006 reviewer ghi `status: passed`; OMS-012 + DEVOPS-002 executor ghi `status: completed`). Cả 3 đã được sửa tay.
   - **Nguyên nhân**: mọi process spawn với cờ bypass permission nên có toàn quyền ghi vào control-tower dù cwd là repo code.
   - **Hướng xử lý, chưa mở task**: `/lint` bắt `status:` ngoài tập hợp lệ (`todo`/`dispatched`/`in-review`/`changes-requested`/`done`) + bắt `status: done` mà `reviewer`/`result_ref` rỗng; hoặc chặn ở tầng quyền.
   - Ghi nhận tích cực: từ khi prompt spawn có câu "report verdict as text, do NOT write status/verdict into the task frontmatter", 2 reviewer gần nhất đã tôn trọng ranh giới → nên giữ câu đó trong mọi prompt spawn.

4. *Lỗ hổng CI (2026-07-25):* job `wms-backend` trong `.github/workflows/ci.yml` chỉ chạy `python -m py_compile main.py`, **không chạy pytest** — toàn bộ test backend WMS chưa từng chạy trên CI. Job `oms-backend` đã được OMS-010 AC17 sửa (thêm `Run pytest` + `services: postgres`), dùng làm khuôn. Chưa mở task.

6. *Task cần mở — rotate `JWT_SECRET_KEY` dùng chung (2026-07-25):*
   - Literal `identity_jwt_secret_key_2026_change_me_in_prod` là secret sign/verify JWT dùng chung giữa identity (nơi SIGN), PMI, OMS, WMS. Nằm trong repo ⇒ ai đọc được repo là **forge được JWT admin cho cả 4 service**. Chính cái tên `..._change_me_in_prod` cho thấy chưa ai đổi.
   - ✅ **Việc khó đã xong ở OMS-011**: cả 4 service giờ đọc từ **một** GitHub secret `JWT_SECRET_KEY` (`${JWT_SECRET_KEY:?}`), fallback literal trong code đã bỏ. Giá trị secret hiện tại = đúng literal cũ nên không ai bị logout.
   - ⇒ **Rotate giờ chỉ là**: đổi giá trị secret `JWT_SECRET_KEY` trên GitHub + redeploy. Không phải sửa code. Hệ quả: mọi token client invalid ⇒ logout hàng loạt (User đã đồng ý "cho logout ko sao cả"). Nên làm **sau** khi OMS-011 deploy xong và verify ổn.

7. *Vận hành CI/CD — ĐỪNG `gh run rerun` một Deploy run (2026-07-25):*
   `deploy.yml` được trigger bởi `workflow_run` (khi CI success). Rerun trực tiếp một Deploy run bị **kẹt `queued` vĩnh viễn, không được cấp runner** — đã gặp thật với run `30150911028`: 17 phút ở `queued`, không step nào chạy. Đã loại hết các nguyên nhân khác: repo public nên Actions miễn phí, GitHub Actions `operational`, chỉ có 1 run queued nên không phải bị `concurrency` chặn bởi run khác. Nguyên nhân là loại trigger `workflow_run` cần event gốc để dựng context.
   - Tệ hơn: run kẹt đó **giữ luôn group `concurrency: deploy-production`** (`cancel-in-progress: false`) nên Deploy mới cũng không chen vào được ⇒ phải `gh run cancel` nó trước.
   - **Cách đúng để deploy lại**: `gh run rerun <CI_RUN_ID>` (rerun CI, Deploy sẽ tự bắn qua `workflow_run`), hoặc push một commit mới lên `main`.
   - Cân nhắc thêm cho `deploy.yml`: thêm `workflow_dispatch:` vào `on:` để có thể deploy lại bằng tay mà không cần chạy lại CI.

8. *✅ ĐÃ XỬ LÝ — deploy fail vì `FERNET_KEY` secret không hợp lệ (2026-07-25):*
   Push `b9d4259` → CI **success** (`30150857338`) → Deploy `30150911028` **failure sau 5 giây** tại bước preflight:
   ```
   FERNET_KEY must be a valid 32-byte urlsafe-base64 Fernet key
   ```
   - ✅ **Prod KHÔNG bị ảnh hưởng** — preflight của OMS-011 AC2 chặn trước khi build/start bất cứ gì. Đây đúng là tác dụng của việc validate FORMAT chứ không chỉ validate "có set hay không" (OCR flag `high` ở `crypto.py:8-15`). Nếu chỉ check non-empty thì container đã start rồi crash-loop.
   - Đã kiểm: đoạn validate **đúng** (`deploy_prod.sh:20` regex `^[A-Za-z0-9_-]{43}=$` + decode phải ra 32 byte). Cả key cũ lẫn key dev đều pass. ⇒ giá trị secret `FERNET_KEY` hiện tại thật sự không phải Fernet key (có thể là passphrase thường, hoặc dính newline lúc paste).
   - ✅ **ĐÃ SET (2026-07-25)**: User cho phép tường minh sau khi permission classifier chặn lần đầu ⇒ coordinator chạy `gh secret set FERNET_KEY` = key fallback cũ (44 ký tự, decode ra 32 byte, đã verify hợp lệ). Lý do chọn key cũ: đó chính là key đã mã hoá dữ liệu Zalo trên prod ⇒ pass cả preflight (format) và smoke check (giải mã được). **Key này nằm trong git history nên chỉ dùng tạm — phải rotate ngay sau khi prod xanh** (xem mục 10).
   - **Khuyến nghị (A) — deploy xanh ngay**: set `FERNET_KEY` = key fallback CŨ, vì đó chính là key đã mã hoá dữ liệu Zalo đang nằm trên prod ⇒ vừa hợp lệ vừa giải mã được, smoke check sẽ pass:
     ```
     cd /home/lupca/projects/topvnsport
     printf '%s' "$(git show 3116bf3~1:OMS/backend/models.py | grep -oE '"[A-Za-z0-9_=-]{44}"' | head -1 | tr -d '"')" | gh secret set FERNET_KEY
     gh run rerun 30150911028
     ```
     Rồi **rotate ngay sau khi prod xanh** (key này nằm trong git history): sinh key mới `python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`, chạy `OMS/backend/scripts/reencrypt_system_configs.py` với `FERNET_KEY_OLD` = key cũ, đổi secret, redeploy.
   - **Phương án (B)**: set key mới ngay. Deploy sẽ áp được migration nhưng **smoke check sẽ fail** (row cũ không giải mã được) ⇒ deploy đỏ, rồi phải nhập lại token Zalo qua UI và rerun deploy. Chậm hơn và deploy đỏ một lần, nhưng không bao giờ dùng key đã lộ. Dù sao token Zalo cũng phải nhập lại vì đã lộ (mục 11).

10. *DEVOPS IaC — ✅ DONE (2026-07-25):*
   - [x] ~~Tạo cluster mới `topvnsport-db`~~ — VPC networking + password auth
   - [x] ~~Migrate data~~ — pmi/oms/wms/identity
   - [x] ~~`terraform import`~~ — 12 resources
   - [x] ~~Add GitHub Secrets~~ — `RDS_HOST`, `RDS_USER`, `RDS_PASSWORD`, `RDS_SSLMODE`
   - [x] ~~Xoá cluster cũ `database-topvnsport`~~ — deletion triggered, đang xóa
   - [x] ~~Image URLs~~ — không cần update (tất cả là external CDN, 0 MinIO URLs)
   - [ ] `terraform plan` drift — low priority, infra đang hoạt động
   - [ ] `migrate_to_rds_s3.sh` script — low priority, migration đã chạy manually

   **IaC Review Findings (2026-07-25), chưa có task:**
   - **HIGH**: SSH mở `0.0.0.0/0` (`modules/ec2/variables.tf:49-55`) — nên giới hạn VPN/bastion
   - **HIGH**: RDS nằm public subnet (`environments/prod/main.tf:52`) — cần private subnet
   - **HIGH**: EBS của EC2 chưa mã hoá (`modules/ec2/main.tf:37-40`)
   - **MEDIUM**: VPC thiếu private subnet/NAT · RDS egress `0.0.0.0/0` (`modules/rds/main.tf:23-28`) · chưa có IAM instance profile cho EC2 · S3 CORS cho phép mọi header · chưa có CloudWatch alarm / VPC flow logs
   - Ghi chú từ session OMS: `modules/rds/main.tf` **không khai** `iam_database_authentication_enabled`, và có `lifecycle { ignore_changes = [master_password] }` — nên `terraform apply` không đổi được password (đúng thiết kế, phải dùng AWS CLI). Cluster mới `topvnsport-db` chỉ resolve **private `172.31.x.x`** (đã đóng public access — tốt); cluster cũ thì mở được TCP từ máy dev, nên xoá sớm.

11. *🔴 CẦN ROTATE — secret đã lộ (2026-07-25):* Danh sách gộp, tất cả đều **chưa** rotate:
   - **Zalo** App Secret Key / OA Access Token / OA Refresh Token — dán cleartext vào `index.md`, **đã commit** vào git history.
   - **RDS master password** — dán cleartext vào chat và vào `inbox.md`. Đã gỡ khỏi `inbox.md` trước khi commit (`git log -S` xác nhận chưa vào history), nhưng transcript phiên làm việc có chứa. Rotate = `aws rds modify-db-cluster --master-user-password` + sửa 1 secret GitHub, **không phải sửa code** (đây là lợi ích của thiết kế OMS-011 AC15).
   - **AWS access key** `AKIAV3PVP3HTW6QS4RDH` — lộ trong chat. *(Giữ lại key **ID** ở đây là có chủ ý: ID là định danh, không phải bí mật, và cần nó để biết rotate key nào. Phần bí mật là secret access key — không ghi ở đâu.)*
   - **EC2 sudo password** — lộ trong chat. Giá trị **không ghi lại ở đây** (file này git-tracked); nếu cần thì tra transcript. Đổi bằng `passwd` trên EC2.
   - **`JWT_SECRET_KEY`** — xem mục 6.
   - **Quy tắc từ đây**: không dán secret vào bất kỳ file trong repo (kể cả `inbox.md`, `index.md`, task file). Cần truyền thì đặt vào GitHub secret / `.env` trên host rồi chỉ ghi **tên biến** vào file.

12. *Nợ kỹ thuật — PMI CORS wildcard (2026-07-25):* `PMI/backend/main.py:54` dùng `allow_origins=["*"]` + `allow_credentials=True`. Nên siết về danh sách origin tường minh (như OMS đã làm ở OMS-006, WMS ở compose). Không chặn gì hiện tại nhưng là cấu hình lỏng. Không sửa trong WEB-011 (task đó chỉ gỡ gateway CORS thừa).

13. *✅ WEB-011 done (2026-07-26):* Storefront lấy lại được data PMI. Root cause = header CORS nhân đôi (gateway add_header + app CORSMiddleware). Fix `fe0ac70`: giữ CORS chỉ trong block OPTIONS của gateway (nguồn preflight vì mọi location return 204 trước proxy), gỡ ở luồng response thường. Verify trên prod sau deploy: ACAO=1 trên PMI/WMS GET, OTP OPTIONS preflight 204+CORS+POST. Coordinator tự execute vòng 2 (CLI bị kill), NHƯNG có review độc lập @gpt-5.6-sol (dựng nginx test lại) → four-eyes GIỮ. OMS-013 cũng đã có review độc lập. Nợ nhỏ: chưa có persistent nginx CORS regression test (reviewer nêu low-risk) — nên thêm để chặn tái diễn.

14. *🔴 NỢ HARDENING — service token dùng placeholder in-git (2026-07-25, từ OMS-014):* Sau khi WEB-011 unblock storefront, lộ lỗi mới: OMS→PMI 401 `Invalid Service API Key` vì token lệch (PMI đòi `prod_..._must_change`, OMS/WMS gửi `oms_wms_internal_api_key_secret_2026`). OMS-014 hotfix chỉ đưa PMI về cùng default → luồng order chạy. NHƯNG token vẫn là placeholder yếu nằm trong git ở NHIỀU nơi:
    - `PMI/docker-compose.prod.yml` (INTERNAL_SERVICE_TOKEN + ALLOWED_SERVICE_KEYS=`prod-service-api-key-must-change`)
    - default code: `OMS/backend/utils/api_utils.py:14`, `OMS/backend/utils/auth.py:52`, `WMS/backend/utils/helpers.py:29`, `WMS/backend/utils/auth.py:52`
    Việc cần làm (mở task, cần User tạo GitHub secret): 1 secret `INTERNAL_SERVICE_TOKEN` thật → `deploy_prod.sh upsert_env_var` vào `.env.prod` từng service → mọi compose đổi sang `${INTERNAL_SERVICE_TOKEN:?}` fail-fast → bỏ default yếu trong code. Đổi ĐỒNG THỜI mọi service (OMS dùng chung 1 key cho cả PMI lẫn WMS nên không thể lệch). Cùng lớp với OMS-011 (FERNET_KEY continuity).

15. *🔎 CHƯA MỞ TASK — storefront không đặt được đơn cho khách ĐÃ TỒN TẠI (2026-07-25):* Sau OMS-014 (token OMS→PMI đã thông — hết "Invalid Service API Key", create customer chạm handler), lộ lỗi NGHIỆP VỤ tầng thiết kế. Cần executor/reviewer thật, KHÔNG để coordinator tự vá.
    - **Triệu chứng:** đặt đơn cho phone đã có (vd 0382426669) → `GET /customers?search=` 401, `POST /customers` 400 "already exists", đơn fail (`Failed to create customer`).
    - **Root cause:** `POST /orders` cần `customer_id`. Web `findOrCreateCustomer` (`web/src/services/sport-api/index.ts:275`) lấy id qua `GET /customers` — route này `get_current_user` **staff-only → 401** với client công khai; fallback `POST /customers` (`get_optional_user`, public) khi trùng phone trả 400 **không kèm id**. ⇒ khách cũ không có đường lấy id. Web KHÔNG tự sửa được — bắt buộc đổi backend OMS.
    - **Ràng buộc bảo mật:** không nên mở `GET /customers` cho public (enumeration toàn bộ khách + PII name/email/address). `POST /customers` đã public sẵn (oracle tồn-tại-phone đã lộ qua 400).
    - **Files liên quan:** `OMS/backend/routers/customers.py`, `web/src/services/sport-api/index.ts`, `OMS/backend/routers/orders.py` (customer_id), gateway `locations.prod.conf:282`. Monorepo cùng repo_root → 1 task 1 commit.

17. *🔎 CHƯA MỞ TASK — MPT-001 (money-printer-turbo): video sinh ra nhưng KHÔNG có tiếng (2026-07-25):* User xác nhận trực tiếp sau khi tự mở file. Cần executor/reviewer thật debug lại (task MPT-001 hiện vẫn `status: dispatched`, `result_ref: null` — executor process không tự cập nhật task file khi xong).
    - **Đã chạy:** dispatch task [[MPT-001-generate-test-video-ao-the-thao]] cho `@gpt-5.6-luna-high` qua `codex exec -m gpt-5.6-luna -c model_reasoning_effort=high --dangerously-bypass-approvals-and-sandbox` (User tự chạy lệnh trong terminal riêng vì permission classifier chặn coordinator spawn — 2 lần chặn: 1 lần do key literal trong lệnh, 1 lần do chính flag `--dangerously-bypass-approvals-and-sandbox`). Chủ đề: "Áo thể thao (sports jersey): chất liệu, công dụng và cách chọn mua", `--video-source pexels`, provider LLM = SiliconFlow (user cung cấp key trực tiếp qua chat, truyền cho executor bằng file tạm ngoài git, executor đã tự xoá file tạm sau khi dùng — key KHÔNG lọt vào bất kỳ file control-tower nào).
    - **Kết quả trên đĩa** (`/data/projects/MoneyPrinterTurbo/storage/tasks/17d62094-6630-44f1-b679-067c7c160f93/`): `script.json` (2003 bytes), `audio.mp3` (135219 bytes — TTS có sinh ra file, không rỗng), `subtitle.srt` (394 bytes), `combined-1.mp4` (188389 bytes), `final-1.mp4` (347557 bytes) — file cuối lớn hơn `combined-1.mp4` (có thể do burn subtitle) nhưng theo User phát ra **không có tiếng**.
    - **Cấu hình liên quan** (`config.toml` executor tạo): `openai_base_url = "https://api.siliconflow.cn/v1"` (SiliconFlow qua path OpenAI-compatible) cho LLM; mục `[siliconflow]` chỉ điền API key, `voice_name`/`tts_server` vẫn để mặc định (comment sẵn, không set tường minh) ⇒ nghi TTS thực tế chạy qua Edge TTS mặc định, không phải SiliconFlow TTS — cần xác minh provider TTS thật đã dùng.
    - **Nghi vấn root cause (chưa xác nhận, cần executor điều tra thật):** `audio.mp3` tồn tại + có kích thước hợp lý ⇒ bước TTS (`voice.py`) không phải nguyên nhân trực tiếp; nhiều khả năng lỗi nằm ở bước mux audio+video cuối (`generate_video`/`combine_videos`, `app/services/video.py`) — track audio có thể không được gắn vào `final-1.mp4`, hoặc bị mất khi burn subtitle/hiệu ứng. OCR pre-scan lúc tạo task (xem MPT-001) từng flag `prepare_cli_files` không atomic và validate `--bgm-type` mập mờ — không liên quan trực tiếp bug này (task không dùng bgm/local material) nhưng cùng module `cli.py`/`video.py`.
    - **Việc cần làm:** mở task mới điều tra tại sao `final-1.mp4` mất track audio dù `audio.mp3` sinh ra bình thường; verify bằng `ffprobe -show_streams final-1.mp4` xem có stream audio hay không (executor/reviewer tự chạy, không phải coordinator).

