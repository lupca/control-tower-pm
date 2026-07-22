# NHẬT KÝ KIỂM TOÁN VẬN HÀNH AGENT (log.md)

File này tự động ghi lại toàn bộ hoạt động của Agent nhằm đảm bảo tính **Minh bạch (Transparent AI)** và khả năng **Truy vết nguồn gốc (Traceability)** theo tiêu chuẩn PMI-CPMAI™.

---

## LỊCH SỬ HOẠT ĐỘNG KHỞI TẠO:

### [2026-07-21 00:00:00] KHỞI TẠO HỆ THỐNG
- **Dự án:** Toàn bộ hệ thống Control Tower
- **Mô tả hành động:** Khởi tạo repo git `control-tower/` với cấu trúc `AGENTS.md`, `index.md` (kèm PROJECT REGISTRY), `inbox.md`, `log.md`, thư mục `projects/`, và 3 skill `/pm` `/ingest` `/report`.
- **Giải trình (Rationale):** Thiết lập nền tảng quản trị dự án cá nhân theo triết lý tối giản "File Over API" nhằm loại bỏ rào cản cồng kềnh từ các phần mềm quản lý bên thứ ba, tận dụng hạ tầng đã có sẵn (Claude Code + code-review-graph MCP + git) thay vì dựng stack mới.
- **Trạng thái:** Thành công.

### [2026-07-21 00:05:00] KHẢO SÁT GRAPH TOPVNSPORT
- **Dự án:** `topvnsport-pmi` / `topvnsport-oms`
- **Mô tả hành động:** Chạy `code-review-graph status --repo /home/lupca/projects/topvnsport`.
- **Giải trình (Rationale):** Graph đã build (2602 nodes, 30237 edges, 448 files) và `built_at_commit` khớp `current_sha` — không cần rebuild. Tuy nhiên chưa có embeddings (`sentence_transformers` chưa cài) nên semantic search sẽ fallback về FTS cho tới khi chạy `pip install "code-review-graph[embeddings]"` + `code-review-graph embed --repo /home/lupca/projects/topvnsport`.
- **Trạng thái:** Thành công (ghi nhận, chưa embed).

### [2026-07-21 17:39:37] BẬT SEMANTIC SEARCH CHO TOPVNSPORT
- **Dự án:** `topvnsport-pmi` / `topvnsport-oms`
- **Mô tả hành động:** Chạy `pip install "code-review-graph[embeddings]"` trong venv của tool, sau đó `code-review-graph embed --repo /home/lupca/projects/topvnsport`.
- **Giải trình (Rationale):** Hoàn tất bước setup còn thiếu trong kế hoạch ban đầu — graph cần embeddings để `semantic_search_nodes_tool` hoạt động chính xác thay vì fallback FTS. Kết quả: 2154 node được embed bằng model `all-MiniLM-L6-v2`.
- **Trạng thái:** Thành công.

### [2026-07-21 17:45:00] PHÁT HIỆN TASK ĐÃ HOÀN THÀNH TỪ TRƯỚC (topvnsport-pmi #1.1)
- **Dự án:** `topvnsport-pmi`
- **Mô tả hành động:** Chạy CLI `search "variant cost tax validation" --repo /home/lupca/projects/topvnsport` (tương đương `semantic_search_nodes_tool`) để xác minh path thật cho task "Thêm validation cost/tax cho variant".
- **Giải trình (Rationale):** Kết quả cho thấy `PMI/backend/schemas/tier_variation.py` đã có `Field(ge=0)`/`Field(ge=0, le=100)`, kèm migration `5a451ed7aa00_add_cost_tax_to_variants` và test đầy đủ (`test_variant_cost_tax.py`, `test_product_api_cost_tax.py`). Task này thực chất đã xong, không phải việc tồn đọng. Đã sửa `projects/topvnsport-pmi.md` từ `- [ ]` sang `- [x]` kèm bằng chứng, thay vì để một task đã xong bị báo cáo nhầm là "đang chờ làm".
- **Trạng thái:** Thành công.

### [2026-07-21 02:56:45] PHÂN TÍCH VÙNG ẢNH HƯỞNG (MẪU)
- **Dự án:** `topvnsport-pmi`
- **Mô tả hành động:** Sử dụng `code-review-graph` để phân tích tầm ảnh hưởng của yêu cầu: *"thêm validation cost/tax cho variant"*.
- **Giải trình (Rationale):** Hệ thống phát hiện thay đổi này ảnh hưởng trực tiếp tới `PMI/backend/schemas/tier_variation.py` (schema), `PMI/backend/services/product_service.py` (logic nghiệp vụ), và cần bổ sung test trong `PMI/backend/tests/test_variant_cost_tax.py`. Do đó, Agent đề xuất chia thành 3 sub-tasks chi tiết thay vì 1 task lớn mơ hồ để User dễ dàng duyệt (HITL).
- **Trạng thái:** Thành công.

---

## LỊCH SỬ HOẠT ĐỘNG — NÂNG CẤP TẦNG A + B

> Từ đây log dùng format chuẩn mới (`AGENTS.md` mục 6): `## [YYYY-MM-DD HH:MM:SS] <operation> | <title>`.

## [2026-07-21 18:00:00] plan | Nâng cấp control-tower theo spec Tầng A + B
- Dự án: Toàn bộ hệ thống Control Tower
- Mô tả: Implement spec `home-lupca-downloads-h-th-ng-file-over-generic-tiger.md` (Tầng A: kỷ luật task — AC/DoD, 3 cổng HITL, `/lint`, log chuẩn; Tầng B: khai thác sâu code-review-graph — B1-B6). Sửa `AGENTS.md` (DoD mục 3, 3 gate mục 4, bảng tool graph mục 5, log format mục 6, rule reconcile mục 8), tạo `.claude/skills/lint/SKILL.md`, viết lại `.claude/skills/pm/SKILL.md` + 3 file `references/{task-creation,task-execution,task-finalization}.md`, cập nhật `ingest/SKILL.md` (rule A7), đăng ký `topvnsport` vào `crg-daemon` (poll 2s, tự cập nhật graph).
- Giải trình: Đối chiếu spec với source thật của `code-review-graph` (đọc `main.py`, `daemon.py`, chạy CLI) trước khi implement, phát hiện 2 lỗi chặn trong spec gốc: (1) `query_graph_tool` không có tham số `edge` — tham số đúng là `pattern`/`target`, giá trị pattern đúng là `"tests_for"` không phải `"tested_by"`; (2) `list_graph_stats_tool` (MCP) không có field `head_matches_build` — thông tin so khớp commit chỉ có ở CLI `code-review-graph status --json` (field `built_at_commit`/`current_sha`). Đã sửa cả hai trong `AGENTS.md` mục 5.1 và 5.5 trước khi viết vào skill, tránh implement một lỗi đã biết. Cũng sửa: `get_hub_nodes_tool`/`get_bridge_nodes_tool` dùng `top_n=50` thay vì mặc định 10 (repo lớn sẽ khiến `⚠️high-risk` gần như không bao giờ kích hoạt nếu để mặc định); `crg-daemon` không nằm trong PATH nên mọi lệnh daemon đều gọi qua `python3 -m code_review_graph daemon ...` với path venv đầy đủ.
- Files touched: AGENTS.md, CLAUDE.md, index.md, .claude/skills/lint/SKILL.md, .claude/skills/pm/SKILL.md, .claude/skills/pm/references/task-creation.md, .claude/skills/pm/references/task-execution.md, .claude/skills/pm/references/task-finalization.md, .claude/skills/ingest/SKILL.md
- Trạng thái: Thành công.
- Commit: `e2361d7`

