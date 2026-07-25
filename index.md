# CONTROL TOWER - BẢN ĐỒ DỰ ÁN TỔNG THỂ (index.md)

Chào mừng bạn đến với tháp điều khiển trung tâm. Đây là nơi bạn giám sát toàn bộ các dự án hiện tại, trạng thái vận hành của hệ thống Agentic và tiến độ thực tế của từng phân hệ.

---

## 1. THỐNG KÊ TỔNG QUAN (System Status)

*   **Thời gian cập nhật cuối:** 2026-07-25 01:37 (Nhiều cập nhật từ báo cáo tự động)
*   **Trạng thái Agent:** 🟢 Hoạt động bình thường — **Mô hình B**: control-tower chỉ PLAN + COORDINATE (`/pm`, `/ingest`, `/report`, `/lint`, `/review-order`, `/verdict`); EXECUTE + REVIEW đều ngoài hệ.
*   **Tổng số dự án:** 8 dự án đang hoạt động

---

## 2. PROJECT REGISTRY (Tra `repo_root` cho `code-review-graph`)

**Bắt buộc đọc trước khi gọi bất kỳ tool `code-review-graph` nào.** cwd của phiên control-tower không phải là repo đích — mọi tool phải được gọi kèm `repo_root` tuyệt đối lấy từ bảng dưới đây.

| Project (tên dùng trong `--project`) | repo_root (tuyệt đối) | Task dir | Graph build? | Graph embedded? | Daemon watch? | `patterns_exportable` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `topvnsport-pmi` | `/home/lupca/projects/topvnsport` | `projects/topvnsport-pmi/tasks/` (`topvnsport-pmi.md`) | ✅ yes | ✅ yes (2154 node, model `all-MiniLM-L6-v2`) | ✅ yes (alias `topvnsport`, `crg-daemon` poll 2s) | `true` |
| `topvnsport-oms` | `/home/lupca/projects/topvnsport` | `projects/topvnsport-oms/tasks/` (`topvnsport-oms.md`) | ✅ yes (dùng chung graph với PMI, cùng monorepo) | ✅ yes (dùng chung embeddings) | ✅ yes (dùng chung daemon watch với PMI) | `true` |
| `topvnsport-wms` | `/home/lupca/projects/topvnsport` | `projects/topvnsport-wms/tasks/` (`topvnsport-wms.md`) | ✅ yes (dùng chung graph, cùng monorepo) | ✅ yes (dùng chung embeddings) | ✅ yes (dùng chung daemon watch) | `true` |
| `topvnsport-web` | `/home/lupca/projects/topvnsport` | `projects/topvnsport-web/tasks/` (`topvnsport-web.md`) | ✅ yes (dùng chung graph, cùng monorepo) | ✅ yes (dùng chung embeddings) | ✅ yes (dùng chung daemon watch) | `true` |
| `control-tower` | `/home/lupca/projects/control-tower` | `projects/control-tower/tasks/` (`control-tower.md`) | n/a (meta-project, no code graph) | n/a | n/a | `false` |
| `marketing-video-agent` | `/data/projects/marketing-video-agent` | `projects/marketing-video-agent/tasks/` (`marketing-video-agent.md`) | ✅ yes (1035 nodes) | ✅ yes (867 embeddings, model `all-MiniLM-L6-v2`) | ✅ yes (alias `mva`) | `false` |
| `control-tower-web` | `/home/lupca/projects/control-tower-web` | `projects/control-tower-web/tasks/` (`control-tower-web.md`) | ✅ yes (62 nodes) | ✅ yes (29 embeddings, model `all-MiniLM-L6-v2`) | ✅ yes (alias `ctw`, poll 2s) | `false` |
| `money-printer-turbo` | `/data/projects/MoneyPrinterTurbo` | `projects/money-printer-turbo/tasks/` (`money-printer-turbo.md`) | ✅ yes (1380 nodes, 16438 edges) | ✅ yes (1301 embeddings, model `all-MiniLM-L6-v2`) | ✅ yes (alias `mpt`, poll 2s) | `false` |

