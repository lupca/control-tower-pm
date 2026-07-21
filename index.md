# CONTROL TOWER - BẢN ĐỒ DỰ ÁN TỔNG THỂ (index.md)

Chào mừng bạn đến với tháp điều khiển trung tâm. Đây là nơi bạn giám sát toàn bộ các dự án hiện tại, trạng thái vận hành của hệ thống Agentic và tiến độ thực tế của từng phân hệ.

---

## 1. THỐNG KÊ TỔNG QUAN (System Status)

*   **Thời gian cập nhật cuối:** 2026-07-21
*   **Trạng thái Agent:** 🟢 Hoạt động bình thường (Skill `/pm` + `code-review-graph` sẵn sàng)
*   **Tổng số dự án:** 2 dự án đang hoạt động

---

## 2. PROJECT REGISTRY (Tra `repo_root` cho `code-review-graph`)

**Bắt buộc đọc trước khi gọi bất kỳ tool `code-review-graph` nào.** cwd của phiên control-tower không phải là repo đích — mọi tool phải được gọi kèm `repo_root` tuyệt đối lấy từ bảng dưới đây.

| Project (tên dùng trong `--project`) | repo_root (tuyệt đối) | Task file | Graph build? | Graph embedded? |
| :--- | :--- | :--- | :--- | :--- |
| `topvnsport-pmi` | `/home/lupca/projects/topvnsport` | `projects/topvnsport-pmi.md` | ✅ yes | ⚠️ no (cần `pip install "code-review-graph[embeddings]"` rồi `code-review-graph embed`) |
| `topvnsport-oms` | `/home/lupca/projects/topvnsport` | `projects/topvnsport-oms.md` | ✅ yes (dùng chung graph với PMI, cùng monorepo) | ⚠️ no |

Ghi chú: `topvnsport-pmi` và `topvnsport-oms` cùng trỏ về một `repo_root` (monorepo `topvnsport`) vì PMI/OMS là các thư mục con trong cùng repo git. Khi build/embed graph cho `topvnsport`, cả hai dự án đều được hưởng.

---

## 3. BẢN ĐỒ TIẾN ĐỘ DỰ ÁN (Project Map)

| Dự án | File Quản Lý | Trạng thái | Tiến độ (Done/Total) | Người Phụ Trách | Ghi chú |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TopVNSport - PMI** | `projects/topvnsport-pmi.md` | 🔄 Đang chạy | 0/3 | `/pm` Skill + Subagent | Quản lý quy trình, nghiệp vụ PMI |
| **TopVNSport - OMS** | `projects/topvnsport-oms.md` | ⏳ Tạm dừng | 0/0 | Chưa gán | Quản lý đơn hàng & hoàn tất đơn |

---

## 4. THƯ MỤC CÔNG VIỆC CHỜ XỬ LÝ (Inbox & Logs Quicklink)

*   **[`inbox.md`](inbox.md):** Nơi bạn ném mọi ý tưởng thô, yêu cầu phát sinh hoặc feedback nhanh từ team. Gõ `/ingest` để Agent tự động đọc và phân rã thành các task chính thức.
*   **[`log.md`](log.md):** Nhật ký kiểm toán (Audit Trail) ghi lại mọi hành động tự trị hoặc được duyệt của Agent. Đảm bảo tính minh bạch và an toàn hệ thống.

---

## 5. QUY TRÌNH VẬN HÀNH NHANH (Runbook)

1.  **Giao task mới:** Thêm ý tưởng vào `inbox.md` hoặc gõ thẳng `/pm <yêu cầu_của_bạn>` trong chat.
2.  **Duyệt kế hoạch:** Kiểm tra các task Agent đề xuất trong `projects/topvnsport-pmi.md`. Nếu đồng ý, hãy phản hồi để Agent bắt đầu code.
3.  **Xem báo cáo:** Gõ `/report` để Agent quét các file `.md` và cập nhật lại bảng tiến độ trên đây.
4.  **Thêm dự án mới:** Xem mục 5 của `AGENTS.md` (Onboard dự án mới).