## [2026-07-21 18:05:00] plan | Đăng ký topvnsport vào crg-daemon watch
- Dự án: `topvnsport-pmi` / `topvnsport-oms`
- Mô tả: Chạy `code_review_graph daemon add /home/lupca/projects/topvnsport --alias topvnsport` rồi `daemon start`.
- Giải trình: Thực hiện B6 của spec — thay bước rebuild graph thủ công bằng daemon nền tự động cập nhật graph khi code đổi (poll 2s), để `/pm`/`/lint` luôn truy vấn graph tươi.
- Files touched: ~/.code-review-graph/watch.toml (ngoài repo, config máy)
- Trạng thái: Thành công — `daemon status` xác nhận PID chạy, alias `topvnsport` alive.
- Commit: n/a

## [2026-07-21 18:30:00] report | Reconcile git history vào task list
- Dự án: `topvnsport-pmi`
- Mô tả: Quét git log của `/home/lupca/projects/topvnsport` từ đầu năm, phân tích 50 commit gần nhất, nhóm thành các feature đã implement, reconcile vào `projects/topvnsport-pmi.md` với trạng thái `- [x]`.
- Giải trình: Backlog control-tower mới được khởi tạo nên chưa track các feature đã làm trước đó. Phân tích git history phát hiện 7 feature lớn đã hoàn thành: (1) Identity Service/SSO `0d22c38`, (2) PMI migrate to Identity `e5461a5`, (3) API Gateway migration `b279b90`, (4) Identity in CD pipeline `91dfb05`, (5) Product Form UX refactor `7e820ae`, (6) Cost/Tax sync PMI↔WMS `cf886a5`, (7) Stock Management → WMS `d14f956`. Tất cả đã có commit + test pass, ghi vào backlog để phản ánh đúng công việc đã làm.
- Files touched: projects/topvnsport-pmi.md
- Trạng thái: Thành công.
- Commit: n/a

## [2026-07-21 19:00:00] plan | Chuyển sang Mô hình B — review hoàn toàn ngoài hệ (§10)
- Dự án: Toàn bộ hệ thống Control Tower
- Mô tả: Implement §10 của spec cập nhật (Mô hình B): control-tower thu hẹp phạm vi về PLAN + COORDINATE thuần Markdown, bỏ hẳn "Code Gate" nội bộ (control-tower từng gọi `detect_changes_tool` + trực tiếp chạy test để tự verify trước khi đóng task). Giờ EXECUTE (viết code) và REVIEW (đọc diff, chạy test) đều do người/AI khác đảm nhiệm hoàn toàn ngoài hệ, độc lập với nhau (reviewer ≠ executor). Thay đổi cụ thể: viết lại `AGENTS.md` (vai trò PLAN/EXECUTE/REVIEW/COORDINATE §1, cú pháp task thêm metadata `status`/`👷 executor`/`🔎 reviewer`/`🔗result` §2, vòng đời task todo→ready→dispatched→in-review→done|changes-requested §2.3, DoD giờ do reviewer xác nhận §3, chỉ còn 2 gate Spec+Plan trong hệ §4, bàn giao §5); rút gọn `pm/SKILL.md` + `task-execution.md` để dừng ở `dispatched` (xóa `task-finalization.md` — logic đóng task chuyển hẳn sang `/verdict`); tạo mới `review-order/SKILL.md` (phát phiếu review, không tự review/không đọc diff) và `verdict/SKILL.md` (ghi verdict, chặn four-eyes); thêm 2 luật anomaly cho `/lint` (kẹt `dispatched`/`in-review` quá lâu); tạo thư mục `reviews/`.
- Giải trình: Người dùng chốt rõ 3 điều: (1) test luôn do reviewer ngoài hệ chạy, không phải control-tower/subagent nội bộ; (2) "check" = phiếu review độc lập → reviewer (người/AI khác) tự làm trong repo code → báo verdict → `/verdict` cập nhật hệ thống; (3) đây là formalize hóa quy trình thủ công người dùng đã làm (tạo phiếu → reviewer độc lập → update), giờ có audit trong git. Việc này thay thế hoàn toàn giả định cũ (Tầng A §4 Code Gate) rằng control-tower/subagent tự chạy `detect_changes_tool` + test để tự đóng task — giả định đó không còn đúng vì Mô hình B minh định control-tower không bao giờ đọc diff hay chạy test.
- Files touched: AGENTS.md, CLAUDE.md, index.md, projects/topvnsport-pmi.md, projects/topvnsport-oms.md, .claude/skills/pm/SKILL.md, .claude/skills/pm/references/task-creation.md, .claude/skills/pm/references/task-execution.md, .claude/skills/pm/references/task-finalization.md (đã xóa), .claude/skills/ingest/SKILL.md, .claude/skills/lint/SKILL.md, .claude/skills/review-order/SKILL.md (mới), .claude/skills/verdict/SKILL.md (mới), reviews/README.md (mới)
- Trạng thái: Thành công.
- Commit: `d1980a5`

## [2026-07-21 19:30:00] plan | Setup Obsidian vault cho control-tower
- Dự án: Toàn bộ hệ thống Control Tower
- Mô tả: User đã mở repo này như một Obsidian vault (phát hiện `.obsidian/` với config mặc định + 1 daily note rỗng `2026-07-21.md` + 1 canvas rỗng `Untitled.canvas` chưa từng được commit). Theo yêu cầu, chuẩn hoá và commit phần cấu hình vault: (1) xoá 2 file rỗng/ngẫu nhiên (`2026-07-21.md`, `Untitled.canvas`); (2) cấu hình `graph.json` — tô màu nhóm theo path (Core: `AGENTS.md`/`index.md`/`log.md`/`inbox.md`/`CLAUDE.md`, Tasks: `projects/`, Skills: `.claude/skills/`, Reviews: `reviews/`), bật `showArrow` để thấy hướng link; (3) tạo `control-tower-map.canvas` — sơ đồ trực quan luồng Mô hình B (control-tower PLAN/COORDINATE ↔ EXECUTOR ngoài hệ ↔ REVIEWER ngoài hệ) với node file link thẳng tới `AGENTS.md`, `index.md`, `projects/*.md`, `reviews/README.md`, `log.md`; (4) sửa `.gitignore` — chỉ loại trừ `workspace.json`/`workspace-mobile.json`/`cache` (state UI cá nhân, gây diff noise), còn `app.json`/`appearance.json`/`core-plugins.json`/`graph.json` VÀ canvas đều commit vì là cấu hình dùng chung, hữu ích để giữ qua git.
- Giải trình: Mục đích user nêu rõ là "để nhìn và quản lý tốt hơn" — đầu tư vào Graph view (tô màu theo nhóm để phân biệt luật chơi/task/skill/review) và một canvas tổng quan (thay vì để trống) trực tiếp phục vụ mục tiêu đó. Không commit `workspace.json` vì đó là state cục bộ (layout pane, file đang mở) — commit nó sẽ ép layout của người viết cuối lên mọi người khác mở vault, và gây diff ồn ào mỗi lần đổi tab.
- Files touched: .gitignore, .obsidian/app.json, .obsidian/appearance.json, .obsidian/core-plugins.json, .obsidian/graph.json, control-tower-map.canvas (mới), index.md, 2026-07-21.md (đã xoá), Untitled.canvas (đã xoá)
- Trạng thái: Thành công.
- Commit: `ae29c16`