Ghi chú: `topvnsport-pmi`, `topvnsport-oms`, `topvnsport-wms` cùng trỏ về một `repo_root` (monorepo `topvnsport`) vì PMI/OMS/WMS là các thư mục con trong cùng repo git. Khi build/embed graph cho `topvnsport`, cả ba dự án đều được hưởng. `patterns_exportable` (`AGENTS.md` §14.1): `true` khi code trong repo đủ generic để đáng surface sang project khác (case này — cùng 1 monorepo topvnsport, code dùng chung thật sự); `control-tower` là `false` vì không có code, chỉ có process Markdown.

---

## 3. BẢN ĐỒ TIẾN ĐỘ DỰ ÁN (Project Map)

| Dự án | Thư mục quản lý | Trạng thái | Tiến độ (Done/Total) | Executor/Reviewer hiện tại | Ghi chú |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TopVNSport - PMI** | `projects/topvnsport-pmi/` | 🔄 Đang chạy | 11/22 | — | 11 todo: PMI-002, PMI-013...PMI-022 |
| **TopVNSport - OMS** | `projects/topvnsport-oms/` | 🔄 Đang chạy | 5/9 | — | 4 todo: OMS-006...OMS-009 |
| **TopVNSport - WMS** | `projects/topvnsport-wms/` | 🔄 Đang chạy | 3/5 | — | 2 todo: WMS-004, WMS-005 |
| **TopVNSport - Web** | `projects/topvnsport-web/` | 🔄 Đang chạy | 6/10 | WEB-005: in-review | 1 in-review: WEB-005; 3 todo: WEB-008...WEB-010 |
| **Control Tower** | `projects/control-tower/` | 🔄 Đang chạy | 29/30 | CT-019: dispatched | 1 dispatched: CT-019 |
| **Marketing Video Agent** | `projects/marketing-video-agent/` | 🔄 Đang chạy | 8/10 | — | 2 todo: MVA-005 TTS resilience, MVA-006 CapCut parser |
| **Control Tower Web** | `projects/control-tower-web/` | ✅ Hoàn thành | 13/13 | — | Dashboard fixes complete |
| **MoneyPrinterTurbo** | `projects/money-printer-turbo/` | 🆕 Mới onboard | 0/0 | — | Chưa có task; graph chưa build |

---

## 4. THƯ MỤC CÔNG VIỆC CHỜ XỬ LÝ (Inbox & Logs Quicklink)

*   **[`inbox.md`](inbox.md):** Nơi bạn ném mọi ý tưởng thô, yêu cầu phát sinh hoặc feedback nhanh từ team. Gõ `/ingest` để Agent tự động đọc và phân rã thành các task chính thức.
*   **`projects/<tên>/reviews/`:** Phiếu review do `/review-order` sinh cho reviewer độc lập, nằm ngay trong từng project (không còn thư mục `reviews/` chung ở root).
*   **[`knowledge/`](knowledge/):** Domain knowledge, ADR, quy ước dùng chung nhiều dự án — xem `knowledge/_index.md` và mục 6 dưới đây.
*   **[`log.md`](log.md):** Nhật ký kiểm toán (Audit Trail) ghi lại mọi hành động tự trị hoặc được duyệt của Agent. Đảm bảo tính minh bạch và an toàn hệ thống.

---

## 5. QUY TRÌNH VẬN HÀNH NHANH (Runbook) — Mô hình B

1.  **Giao task mới:** Thêm ý tưởng vào `inbox.md` hoặc gõ thẳng `/pm <yêu cầu_của_bạn>` trong chat — task sinh ra sẽ có Acceptance Criteria + test + rủi ro (xem `AGENTS.md` mục 2, 6).
2.  **Đi qua các checkpoint:** Spec Gate (duyệt AC) → Plan Gate (duyệt kế hoạch trong `## Plan`) → Dispatch Gate → task chuyển thẳng từ `todo` sang `dispatched` kèm `executor:`. `/mode` quyết định dừng hay tiếp tục tại từng Gate; xem `AGENTS.md` mục 4.
3.  **Giao việc ra ngoài:** executor (người/AI khác, ngoài hệ) tự viết code + chạy test trong repo code đích, rồi báo lại result-ref (branch/commit/PR).
4.  **Phát phiếu review:** Gõ `/review-order <task> --ref <result-ref>` → sinh phiếu tại `projects/<tên>/reviews/`, giao reviewer độc lập (≠ executor).
5.  **Review ngoài hệ:** reviewer đọc diff + chạy test trong repo code đích (khuyến khích dùng `/code-review` của repo đó) — hoàn toàn ngoài control-tower.
6.  **Ghi verdict:** Gõ `/verdict <task> pass --reviewer @id --commit <hash>` (hoặc `changes --notes ...`) → đóng task hoặc mở lại kèm findings.
7.  **Xem báo cáo:** Gõ `/report` để Agent quét các file `.md` và cập nhật lại bảng tiến độ trên đây.
8.  **Health-check backlog:** Gõ `/lint` định kỳ để phát hiện task trễ hạn, thiếu AC, link file chết, task mồ côi, kẹt ở `dispatched`/`in-review`.
9.  **Thêm dự án mới:** Xem mục 10 của `AGENTS.md` (Onboard dự án mới).

