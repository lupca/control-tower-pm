---
id: CTV2-096
task_path: projects/control-tower-v2/tasks/CTV2-096-llm-compaction-token-threshold.md
project: control-tower-v2
result_ref: 4248dce
executor: "@gpt-5.6-luna"
reviewer: "@gemini-2.5-pro"
status: passed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-096 — compact_context: tóm tắt thật bằng LLM rẻ, kích hoạt theo ngưỡng token

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-096-llm-compaction-token-threshold.md`
- Result-ref: 4248dce
- Executor: @gpt-5.6-luna
- Reviewer: @gemini-2.5-pro
- Ngày phát phiếu: 2026-07-27
- Trạng thái: **passed** (Verdict: `pass`)

## Acceptance Criteria cần verify

- [x] Ngưỡng kích hoạt tính theo **token** (tỉ lệ context window của model đang dùng), không theo số message
  - *Đã kiểm tra*: `compact_context` tính `threshold_tokens` theo `settings.COMPACTION_THRESHOLD_RATIO` (default 0.75) nhân với context window của model active (qua `context_window_for_model(model)`). `CoordinatorService` tự động truyền model và context window tương ứng mỗi turn.
- [x] Tóm tắt sinh bằng LLM model rẻ, giữ nguyên: quyết định đã chốt, task ID, result_ref, ràng buộc/AC đã thống nhất
  - *Đã kiểm tra*: Cấu hình `COMPACTION_MODEL` mặc định dùng `"moonshotai/Kimi-K2-Instruct"`. Prompt yêu cầu bảo lưu chính xác mọi confirmed decisions, task IDs, result_ref values, verdicts, AC và constraints.
- [x] Nếu LLM tóm tắt lỗi → giữ nguyên history, không cắt cụt mù (fail-safe nghiêng về giữ thông tin)
  - *Đã kiểm tra*: Khối `try/except` bắt ngoại lệ khi gọi `summarizer`; nếu bị exception hoặc kết quả trả về rỗng/không phải chuỗi hợp lệ/chứa placeholder, `compact_context` lập tức log warning và trả `False` mà không thay đổi `session.messages`.
- [x] Có test kiểm chứng thông tin then chốt (task ID + verdict) vẫn truy xuất được sau compaction
  - *Đã kiểm tra*: `test_context_compaction_uses_token_window_and_llm_summary` và `test_compact_command_via_router` trong `backend/tests/test_context_hierarchy.py` khẳng định summary chứa `CTV2-096` và verdict/result_ref sau khi compaction.
- [x] Không phá prefix cache của CTV2-095: compaction viết lại prefix một lần, không mỗi turn
  - *Đã kiểm tra*: `compact_context` kiểm tra sự tồn tại của message có ID `msg-compact-{session.id}`; nếu đã có trong `raw_msgs`, trả về `False` ngay từ đầu turn để giữ ổn định prefix cache.

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: `backend/tests/test_context_hierarchy.py`, `backend/tests/test_command_router.py`, `backend/tests/test_token_telemetry.py` (62/62 PASSED)
- [x] Không regression (module tests xanh 100%)
- [x] Reviewer khác executor (xác nhận reviewer @gemini-2.5-pro ≠ executor @gpt-5.6-luna)

## Review Toolchain

1. **OCR Review Tool**:
   - Chạy command: `/home/lupca/.local/bin/ocr review --commit 4248dce --format json`
   - Kịch bản: Tự động phân tích diff của commit `4248dce`. Trả về status `completed_with_errors` (do warnings 4249 trên siliconflow endpoint phụ), các khuyến nghị về maintainability đều ở mức low/medium (như substring matching trong `context_window_for_model`), không có lỗi blocking.
2. **Linter**:
   - `ruff check`: Không có lỗi linter mới đối với các file đã chỉnh sửa (`backend/app/services/context_hierarchy.py`, `backend/app/core/compression.py`, `backend/app/core/config.py`, `backend/app/services/command_router.py`, `backend/tests/test_context_hierarchy.py`).

## Test Execution Results

- Command: `.venv/bin/pytest backend/tests/test_context_hierarchy.py backend/tests/test_command_router.py backend/tests/test_token_telemetry.py -v`
- Result: **62 passed, 0 failed in 1.19s**

## Trả kết quả

`/verdict CTV2-096 pass --reviewer @gemini-2.5-pro --commit 4248dce --notes "Tất cả 5 AC pass 100%. Ngưỡng compaction theo token window ratio, fail-safe giữ nguyên history khi LLM tóm tắt lỗi, không tái sinh summary làm phá cache."`
