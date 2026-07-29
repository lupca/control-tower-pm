---
id: CTV2-095
task_path: projects/control-tower-v2/tasks/CTV2-095-snapshot-last-tool-result-pruning.md
project: control-tower-v2
result_ref: be276d4
executor: @claude-sonnet-high
reviewer: "@claude-opus"
status: passed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-095 — Token: đưa snapshot xuống cuối prefix + prune tool result cũ khỏi replay

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-095-snapshot-last-tool-result-pruning.md`
- Result-ref: be276d4
- Executor: @claude-sonnet-high
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [ ] Thứ tự mới: `[global][project][history][snapshot][user_msg]` — history append-only nằm trong prefix ổn định
- [ ] Có test khẳng định prefix trước snapshot **không đổi** giữa hai turn khi chỉ có mutation task (không phụ thuộc mắt người đọc log)
- [ ] Chỉ replay tool result đầy đủ của N turn gần nhất (N cấu hình được); cũ hơn thay bằng 1 dòng tóm tắt giữ được ID/kết quả then chốt
- [ ] Không mất thông tin quyết định: ID task, verdict, ràng buộc vẫn còn sau khi prune
- [ ] Đo được: telemetry ghi cached vs uncached token mỗi turn, có số liệu trước/sau trong phần review

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: backend/tests/test_context_hierarchy.py, backend/tests/unit/test_context_snapshot.py, backend/tests/integration/test_chat_context.py, backend/tests/test_token_telemetry.py
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-high)

## Test gợi ý chạy trong repo code
- `backend/tests/test_context_hierarchy.py`
- `backend/tests/unit/test_context_snapshot.py`
- `backend/tests/integration/test_chat_context.py`
- `backend/tests/test_token_telemetry.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-095 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`

## Ghi chú từ điều phối — vòng 3 (không thay việc bạn tự verify)

Bạn là **reviewer thứ hai** trên task này (`rejections` = 2 → quy tắc xoay vòng). Hai vòng trước do
`@claude-opus-5-medium` review; vòng 2 đã kết luận **5/5 AC PASS** và chỉ chặn vì một finding.
Đừng chỉ xác nhận lại kết luận đó — nếu bạn thấy vấn đề ở chỗ họ cho qua, đó là lý do bạn được gọi vào.

**Phạm vi vòng 3 rất hẹp**, executor được dặn không thiết kế lại thứ đã pass:
- B-1 (blocking): gate `by_turn` theo `session_id`/`task_id` hoặc cap — trước đó nó trả một entry cho
  MỖI row `llm_usage`, trong khi `Dashboard.tsx:91` và `Tokens.tsx:26` gọi `/stats/tokens` không filter.
- NB-1: `N=0` phải TẮT pruning, nhưng `tool_turns[-0:]` trả cả list nên đang giữ toàn bộ — ngữ nghĩa ngược.
- NB-2: `turn_index` đếm theo row đã filter.

Cần soi kỹ:
1. **Bản sửa B-1 có làm hồi quy AC5 không** — AC5 đo per-turn cached/uncached; gate theo filter có thể
   làm rỗng dữ liệu ở đường gọi khác. Kiểm cả đường có filter lẫn không filter.
2. **NB-1 có test ghim hành vi `N=0` không**, hay chỉ sửa code. `N=0` là ranh giới kinh điển.
3. **Năm AC đã pass ở `eb9a8a1` có còn pass ở `be276d4` không** — vòng 3 chạm `stats.py` và
   `context_hierarchy.py`, đúng hai file của AC4/AC5.

Đừng tính vào commit này: bug orphan `compact_context` (NB-4) — reviewer vòng 2 đã chứng minh nó có ở
cả `61878d4^`, tức tiền tồn, sẽ tách task riêng. Xem `knowledge/patterns/tool-finding-misattribution.md`.

**Toolchain bắt buộc, không được skip:** `ocr` ở `/home/lupca/.local/bin/ocr` (v1.7.15), `ruff` ở
`.venv/bin/ruff` (0.16.0, không nằm trên PATH). Repo khai `ocr` trong `.claude/review-toolchain.md` nên
nó là `required: hard` — hỏng sau khi thử cài thì BLOCK + escalate, không skip rồi đi tiếp. Một lượt review
của CTV2-102 đã bị BÁC vì đúng lỗi này.
