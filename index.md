# CONTROL TOWER - BẢN ĐỒ DỰ ÁN TỔNG THỂ (index.md)

Chào mừng bạn đến với tháp điều khiển trung tâm. Đây là nơi bạn giám sát toàn bộ các dự án hiện tại, trạng thái vận hành của hệ thống Agentic và tiến độ thực tế của từng phân hệ.

---

## 1. THỐNG KÊ TỔNG QUAN (System Status)

*   **Thời gian cập nhật cuối:** 2026-07-22
*   **Trạng thái Agent:** 🟢 Hoạt động bình thường — **Mô hình B**: control-tower chỉ PLAN + COORDINATE (`/pm`, `/ingest`, `/report`, `/lint`, `/review-order`, `/verdict`); EXECUTE + REVIEW đều ngoài hệ.
*   **Tổng số dự án:** 7 dự án đang hoạt động

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
| `control-tower-web` | `/home/lupca/projects/control-tower-web` | `projects/control-tower-web/tasks/` (`control-tower-web.md`) | ❌ chưa build | ❌ chưa embed | ❌ chưa watch | `false` |

Ghi chú: `topvnsport-pmi`, `topvnsport-oms`, `topvnsport-wms` cùng trỏ về một `repo_root` (monorepo `topvnsport`) vì PMI/OMS/WMS là các thư mục con trong cùng repo git. Khi build/embed graph cho `topvnsport`, cả ba dự án đều được hưởng. `patterns_exportable` (`AGENTS.md` §14.1): `true` khi code trong repo đủ generic để đáng surface sang project khác (case này — cùng 1 monorepo topvnsport, code dùng chung thật sự); `control-tower` là `false` vì không có code, chỉ có process Markdown.

---

## 3. BẢN ĐỒ TIẾN ĐỘ DỰ ÁN (Project Map)

| Dự án | Thư mục quản lý | Trạng thái | Tiến độ (Done/Total) | Executor/Reviewer hiện tại | Ghi chú |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TopVNSport - PMI** | `projects/topvnsport-pmi/` (`topvnsport-pmi.md`, `tasks/`) | 🔄 Đang chạy | 8/9 | Chưa có task nào ở `dispatched`/`in-review` | Quản lý quy trình, nghiệp vụ PMI |
| **TopVNSport - OMS** | `projects/topvnsport-oms/` (`topvnsport-oms.md`, `tasks/`) | ⏳ Tạm dừng | 0/0 | Chưa gán | Quản lý đơn hàng & hoàn tất đơn |
| **TopVNSport - WMS** | `projects/topvnsport-wms/` (`topvnsport-wms.md`, `tasks/`) | 🔄 Đang chạy | 1/1 | — | Quản lý kho hàng, tồn kho, barcode |
| **TopVNSport - Web** | `projects/topvnsport-web/` (`topvnsport-web.md`, `tasks/`) | 🔄 Đang chạy | 0/0 | — | Frontend application (Vue/React) |
| **Control Tower** | `projects/control-tower/` (`control-tower.md`, `tasks/`) | ✅ Hoàn thành | 11/11 | — | Meta-project: paradigm shifts, self-improvement. All 10 paradigm shifts implemented + CT-011 independent review passed. |
| **Marketing Video Agent** | `projects/marketing-video-agent/` (`marketing-video-agent.md`, `tasks/`) | 🆕 Mới onboard | 0/0 | — | AI video creation pipeline với workers: leader, capcut, slideshow, tts, delivery... |
| **Control Tower Web** | `projects/control-tower-web/` (`control-tower-web.md`, `tasks/`) | 🆕 Mới onboard | 0/0 | — | Web dashboard cho control-tower (Astro + Tailwind) |

---

## 4. THƯ MỤC CÔNG VIỆC CHỜ XỬ LÝ (Inbox & Logs Quicklink)

*   **[`inbox.md`](inbox.md):** Nơi bạn ném mọi ý tưởng thô, yêu cầu phát sinh hoặc feedback nhanh từ team. Gõ `/ingest` để Agent tự động đọc và phân rã thành các task chính thức.
*   **`projects/<tên>/reviews/`:** Phiếu review do `/review-order` sinh cho reviewer độc lập, nằm ngay trong từng project (không còn thư mục `reviews/` chung ở root).
*   **[`knowledge/`](knowledge/):** Domain knowledge, ADR, quy ước dùng chung nhiều dự án — xem `knowledge/_index.md` và mục 6 dưới đây.
*   **[`log.md`](log.md):** Nhật ký kiểm toán (Audit Trail) ghi lại mọi hành động tự trị hoặc được duyệt của Agent. Đảm bảo tính minh bạch và an toàn hệ thống.

---

## 5. QUY TRÌNH VẬN HÀNH NHANH (Runbook) — Mô hình B

1.  **Giao task mới:** Thêm ý tưởng vào `inbox.md` hoặc gõ thẳng `/pm <yêu cầu_của_bạn>` trong chat — task sinh ra sẽ có Acceptance Criteria + test + rủi ro (xem `AGENTS.md` mục 2, 6).
2.  **Duyệt 2 cổng trong hệ:** Spec Gate (duyệt AC) → Plan Gate (duyệt kế hoạch trong `## Plan`) → task chuyển `ready` rồi `dispatched` kèm `executor:`. Xem `AGENTS.md` mục 4.
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
| domains | 0 | 0 |
| decisions | 1 | 0 |
| conventions | 0 | 0 |
| research | 0 | 0 |