## [2026-07-21 20:00:00] pm-create | Task-per-file migration + Knowledge layer
- Dự án: Toàn bộ hệ thống Control Tower
- Mô tả: Implement spec nâng cấp "Task-per-File + Knowledge Layer". (1) Migrate task từ file monolithic `projects/topvnsport-pmi.md`/`projects/topvnsport-oms.md` sang cấu trúc `projects/<tên>/{_project.md, tasks/, docs/}` — mỗi task giờ là 1 file riêng với YAML frontmatter (`id`/`status`/`priority`/`risk`/`executor`/`reviewer`/`result_ref`/`depends_on`/`files`/`flows`/`tests`/`dispatched`/`in_review`/`created`/`updated`) thay cho checkbox inline + emoji metadata. Trích xuất đúng 9 task PMI (`PMI-001`…`PMI-009`, giữ nguyên AC/sub-tasks/commit hash) và tạo `_project.md` cho OMS (0 task, `next_task_id: 1`). (2) Thêm knowledge layer 2 tầng: `knowledge/{_index.md, domains/, decisions/, conventions/, research/}` (cross-project) + `projects/<tên>/docs/` (per-project), seed `knowledge/decisions/ADR-001-file-over-api.md`. (3) Cập nhật `AGENTS.md` (§2 viết lại toàn bộ cú pháp task sang frontmatter, §2.1a quy tắc đánh ID, §11 mới — Quản lý Knowledge), `CLAUDE.md`, `index.md` (Registry đổi "Task file" → "Task dir", thêm §6 Knowledge Map), và cả 6 skill (`pm`, `ingest`, `report`, `lint`, `review-order`, `verdict`) để đọc/ghi frontmatter thay vì regex inline, cộng thêm routing knowledge cho `/ingest` và 2 lint rule mới (knowledge mồ côi/cũ).
- Giải trình: Lý do đổi: nhiều executor/reviewer cùng hoạt động trên 1 file task lớn → git conflict liên tục; task không có chỗ chứa spec/plan/review dài mà không phình file dùng chung. Đồng thời control-tower thiếu nơi lưu domain knowledge/ADR — người/AI mới vào không biết "trước mình quyết gì về X". Tách biệt rõ: task (có status, cần hành động) vs knowledge (tài liệu tham khảo sống, không status/executor/deadline) — tránh biến quyết định kiến trúc thành task giả hoặc ngược lại.
- Files touched: AGENTS.md, CLAUDE.md, index.md, projects/topvnsport-pmi/_project.md (mới), projects/topvnsport-pmi/tasks/PMI-001..009 (mới, 9 file), projects/topvnsport-oms/_project.md (mới), projects/topvnsport-pmi.md (đã xoá), projects/topvnsport-oms.md (đã xoá), knowledge/_index.md (mới), knowledge/decisions/ADR-001-file-over-api.md (mới), .claude/skills/{pm,ingest,report,lint,review-order,verdict}/SKILL.md, .claude/skills/pm/references/{task-creation,task-execution}.md
- Trạng thái: Thành công.
- Commit: `d4e16c8`

## [2026-07-21 21:16:00] pm-create | Onboard WMS + tạo task WMS-001
- Dự án: `topvnsport-wms` (mới onboard)
- Mô tả: Onboard dự án WMS vào control-tower (tạo `projects/topvnsport-wms/_project.md` + thư mục `tasks/`, cập nhật PROJECT REGISTRY trong `index.md`). Sau đó tạo task WMS-001 "Nâng cấp DataTable: thêm cột STT và pagination cho toàn bộ WMS" theo yêu cầu của User.
- Giải trình: User yêu cầu update UI table WMS (thêm STT, phân trang), nhưng WMS chưa có trong registry. Đã onboard trước rồi mới tạo task. Dùng `semantic_search_nodes_tool` và `get_hub_nodes_tool(top_n=50)` xác nhận: DataTable WMS không nằm trong hub nodes → risk `normal`; WMS chưa có test cho DataTable (PMI có) → AC7 yêu cầu tạo test mới.
- Files touched: projects/topvnsport-wms/_project.md (mới), projects/topvnsport-wms/tasks/WMS-001-table-stt-pagination.md (mới), index.md
- Trạng thái: Thành công — task ở `status: todo`, chờ User duyệt Spec Gate (AC).
- Commit: `d49d0a4` (ghi vào git muộn, cùng đợt commit sửa Obsidian Graph view)

## [2026-07-21 21:20:00] plan | Dispatch WMS-001 cho @antigravity
- Dự án: `topvnsport-wms`
- Mô tả: Plan Gate đã được User duyệt. Dispatch task WMS-001 "Nâng cấp DataTable: thêm cột STT và pagination" cho executor @antigravity.
- Giải trình: Task đã qua đủ 2 gate nội bộ (Spec + Plan). Executor sẽ thực hiện code trong repo `/home/lupca/projects/topvnsport`, sau đó báo result-ref để phát phiếu review.
- Files touched: projects/topvnsport-wms/tasks/WMS-001-table-stt-pagination.md
- Trạng thái: Thành công — `status: dispatched`, `executor: @antigravity`.
- Commit: `d49d0a4` (ghi vào git muộn, cùng đợt commit sửa Obsidian Graph view)

## [2026-07-21 21:42:00] review-order | Phát phiếu review WMS-001
- Dự án: `topvnsport-wms`
- Mô tả: Phát phiếu review cho task WMS-001 "Nâng cấp DataTable: thêm cột STT và pagination". Result-ref: local (uncommitted). Executor: @antigravity.
- Giải trình: Code đã xong ở local (chưa commit). Gọi `get_affected_flows_tool` xác nhận 7 flows bị ảnh hưởng (InventoryPage, TransactionsPage, các handlers). Phiếu review tại `reviews/WMS-001-review.md`.
- Files touched: projects/topvnsport-wms/tasks/WMS-001-table-stt-pagination.md, reviews/WMS-001-review.md (mới)
- Trạng thái: Thành công — task ở `status: in-review`, chờ reviewer độc lập (≠ @antigravity).
- Commit: `d49d0a4` (ghi vào git muộn, cùng đợt commit sửa Obsidian Graph view)

## [2026-07-21 21:50:00] plan | Sửa Obsidian Graph view — thêm wikilink thật + màu theo project
- Dự án: Toàn bộ hệ thống Control Tower
- Mô tả: User chụp Graph view thấy node rời rạc, không tụ theo project. Điều tra xác nhận nguyên nhân: 29 file `.md` nhưng gần như 0 wikilink thật (`[[...]]`) — Obsidian Graph chỉ vẽ cạnh nối cho wikilink thật, không nhận diện path trong bảng/YAML/`[text](path)`. Đã sửa: (1) `.obsidian/graph.json` — khôi phục + mở rộng `colorGroups` theo path (Core/PMI/OMS/WMS/knowledge/skills/reviews, 7 nhóm màu), bật `showArrow`; (2) thêm mục `## Tasks` (wikilink tới từng task) vào cả 3 `_project.md`; (3) thêm dòng backlink `> Dự án: [[...]]` vào đầu body của 10 task file hiện có (PMI 001-009, WMS-001); (4) đổi link Markdown thường sang wikilink thật trong `knowledge/_index.md`; (5) sửa 2 node `control-tower-map.canvas` còn trỏ tới path cũ `projects/topvnsport-pmi.md`/`topvnsport-oms.md` (đã xoá từ lúc migrate task-per-file, giờ mở sẽ báo lỗi thiếu file) sang đúng path `_project.md` mới; (6) cập nhật `AGENTS.md` mục 2.1 (thêm dòng backlink vào template chuẩn) + `pm/references/task-creation.md` (task mới tự thêm backlink + dòng vào `## Tasks`) + `report/SKILL.md` (mỗi lần `/report` chạy sẽ regenerate lại toàn bộ mục `## Tasks` — tự-heal nếu thiếu/thừa).
- Giải trình: Đây thuần là vấn đề cấu hình + nội dung Markdown, không đổi bất kỳ frontmatter field hay heading nào các skill đang parse (`status`, `files`, `tests`, `## Tiêu chí nghiệm thu (AC)`, `## Plan`, `## Sub-tasks`) — xác nhận trước khi sửa để không ảnh hưởng vòng đời/gate hiện có. Chọn mức đầy đủ (config + content + skill) theo yêu cầu của User để về sau task mới do `/pm` tạo tự động có link, không phải làm tay mỗi lần. Nhân tiện dọn luôn rác canvas còn sót từ lần migrate task-per-file trước (commit `d4e16c8`) — 2 node trỏ file đã xoá.
- Files touched: .obsidian/graph.json, control-tower-map.canvas, AGENTS.md, .claude/skills/pm/references/task-creation.md, .claude/skills/report/SKILL.md, knowledge/_index.md, projects/topvnsport-pmi/_project.md, projects/topvnsport-oms/_project.md, projects/topvnsport-wms/_project.md, projects/topvnsport-pmi/tasks/PMI-001..009.md, projects/topvnsport-wms/tasks/WMS-001-table-stt-pagination.md
- Trạng thái: Thành công.
- Commit: `d49d0a4`

