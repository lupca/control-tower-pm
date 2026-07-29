---
id: CTV2-104
title: "compact_context sinh orphan assistant tool_calls (bug tiền tồn, tách từ NB-4 của CTV2-095)"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "0469528"
depends_on: []
files:
  - backend/app/services/command_router.py
  - backend/app/services/context_hierarchy.py
flows: []
tests:
  - backend/tests/test_command_router.py
  - backend/tests/test_context_hierarchy.py
  - backend/tests/integration/test_chat_context.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "hub node: execute_tool (36), CoordinatorService (43) (-0.2)"
    - "phạm vi hẹp, đã có repro rõ ràng từ reviewer (-0.05)"
created: 2026-07-27
updated: 2026-07-27
rejections: 1
---

# CTV2-104: Orphan `tool_calls` do `compact_context` — bug tiền tồn

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Tách từ finding **NB-4** của [[CTV2-095-snapshot-last-tool-result-pruning]]

## Bối cảnh — vì sao đây là task riêng

Baseline `/code-review` báo rằng slice `compact_context` **mới** gây lỗi provider 400 và quy cho commit `eb9a8a1` của CTV2-095. Reviewer `@claude-opus-5-medium` không chấp nhận mà tự kiểm chứng: orphan xuất hiện ở **cả `eb9a8a1` lẫn `61878d4^`** — tức **có trước khi CTV2-095 bắt đầu**.

Đúng biến thể nguy hiểm của [[tool-finding-misattribution]]: khiếm khuyết vòng 1 của CTV2-095 (làm mất `tool_call_id` khiến `OpenAIAdapter` hạ mọi summary xuống `role="user"`) đã **vô tình che** bug này. Vòng 2 sửa đúng — giữ lại `role="tool"` — thì bug tiền tồn lộ ra, và tool quy nhầm cho chính bản sửa.

Vì vậy nó **không** được tính vào verdict của CTV2-095, nhưng cũng **không** được bỏ qua.

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

## Verification

- `pytest backend/tests/test_command_router.py backend/tests/test_context_hierarchy.py backend/tests/integration/test_chat_context.py -v` → xanh
- `pytest backend/tests/ -v` → không hồi quy
- Test tái hiện: dựng session vượt ngưỡng compaction có ≥2 cặp tool call → render qua `OpenAIAdapter` → 0 orphan
- Đối chứng: cùng test đó chạy trên `61878d4^` → phải ĐỎ (chứng minh bug tiền tồn có thật)

## Plan

*(điền ở Plan Gate)*

## Sub-tasks

- [x] Tái hiện + ghi chuỗi tái hiện trên commit tiền CTV2-095
- [x] Sửa `compact_context` giữ nguyên cặp assistant↔tool
- [x] Test pairing qua adapter, có ≥2 cặp tool call
- [x] Kiểm test đỏ khi revert
- [x] Kiểm không phá bất biến CTV2-095

## Findings từ reviewer
- [x] P1: budget_messages can re-orphan tool pairs — fixed: extracted `drop_orphan_tool_pairs()` (shared with `compact_context`) and applied it to `CoordinatorService.budget_messages`'s final prefix+recent selection, since token budgeting can drop the assistant `tool_calls` side while keeping a smaller/newer `tool` result. Regression test: `test_context_budget_does_not_reorphan_tool_call_pairs` (verified red on revert).
- [x] AC1 missing repro steps in task — added under AC1 above, verified against commit `e24561e` (`61878d4^`).
- [x] summary count inaccurate after boundary expansion — fixed: the compaction summary now reports the actual post-expansion `start` index instead of the pre-expansion `len(raw_msgs) - 10` guess. Covered by the added assertion in `test_context_compaction_keeps_tool_call_pairs_through_adapter`.
