---
id: CTV2-100
title: "Bỏ LangGraph khỏi runtime: một FSM duy nhất là TaskOrchestrationService"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: medium
risk: normal
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@gemini-2.5-pro"
result_ref: "ed404b0"
depends_on:
  - CTV2-091
files:
  - backend/app/graph/nodes.py
  - backend/app/graph/builder.py
  - backend/app/graph/router.py
  - backend/app/graph/gates/
  - backend/app/services/context_hierarchy.py
  - backend/app/services/coordinator.py
flows: []
tests:
  - backend/tests/test_graph_nodes.py
  - backend/tests/test_graph_state.py
  - backend/tests/test_context_hierarchy.py
dispatched: 2026-07-27
in_review: 2026-07-27
completed: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "xoá code có người đọc: _graph_state_summary đang hiển thị trạng thái (-0.2)"
    - "phạm vi rõ ràng, có test bao (-0.05)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-100: Dọn hai state machine song song

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Nguồn: `docs/research/autonomous-coordination-gap-analysis.md` §2 (G10), §3.7
> **Quyết định: phương án (a) — gỡ khỏi runtime. User chốt 2026-07-27.** KHÔNG cài lại LangGraph cho chạy thật (phương án b).

`TaskOrchestrationService` là FSM authoritative (ledger, idempotency, `with_for_update`). LangGraph là FSM thứ hai, stub, `sync_to_db` chỉ `logger.info` — không ghi DB. `app/graph/gates/*` (kể cả `generate_review_sheet`) là module orphan. Giá trị LangGraph mang lại (checkpoint + resume) đã được `GateRecord` ledger phủ; giữ cả hai chỉ tạo hai nguồn sự thật.

> ⚠️ **`app/graph/` ≠ LangGraph.** Chỉ `nodes.py`, `builder.py`, `router.py`, `gates/*` là phần chết. **KHÔNG động vào** `app/graph/context.py` (context snapshot + `invalidate_context_snapshot`, được import ở 8 chỗ trong API và services) và `app/graph/state.py` (export `FourEyesViolation` dùng bởi `db/models.py:23`) — gỡ hai file này là gãy `models.py` ngay.
>
> Bằng chứng phần còn lại đã chết (đã verify 2026-07-27): `build_graph()` không có call site nào trong runtime, chỉ được export ở `app/graph/__init__.py`; `CoordinatorService.graph` không ai truyền nên luôn `None` → `_graph_state_summary` luôn trả `None`, dòng `[LangGraph State] ...` chưa từng xuất hiện thật; `sync_to_db` (`nodes.py:50`) chỉ `logger.info`.

## Tiêu chí nghiệm thu (AC)

- [x] LangGraph không còn nằm trên runtime path nào (chat, driver, API); dependency gỡ khỏi requirements nếu không còn ai dùng
- [x] `ContextHierarchy._graph_state_summary` thay bằng dữ liệu từ `TaskOrchestrationService`/`GateRecord` — UI không mất phần hiển thị trạng thái
- [x] Không xoá nhầm logic đang được dùng thật: liệt kê rõ những gì `graph/gates/*` cung cấp và ánh xạ sang service tương ứng (đặc biệt `generate_review_sheet` — nếu còn cần thì port sang CTV2-087 trước khi xoá)
- [x] Test cũ của LangGraph được gỡ hoặc chuyển thành test of service, không để test chết
- [x] `app/graph/context.py` và `app/graph/state.py` **không bị sửa/xoá**; `from app.graph.context import ...` ở 8 call site và `FourEyesViolation` trong `db/models.py` vẫn nguyên
- [x] Toàn bộ suite xanh sau khi gỡ

## Verification

- `pytest backend/tests/ -v` → xanh
- `grep -rn "langgraph" backend/app backend/requirements.txt` → 0 kết quả trên runtime path
- UI: trang task vẫn hiển thị trạng thái gate đúng

## Plan

1. Kiểm kê trước khi xoá: liệt kê mọi thứ `app/graph/*` cung cấp và ai gọi (đặc biệt `generate_review_sheet` và `_graph_state_summary`). Ghi bảng ánh xạ sang service tương ứng vào PR description.
2. Port `_graph_state_summary` sang truy vấn `TaskOrchestrationService`/`GateRecord` để UI giữ nguyên phần hiển thị trạng thái.
3. Nếu review sheet còn cần → port sang đường của CTV2-087 **trước**, rồi mới xoá module.
4. Gỡ `app/graph/nodes.py`, `builder.py`, `router.py`, `state.py`, `gates/*` khỏi runtime path; gỡ dependency `langgraph` khỏi requirements nếu không còn ai dùng.
5. Chuyển test LangGraph thành test của service hoặc xoá kèm lý do; chạy full suite.

## Sub-tasks

- [x] Kiểm kê những gì graph/* thực sự cung cấp
- [x] Port `_graph_state_summary` sang service
- [x] Gỡ module + dependency
- [x] Dọn/chuyển test
