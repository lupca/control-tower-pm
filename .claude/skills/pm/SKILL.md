---
name: pm
description: Giao task mới hoặc chia nhỏ yêu cầu mơ hồ thành task có Acceptance Criteria kiểm chứng được, dùng code-review-graph để tìm blast radius/test/rủi ro trước khi ghi vào projects/*.md, rồi dẫn qua 3 cổng HITL (Spec/Plan/Code) trước khi đóng. Kích hoạt khi user gõ /pm hoặc nói về giao/quản lý/lên kế hoạch task cho một dự án cụ thể.
argument-hint: <mô tả task> [--project <tên dự án>]
allowed-tools: Read, Edit, Write, Grep, Glob, Bash, mcp__code-review-graph__get_minimal_context_tool, mcp__code-review-graph__get_impact_radius_tool, mcp__code-review-graph__query_graph_tool, mcp__code-review-graph__semantic_search_nodes_tool, mcp__code-review-graph__get_knowledge_gaps_tool, mcp__code-review-graph__get_hub_nodes_tool, mcp__code-review-graph__get_bridge_nodes_tool, mcp__code-review-graph__get_affected_flows_tool, mcp__code-review-graph__detect_changes_tool, mcp__code-review-graph__get_architecture_overview_tool
---

## Project Manager — task có AC, gate hóa qua code-review-graph

Người dùng gọi: `/pm $ARGUMENTS`. Bạn đang chạy trong repo `control-tower`, KHÔNG phải repo đích — mọi tool graph phải kèm `repo_root` tuyệt đối.

### Bước 0 — Định vị dự án

1. Đọc `AGENTS.md` (Decision-Authority Matrix, DoD, 3 gate, cú pháp task, quy tắc graph) và `index.md` mục 2 (PROJECT REGISTRY) nếu chưa đọc trong phiên.
2. Xác định dự án đích:
   - Nếu `$ARGUMENTS` có `--project <tên>`, dùng đúng tên đó để tra bảng registry.
   - Nếu không, suy luận từ nội dung mô tả (vd "variant"/"PMI" → `topvnsport-pmi`; "đơn hàng"/"OMS" → `topvnsport-oms`). Nếu không chắc, hỏi lại User.
   - Lấy `repo_root` tuyệt đối + `Task file` từ registry. Nếu dự án chưa có trong registry, dừng lại, báo User cần onboard trước (`AGENTS.md` mục 9).

### Bước 1 — Xác định giai đoạn đang ở đâu

`/pm` phục vụ cả 3 giai đoạn của vòng đời task, tùy ngữ cảnh:

- **Yêu cầu mới / task chưa tồn tại trong `projects/*.md`** → thực hiện theo `.claude/skills/pm/references/task-creation.md` (Spec Gate). Dừng chờ duyệt sau khi viết task.
- **Task đã có, Spec Gate vừa được User duyệt** (User nói "ok", "duyệt", "đồng ý với AC này"...) → thực hiện theo `references/task-execution.md` (Plan Gate). Dừng chờ duyệt kế hoạch.
- **Plan Gate đã duyệt, code đã viết xong, cần đóng task** → thực hiện theo `references/task-finalization.md` (Code Gate + DoD). Chỉ đóng `- [x]` khi đủ điều kiện.

Không tự suy luận đã qua gate nếu User chưa xác nhận rõ ràng bằng lời — im lặng hoặc mơ hồ KHÔNG tính là duyệt.

### Lỗi thường gặp cần tránh

- Quên `repo_root` → graph tool auto-detect theo cwd của `control-tower` và trả kết quả sai/rỗng.
- Gọi `query_graph_tool` với tham số `edge` — tool thật chỉ có `pattern`/`target`, không có `edge`.
- Dùng `top_n` mặc định (10) cho `get_hub_nodes_tool`/`get_bridge_nodes_tool` — quá nhỏ so với repo lớn, khiến `⚠️high-risk` gần như không bao giờ kích hoạt. Luôn truyền `top_n=50`.
- Ghi path tuyệt đối vào `projects/*.md` thay vì path tương đối so với `repo_root`.
- Tự động nhảy qua gate mà chưa có xác nhận rõ ràng của User.
- Đóng task (`- [x]`) khi test đỏ hoặc `detect_changes_tool` báo rủi ro mới — xem `task-finalization.md`.
