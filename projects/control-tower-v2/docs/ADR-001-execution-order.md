# ADR-001 Migration — Thứ tự thực thi CTV2-077..085

> Handoff cho session điều phối. Executor: `@claude-sonnet` · Reviewer: `@claude-opus-4.5` (đã set sẵn trong frontmatter từng task).
> Thiết kế gốc: `control-tower-v2/docs/adr/ADR-001-unified-tool-architecture.md`.

## Nguyên tắc

- Mỗi task: `/dispatch <ID>` → executor trả result-ref → `/review-order <ID> --ref <ref>` → reviewer chạy review ngoài hệ → `/verdict <ID> pass --reviewer @claude-opus-4.5`.
- Chỉ sang wave kế khi mọi task wave trước có verdict `pass` (tránh executor build trên code chưa được duyệt).
- Các task cùng wave chạy song song được (không đụng chung file).

## Thứ tự

| Wave | Task | Lý do thứ tự |
|---|---|---|
| **1** | **CTV2-077** (Tool Registry SSoT) ∥ **CTV2-078** (Cache-aware context layout) | Không phụ thuộc gì; file không giao nhau (077: registry/command_router/chat.py — 078: context_hierarchy/coordinator.py) |
| **2** | **CTV2-079** (xoá legacy adapters) ∥ **CTV2-080** (System State + query_db) ∥ **CTV2-085** (UI tool palette) | Đều chỉ cần 077. 079 sửa coordinator.py, 080 sửa graph/context.py, 085 sửa frontend — không giao nhau |
| **3** | **CTV2-081** (load_tools meta-tool) | Về dependency chỉ cần 077, nhưng sửa tool-execution loop trong coordinator.py — chạy SAU 079 để tránh conflict trên cùng file |
| **4** | **CTV2-082** (Entity CRUD tools + gate wiring) | Cần 080 (query_db pattern) + 081 (group/deferred). Risk `high` — review kỹ nhất: guard api_key, không hard delete, gate admin |
| **5** | **CTV2-083** (Settings KV) ∥ **CTV2-084** (FastMCP chat-CLI) | Đều chỉ cần 082; file không giao nhau. 083 có migration → bắt buộc kèm downgrade (project gate) |

## Lưu ý cho reviewer/điều phối

1. **Wave 1–2 là refactor behavior-preserving** — verify chủ yếu bằng test hiện có (`test_command_router.py`, `test_context_hierarchy.py`, `test_coordinator.py`, `test_providers.py`) + test parity/prefix-stability mới.
2. **CTV2-078**: AC then chốt là prefix-stability — build_messages 2 lần với mutation ở giữa, bytes Global+Project không đổi.
3. **CTV2-082**: điểm review trọng tâm — `manage_agent` không được nhận/trả `api_key`; `manage_project` không có hard delete; mutation admin ở mode supervised phải dừng ở GateRecord pending.
4. **CTV2-084**: scope CHỈ coordinator chat CLI; `git diff backend/app/workers/agent_runner.py` phải rỗng (executor dispatch CLI không được chạm).
5. Sau khi cả 9 task pass: chạy `/report` để cập nhật tiến độ, cân nhắc archive `docs/research/tool-system-architecture.md` (đã bị ADR-001 supersede một phần).
