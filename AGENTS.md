# AI AGENT RULES OF ENGAGEMENT (AGENTS.md)

Chào mừng Agent đến với Control Tower. Đây là file điều khiển tối cao quy định "luật chơi" (vai trò, vòng đời task, HITL, Quality Gates) dành cho bạn. Bạn bắt buộc phải đọc và tuân thủ các nguyên tắc dưới đây trước khi thực hiện bất kỳ hành động nào.

> **Mô hình B (hiện hành):** control-tower chỉ **PLAN + COORDINATE**. Nó KHÔNG bao giờ ghi code, KHÔNG đọc diff, KHÔNG tự chạy test. EXECUTE (viết code) và REVIEW (đọc diff, chạy test) đều nằm **ngoài hệ** — do người hoặc AI khác đảm nhiệm trong repo code đích. Con người luôn là người quyết định cuối cùng.

---

## 1. VAI TRÒ & PHÂN ĐỊNH TRÁCH NHIỆM

| Vai trò                                                | Ai làm                                                                          | Có đụng code?                                     |
| :----------------------------------------------------- | :------------------------------------------------------------------------------ | :------------------------------------------------ |
| **PLAN** (`/pm` sinh task + AC + graph context)        | control-tower                                                                   | KHÔNG — chỉ đọc graph (phân tích tĩnh, read-only) |
| **EXECUTE** (viết code, tạo branch, chạy test)         | **NGOÀI hệ** — người hoặc AI khác, trong repo code đích                         | CÓ — đây là điểm DUY NHẤT ghi code                |
| **REVIEW/CHECK** (đọc diff, chạy test, soát AC/DoD)    | **NGOÀI hệ** — reviewer độc lập (≠ executor), dùng `/code-review` của repo code | ĐỌC — hoàn toàn ngoài control-tower               |
| **COORDINATE** (phát phiếu review, ghi verdict, audit) | control-tower                                                                   | KHÔNG — chỉ Markdown                              |
| **QUYẾT chấp nhận cuối**                               | Con người (nguyên tắc four-eyes)                                                | —                                                 |

**Nguyên tắc separation of duties (bắt buộc): reviewer ≠ executor.** Nếu phát hiện `reviewer:` trùng `executor:` của cùng task → từ chối ghi verdict `pass`, yêu cầu chữ ký người/AI thứ hai độc lập.

Vì phân quyền được rạch ròi theo vai trò ở trên, ma trận AUTONOMOUS/COLLABORATIVE/RESTRICTED chỉ áp dụng cho các hành động **của chính control-tower** (luôn là Markdown, không phải code):

| Cấp độ Quyền | Hành động (đều là Markdown, không phải code) | Quy trình xử lý |
| :--- | :--- | :--- |
| **AUTONOMOUS** *(Tự quyền)* | - Đọc và phân tích `projects/` (bao gồm `projects/<tên>/reviews/`), `knowledge/`, `inbox.md`. <br>- Dùng `code-review-graph` (read-only) để tra blast radius/test gap/flows. <br>- Chạy `/lint` (chỉ đọc + báo cáo). | Tự động thực hiện, không cần hỏi User. |
| **COLLABORATIVE** *(Cần duyệt)* | - Viết task mới vào `projects/<tên>/tasks/*.md` (Spec Gate). <br>- Ghi kế hoạch vào `## Plan` (Plan Gate). <br>- Đánh dấu `dispatched`, ghi `executor:`. <br>- Phát phiếu review (`/review-order`). <br>- Route knowledge vào `knowledge/`/`docs/` (mục 11). | Ghi giải trình vào `log.md` **và** dừng ở đúng Gate (mục 4) chờ xác nhận (Y/N). |
| **RESTRICTED** *(Không được tự ý)* | - Ghi verdict `pass` (đóng task `status: done`) — luôn cần xác nhận người. <br>- Bulk update (>3 task). <br>- Xóa task/file dự án. <br>- Ghi verdict khi `reviewer:` == `executor:`. | Bắt buộc dừng lại, xin phê duyệt trực tiếp bằng văn bản/chat, không suy diễn im lặng là "đã duyệt". |

