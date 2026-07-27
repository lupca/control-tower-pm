---
id: CTV2-102
title: "Review result schema: /code-review ghi JSON có cấu trúc thay vì text tự do (tách từ CTV2-087)"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@claude-opus"
result_ref: "0bb2834"
depends_on: []
files:
  - backend/app/services/command_builder.py
  - backend/app/workers/agent_runner.py
  - backend/app/schemas/task.py
flows: []
tests:
  - backend/tests/unit/test_command_builder.py
  - backend/tests/unit/test_agent_runner.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "hub node: run_agent (53) (-0.2)"
    - "phạm vi hẹp, không đụng FSM (-0.05)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-102: Kết quả review là dữ liệu, không phải văn xuôi

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Tách từ CTV2-087 — `prediction_factors` của task đó chỉ ra chính parser là điểm dễ vỡ (-0.2). Gộp chung nghĩa là parser hỏng thì cả review run bị `changes` và phải làm lại cả phần đã đúng.

Đổi cách lấy kết quả: thay vì parse text tự do do `/code-review` in ra, **review run tự ghi file JSON theo schema**. Rủi ro tụt từ "parse output không kiểm soát được" xuống "đọc file đúng schema".

## Tiêu chí nghiệm thu (AC)

- [x] Schema `ReviewResult` được định nghĩa và version hoá: `{schema_version, task_id, base, head, ac_results: [{ac_index, ac_text, verdict: pass|fail, evidence}], findings: [...], tests_run, tests_passed}`
- [x] Prompt/lệnh review run yêu cầu ghi kết quả ra đường dẫn file định trước trong `repo_root` (ví dụ `.ct/review-<task_id>.json`), không phụ thuộc vào việc đọc stdout
- [x] Loader validate schema chặt; thiếu field bắt buộc hoặc sai kiểu → raise lỗi có cấu trúc, KHÔNG suy diễn giá trị mặc định
- [x] `verdict` chỉ nhận `pass|fail` — không có giá trị mơ hồ; số phần tử `ac_results` khớp số AC của task
- [x] File tạm được dọn hoặc gitignore, không làm bẩn working tree của repo đích (ảnh hưởng trực tiếp `result_ref` của CTV2-099)
- [x] Có fixture file JSON hợp lệ + vài file hỏng (thiếu field, sai kiểu, rỗng) để test loader

## Verification

- `pytest backend/tests/unit/test_command_builder.py backend/tests/unit/test_agent_runner.py -v` → xanh
- Test: load fixture hợp lệ → object đúng; load 3 fixture hỏng → 3 lỗi có cấu trúc khác nhau, không cái nào trả "pass"
- `git status` trong repo đích sau review run → không có file lạ chưa ignore

## Plan

1. Định nghĩa schema (Pydantic) + `schema_version` để sau này đổi không vỡ ngược.
2. `command_builder`: thêm chỉ dẫn ghi file JSON vào prompt review run + truyền đường dẫn đích.
3. Loader + validate ở `agent_runner`, trả lỗi có cấu trúc.
4. Dọn file tạm / thêm vào gitignore của repo đích.
5. Fixtures hợp lệ + hỏng, tests.

## Sub-tasks

- [ ] Schema + version
- [ ] Prompt/command ghi file
- [ ] Loader + validate
- [ ] Dọn file tạm
- [ ] Fixtures + tests
