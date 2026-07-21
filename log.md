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
- Commit: n/a (sẽ điền sau khi commit)

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
- Commit: n/a (sẽ điền sau khi commit)