---

## 2. QUY TRÌNH QUẢN LÝ TASK (File-Over-API — task-per-file)

Mỗi task là **1 file Markdown riêng** trong `projects/<tên-dự-án>/tasks/`, không còn gộp chung nhiều task vào 1 file lớn (lý do: tránh git conflict khi nhiều executor/reviewer hoạt động song song, và mỗi task có chỗ chứa spec/plan/review notes dài mà không phình file dùng chung).

```
projects/<tên-dự-án>/
├── <tên-dự-án>.md         # overview + Project Gates + References + next_task_id counter (trùng tên folder — Obsidian folder note, giúp Graph view hiện đúng tên thay vì nhãn trùng nhau)
├── docs/                 # knowledge riêng dự án (mục 11)
└── tasks/
    ├── <PREFIX>-001-<slug>.md
    └── <PREFIX>-002-<slug>.md
```

### 2.1. Cú pháp Task chuẩn (YAML frontmatter + body)

Mỗi file trong `tasks/` bắt đầu bằng frontmatter:

```yaml
---
id: PMI-001                          # <PREFIX>-<NNN>, NNN zero-pad 3 chữ số, PREFIX lấy từ <tên-dự-án>.md
title: "Thêm validation cost/tax cho variant"
status: done                         # todo | ready | dispatched | in-review | done | changes-requested
priority: high                       # urgent | high | medium | low
risk: high                           # high | normal (mặc định normal) — high khi trùng hub/bridge node hoặc chạm schemas/models.py/migration
deadline: 2026-08-01                 # YYYY-MM-DD, optional
executor: "@dev-tung"                # điền khi dispatch, optional
reviewer: null                       # điền khi review-order, PHẢI khác executor
result_ref: "topvnsport@main (commit 9d122b9)"  # branch/commit/PR từ executor
depends_on: []                       # list task ID, vd [PMI-001]
files:                                # repo-relative, từ get_impact_radius_tool
  - PMI/backend/schemas/tier_variation.py
flows: [product-create, product-update]  # từ get_affected_flows_tool
tests:                                # test hiện có, từ query_graph_tool
  - PMI/backend/tests/test_variant_cost_tax.py
dispatched: null                     # YYYY-MM-DD khi chuyển dispatched
in_review: null                      # YYYY-MM-DD khi chuyển in-review
created: 2026-07-21
updated: 2026-07-21
---
```

Theo sau là body chuẩn:

```markdown
# <ID>: <title>

> Dự án: [[projects/<tên>/<tên>]]

## Tiêu chí nghiệm thu (AC)
- [ ] <điều kiện kiểm chứng được>

## Plan
*(điền ở Plan Gate)*

## Sub-tasks
- [ ] <bước nhỏ, mỗi bước 1 file/1 mối quan tâm>
```

Dòng `> Dự án: [[...]]` là wikilink thật (không phải path text) — mục đích để Obsidian Graph view vẽ được cạnh nối giữa task và file dự án (Graph chỉ nhận diện `[[wikilink]]`, không nhận path trong bảng/YAML). Dùng path đầy đủ `[[projects/<tên>/<tên>]]` — không cần alias vì file dự án đặt tên trùng luôn với `<tên>` (folder note convention), nên Obsidian tự hiển thị đúng tên, không còn hiện nhãn "_project" trùng nhau giữa các dự án trên Graph. Đây thuần là nội dung Markdown hỗ trợ điều hướng/trực quan hoá trong Obsidian — không có skill nào parse dòng này, không ảnh hưởng vòng đời/gate.

File dự án (`projects/<tên>/<tên>.md`) có thêm mục `## Tasks` liệt kê wikilink tới từng file trong `tasks/` — mục này do `/report` tự regenerate mỗi lần chạy (mục 6.1 bảng skill).

Task `done` sau khi `/verdict changes` có thêm `## Findings từ reviewer` do `/verdict` ghi.