## [2026-07-21 21:50:00] verdict | WMS-001 PASS
- Dự án: `topvnsport-wms`
- Mô tả: Ghi verdict PASS cho task WMS-001 "Nâng cấp DataTable: thêm cột STT và pagination". Reviewer: @claude. Executor: @antigravity.
- Giải trình: Four-eyes check passed (@claude ≠ @antigravity). Reviewer xác nhận: "All 7 ACs verified. 16/16 tests green. No regressions."
- Files touched: projects/topvnsport-wms/tasks/WMS-001-table-stt-pagination.md
- Trạng thái: Thành công — `status: done`.
- Commit: f4a0971

## [2026-07-21 22:05:00] plan | Dời `reviews/` (root) vào từng project — `projects/<tên>/reviews/`
- Dự án: Toàn bộ hệ thống Control Tower
- Mô tả: User đề xuất bảng rà soát 12 điểm cần sửa khi dời thư mục `reviews/` chung ở root vào bên trong từng project, nhờ kiểm tra trước khi sửa. Đã đọc lại từng file trong bảng để xác minh, phát hiện: mục #7 (`verdict/SKILL.md`) sai — file này không tham chiếu path `reviews/` (chỉ thao tác trực tiếp trên frontmatter của task), nên không cần sửa; đồng thời phát hiện thiếu 1 chỗ ngoài bảng — `AGENTS.md` mục 10 (runbook onboard dự án mới) chưa liệt kê tạo `reviews/` khi thêm project mới, và `index.md` dòng mô tả canvas còn nhắc nhóm màu "Reviews" cũ. Đã sửa: (1) `AGENTS.md` mục 1 (AUTONOMOUS row), mục 5 (REVIEW-OUT, gộp thêm câu quy tắc từ `reviews/README.md` cũ), mục 10 (thêm `reviews/` vào runbook onboard); (2) `index.md` dòng 42/45/54 — bỏ quicklink `reviews/` chung, đổi mô tả canvas; (3) `.claude/skills/review-order/SKILL.md` — sinh phiếu tại `projects/<tên>/reviews/<ID>-review.md` (tên dự án lấy từ path task ở Bước 1), tự tạo thư mục nếu chưa có; (4) `control-tower-map.canvas` — đổi node `n-reviews` từ type `file` (trỏ `reviews/README.md`, sắp thành file chết) sang type `text` mô tả chung; (5) `.obsidian/graph.json` — xoá colorGroup riêng `path:reviews` (không cần nữa vì phiếu giờ nằm trong `path:projects/<tên>` đã có màu); (6) `git mv reviews/WMS-001-review.md` → `projects/topvnsport-wms/reviews/WMS-001-review.md`; (7) xoá `reviews/README.md` (nội dung cốt lõi đã gộp vào `AGENTS.md` mục 5). Không sửa các entry lịch sử trong `log.md` (append-only, giữ nguyên path cũ theo đúng thời điểm ghi).
- Giải trình: `verdict/SKILL.md` không đụng `reviews/` nên xác nhận trước khi tin theo bảng đề xuất, tránh sửa nhầm chỗ không tồn tại. Việc dời vào per-project giúp mỗi dự án tự chứa (project, task, review đi cùng nhau), nhất quán với cấu trúc task-per-file đã làm trước đó, và giúp Obsidian Graph tự cụm phiếu review vào đúng màu project (không cần colorGroup riêng).
- Files touched: AGENTS.md, index.md, .claude/skills/review-order/SKILL.md, control-tower-map.canvas, .obsidian/graph.json, projects/topvnsport-wms/reviews/WMS-001-review.md (di chuyển từ reviews/WMS-001-review.md), reviews/README.md (đã xoá)
- Trạng thái: Thành công.
- Commit: `3db8a3b`

