# CONTROL TOWER - BẢN ĐỒ DỰ ÁN TỔNG THỂ (index.md)

Chào mừng bạn đến với tháp điều khiển trung tâm. Đây là nơi bạn giám sát toàn bộ các dự án hiện tại, trạng thái vận hành của hệ thống Agentic và tiến độ thực tế của từng phân hệ.

---

## 1. THỐNG KÊ TỔNG QUAN (System Status)

*   **Thời gian cập nhật cuối:** 2026-07-21
*   **Trạng thái Agent:** 🟢 Hoạt động bình thường — **Mô hình B**: control-tower chỉ PLAN + COORDINATE (`/pm`, `/ingest`, `/report`, `/lint`, `/review-order`, `/verdict`); EXECUTE + REVIEW đều ngoài hệ.
*   **Tổng số dự án:** 2 dự án đang hoạt động

---

## 2. PROJECT REGISTRY (Tra `repo_root` cho `code-review-graph`)

**Bắt buộc đọc trước khi gọi bất kỳ tool `code-review-graph` nào.** cwd của phiên control-tower không phải là repo đích — mọi tool phải được gọi kèm `repo_root` tuyệt đối lấy từ bảng dưới đây.

| Project (tên dùng trong `--project`) | repo_root (tuyệt đối) | Task dir | Graph build? | Graph embedded? | Daemon watch? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `topvnsport-pmi` | `/home/lupca/projects/topvnsport` | `projects/topvnsport-pmi/tasks/` (`_project.md`) | ✅ yes | ✅ yes (2154 node, model `all-MiniLM-L6-v2`) | ✅ yes (alias `topvnsport`, `crg-daemon` poll 2s) |
| `topvnsport-oms` | `/home/lupca/projects/topvnsport` | `projects/topvnsport-oms/tasks/` (`_project.md`) | ✅ yes (dùng chung graph với PMI, cùng monorepo) | ✅ yes (dùng chung embeddings) | ✅ yes (dùng chung daemon watch với PMI) |

Ghi chú: `topvnsport-pmi` và `topvnsport-oms` cùng trỏ về một `repo_root` (monorepo `topvnsport`) vì PMI/OMS là các thư mục con trong cùng repo git. Khi build/embed graph cho `topvnsport`, cả hai dự án đều được hưởng.

---

## 3. BẢN ĐỒ TIẾN ĐỘ DỰ ÁN (Project Map)

| Dự án | Thư mục quản lý | Trạng thái | Tiến độ (Done/Total) | Executor/Reviewer hiện tại | Ghi chú |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TopVNSport - PMI** | `projects/topvnsport-pmi/` (`_project.md`, `tasks/`) | 🔄 Đang chạy | 8/9 | Chưa có task nào ở `dispatched`/`in-review` | Quản lý quy trình, nghiệp vụ PMI |
| **TopVNSport - OMS** | `projects/topvnsport-oms/` (`_project.md`, `tasks/`) | ⏳ Tạm dừng | 0/0 | Chưa gán | Quản lý đơn hàng & hoàn tất đơn |

---

## 4. THƯ MỤC CÔNG VIỆC CHỜ XỬ LÝ (Inbox & Logs Quicklink)

*   **[`inbox.md`](inbox.md):** Nơi bạn ném mọi ý tưởng thô, yêu cầu phát sinh hoặc feedback nhanh từ team. Gõ `/ingest` để Agent tự động đọc và phân rã thành các task chính thức.
*   **[`reviews/`](reviews/):** Phiếu review do `/review-order` sinh cho reviewer độc lập — xem `reviews/README.md`.
*   **[`knowledge/`](knowledge/):** Domain knowledge, ADR, quy ước dùng chung nhiều dự án — xem `knowledge/_index.md` và mục 6 dưới đây.
*   **[`log.md`](log.md):** Nhật ký kiểm toán (Audit Trail) ghi lại mọi hành động tự trị hoặc được duyệt của Agent. Đảm bảo tính minh bạch và an toàn hệ thống.
*   **[`control-tower-map.canvas`](control-tower-map.canvas):** Sơ đồ Obsidian Canvas trực quan hoá luồng Mô hình B (PLAN/COORDINATE ↔ EXECUTE ↔ REVIEW), có link nhấn được tới `AGENTS.md`, `projects/<tên>/_project.md`, `reviews/`, `log.md`. Mở repo này bằng Obsidian để xem — Graph view cũng đã được tô màu theo nhóm (Core/Tasks/Skills/Reviews).

---

## 5. QUY TRÌNH VẬN HÀNH NHANH (Runbook) — Mô hình B

1.  **Giao task mới:** Thêm ý tưởng vào `inbox.md` hoặc gõ thẳng `/pm <yêu cầu_của_bạn>` trong chat — task sinh ra sẽ có Acceptance Criteria + test + rủi ro (xem `AGENTS.md` mục 2, 6).
2.  **Duyệt 2 cổng trong hệ:** Spec Gate (duyệt AC) → Plan Gate (duyệt kế hoạch trong `## Plan`) → task chuyển `ready` rồi `dispatched` kèm `executor:`. Xem `AGENTS.md` mục 4.
3.  **Giao việc ra ngoài:** executor (người/AI khác, ngoài hệ) tự viết code + chạy test trong repo code đích, rồi báo lại result-ref (branch/commit/PR).
4.  **Phát phiếu review:** Gõ `/review-order <task> --ref <result-ref>` → sinh phiếu tại `reviews/`, giao reviewer độc lập (≠ executor).
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