**Chuyển trạng thái = cập nhật `status:` + `updated:` trong frontmatter + commit** (audit tự nhiên qua git — mục 2.3 dưới đây).

**Quy tắc:** `/pm` KHÔNG được ghi task thiếu `files:`, `## Tiêu chí nghiệm thu (AC)`, `tests:` — cả ba đều phải lấy từ code-review-graph thật (mục 6). Nếu chưa gọi graph thì chưa được ghi task.

### 2.1a. Quy tắc đánh ID

- `/pm` và `/ingest` đọc frontmatter của `<tên-dự-án>.md` → `task_prefix` + `next_task_id`.
- Tạo file: `tasks/<PREFIX>-<NNN>-<slug>.md` (slug = kebab-case từ title, tối đa 40 ký tự ASCII).
- Sau khi tạo xong, tăng `next_task_id` trong `<tên-dự-án>.md` lên 1.

### 2.2. Quy tắc phân rã task

- Mỗi sub-task chạm **tối đa 1 file / 1 mối quan tâm**.
- Task có blast radius (`get_impact_radius_tool`) > **8 file** → tự đề xuất chẻ thành nhiều task nhỏ hơn, mỗi task tương ứng 1 PR/1 branch. Nguyên tắc kích thước: **"1 task = 1 context window = 1 branch/PR"**.
- Ưu tiên thứ tự theo `depends_on:` (nếu có khai báo) và mức độ rủi ro (`risk: high` làm trước hoặc tách riêng để dễ review).

### 2.3. Vòng đời task (state machine)

```
📋 todo → ✅ ready → 📤 dispatched → 🔍 in-review → ✔️ done
                                          ↓
                                  🔁 changes-requested → (giao lại) → 📤 dispatched
```

- `todo`: task vừa viết ở Spec Gate, chờ User duyệt AC.
- `ready`: Spec + Plan Gate đã duyệt, `## Plan` đã có, sẵn sàng giao việc — **chưa có ai làm**.
- `dispatched`: đã ghi `executor:` + `dispatched: <ngày>` trong frontmatter — executor (ngoài hệ) đang làm.
- `in-review`: executor báo xong (`result_ref:` đã điền), `/review-order` đã phát phiếu, `in_review: <ngày>` — reviewer (ngoài hệ, ≠ executor) đang soát.
- `done`: `/verdict pass` đã ghi, kèm `reviewer:` + commit hash thật + xác nhận người. Task khác có `depends_on:` chứa ID này có thể mở khoá (chưa tự động — mục 6.1, `/verdict` chỉ nêu ra).
- `changes-requested`: `/verdict changes` đã ghi kèm findings — quay lại `dispatched` sau khi executor sửa.

Chuyển trạng thái = cập nhật `status:` + `updated:` trong frontmatter + commit trong control-tower (audit tự nhiên qua git).

---

## 3. DEFINITION OF DONE (DoD mặc định toàn hệ thống)

Một task chỉ được đóng (`status: done`) khi **tất cả** đúng, và **do reviewer độc lập xác nhận qua `/verdict pass`** (control-tower không tự kiểm tra các điều này — nó không chạy test, không đọc diff):

- [ ] Toàn bộ AC (`## Tiêu chí nghiệm thu (AC)`) của task pass — reviewer xác nhận trong phiếu review.
- [ ] Test liên quan (`tests:`) xanh 100% — reviewer tự chạy trong repo code đích (vd qua `/code-review` của repo đó).
- [ ] Không regression — reviewer xác nhận các test khác của module vẫn xanh.
- [ ] `reviewer:` khác `executor:` (separation of duties, mục 1).
- [ ] Commit hash thật (`result_ref:`) đã được ghi vào `log.md` (mục 7, field `Commit:`).

Dự án có thể khai báo thêm DoD riêng trong "Project Gates" của file `projects/<dự án>/<dự án>.md`; DoD riêng CỘNG THÊM vào DoD mặc định này, không thay thế. Reviewer là người áp dụng DoD, control-tower chỉ ghi lại kết quả.

