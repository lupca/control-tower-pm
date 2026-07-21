# AI AGENT RULES OF ENGAGEMENT (AGENTS.md)

Chào mừng Agent đến với Control Tower. Đây là file điều khiển tối cao quy định "luật chơi" (Decision-Authority Matrix), quy trình làm việc, và các tiêu chuẩn kiểm soát chất lượng (Quality Gates) dành cho bạn. Bạn bắt buộc phải đọc và tuân thủ các nguyên tắc dưới đây trước khi thực hiện bất kỳ hành động nào.

---

## 1. VAI TRÒ & PHÂN ĐỊNH QUYỀN HẠN (Decision-Authority Matrix)

Để đảm bảo tính **Đáng tin cậy (Trustworthy AI)** và duy trì nguyên tắc **Con người trong vòng lặp (Human-in-the-Loop - HITL)**, quyền hạn của bạn được phân chia nghiêm ngặt thành 3 cấp độ:

| Cấp độ Quyền | Hành động | Quy trình xử lý |
| :--- | :--- | :--- |
| **AUTONOMOUS** *(Tự quyền)* | - Đọc và phân tích `projects/` và `inbox.md`. <br>- Sử dụng `code-review-graph` để tra cứu tầm ảnh hưởng của task. <br>- Gợi ý task mới hoặc chia nhỏ task có sẵn. <br>- Chạy `/lint` (chỉ đọc + báo cáo, không tự sửa). | Tự động thực hiện, không cần hỏi ý kiến bạn (User). |
| **COLLABORATIVE** *(Cần duyệt)* | - Viết task mới vào `projects/*.md`. <br>- Đánh dấu hoàn thành task `- [x]`. <br>- Cập nhật trạng thái trong `index.md`. <br>- Bắt đầu viết code thực thi cho một task. | Phải ghi chi tiết giải trình (rationale) vào `log.md` **và** dừng ở đúng HITL Gate tương ứng (mục 4) chờ xác nhận (Y/N). |
| **RESTRICTED** *(Không được tự ý)* | - Bulk update (cập nhật hàng loạt > 3 task). <br>- Xóa task hoặc xóa file dự án. <br>- Bypass hoặc bỏ qua các test case bị fail. <br>- Bất kỳ task nào gắn cờ `⚠️high-risk` (mục 4). <br>- Chạm file trong `schemas/`, `models.py`, hoặc thư mục migration (`alembic/versions/`, ...). | Bắt buộc phải dừng lại và xin phê duyệt trực tiếp từ User bằng văn bản/chat, không được tự suy diễn là "đã duyệt". |

---

## 2. QUY TRÌNH QUẢN LÝ TASK (File-Over-API)

Mọi task được quản lý dưới dạng Markdown Checklist trong thư mục `projects/`.

### 2.1. Cú pháp Task chuẩn (có Acceptance Criteria)

```markdown
- [ ] <Mô tả task> 📅 <YYYY-MM-DD> <⏫|🔼|🔽> [⚠️high-risk]
    🔗 <file1, file2>                        # repo-relative, từ get_impact_radius_tool
    🌀 Luồng ảnh hưởng: <flow1, flow2>       # từ get_affected_flows_tool (mục 5, B4)
    ✅ Tiêu chí nghiệm thu (AC):
       - [ ] <điều kiện kiểm chứng được 1>
       - [ ] <điều kiện kiểm chứng được 2>
    🧪 Test: <path::test_name, ...>          # test hiện có + test cần bổ sung
    ▸ Plan: <điền ở Plan Gate — kế hoạch code cụ thể, xem mục 4>
    ▸ Sub-tasks:
       - [ ] <bước nhỏ, mỗi bước 1 file/1 mối quan tâm>
```

Task cũ (cú pháp không có AC) vẫn hợp lệ và không cần sửa hàng loạt — chỉ migrate sang cú pháp mới khi `/pm`/`/ingest` chạm lại đúng task đó.

**Quy tắc:** `/pm` KHÔNG được ghi task thiếu `🔗`, `✅ AC`, `🧪` — cả ba đều phải lấy từ code-review-graph thật (mục 5). Nếu chưa gọi graph thì chưa được ghi task.

### 2.2. Quy tắc phân rã task

- Mỗi sub-task chạm **tối đa 1 file / 1 mối quan tâm**.
- Task có blast radius (`get_impact_radius_tool`) > **8 file** → tự đề xuất chẻ thành nhiều task nhỏ hơn, mỗi task tương ứng 1 PR/1 branch. Nguyên tắc kích thước: **"1 task = 1 context window = 1 branch/PR"**.
- Ưu tiên thứ tự theo `depends-on` (nếu có khai báo) và mức độ rủi ro (`⚠️high-risk` làm trước hoặc tách riêng để dễ review).

---

## 3. DEFINITION OF DONE (DoD mặc định toàn hệ thống)

Một task chỉ được đóng (`- [x]`) khi **tất cả** các điều sau đúng:

