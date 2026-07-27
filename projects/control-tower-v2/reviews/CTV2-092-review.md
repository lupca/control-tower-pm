---
id: CTV2-092
task_path: projects/control-tower-v2/tasks/CTV2-092-create-task-project-scope-id.md
project: control-tower-v2
result_ref: 49dd71a
executor: @claude-sonnet-medium
reviewer: @claude-opus
status: completed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-092 — create_task: project scope thật + sinh ID an toàn + global session scope cho snapshot

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-092-create-task-project-scope-id.md`
- Result-ref: 49dd71a
- Executor: @claude-sonnet-medium
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [x] `create_task` không còn hardcode `'default'`: suy project từ session scope, hoặc từ tham số, hoặc hỏi lại user — không bao giờ ghi vào project không tồn tại
- [x] Sinh task ID không dùng `COUNT(*)`: dùng sequence/counter per project có khoá, chạy song song 20 lần → 20 ID duy nhất, không tái dùng ID đã xoá
- [x] Session `context_level='global'` vẫn có snapshot liệt kê task gần đây trên **mọi project** (không rỗng như hiện tại)
- [x] Không hồi quy cho session cấp project: vẫn scope đúng project đó

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: backend/tests/test_command_router.py, backend/tests/test_context_hierarchy.py, backend/tests/unit/test_context_snapshot.py, backend/tests/integration/test_chat_context.py
- [x] Không regression (test khác trong module vẫn xanh)
- [x] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-medium)

## Test gợi ý chạy trong repo code
- `backend/tests/test_command_router.py`
- `backend/tests/test_context_hierarchy.py`
- `backend/tests/unit/test_context_snapshot.py`
- `backend/tests/integration/test_chat_context.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-092 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`

---

## Review Notes (@claude-opus, 2026-07-27)

**Verdict: PASS**

All four acceptance criteria verified by code inspection:

| AC | Status | Evidence |
|----|--------|----------|
| No hardcoded `'default'` | ✅ | `command_router.py:384-411` — resolves `--project` → `session.project_id` → `project_required` error |
| Race-safe task IDs | ✅ | Atomic `UPDATE ... SET seq = seq + 1` (lines 413-424); 20-thread barrier test confirms no collisions or ID reuse |
| Global session snapshot | ✅ | `context.py:140-155` — shows "Recent tasks (all projects):" when `project_id` is None |
| Project scope regression | ✅ | Filter still applied when scoped; explicit regression test at `test_context_snapshot.py:107` |

The concurrent-ID test (lines 162-234) is particularly thorough: seeds and deletes RACE-001 first to catch reuse bugs, then fires 20 threads from a barrier, asserts 20 unique IDs none matching the deleted one.

Migration `017_project_task_seq.py` adds `next_task_seq` column with default 0.

No issues found. Four-eyes rule satisfied (@claude-opus ≠ @claude-sonnet-medium).