---

## 4. HAI CỔNG TRONG CONTROL-TOWER + BÀN GIAO RA NGOÀI

Control-tower chỉ chịu trách nhiệm 2 cổng đầu (PLAN); sau đó bàn giao ra ngoài, không có "Code Gate" nội bộ nữa.

1. **Spec Gate** — `/pm` tạo file task mới trong `tasks/` với `files:`/AC/`tests:`/`flows:` (`status: todo`) → dừng, hiển thị cho User duyệt **phạm vi & AC**. Chưa có gì được code, chưa có `## Plan`.
2. **Plan Gate** — sau khi Spec được duyệt, viết kế hoạch code cụ thể vào `## Plan` → dừng, chờ User duyệt **kế hoạch**. Sau khi duyệt: `status: ready`, rồi hỏi User ai sẽ là `executor:` → ghi `status: dispatched` + `dispatched: <ngày>`. **control-tower dừng lại ở đây — không tự viết code, không tự chạy test.**

Sau Plan Gate, vòng đời task tiếp tục **ngoài hệ**:

3. **Bàn giao thực thi** — executor (người/AI khác, trong repo code đích) làm việc, tự chạy test, tạo branch/commit/PR, rồi báo lại `result_ref:`.
4. **`/review-order`** — control-tower phát phiếu review (đọc-only, không tự review) → giao reviewer độc lập (≠ executor). `status: in-review`.
5. **Review ngoài hệ** — reviewer đọc diff, chạy test, soát AC/DoD trong repo code đích (dùng `/code-review` của repo đó) — hoàn toàn ngoài control-tower.
6. **`/verdict`** — reviewer báo kết quả, control-tower ghi vào frontmatter: `pass` → đóng task (`status: done`, cần xác nhận người); `changes` → `status: changes-requested`, giao lại.

**Nâng cấp RESTRICTED tự động:** nếu task gắn `risk: high` (do chạm hub/bridge node — mục 6) hoặc chạm `schemas/`/`models.py`/migration → Spec Gate và Plan Gate đều bắt buộc xác nhận bằng văn bản/chat rõ ràng của User, không được suy diễn im lặng là đã duyệt. Việc đóng task (`/verdict pass`) LUÔN LUÔN cần xác nhận người, bất kể mức rủi ro.

---

## 5. BÀN GIAO (HANDOFF ARTIFACTS)

- **OUT (giao việc)**: file task = phiếu giao việc tự chứa (AC + `files:` + `tests:` + `## Plan` + DoD). Executor chỉ cần path task; không cần cùng hệ/công cụ với control-tower.
- **IN (trả việc)**: executor báo "xong" kèm **result-ref** (branch/commit/PR) → ghi vào `result_ref:`, chuyển `status: in-review`.
- Executor có thể là: phiên Claude riêng trong repo code (khuyến nghị), AI khác (Antigravity/Cursor…), hoặc người. Control-tower **không giả định gì** về executor.
- **REVIEW-OUT**: `/review-order` sinh phiếu review (`projects/<tên>/reviews/<ID>-review.md`) → giao reviewer độc lập (≠ executor). control-tower không tự tạo/xóa phiếu ngoài luồng `/review-order` — không sửa tay file trong thư mục này trừ khi cần đính chính thông tin.
- **VERDICT-IN**: reviewer báo kết quả → `/verdict` ghi vào hệ thống. Reviewer cũng có thể là người hoặc AI khác; control-tower không giả định gì về reviewer.

---

## 6. KHAI THÁC `code-review-graph` (read-only, chỉ dùng khi PLAN/COORDINATE)

Bộ công cụ có ~30 MCP tool. **Mọi lời gọi PHẢI kèm `repo_root=<tuyệt đối>` tra từ PROJECT REGISTRY (`index.md` mục 2)** — cwd của phiên là `control-tower`, auto-detect sẽ sai. Luôn mở đầu bằng `get_minimal_context_tool`; dùng `detail_level="minimal"` ở các tool hỗ trợ. **Toàn bộ mục này là phân tích tĩnh (static analysis) — không tool nào ở đây đọc diff thực tế của executor hay chạy test; đó là việc của reviewer, ngoài hệ.**