- [ ] Toàn bộ AC (✅) của task pass.
- [ ] Test liên quan (🧪) xanh 100% trong file test tương ứng.
- [ ] `detect_changes_tool(repo_root=<dự án>)` không báo rủi ro **mới** chưa xử lý so với phạm vi đã hoạch định ở Plan Gate.
- [ ] Không regression: các test khác của module vẫn xanh.
- [ ] Đã ghi commit hash thật vào `log.md` (mục 6, field `Commit:`).

Dự án có thể khai báo thêm DoD riêng trong "Project Gates" của file `projects/<dự án>.md`; DoD riêng CỘNG THÊM vào DoD mặc định này, không thay thế.

---

## 4. BA CỔNG HITL (Sequential Gates)

Giữ ma trận ở mục 1, nhưng mọi task COLLABORATIVE phải đi qua đúng 3 checkpoint tuần tự sau — không được nhảy cóc:

1. **Spec Gate** — `/pm` sinh task + `🔗`/`✅ AC`/`🧪`/`🌀` xong → dừng, hiển thị cho User duyệt **phạm vi & AC**. Chưa có gì được code.
2. **Plan Gate** — sau khi Spec được duyệt, viết kế hoạch code cụ thể THẲNG vào mục `▸ Plan:` của task (file, hàm, thứ tự sửa) → dừng, chờ User duyệt **kế hoạch** trước khi sửa dòng code đầu tiên.
3. **Code Gate** — code xong → chạy verify theo DoD (mục 3) → dừng, hiển thị kết quả verify cho User review trước khi đánh dấu `- [x]` và commit.

**Nâng cấp RESTRICTED tự động:** nếu task gắn `⚠️high-risk` (do chạm hub/bridge node — mục 5, B3) hoặc chạm `schemas/`/`models.py`/migration → mỗi cổng ở trên đều bắt buộc xác nhận bằng văn bản/chat rõ ràng của User, không được suy diễn im lặng là đã duyệt.

---

## 5. KHAI THÁC `code-review-graph` (Tầng B)

Bộ công cụ có ~30 MCP tool; dùng đúng tool đúng bước thay vì chỉ 2 tool cơ bản. **Mọi lời gọi PHẢI kèm `repo_root=<tuyệt đối>` tra từ PROJECT REGISTRY (`index.md` mục 2)** — cwd của phiên là `control-tower`, auto-detect sẽ sai. Luôn mở đầu bằng `get_minimal_context_tool`; dùng `detail_level="minimal"` ở các tool hỗ trợ tham số này.

### 5.1. Bảng: `/pm` gọi tool nào ở bước nào

| Bước | Tool (tên & tham số THẬT) | Kết quả ghi vào task |
|---|---|---|
| 0. Khởi động | `get_minimal_context_tool(task=..., repo_root=...)` | định hướng, tiết kiệm token |
| 1. Định vị | `semantic_search_nodes_tool(query=..., repo_root=..., detail_level="minimal")` | tìm đúng symbol/file (path thật, không đoán) |
| 2. Blast radius | `get_impact_radius_tool(changed_files=[...], repo_root=..., detail_level="minimal")` | điền `🔗` (file/caller/dependent) |
| 3. Test hiện có | `query_graph_tool(pattern="tests_for", target=<file/symbol>, repo_root=..., detail_level="minimal")` | điền `🧪` test đang có |
| 4. Lỗ hổng test | `get_knowledge_gaps_tool(repo_root=...)` | tự sinh sub-task viết test (5.2) |
| 5. Xếp hạng rủi ro | `get_hub_nodes_tool(top_n=50, repo_root=...)`, `get_bridge_nodes_tool(top_n=50, repo_root=...)` | gắn `⚠️high-risk` nếu trùng (5.3) |
| 6. Ảnh hưởng nghiệp vụ | `get_affected_flows_tool(changed_files=[...], repo_root=...)` | điền `🌀 Luồng ảnh hưởng` |
| 7. Verify (finalization) | `detect_changes_tool(repo_root=..., detail_level="minimal")` | gate đóng task (mục 3) |

> **Lưu ý sửa lỗi so với bản nháp đầu:** `query_graph_tool` KHÔNG có tham số `edge` — tham số đúng là `pattern` (giá trị `"tests_for"` để tìm test) và `target` (tên node/file cần tra). Gọi sai tham số sẽ lỗi ngay lập tức.

### 5.2. Auto-sinh sub-task test từ `get_knowledge_gaps_tool`

Nếu vùng ảnh hưởng chứa hotspot **chưa được test cover** (theo `get_knowledge_gaps_tool`), tự thêm sub-task:
`- [ ] Viết test cho <symbol/file> (hiện chưa có coverage — knowledge gap) 🧪 <file test đề xuất>`

### 5.3. Cờ rủi ro từ hub/bridge nodes

`get_hub_nodes_tool`/`get_bridge_nodes_tool` trả về **top toàn cục của cả repo**, không scope theo task — vì vậy phải gọi với `top_n` đủ lớn (mặc định dùng **50**, không dùng mặc định của tool là 10, vì repo lớn sẽ khiến cờ rủi ro gần như không bao giờ kích hoạt). Nếu bất kỳ file/symbol nào trong `🔗` của task trùng với danh sách hub/bridge trả về → gắn `⚠️high-risk` vào dòng task và áp dụng nâng cấp RESTRICTED (mục 4).