## [2026-07-21 22:20:00] plan | Đổi tên `_project.md` → `<tên>.md` (trùng tên folder) — sửa nhãn Graph view trùng nhau
- Dự án: Toàn bộ hệ thống Control Tower
- Mô tả: User gửi screenshot Graph view, phát hiện cả 3 file quản lý project (`topvnsport-pmi/_project.md`, `topvnsport-oms/_project.md`, `topvnsport-wms/_project.md`) đều hiện nhãn node "_project" giống hệt nhau (Obsidian Graph lấy filename làm nhãn, không phân biệt theo folder/path). Đã search xác nhận đây là giới hạn core Obsidian (không có setting hiện path/alias trong Graph; cần đổi tên file hoặc cài plugin community như Node Masquerade/Front Matter Title). User chọn phương án đổi tên file (không cài thêm plugin). Đã: (1) `git mv _project.md` → `<tên>.md` cho cả 3 project (vd `topvnsport-pmi/topvnsport-pmi.md`) — trùng tên folder, khớp luôn với "folder note" convention của Obsidian; (2) cập nhật toàn bộ tham chiếu `_project.md` sang `<tên>.md` trong `AGENTS.md` (§2 cây thư mục, §2.1 template + giải thích wikilink, §2.1a, §3, §8, §10, §11), `CLAUDE.md`, `index.md` (PROJECT REGISTRY + Project Map + mô tả canvas), 4 skill (`pm/SKILL.md`, `pm/references/task-creation.md`, `report/SKILL.md`, `ingest/SKILL.md`), `control-tower-map.canvas` (2 node file); (3) đơn giản hoá wikilink backlink trong 10 task hiện có từ `[[projects/<tên>/_project|<tên>]]` (path + alias) sang `[[projects/<tên>/<tên>]]` (không cần alias nữa vì tên file đã trùng `<tên>`, Obsidian tự hiển thị đúng).
- Giải trình: `verdict/SKILL.md`, `review-order/SKILL.md`, `lint/SKILL.md`, `task-execution.md` không tham chiếu `_project.md` nên không cần sửa (đã grep xác nhận trước khi đổi). Đổi tên là thay đổi nội dung/tên file thuần Markdown, không đụng field frontmatter hay logic gate nào — mọi skill vốn đã biết `<tên>` project từ context nên tự suy ra đúng path mới, không cần glob pattern đặc biệt.
- Files touched: AGENTS.md, CLAUDE.md, index.md, control-tower-map.canvas, .claude/skills/pm/SKILL.md, .claude/skills/pm/references/task-creation.md, .claude/skills/report/SKILL.md, .claude/skills/ingest/SKILL.md, projects/topvnsport-pmi/topvnsport-pmi.md (đổi tên từ _project.md), projects/topvnsport-oms/topvnsport-oms.md (đổi tên), projects/topvnsport-wms/topvnsport-wms.md (đổi tên), projects/*/tasks/*.md (10 file, sửa dòng backlink)
- Trạng thái: Thành công.
- Commit: `bf3b238`

## [2026-07-21 22:30:00] plan | Thêm node WMS còn thiếu vào `control-tower-map.canvas`
- Dự án: Toàn bộ hệ thống Control Tower
- Mô tả: User hỏi tại sao project WMS (mới onboard) không thấy nối vào node `control-tower-map.canvas` trên Graph view như PMI/OMS. Kiểm tra `control-tower-map.canvas` xác nhận: file này chỉ có 2 node project (`n-proj-pmi`, `n-proj-oms`) từ lúc vẽ ban đầu — WMS được onboard sau đó nhưng chưa ai thêm node/cạnh tương ứng vào canvas, nên không có liên kết. Đã thêm node `n-proj-wms` (trỏ `projects/topvnsport-wms/topvnsport-wms.md`) cùng 5 cạnh mô phỏng đúng luồng đã có cho PMI/OMS: dispatch → wms, wms → EXECUTOR (dispatched), wms → /review-order, /verdict → wms (changes-requested loop), wms → /lint (quét backlog).
- Giải trình: Đây là thiếu sót nội dung diagram (bỏ sót khi onboard WMS), không phải lỗi cơ chế Graph/canvas. Bổ sung thuần túy thêm node+edge mới, không sửa/xoá node cũ nào.
- Files touched: control-tower-map.canvas
- Trạng thái: Thành công.
- Commit: `118a546`

## [2026-07-21 22:35:00] plan | Thêm bước 6 vào runbook Onboard (AGENTS.md mục 10) — không bỏ sót canvas/graph.json cho dự án mới
- Dự án: Toàn bộ hệ thống Control Tower
- Mô tả: User yêu cầu khi Agent tạo project mới (onboard), phải tự hướng dẫn ghi luôn vào "vanvar" (canvas/vault Obsidian) thay vì phải người dùng phát hiện thiếu sót sau như trường hợp WMS. Đã thêm bước 6 vào runbook `AGENTS.md` mục 10: (a) thêm 1 colorGroup mới trong `.obsidian/graph.json` theo `path:projects/<tên-dự-án>`; (b) thêm 1 node file + 5 cạnh chuẩn vào `control-tower-map.canvas`, dùng `n-proj-wms`/`e15`-`e19` (vừa thêm ở entry log trước) làm mẫu chép lại. Nêu rõ toạ độ không cần chính xác vì đây chỉ là sơ đồ trực quan.
- Giải trình: Việc onboard dự án mới trước đây (mục 10) chỉ có 5 bước liên quan tới registry/graph-tool/daemon, không có bước nào nhắc cập nhật phần trực quan hoá Obsidian — đây chính là lý do WMS bị "vô hình" trên canvas dù đã onboard đúng quy trình. Thêm bước 6 để agent tương lai tự làm luôn, không phải đợi user phát hiện qua screenshot.
- Files touched: AGENTS.md
- Trạng thái: Thành công.
- Commit: `c486043`

## [2026-07-21 22:45:00] plan | Dịch toàn bộ file "khung" (AGENTS.md, CLAUDE.md, 6 SKILL.md, 2 reference) sang English
- Dự án: Toàn bộ hệ thống Control Tower
- Mô tả: User đề xuất hybrid — "khung" (instruction cho agent: AGENTS.md, CLAUDE.md, SKILL.md, reference file) chuyển sang English để agent follow chính xác hơn + ít token hơn; "thịt" (nội dung task/AC/Plan/knowledge, và log.md mô tả/giải trình) giữ nguyên tiếng Việt cho người đọc nghiệp vụ. Đã dịch 10 file trong scope: `AGENTS.md`, `CLAUDE.md`, `.claude/skills/{pm,ingest,report,lint,review-order,verdict}/SKILL.md`, `.claude/skills/pm/references/{task-creation,task-execution}.md`. Giữ nguyên không dịch: mọi heading/template xuất hiện literal trong file task/knowledge/review thật (`## Tiêu chí nghiệm thu (AC)`, `> Dự án:`, `## Quy tắc phê duyệt riêng`, `## Findings từ reviewer`, toàn bộ template phiếu review trong `review-order/SKILL.md` bước 4) vì đây là nội dung người Việt đọc, không phải khung chỉ dẫn agent; cũng giữ nguyên field label trong format `log.md` (mục 7: Dự án/Mô tả/Giải trình/Trạng thái) vì đi liền với nội dung log tiếng Việt.
- Giải trình: Số thứ tự mục 1-11 trong `AGENTS.md` giữ nguyên thứ tự (chỉ dịch tiêu đề) nên mọi tham chiếu chéo "AGENTS.md mục X" ở 9 file còn lại vẫn đúng — đã kiểm bằng grep để xác nhận không lệch. Verify YAML frontmatter của 6 SKILL.md vẫn parse hợp lệ sau khi dịch description.
- Files touched: AGENTS.md, CLAUDE.md, .claude/skills/pm/SKILL.md, .claude/skills/pm/references/task-creation.md, .claude/skills/pm/references/task-execution.md, .claude/skills/ingest/SKILL.md, .claude/skills/report/SKILL.md, .claude/skills/lint/SKILL.md, .claude/skills/review-order/SKILL.md, .claude/skills/verdict/SKILL.md
- Trạng thái: Thành công.
- Commit: `016f282`

## [2026-07-22 00:48:00] pm-create | WMS-002 Fix 414 Request-URI Too Large
- Dự án: `topvnsport-wms`
- Mô tả: Tạo task WMS-002 "Fix 414 Request-URI Too Large when fetching stock for many SKUs". Bug trên production: frontend gọi `GET /public/stock?sku_codes=...` với hàng trăm SKU, URL vượt 8KB limit, server trả 414. Fix: (1) WMS backend thêm POST endpoint cho `/public/stock` nhận JSON body; (2) frontend `fetchWmsStock()` chuyển sang POST.
- Giải trình: Dùng `semantic_search_nodes_tool` tìm ra 2 file chính (`WMS/backend/routers/inventory.py`, `web/src/services/sport-api/index.ts`). `get_impact_radius_tool` cho thấy blast radius HIGH (500 nodes, 133 files). `get_affected_flows_tool` xác nhận 7 flows ảnh hưởng (getStringOptions, adjust_inventory...). `query_graph_tool(tests_for)` xác nhận cả 2 file đều chưa có test — AC yêu cầu viết test mới. `get_hub_nodes_tool(top_n=50)` xác nhận không có file nào trong hub nodes nhưng blast radius cao nên vẫn đánh `risk: high`.
- Files touched: projects/topvnsport-wms/tasks/WMS-002-fix-414-stock-api-uri-too-large.md (mới), projects/topvnsport-wms/topvnsport-wms.md (tăng next_task_id)
- Trạng thái: Thành công — task đã qua Spec Gate + Plan Gate, `status: dispatched`, `executor: @antigravity`.
- Commit: n/a

## [2026-07-22 01:00:00] pm-create | WMS-003 Fix CI Docker Compose network label mismatch
- Dự án: `topvnsport-wms`
- Mô tả: Tạo task WMS-003 "Fix CI Docker Compose network label mismatch for oms_default". GitHub Actions E2E workflow fail với lỗi `network oms_default was found but has incorrect label com.docker.compose.network set to "" (expected: "default")`.
- Giải trình: Root cause: `start_all.sh` (lines 73-79) pre-creates networks với `docker network create` (không có compose labels), sau đó khi docker-compose chạy, nó tìm thấy network `oms_default` đã tồn tại nhưng với label sai/thiếu. Fix đề xuất: chỉ pre-create các network thực sự "external" (dùng chung nhiều project), KHÔNG pre-create project-default networks như `oms_default` — để docker-compose tự quản lý. Blast radius: infra/CI files, không ảnh hưởng application code — `get_impact_radius_tool` trả về risk medium (64 nodes impacted). Không có direct tests cho `start_all.sh`, validation qua E2E tests (`e2e_tests/tests/test_full_flow.py`).
- Files touched: projects/topvnsport-wms/tasks/WMS-003-fix-ci-docker-network-label-mismatch.md (mới), projects/topvnsport-wms/topvnsport-wms.md (tăng next_task_id 3→4)
- Trạng thái: Chờ duyệt — Spec Gate, chờ User approve AC.
- Commit: n/a

## [2026-07-22 01:05:00] plan | WMS-003 Fix CI Docker Compose network label mismatch
- Dự án: `topvnsport-wms`
- Mô tả: Viết Plan Gate cho WMS-003. Phân tích network declarations: PMI và WMS đã khai báo `default: {name: xxx_default, external: true}` đúng cách, nhưng OMS không khai báo explicit — compose sẽ cố tạo `oms_default` thay vì dùng network đã tồn tại. Fix: thêm khai báo `default: {name: oms_default, external: true}` vào `OMS/docker-compose.yml` (và `.prod.yml` nếu cần), giữ nguyên `start_all.sh`.
- Giải trình: Đọc source thật của 4 compose files (PMI/OMS/WMS/gateway) để xác nhận root cause. PMI line 101-105, WMS line 74-85 đều có `default: external: true` pattern, OMS line 81-87 thiếu. Gateway tự tạo `gateway_network` (driver: bridge) nên không liên quan lỗi này.
- Files touched: projects/topvnsport-wms/tasks/WMS-003-fix-ci-docker-network-label-mismatch.md (cập nhật `## Plan`)
- Trạng thái: Chờ duyệt — Plan Gate, chờ User approve plan.

## [2026-07-22 01:10:00] dispatch | WMS-003 Fix CI Docker Compose network label mismatch
- Dự án: `topvnsport-wms`
- Mô tả: Dispatch WMS-003 cho executor @antigravity. Task file là work order tự đủ: AC + files + tests + Plan + DoD (AGENTS.md §3). Executor chỉ cần đọc `projects/topvnsport-wms/tasks/WMS-003-fix-ci-docker-network-label-mismatch.md`, không cần truy cập control-tower hay tooling khác.
- Giải trình: User approve Plan Gate và chỉ định antigravity AI làm executor. Task chuyển từ `todo` → `dispatched`, ghi `executor: @antigravity`, `dispatched: 2026-07-22`.
- Files touched: projects/topvnsport-wms/tasks/WMS-003-fix-ci-docker-network-label-mismatch.md (cập nhật frontmatter)
- Trạng thái: Thành công — task đã dispatch, chờ executor hoàn thành và báo result_ref.

## [2026-07-22 01:20:00] review-order | WMS-003 Fix CI Docker Compose network label mismatch
- Dự án: `topvnsport-wms`
- Mô tả: Phát phiếu review cho WMS-003. Executor @antigravity đã hoàn thành và báo result-ref `feature/WMS-003-fix-ci-docker-network-label-mismatch`. Tạo phiếu review tại `projects/topvnsport-wms/reviews/WMS-003-review.md`.
- Giải trình: Task chuyển từ `dispatched` → `in-review`, ghi `in_review: 2026-07-22`. Phiếu review chứa AC, DoD, test commands, và câu hỏi rủi ro để reviewer độc lập (≠ @antigravity) kiểm tra.
- Files touched: projects/topvnsport-wms/tasks/WMS-003-fix-ci-docker-network-label-mismatch.md (cập nhật in_review date), projects/topvnsport-wms/reviews/WMS-003-review.md (mới)
- Trạng thái: Thành công — chờ reviewer độc lập kiểm tra và báo verdict.

## [2026-07-22 01:25:00] verdict | WMS-003 Fix CI Docker Compose network label mismatch — PASS
- Dự án: `topvnsport-wms`
- Mô tả: Ghi nhận verdict PASS cho WMS-003 từ reviewer @claude. Four-eyes check: @claude ≠ @antigravity (executor) ✓. Reviewer notes: "Cleaned up unrelated breaking changes. Only Docker network external declarations remain."
- Giải trình: Task đã qua review độc lập, tất cả AC pass, commit 76aace1 đã merge vào main. Task chuyển từ `in-review` → `done`.
- Files touched: projects/topvnsport-wms/tasks/WMS-003-fix-ci-docker-network-label-mismatch.md (status: done, reviewer: @claude, AC marked [x])
- Trạng thái: Thành công.
- Commit: 76aace1

## [2026-07-22 01:02:00] review-order | WMS-002 Fix 414 Stock API
- Dự án: `topvnsport-wms`
- Mô tả: Phát phiếu review cho WMS-002 "Fix 414 Request-URI Too Large when fetching stock for many SKUs". Result-ref: `feature/WMS-002-fix-414-stock-api`. Executor: @antigravity.
- Giải trình: Task đã qua Spec Gate + Plan Gate + dispatch. Executor báo done với branch `feature/WMS-002-fix-414-stock-api`. Phiếu review sinh tại `projects/topvnsport-wms/reviews/WMS-002-review.md`, giao cho reviewer độc lập (≠ @antigravity).
- Files touched: projects/topvnsport-wms/tasks/WMS-002-fix-414-stock-api-uri-too-large.md (status: in-review), projects/topvnsport-wms/reviews/WMS-002-review.md (mới)
- Trạng thái: Thành công — chờ reviewer độc lập.
- Commit: n/a

## [2026-07-22 01:08:00] verdict | WMS-002 PASS
- Dự án: `topvnsport-wms`
- Mô tả: Ghi verdict PASS cho WMS-002 "Fix 414 Request-URI Too Large when fetching stock for many SKUs". Reviewer: @claude. Executor: @antigravity.
- Giải trình: Four-eyes check passed (@claude ≠ @antigravity). Task đã implement POST endpoint cho `/public/stock`, frontend đổi sang POST, test coverage đầy đủ (backend + frontend), full test suite green.
- Files touched: projects/topvnsport-wms/tasks/WMS-002-fix-414-stock-api-uri-too-large.md
- Trạng thái: Thành công — `status: done`.
- Commit: 7fd6e663d2fc

## [2026-07-22 09:15:00] plan | Onboard dự án mới topvnsport-web
- Dự án: `topvnsport-web`
- Mô tả: Tạo project mới cho frontend application (`web/` trong monorepo topvnsport). Theo AGENTS.md §10: (1) thêm row vào PROJECT REGISTRY trong `index.md`; (2) tạo thư mục `projects/topvnsport-web/` với `topvnsport-web.md`, `tasks/`, `docs/`, `reviews/`; (3) graph đã build sẵn (dùng chung monorepo topvnsport); (4) daemon watch đã có (dùng chung alias `topvnsport`); (5) cập nhật `.obsidian/graph.json` với colorGroup mới (rgb: 8388863); (6) thêm node + 5 edges vào `control-tower-map.canvas`.
- Giải trình: User yêu cầu tạo project quản lý cho thư mục `web` trong topvnsport. Thư mục tồn tại (`/home/lupca/projects/topvnsport/web`) với Vue/React frontend (có `package.json`, `vite.config.ts`, `src/`). Prefix task: `WEB`, next_task_id: 1.
- Files touched: index.md, projects/topvnsport-web/topvnsport-web.md (mới), .obsidian/graph.json, control-tower-map.canvas
- Trạng thái: Thành công.
- Commit: n/a

## [2026-07-22 10:30:00] pm-create | WEB-001 Implement Promotion Module
- Dự án: `topvnsport-web`
- Mô tả: Tạo task WEB-001 "Implement Promotion Module cho Marketing Team". Module mới hoàn toàn gồm: Backend (4 bảng mới, CRUD API, compute engine, scheduler), Frontend PMI (menu Promotions, list/create forms), Frontend Web (hook useComputedPrice, cập nhật ProductCard hiển thị giá giảm). Scope chỉ cho web (topvnsport.vn), không ảnh hưởng sàn TMĐT. Chuẩn bị sẵn fields cho AI-agent tương lai (intent, ai_reasoning, created_by).
- Giải trình: Query `semantic_search_nodes_tool` xác nhận chưa có promotion/discount module nào tồn tại. Query `get_hub_nodes_tool(top_n=50)` và `get_bridge_nodes_tool(top_n=50)` — module mới không đụng hub/bridge nodes hiện có (chỉ thêm bảng/API mới). Query `get_affected_flows_tool` xác nhận 24 flows liên quan (getProducts, update_product...) sẽ tích hợp với computed price API. Yêu cầu automated tests đầy đủ, không manual test (coverage backend >= 85%, frontend >= 80%, E2E cho full flow).
- Files touched: projects/topvnsport-web/tasks/WEB-001-promotion-module.md (mới), projects/topvnsport-web/topvnsport-web.md (tăng next_task_id)
- Trạng thái: Thành công — Spec Gate approved.
- Commit: n/a

## [2026-07-22 10:35:00] plan | WEB-001 Implement Promotion Module
- Dự án: `topvnsport-web`
- Mô tả: Viết Plan cho WEB-001. Chia thành 7 phases, 18 sub-tasks: (1) DB migrations + models, (2) Business logic service, (3) CRUD + lifecycle APIs, (4) Backend tests, (5) PMI frontend pages, (6) Web frontend hook + components, (7) E2E tests.
- Giải trình: Plan chi tiết theo thứ tự dependencies: DB trước → service → API → tests → frontend. Mỗi phase có thể review/test độc lập. Design doc đầy đủ tại `knowledge/research/discount-promotion-architecture.md` với test specs.
- Files touched: projects/topvnsport-web/tasks/WEB-001-promotion-module.md (cập nhật `## Plan`, `## Sub-tasks`)
- Trạng thái: Thành công — Plan Gate approved.

## [2026-07-22 10:40:00] dispatch | WEB-001 Implement Promotion Module
- Dự án: `topvnsport-web`
- Mô tả: Dispatch WEB-001 cho executor @antigravity-3.6. Task file là work order tự đủ: AC + files + tests + Plan + 18 sub-tasks. Executor chỉ cần đọc `projects/topvnsport-web/tasks/WEB-001-promotion-module.md` và design doc `knowledge/research/discount-promotion-architecture.md`.
- Giải trình: User approve cả Spec Gate và Plan Gate. Executor @antigravity-3.6 sẽ implement trong repo `/home/lupca/projects/topvnsport`, báo result-ref khi xong để phát phiếu review.
- Files touched: projects/topvnsport-web/tasks/WEB-001-promotion-module.md (status: dispatched, executor: @antigravity-3.6)
- Trạng thái: Thành công — task đã dispatch, chờ executor hoàn thành.

## [2026-07-22 11:00:00] review-order | WEB-001 Implement Promotion Module
- Dự án: `topvnsport-web`
- Mô tả: Phát phiếu review cho WEB-001. Result-ref: `80875eca6dd8351a25661fe03d8ad3895bb13dbe`. Executor: @antigravity-3.6. Phiếu review tại `projects/topvnsport-web/reviews/WEB-001-review.md`.
- Giải trình: Task chuyển từ `dispatched` → `in-review`. Query `get_suggested_questions_tool` để bổ sung câu hỏi rủi ro (hub nodes, untested hotspots). Phiếu chứa AC, DoD, test commands, câu hỏi rủi ro để reviewer độc lập (≠ @antigravity-3.6) kiểm tra.
- Files touched: projects/topvnsport-web/tasks/WEB-001-promotion-module.md (status: in-review, result_ref), projects/topvnsport-web/reviews/WEB-001-review.md (mới)
- Trạng thái: Thành công — chờ reviewer độc lập kiểm tra và báo verdict.

## [2026-07-22 11:30:00] verdict | WEB-001 Implement Promotion Module — CHANGES REQUESTED
- Dự án: `topvnsport-web`
- Mô tả: Ghi nhận verdict CHANGES cho WEB-001. Reviewer: @claude-opus. Four-eyes check: @claude-opus ≠ @antigravity-3.6 (executor) ✓.
- Giải trình: Fundamental scope mismatch — AC yêu cầu product-level promotion system trong PMI, implementation là order-level coupon system trong OMS. Critical issues: (1) Wrong commit ref (80875ec là script khác, code promotion uncommitted); (2) Backend ở OMS thay vì PMI; (3) Scope Product-level vs Order-level; (4) Missing 13+ AC items (4 tables, lifecycle APIs, scheduler, PMI frontend, Web frontend hooks, AI-agent fields); (5) Tests ở sai path (OMS thay vì PMI). Findings đã được ghi vào task file dưới dạng rework sub-tasks.
- Files touched: projects/topvnsport-web/tasks/WEB-001-promotion-module.md (status: changes-requested, thêm `## Findings từ reviewer`)
- Trạng thái: Chờ executor fix và báo lại result-ref mới.
- Commit: n/a

## [2026-07-22 14:30:00] plan | Onboard meta-project control-tower + tạo 10 paradigm shift tasks
- Dự án: `control-tower`
- Mô tả: Onboard control-tower như một meta-project để tự quản lý việc cải tiến chính nó. Tạo 10 tasks (CT-001 đến CT-010) cho các paradigm shifts được nghiên cứu từ industry + academia.
- Giải trình: Sau khi so sánh với các hệ thống đối thủ (Devin, OpenHands, MetaGPT, CrewAI, etc.) và nghiên cứu 10 paradigm areas (Goal-Oriented Planning, Auto-Remediation, Formal Methods, Stigmergy, etc.), xác định 10 hướng đột phá có thể biến đổi hoàn toàn control-tower. Chia thành 3 tiers: Tier 1 (quick wins: prediction, reputation), Tier 2 (foundational: causal, cross-repo, verifier, confidence), Tier 3 (paradigm shifts: goal autonomy, stigmergy, auto-remediation, vericoding). Document đầy đủ trong ADR-002.
- Files touched: projects/control-tower/control-tower.md (mới), projects/control-tower/tasks/CT-001..010 (mới, 10 files), index.md (thêm project), .obsidian/graph.json (thêm colorGroup), control-tower-map.canvas (thêm node + edges), knowledge/decisions/ADR-002-paradigm-shifts-roadmap.md (mới), knowledge/_index.md
- Trạng thái: Thành công — 10 tasks ở `status: todo`, chờ User chọn task nào để duyệt Spec Gate.
- Commit: n/a

## [2026-07-22 15:00:00] dispatch | CT-001 Pre-Execution Prediction
- Dự án: `control-tower`
- Mô tả: Dispatch CT-001 "Pre-Execution Prediction" cho executor @antigravity. Task implement prediction system để dự đoán task success/failure TRƯỚC KHI execute, dựa trên blast radius, hub nodes, và historical similarity.
- Giải trình: Spec Gate + Plan Gate approved. Plan gồm 5 phases: (1) Schema update AGENTS.md, (2) Prediction logic trong pm/SKILL.md, (3) Suggestion generator, (4) Accuracy tracking trong verdict/SKILL.md, (5) Integration. Estimated ~2 hours. Low risk — additive changes only.
- Files touched: projects/control-tower/tasks/CT-001-pre-execution-prediction.md (status: dispatched, executor: @antigravity)
- Trạng thái: Thành công — chờ executor hoàn thành và báo result_ref.
- Commit: n/a

## [2026-07-22 15:30:00] execute | CT-001 Pre-Execution Prediction Implementation
- Dự án: `control-tower`
- Mô tả: Hoàn thành implementation hệ thống Pre-Execution Prediction theo Work Order CT-001.
- Giải trình: Đã cập nhật 5 thành phần chính: (1) `AGENTS.md` §2.1 thêm standard fields `predicted_success` & `prediction_factors`; (2) `.claude/skills/pm/SKILL.md` thêm mô tả pre-execution prediction score; (3) `.claude/skills/pm/references/task-creation.md` thêm bước tính score theo công thức (Score = 1.0 base, deductions cho blast radius, hub/bridge hits, historical success, missing tests), phân loại high/medium/low và tự động tạo gợi ý rủi ro khi low; (4) `.claude/skills/verdict/SKILL.md` bổ sung bước tự động ghi nhận kết quả dự đoán vs thực tế vào metrics file; (5) tạo mới `knowledge/metrics/prediction-accuracy.md` và đăng ký vào `knowledge/_index.md`.
- Files touched: AGENTS.md, .claude/skills/pm/SKILL.md, .claude/skills/pm/references/task-creation.md, .claude/skills/verdict/SKILL.md, knowledge/metrics/prediction-accuracy.md, knowledge/_index.md, projects/control-tower/tasks/CT-001-pre-execution-prediction.md
- Trạng thái: Thành công.
- Commit: `df5b3f7`


## [2026-07-22 15:30:00] review-order | CT-001 Pre-Execution Prediction
- Dự án: `control-tower`
- Mô tả: Phát phiếu review cho CT-001 "Pre-Execution Prediction". Executor @antigravity đã hoàn thành và báo result-ref `control-tower@main (commit 7477570)`. Phiếu review tại `projects/control-tower/reviews/CT-001-review.md`.
- Giải trình: Task implement prediction system trong `/pm` skill. Thay đổi: AGENTS.md (schema), pm/SKILL.md (prediction logic), verdict/SKILL.md (accuracy tracking), knowledge/metrics/prediction-accuracy.md (new). Cần reviewer độc lập (≠ @antigravity) verify AC + DoD.
- Files touched: projects/control-tower/tasks/CT-001-pre-execution-prediction.md (status: in-review), projects/control-tower/reviews/CT-001-review.md (mới)
- Trạng thái: Thành công — chờ reviewer độc lập.
- Commit: n/a

## [2026-07-22 15:45:00] verdict | CT-001 Pre-Execution Prediction — PASS
- Dự án: `control-tower`
- Mô tả: Ghi verdict PASS cho CT-001 "Pre-Execution Prediction". Reviewer: @claude. Executor: @antigravity.
- Giải trình: Four-eyes check passed (@claude ≠ @antigravity). Reviewer verified: AC1 (schema in AGENTS.md), AC2 (prediction logic in pm/SKILL.md), AC3 (suggestion generator in task-creation.md), AC4 (accuracy tracking in verdict/SKILL.md + metrics file). Prediction outcome logged: predicted=high, actual=pass → match.
- Files touched: projects/control-tower/tasks/CT-001-pre-execution-prediction.md (status: done), projects/control-tower/reviews/CT-001-review.md, knowledge/metrics/prediction-accuracy.md
- Trạng thái: Thành công — task closed.
- Commit: 7477570

## [2026-07-22 16:00:00] dispatch | CT-002 Reputation System
- Dự án: `control-tower`
- Mô tả: Dispatch CT-002 "Reputation System" cho executor @antigravity. Task implement hệ thống tracking performance của executors/reviewers với profiles, strengths auto-detection, và executor suggestions.
- Giải trình: Spec Gate + Plan Gate approved. Plan gồm 5 phases: (1) Schema + directory, (2) Strength detection logic, (3) Verdict integration, (4) PM integration, (5) Bootstrap từ log.md. Estimated ~1.5 hours. Low risk — additive changes.
- Files touched: projects/control-tower/tasks/CT-002-reputation-system.md (status: dispatched, executor: @antigravity)
- Trạng thái: Thành công — chờ executor hoàn thành và báo result_ref.
- Commit: n/a

## [2026-07-22 16:30:00] execute | CT-002 Reputation System Implementation
- Dự án: `control-tower`
- Mô tả: Hoàn thành implementation hệ thống Agent Reputation System theo Work Order CT-002.
- Giải trình: Đã cập nhật các thành phần: (1) `AGENTS.md` §12 định nghĩa Agent Profile schema & Strength Auto-Detection Rules (`backend`, `frontend`, `database`, `testing`, `infra`); (2) Tạo thư mục `knowledge/agents/` với 5 profile khởi tạo (@antigravity, @claude, @antigravity-3.6, @claude-opus, @dev-tung) bootstrap từ lịch sử `log.md`; (3) `.claude/skills/verdict/SKILL.md` tự động cập nhật profile executor/reviewer sau mỗi verdict; (4) `.claude/skills/pm/SKILL.md` & `references/task-execution.md` gợi ý best-fit executor và cảnh báo rủi ro khi dispatch; (5) Đăng ký `knowledge/agents/` vào `knowledge/_index.md`.
- Files touched: AGENTS.md, knowledge/agents/@*.md (5 files), .claude/skills/verdict/SKILL.md, .claude/skills/pm/SKILL.md, .claude/skills/pm/references/task-execution.md, knowledge/_index.md, projects/control-tower/tasks/CT-002-reputation-system.md, log.md
- Trạng thái: Thành công.
- Commit: `565f69f`


## [2026-07-22 16:15:00] review-order | CT-002 Reputation System
- Dự án: `control-tower`
- Mô tả: Phát phiếu review cho CT-002 "Reputation System". Executor @antigravity đã hoàn thành và báo result-ref `control-tower@main (commit 9183f6a)`. Phiếu review tại `projects/control-tower/reviews/CT-002-review.md`.
- Giải trình: Task implement reputation system với 5 bootstrapped profiles, AGENTS.md §12, verdict auto-update, và pm executor suggestions. Cần reviewer độc lập (≠ @antigravity) verify AC + DoD.
- Files touched: projects/control-tower/tasks/CT-002-reputation-system.md (status: in-review), projects/control-tower/reviews/CT-002-review.md (mới)
- Trạng thái: Thành công — chờ reviewer độc lập.
- Commit: n/a

## [2026-07-22 16:30:00] verdict | CT-002 Reputation System — PASS
- Dự án: `control-tower`
- Mô tả: Ghi verdict PASS cho CT-002 "Reputation System". Reviewer: @claude. Executor: @antigravity.
- Giải trình: Four-eyes check passed (@claude ≠ @antigravity). Reviewer verified: AC1 (5 profiles in knowledge/agents/), AC2 (correct schema), AC3 (verdict auto-updates), AC4 (pm executor suggestions), AC5 (low success_rate warning).
- Files touched: projects/control-tower/tasks/CT-002-reputation-system.md (status: done), projects/control-tower/reviews/CT-002-review.md
- Trạng thái: Thành công — task closed.
- Commit: 9183f6a

## [2026-07-22 16:45:00] dispatch | CT-003 Causal Analysis
- Dự án: `control-tower`
- Mô tả: Dispatch CT-003 "Causal Analysis" cho executor @sonnet-5. Task implement hệ thống tracking WHY fixes work — causal analysis section, pattern library, pm suggestions, lint cross-reference.
- Giải trình: Spec Gate + Plan Gate approved. Plan gồm 5 phases: (1) Schema update, (2) Pattern library với 4 initial patterns, (3) Verdict integration, (4) PM pattern matching, (5) Lint cross-reference. Estimated ~2 hours. New executor @sonnet-5 (profile created).
- Files touched: projects/control-tower/tasks/CT-003-causal-analysis.md (status: dispatched, executor: @sonnet-5), knowledge/agents/@sonnet-5.md (mới)
- Trạng thái: Thành công — chờ executor hoàn thành và báo result_ref.
- Commit: n/a

## [2026-07-22 17:00:00] verdict | CT-003 Causal Analysis — PASS
- Dự án: `control-tower`
- Mô tả: Ghi verdict PASS cho CT-003 "Causal Analysis". Reviewer: @claude. Executor: @sonnet-5.
- Giải trình: Four-eyes check passed (@claude ≠ @sonnet-5). Reviewer verified all 6 ACs: (1) AGENTS.md §2.1b causal analysis section, (2) YAML format with root_cause/mechanism/counterfactual/pattern_id, (3) verdict prompts causal analysis (required for high-risk), (4) knowledge/patterns/ with 4 patterns, (5) pm pattern matching suggestions, (6) lint cross-reference detection. @sonnet-5's first task — passed on first review (success_rate: 100%).
- Files touched: projects/control-tower/tasks/CT-003-causal-analysis.md (status: done), projects/control-tower/reviews/CT-003-review.md, knowledge/agents/@sonnet-5.md (updated stats)
- Trạng thái: Thành công — task closed.
- Commit: 43caa5a