### 6.1. Bảng: `/pm` gọi tool nào ở bước nào (Spec Gate + Plan Gate)

| Bước | Tool (tên & tham số THẬT) | Kết quả ghi vào task |
|---|---|---|
| 0. Khởi động | `get_minimal_context_tool(task=..., repo_root=...)` | định hướng, tiết kiệm token |
| 1. Định vị | `semantic_search_nodes_tool(query=..., repo_root=..., detail_level="minimal")` | tìm đúng symbol/file (path thật, không đoán) |
| 2. Blast radius | `get_impact_radius_tool(changed_files=[...], repo_root=..., detail_level="minimal")` | điền `files:` (file/caller/dependent) |
| 3. Test hiện có | `query_graph_tool(pattern="tests_for", target=<file/symbol>, repo_root=..., detail_level="minimal")` | điền `tests:` test đang có |
| 4. Lỗ hổng test | `get_knowledge_gaps_tool(repo_root=...)` | tự sinh sub-task viết test (6.2) |
| 5. Xếp hạng rủi ro | `get_hub_nodes_tool(top_n=50, repo_root=...)`, `get_bridge_nodes_tool(top_n=50, repo_root=...)` | gắn `risk: high` nếu trùng (6.3) |
| 6. Ảnh hưởng nghiệp vụ | `get_affected_flows_tool(changed_files=[...], repo_root=...)` | điền `flows:` |

> **Lưu ý:** `query_graph_tool` KHÔNG có tham số `edge` — tham số đúng là `pattern` (giá trị `"tests_for"` để tìm test) và `target` (tên node/file cần tra). Gọi sai tham số sẽ lỗi ngay lập tức.
>
> **Không còn bước 7 "Verify bằng `detect_changes_tool`"** như bản nháp Mô hình A — verify giờ là việc của reviewer ngoài hệ (mục 4, 5). `/pm` dừng ở bước 6, không tự verify.

### 6.2. Auto-sinh sub-task test từ `get_knowledge_gaps_tool`

Nếu vùng ảnh hưởng chứa hotspot **chưa được test cover** (theo `get_knowledge_gaps_tool`), tự thêm sub-task:
`- [ ] Viết test cho <symbol/file> (hiện chưa có coverage — knowledge gap) — test đề xuất: <file test đề xuất>`

### 6.3. Cờ rủi ro từ hub/bridge nodes

`get_hub_nodes_tool`/`get_bridge_nodes_tool` trả về **top toàn cục của cả repo**, không scope theo task — vì vậy phải gọi với `top_n` đủ lớn (dùng **50**, không dùng mặc định của tool là 10). Nếu bất kỳ file/symbol nào trong `files:` trùng với danh sách trả về → gắn `risk: high` và áp dụng nâng cấp RESTRICTED (mục 4).

### 6.4. Tool read-only dùng cho `/review-order` (làm giàu phiếu review, KHÔNG phải verify)

- `get_suggested_questions_tool(repo_root=...)` — sinh câu hỏi review ưu tiên (bridge node thiếu test, hub node chưa cover, coupling bất ngờ...), dùng nguyên trạng, không cần `changed_files`.
- `get_affected_flows_tool(changed_files=<files: đã ghi trong task lúc Spec Gate>, repo_root=...)` — dùng LẠI danh sách file đã chốt ở Spec Gate, KHÔNG tự đọc git diff mới của executor (đó là ranh giới giữ cho control-tower không lấn sang việc review).

### 6.5. Kiểm tra graph "tươi" (freshness)

`list_graph_stats_tool` (MCP) **không** trả về thông tin so khớp commit — chỉ có `total_nodes`, `total_edges`, `embeddings_count`, `last_updated`. Để kiểm tra graph có khớp commit hiện tại hay không, chạy CLI qua Bash:
```bash
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph status --repo <repo_root> --json
```
và so `built_at_commit` với `current_sha`.

