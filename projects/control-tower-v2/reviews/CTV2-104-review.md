---
id: CTV2-104
task_path: projects/control-tower-v2/tasks/CTV2-104-compact-context-orphan-tool-calls.md
project: control-tower-v2
result_ref: 0469528
executor: @claude-sonnet-medium
reviewer: @claude-opus
status: closed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-104 — compact_context sinh orphan assistant tool_calls (bug tiền tồn, tách từ NB-4 của CTV2-095)

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-104-compact-context-orphan-tool-calls.md`
- Result-ref: 0469528
- Executor: @claude-sonnet-medium
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [x] Tái hiện được lỗi trên commit **trước** CTV2-095 (`61878d4^`) và ghi lại chuỗi tái hiện vào task — xác nhận nó là tiền tồn, không phải hồi quy
- [x] Sau khi `compact_context` cắt/tóm tắt history, **không** còn assistant message nào mang `tool_calls` mà thiếu `tool` message tương ứng theo từng `tool_call_id`
- [x] Test dựng history có **ít nhất 2 cặp** assistant `tool_calls` + `tool` result, ép chạy qua ngưỡng compaction, rồi render qua `OpenAIAdapter` và assert đúng bất biến pairing của OpenAI — không chỉ assert số lượng message
- [x] Test phải **đỏ** khi revert bản sửa (chứng minh không rỗng nghĩa — xem [[vacuous-acceptance-test]])
- [x] Không phá bất biến của CTV2-095: prefix trước snapshot vẫn ổn định, thông tin quyết định (task ID, verdict, ràng buộc) vẫn sống sót qua pruning

### AC1 — chuỗi tái hiện trên `61878d4^` (commit `e24561e`, tiền CTV2-095)

`git show e24561e:backend/app/services/context_hierarchy.py` cho thấy `compact_context` tại thời điểm đó chỉ cắt suffix thô, không có logic bảo vệ cặp tool call/result:

```python
kept = raw_msgs[-10:] if len(raw_msgs) > 10 else raw_msgs
```

Chuỗi tái hiện (đã chạy thủ công bằng cách dựng `ContextHierarchy` từ mã nguồn tại `e24561e`):

1. Dựng `session.messages` với >10 message, trong đó một assistant message mang `tool_calls=[{"id": "c1", ...}]` nằm ở vị trí index sao cho `-10:` slice giữ lại `tool` message (`tool_call_id="c1"`) nhưng cắt bỏ chính assistant message đó (hoặc ngược lại).
2. Gọi `hierarchy.compact_context(session, threshold=0)`.
3. `session.messages` sau compaction chứa một `tool` message với `tool_call_id="c1"` không có assistant message tương ứng mang `tool_calls` cùng id (hoặc một assistant `tool_calls` không có `tool` message trả lời) — orphan.
4. Render qua `OpenAIAdapter.render_messages` rồi gửi cho provider OpenAI-compatible → 400 vì vi phạm bất biến pairing `tool_call_id`.

Kết luận: bug có thật và tồn tại từ trước `eb9a8a1` (CTV2-095) — không phải hồi quy do CTV2-095 gây ra. Bản sửa ở `context_hierarchy.py::compact_context` hiện tại (boundary expansion + `drop_orphan_tool_pairs`) khắc phục bằng cách mở rộng điểm cắt để không bao giờ tách một cặp, rồi sanitize phần còn lại.

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: backend/tests/test_command_router.py, backend/tests/test_context_hierarchy.py, backend/tests/integration/test_chat_context.py
- [x] Không regression (test khác trong module vẫn xanh)
- [x] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-medium)

## Test gợi ý chạy trong repo code
- `backend/tests/test_command_router.py`
- `backend/tests/test_context_hierarchy.py`
- `backend/tests/integration/test_chat_context.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-104 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`

---

## Verdict

**PASS** — 2026-07-27

All ACs verified:
- AC1: Repro documented, confirms bug existed at `e24561e` (pre-CTV2-095)
- AC2: `drop_orphan_tool_pairs()` sanitizes after compaction
- AC3: Test uses 2 tool call pairs, validates through `OpenAIAdapter`, asserts exact id matching
- AC4: `test_context_budget_does_not_reorphan_tool_call_pairs` and summary count assertion fail without fix
- AC5: Decision fields (`CTV2-095`, `CTV2-104`) survive pruning

Tests: 68 passed (test_command_router, test_context_hierarchy, test_chat_context, test_coordinator)

Reviewer: @claude-opus
