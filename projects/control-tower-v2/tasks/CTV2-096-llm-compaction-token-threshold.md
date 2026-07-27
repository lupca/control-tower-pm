---
id: CTV2-096
title: "compact_context: tóm tắt thật bằng LLM rẻ, kích hoạt theo ngưỡng token"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: medium
risk: normal
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@gemini-2.5-pro"
result_ref: "4248dce"
depends_on:
  - CTV2-095
files:
  - backend/app/services/command_router.py
  - backend/app/services/context_hierarchy.py
  - backend/app/core/compression.py
flows: []
tests:
  - backend/tests/test_context_hierarchy.py
  - backend/tests/test_command_router.py
  - backend/tests/test_token_telemetry.py
dispatched: 2026-07-27
in_review: 2026-07-27
completed: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "hub node: compress_for_prompt (37) (-0.2)"
    - "không có test hiện tại cho compaction path (-0.05)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-096: Compaction thật thay cho cắt cụt

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Nguồn: `docs/research/autonomous-coordination-gap-analysis.md` §2 (G9.4), §3.6

`compact_context` hiện giữ 10 message cuối + một dòng placeholder `[Context Compaction: Summarized N previous messages]` — **không tóm tắt gì cả**. Vừa mất context (giảm chất lượng), vừa kích hoạt quá muộn (ngưỡng 50 message thay vì đếm token).

## Tiêu chí nghiệm thu (AC)

- [x] Ngưỡng kích hoạt tính theo **token** (tỉ lệ context window của model đang dùng), không theo số message
- [x] Tóm tắt sinh bằng LLM model rẻ, giữ nguyên: quyết định đã chốt, task ID, result_ref, ràng buộc/AC đã thống nhất
- [x] Nếu LLM tóm tắt lỗi → giữ nguyên history, không cắt cụt mù (fail-safe nghiêng về giữ thông tin)
- [x] Có test kiểm chứng thông tin then chốt (task ID + verdict) vẫn truy xuất được sau compaction
- [x] Không phá prefix cache của CTV2-095: compaction viết lại prefix một lần, không mỗi turn

## Verification

- `pytest backend/tests/test_context_hierarchy.py backend/tests/test_command_router.py -v` → xanh
- Test: hội thoại vượt ngưỡng token → có bản tóm tắt thật (không phải placeholder), chứa task ID đã nhắc trước đó
- Test: LLM tóm tắt raise → history nguyên vẹn

## Plan

1. Đổi trigger từ đếm message sang đếm token (dùng bộ đếm token sẵn có), ngưỡng = tỉ lệ context window của model đang dùng, cấu hình được.
2. Summarizer: gọi model rẻ với prompt yêu cầu giữ nguyên quyết định đã chốt, task ID, result_ref, AC/ràng buộc; output thay thế đoạn history cũ.
3. Fail-safe: summarizer lỗi/timeout → giữ nguyên history, log cảnh báo; tuyệt đối không cắt cụt mù như hiện tại.
4. Ghi bản tóm tắt một lần vào đầu prefix (không sinh lại mỗi turn) để không phá cache của CTV2-095.
5. Tests: vượt ngưỡng → tóm tắt thật chứa task ID đã nhắc; summarizer raise → history nguyên vẹn.

## Sub-tasks

- [x] Ngưỡng theo token
- [x] Summarizer LLM rẻ + prompt giữ quyết định/ID
- [x] Fail-safe
- [x] Tests per AC