### 5.4. Business impact & Verify

- `get_affected_flows_tool` → điền `🌀 Luồng ảnh hưởng:` giúp User duyệt Spec Gate nhanh hơn.
- Code Gate (mục 4) verify bằng `detect_changes_tool(repo_root=<dự án>)`: đối chiếu blast radius thực tế vs kế hoạch ở `▸ Plan:`. Nếu code chạm file **ngoài phạm vi đã duyệt** → cảnh báo, quay lại Plan Gate thay vì tự ý mở rộng.

### 5.5. Kiểm tra graph "tươi" (freshness)

`list_graph_stats_tool` (MCP) **không** trả về thông tin so khớp commit — chỉ có `total_nodes`, `total_edges`, `embeddings_count`, `last_updated`. Để kiểm tra graph có khớp commit hiện tại của dự án đích hay không, phải chạy CLI qua Bash:
```bash
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph status --repo <repo_root> --json
```
và so `built_at_commit` với `current_sha` trong kết quả trả về.

### 5.6. `crg-daemon` — tự cập nhật graph nền (thay rebuild thủ công)

Binary `crg-daemon` KHÔNG nằm trong PATH mặc định — phải gọi qua module Python:
```bash
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph daemon add <repo_root> --alias <tên>
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph daemon start
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph daemon status
```
(dùng subcommand `daemon add` thay vì tay sửa `~/.code-review-graph/watch.toml`, để CLI tự validate path tồn tại trước khi ghi.) Daemon poll 2s, tự cập nhật graph khi code đổi → `/pm` luôn truy vấn graph tươi mà không cần nhớ rebuild tay.

An toàn token: có thể đặt trần qua env khi cần (`CRG_MAX_IMPACT_DEPTH`, `CRG_MAX_IMPACT_NODES`, `CRG_TOOL_TIMEOUT`).

---

## 6. CHUẨN MỰC KIỂM TOÁN (log.md - Audit Trail)

Format append-only, prefix nhất quán để `grep`/`awk` phân tích được:

```markdown
## [YYYY-MM-DD HH:MM:SS] <operation> | <title>
- Dự án: <file dự án>
- Mô tả: <tóm tắt những gì vừa làm>
- Giải trình: <tại sao làm thế? AI đã phát hiện gì qua graph?>
- Files touched: <path1, path2>
- Trạng thái: [Thành công | Chờ duyệt | Đã hủy]
- Commit: <hash | n/a>
```
`<operation>` ∈ `{ingest, pm-create, plan, code, verify, report, lint}`. Ghi 1 entry cho mọi hành động COLLABORATIVE hoặc RESTRICTED.

---

## 7. MACRO VÀ LỆNH ĐIỀU KHIỂN

*   `/pm <mô tả_task> [--project <tên>]`: Spec Gate — sinh task đầy đủ `🔗`/`✅ AC`/`🧪`/`🌀` bằng graph, viết vào `projects/`, dừng chờ duyệt.
*   `/ingest`: Đọc `inbox.md`, **reconcile vào task tương tự đã có** thay vì tạo trùng (mục 8, A7), làm giàu bằng graph, xóa mục đã xử lý khỏi inbox.
*   `/report`: Quét `projects/*.md`, tổng hợp Done/Total, cập nhật `index.md`.
*   `/lint [--project <tên>]`: Health-check backlog — task trễ hạn, thiếu AC/test, link file chết, task mồ côi, mâu thuẫn, lệch trạng thái. Chỉ báo cáo, không tự sửa (RESTRICTED nếu cần sửa hàng loạt).

---

## 8. RULE "RECONCILE, ĐỪNG APPEND" CHO `/ingest`

Khi phân loại 1 ghi chú từ `inbox.md`: nếu **task tương tự đã tồn tại** trong `projects/*.md` (cùng file/symbol hoặc cùng chủ đề) → **viết lại/bổ sung mạch lạc vào task đó**, KHÔNG tạo task trùng lặp mới. Sau khi xử lý xong 1 mục → xóa khỏi `inbox.md`, ghi log `ingest`.

---

## 9. ONBOARD DỰ ÁN MỚI (Runbook)

Khi cần thêm một dự án mới vào Control Tower:

1. Thêm 1 hàng vào bảng **PROJECT REGISTRY** trong `index.md` (mục 2): tên dự án, `repo_root` tuyệt đối, tên file task.
2. Tạo file `projects/<tên-dự-án>.md` (có thể copy khung từ `projects/topvnsport-pmi.md`).
3. Build graph cho repo đó (nếu chưa có):
   ```bash
   /home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph build --repo <repo_root>
   /home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph embed --repo <repo_root>
   ```
4. Đăng ký daemon watch để graph tự cập nhật (mục 5.6): `daemon add <repo_root> --alias <tên>`.
5. (Tùy chọn) `code-review-graph register <repo_root> --alias <tên>` nếu cần `cross_repo_search_tool` truy vấn chéo nhiều dự án cùng lúc.
