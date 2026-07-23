---
id: MVA-006
title: "Khôi phục CapCut draft parser + skill agent"
status: todo
priority: low
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - engines/capcut/
  - tools/capcut_tool.py
flows: []
tests: []
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "code cũ có sẵn trong git history (-0.0)"
    - "Dify LLM integration có thể cần thay đổi (-0.15)"
    - "chưa có test (-0.1)"
confidence_interval: [0.6, 0.85]
created: 2026-07-23
updated: 2026-07-23
plan_approved: false
---

# MVA-006: Khôi phục CapCut draft parser + skill agent

> Dự án: [[projects/marketing-video-agent/marketing-video-agent]]

## Bối cảnh

`worker_capcut` bị xóa hoàn toàn. Gồm 2 phần: CapCutDraftParser (đọc draft JSON → Semantic Graph) và CapCutSkillAgent (dịch lệnh edit trừu tượng → tham số CapCut). Nice-to-have cho workflow học template từ CapCut.

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1:** `engines/capcut/parser.py` — đọc `draft_content.json`, trích xuất timeline/effects/text/audio thành Semantic Graph
- [ ] **AC2:** `engines/capcut/skill_agent.py` — dịch lệnh trừu tượng ("fade", "camera shake") → tham số CapCut chuẩn
- [ ] **AC3:** `tools/capcut_tool.py` — CapCutTool wrap parser + skill agent
- [ ] **AC4:** Không phụ thuộc Dify — dùng smolagents LLM hoặc heuristic fallback
- [ ] **AC5:** Test: `pytest tests/test_capcut.py` pass

## Plan

1. `git show 77bc43b^:worker_capcut/` — lấy code cũ
2. Port CapCutDraftParser → `engines/capcut/parser.py`
3. Port CapCutSkillAgent → `engines/capcut/skill_agent.py`, thay Dify bằng smolagents
4. Tạo `tools/capcut_tool.py`
5. Tạo tests
6. Đăng ký tool trong `agent.py`

## Effort ước tính: 3-5 giờ