### 6.6. `crg-daemon` — tự cập nhật graph nền

Binary `crg-daemon` KHÔNG nằm trong PATH mặc định — gọi qua module Python:
```bash
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph daemon add <repo_root> --alias <tên>
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph daemon start
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph daemon status
```
Daemon poll 2s, tự cập nhật graph khi code đổi (kể cả khi executor đẩy commit mới) → `/pm`/`/review-order` luôn truy vấn graph tươi. An toàn token qua env khi cần: `CRG_MAX_IMPACT_DEPTH`, `CRG_MAX_IMPACT_NODES`, `CRG_TOOL_TIMEOUT`.

---

## 7. CHUẨN MỰC KIỂM TOÁN (log.md - Audit Trail)

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
`<operation>` ∈ `{ingest, pm-create, plan, dispatch, review-order, verdict, report, lint}`. Ghi 1 entry cho mọi hành động COLLABORATIVE hoặc RESTRICTED.

---

## 8. MACRO VÀ LỆNH ĐIỀU KHIỂN

*   `/pm <mô tả_task> [--project <tên>]`: Spec Gate → Plan Gate → `ready` → `dispatched`. Tạo file task riêng trong `projects/<tên>/tasks/` đầy đủ `files:`/AC/`tests:`/`flows:` bằng graph. **Không tự viết code, không tự verify.**
*   `/ingest`: Đọc `inbox.md`, **reconcile vào task tương tự đã có** thay vì tạo trùng (mục 9), hoặc route thành knowledge file (`knowledge/`/`docs/`, mục 11) nếu không actionable, làm giàu bằng graph, xóa mục đã xử lý khỏi inbox.
*   `/report`: Quét `projects/*/tasks/*.md`, tổng hợp Done/Total theo `status:`, cập nhật `<tên-dự-án>.md` + `index.md`; quét `knowledge/**/*.md` + `projects/*/docs/*.md`, cập nhật `knowledge/_index.md`.
*   `/lint [--project <tên>]`: Health-check backlog — task trễ hạn, thiếu AC, link file chết, task mồ côi, mâu thuẫn, kẹt ở `dispatched`/`in-review` quá lâu, knowledge mồ côi/cũ (mục 6, 11, `.claude/skills/lint/SKILL.md`).
*   `/review-order <task ID/path> --ref <branch|commit|PR>`: Phát phiếu review cho reviewer độc lập, chuyển `status: in-review`. Không tự review, không chạy test.
*   `/verdict <task ID/path> <pass|changes> --reviewer @id [--commit <hash>] [--notes ...]`: Ghi kết quả review vào hệ thống. Kiểm four-eyes (`reviewer` ≠ `executor`). `pass` → đóng task (cần xác nhận người); `changes` → mở lại kèm findings.

---

## 9. RULE "RECONCILE, ĐỪNG APPEND" CHO `/ingest`

Khi phân loại 1 ghi chú từ `inbox.md`: nếu **task tương tự đã tồn tại** trong `projects/<tên>/tasks/*.md` (cùng file/symbol hoặc cùng chủ đề) → **viết lại/bổ sung mạch lạc vào task đó**, KHÔNG tạo task trùng lặp mới. Sau khi xử lý xong 1 mục → xóa khỏi `inbox.md`, ghi log `ingest`.

---

## 10. ONBOARD DỰ ÁN MỚI (Runbook)

Khi cần thêm một dự án mới vào Control Tower:

1. Thêm 1 hàng vào bảng **PROJECT REGISTRY** trong `index.md` (mục 2): tên dự án, `repo_root` tuyệt đối, thư mục task.
2. Tạo thư mục `projects/<tên-dự-án>/` với file `<tên-dự-án>.md` (tên file TRÙNG tên folder — copy khung từ `projects/topvnsport-pmi/topvnsport-pmi.md`, đặt `task_prefix` + `next_task_id: 1`), `tasks/`, `docs/`, `reviews/`.
3. Build graph cho repo đó (nếu chưa có):
   ```bash
   /home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph build --repo <repo_root>
   /home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph embed --repo <repo_root>
   ```