---

## 6. KNOWLEDGE MAP

Domain knowledge, quyết định kiến trúc (ADR), quy ước — xem `AGENTS.md` mục 11. Cập nhật bởi `/report`. Danh mục đầy đủ: [`knowledge/_index.md`](knowledge/_index.md).

| Type | Số file (cross-project, `knowledge/`) | Số file (per-project, `projects/*/docs/`) |
| :--- | ---: | ---: |
| decisions | 8 | 0 |
| research | 1 | 0 |
| guides | 2 | 0 |
| metrics | 1 | 0 |
| agents | 17 | 0 |

7. Lỗi trên prod khi cấu hình kết nối Zalo OA
API Request Failed with status 500
page-ed20edf269cd732f.js:1 
 PUT http://oms.topvnsport.com/oms-api/api/configs/sms 500 (Internal Server Error)

23-725b2961b84f75f6.js:1 Error: API Request Failed with status 500
    at a (page-ed20edf269cd732f.js:1:15310)
    at async V (page-c3d42f0792ec37cb.js:36:2531)
    at async 46-ab39f333bde1cabd.js:21:22081

Thông tin input: 
3966711013871443834
Zalo APP Secret Key
*
SOdG1NRnMFaT2N79Z64M

Zalo OA Access Token
*
QqGkIVc1uLXiGYXBy8RXNs168Kpmcx4E8o0FR_I1i7aAEGSBoxcAUmeOD2pFZfGxHZGTQRMLbW18CI9ajg6LTL0uMGIyfSHXSXXo0BkpysrLD6C1egNhGqTlHJEgiVHPH714EuRpnMDgBGeHg9-gUcWRC6lvag4JRr8VLgF8gJf1LM1_YC7-PrvQJGMjszuIN5f5NvRPpYP6GdH2rSUwKG823mVoi9b0PoXGMVQHoJ8X0Lqcl9dFOYy2PoZHcwnFCrac2kNrWKK9Kqytw_NHPHqhTdEDYz5dNHbeCPhUfKjLUGqIX_AGTar9AY6GyOPf6N4KSDMpdYGZ1J92wwEC3GfaGNd3mTTXKbfY9AxCwKfYQZmoZkwUTavmB0MuwuH1ML5E6yMIsXOjLM54wCND8tvd3K2nsRa1EAJp-23xcULG

Zalo OA Refresh Token
*
1Gk7MFzaGW823O5QzcD21Gu9Y5tsVZHIVL-B3ibE6Y9ETg4disOG9amDgI_XPXaSHmw84jyEEJv-ElzczpfNE70xvc3H65ryQZJ-UF5SG75fJyT_va9_O4TttplDLdG9JMBKDT5OTmWmTROaadK7UZzveaALPnzdF7QiEuHsDMK36uy_fWOrFZWpaJQWMoHjN6siIVO23cXRRRrYfKukEb56bJBEIZ8DL5-I8Q52AnC0KgfLc5uA3cHcjXNCVYeaOH2NAzmwA05u5Om5rY582cWYpGVpLci8JchIA-vwImTwLlqUmpOxM6GPedNP5nfA9pcmM9u465SDEg5zkJ0295Wpj3hY3oW37YwIBBS5E1zMFQ06hpirDm1GbYkMIb4CENhbDSnfMJnXK_eyvpD3EN4xwprvp5doQ_ryHWe

Zalo Template ID
*
611498
