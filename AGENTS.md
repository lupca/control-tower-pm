# AI AGENT RULES OF ENGAGEMENT (AGENTS.md)

Chào mừng Agent đến với Control Tower. Đây là file điều khiển tối cao quy định "luật chơi" (Decision-Authority Matrix), quy trình làm việc, và các tiêu chuẩn kiểm soát chất lượng (Quality Gates) dành cho bạn. Bạn bắt buộc phải đọc và tuân thủ các nguyên tắc dưới đây trước khi thực hiện bất kỳ hành động nào.

---

## 1. VAI TRÒ & PHÂN ĐỊNH QUYỀN HẠN (Decision-Authority Matrix)

Để đảm bảo tính **Đáng tin cậy (Trustworthy AI)** và duy trì nguyên tắc **Con người trong vòng lặp (Human-in-the-Loop - HITL)**, quyền hạn của bạn được phân chia nghiêm ngặt thành 3 cấp độ:

| Cấp độ Quyền | Hành động | Quy trình xử lý |
| :--- | :--- | :--- |
| **AUTONOMOUS** *(Tự quyền)* | - Đọc và phân tích `projects/` và `inbox.md`. <br>- Sử dụng `code-review-graph` để tra cứu tầm ảnh hưởng của task. <br>- Gợi ý task mới hoặc chia nhỏ task có sẵn. | Tự động thực hiện, không cần hỏi ý kiến bạn (User). |
| **COLLABORATIVE** *(Cần duyệt)* | - Viết task mới vào `projects/*.md`. <br>- Đánh dấu hoàn thành task `- [x]`. <br>- Cập nhật trạng thái trong `index.md`. <br>- Bắt đầu viết code thực thi cho một task. | Phải ghi chi tiết giải trình (rationale) vào `log.md` hoặc xuất hiện dưới dạng đề xuất trong chat để chờ xác nhận (Y/N). |
| **RESTRICTED** *(Không được tự ý)* | - Bulk update (cập nhật hàng loạt > 3 task). <br>- Xóa task hoặc xóa file dự án. <br>- Bypass hoặc bỏ qua các test case bị fail. | Bắt buộc phải dừng lại và xin phê duyệt trực tiếp từ User. |

---

## 2. QUY TRÌNH QUẢN LÝ TASK (File-Over-API)

Mọi task được quản lý dưới dạng Markdown Checklist trong thư mục `projects/`.

### 2.1. Cú pháp Task chuẩn:
Mỗi task phải tuân thủ cú pháp sau để AI và con người có thể phân tích dễ dàng:
```markdown
- [ ] <Mô tả task rõ ràng, cụ thể> 📅 YYYY-MM-DD [Độ ưu tiên: ⏫ Cao | 🔼 Trung bình | 🔽 Thấp] 🔗 <File liên quan 1, File liên quan 2>
```
*Ví dụ:*
```markdown
- [ ] Thêm validation cost/tax cho variant 📅 2026-08-01 ⏫ 🔗 PMI/backend/services/product_service.py, PMI/backend/schemas/tier_variation.py
```

### 2.2. Quy tắc sinh Task của Skill `/pm` (Sử dụng code-review-graph):

Khi User giao một task mơ hồ, bạn không được phép ghi ngay vào file dự án một cách mơ hồ. Bạn phải:

1. **Tra `repo_root` của dự án đích trong PROJECT REGISTRY (`index.md`, mục 2).** cwd của phiên control-tower KHÔNG PHẢI là repo đích, nên mọi tool `code-review-graph` phải được gọi với tham số `repo_root=<đường dẫn tuyệt đối>` lấy từ registry — không dựa vào auto-detect theo cwd.
2. Gọi `get_minimal_context` trước, sau đó `get_impact_radius_tool` để tìm "vùng ảnh hưởng" (blast radius) của task trong codebase — luôn kèm `repo_root` và `detail_level="minimal"`.
3. Gọi `query_graph_tool` (pattern `tests_for`) để tìm các test case liên quan đến vùng ảnh hưởng đó.
4. Viết lại task cụ thể, liệt kê rõ các file bị tác động trực tiếp và các file test cần chạy. **Path ghi vào task phải là đường dẫn thật, tương đối so với `repo_root` của dự án** (cắt bỏ tiền tố `repo_root` khỏi path tuyệt đối mà graph trả về) — không dùng path đoán mò/generic (vd `schema.py`, `test_product.py`).
5. Ghi task chi tiết này vào file dự án tương ứng dưới dạng các sub-task thụt lề:
   *Ví dụ:*
   ```markdown
   - [ ] Thêm validation cost/tax cho variant 📅 2026-08-01 ⏫
       - [ ] Cập nhật schema validation trong `PMI/backend/schemas/tier_variation.py` 🔗 PMI/backend/schemas/tier_variation.py
       - [ ] Viết logic kiểm tra trong `PMI/backend/services/product_service.py` 🔗 PMI/backend/services/product_service.py
       - [ ] Chạy và bổ sung test case trong `PMI/backend/tests/test_variant_cost_tax.py` 🔗 PMI/backend/tests/test_variant_cost_tax.py
   ```

---

## 3. CHUẨN MỰC KIỂM TOÁN (log.md - Audit Trail)

Mỗi khi thực hiện một hành động thuộc cấp độ **COLLABORATIVE** hoặc **RESTRICTED**, Agent phải cập nhật một dòng nhật ký vào `log.md` theo định dạng sau:

```markdown
### [YYYY-MM-DD HH:MM:SS] <TÊN_HÀNH_ĐỘNG>
- **Dự án:** <Tên file dự án>
- **Mô tả hành động:** <Tóm tắt những gì vừa làm>
- **Giải trình (Rationale):** <Tại sao làm thế? AI đã phát hiện ra vùng ảnh hưởng gì qua graph?>
- **Trạng thái:** [Thành công | Chờ duyệt | Đã hủy]
```

---

## 4. MACRO VÀ LỆNH ĐIỀU KHIỂN

Khi giao tiếp với bạn trong phiên, Agent sẽ nhận dạng các lệnh macro sau để tự động kích hoạt các luồng xử lý:

*   `/pm <mô tả_task> [--project <tên>]`: Kích hoạt skill Project Manager để đọc `projects/`, tra `repo_root` trong PROJECT REGISTRY, chạy `code-review-graph`, đề xuất task và viết vào `projects/`.
*   `/ingest`: Đọc toàn bộ nội dung thô trong `inbox.md`, phân tích và phân loại chúng thành các task cụ thể đưa vào `projects/` tương ứng (dùng cùng quy tắc graph như `/pm`).
*   `/report`: Tự động quét toàn bộ thư mục `projects/`, tổng hợp trạng thái các task (Done vs Pending), vẽ tiến độ và cập nhật vào `index.md`.

---

## 5. ONBOARD DỰ ÁN MỚI (Runbook)

Khi cần thêm một dự án mới vào Control Tower:

1. Thêm 1 hàng vào bảng **PROJECT REGISTRY** trong `index.md` (mục 2): tên dự án, `repo_root` tuyệt đối, tên file task.
2. Tạo file `projects/<tên-dự-án>.md` (có thể copy khung từ `projects/topvnsport-pmi.md`).
3. Build + embed graph cho repo đó:
   ```bash
   code-review-graph build --repo <repo_root>
   code-review-graph embed --repo <repo_root>
   ```
4. (Tùy chọn) `code-review-graph register <repo_root> --alias <tên>` nếu cần `cross_repo_search_tool` truy vấn chéo nhiều dự án cùng lúc.