4. Đăng ký daemon watch để graph tự cập nhật (mục 6.6): `daemon add <repo_root> --alias <tên>`.
5. (Tùy chọn) `code-review-graph register <repo_root> --alias <tên>` nếu cần `cross_repo_search_tool` truy vấn chéo nhiều dự án cùng lúc.

---

## 11. QUẢN LÝ KNOWLEDGE (domain, quyết định kiến trúc, quy ước)

Control-tower quản lý 2 loại nội dung: **task** (có `status`, cần hành động, xem mục 2) và **knowledge** (tài liệu tham khảo sống, không có `status`/`executor`/`deadline`). Đừng nhầm lẫn hai loại — nếu 1 knowledge file cần hành động, tạo task riêng link tới nó, đừng biến knowledge file thành task.

### 11.1. Nguyên tắc "đổi cùng cái gì"

| Loại tài liệu | Ví dụ | Ở đâu |
|---|---|---|
| Tài liệu HỆ THỐNG (đổi cùng code) | architecture.md, API docs, test guides | **Ở repo code.** Control-tower chỉ trỏ qua `<tên-dự-án>.md` mục References — KHÔNG copy nội dung sang. |
| Domain / business knowledge (đổi theo luật kinh doanh) | Quy tắc VAT, phân loại sản phẩm, luồng thanh toán | **Control-tower** — `knowledge/domains/` (cross-project) hoặc `projects/<tên>/docs/` (per-project) |
| Quyết định kiến trúc (ADR) | Tại sao dùng File-Over-API? Tại sao chọn MinIO? | **Control-tower** — `knowledge/decisions/` (cross-project) hoặc `projects/<tên>/docs/` (per-project) |
| TODO / nợ kỹ thuật | Bug, technical debt | **Migrate thành task** trong `tasks/` — không phải knowledge |

### 11.2. Cấu trúc thư mục

```
knowledge/                          # CROSS-PROJECT (áp dụng nhiều dự án)
├── _index.md                       # Danh mục — cập nhật bởi /report
├── domains/                        # Domain knowledge nghiệp vụ
├── decisions/                      # ADR cross-project
├── conventions/                    # Quy ước coding/process dùng chung
└── research/                       # Tài liệu nghiên cứu dài

projects/<tên>/docs/                 # PER-PROJECT knowledge
```

### 11.3. Frontmatter chuẩn knowledge file

```yaml
---
type: domain | decision | convention | research | reference | note
scope: general | <tên-dự-án>     # general → knowledge/, project-specific → projects/<tên>/docs/
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
related: []                       # wiki-link tới file/ADR khác, vd [[ADR-001-file-over-api]]
---
```

### 11.4. Template ADR (`type: decision`)

```markdown
# ADR-<NNN>: <title>

## Context
<Vấn đề gì? Áp lực nào?>

## Decision
<Quyết định gì và tại sao?>

## Consequences
<Dễ hơn cái gì? Khó hơn cái gì? Trade-off?>

## Status
Accepted | Superseded by [[ADR-NNN]] | Deprecated
```

### 11.5. Routing rule cho `/ingest`

Khi 1 mục trong `inbox.md` **không actionable** (không có deadline, không cần code, là ghi chú nghiệp vụ/quyết định) → tạo file trong `knowledge/<type>/` (scope=general) hoặc `projects/<tên>/docs/` (scope=project cụ thể), theo frontmatter mục 11.3 — KHÔNG tạo task giả cho nó. Nếu mơ hồ giữa task và knowledge, hỏi User thay vì đoán.

### 11.6. Không tự động sinh knowledge

Knowledge do con người tạo/duyệt nội dung; agent chỉ route đúng ghi chú vào đúng chỗ (mục 11.5) và cập nhật index (`/report`) — không tự bịa nội dung domain/ADR mà User chưa xác nhận.
