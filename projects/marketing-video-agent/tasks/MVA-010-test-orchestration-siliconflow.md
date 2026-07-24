---
id: MVA-010
title: "Test orchestration pipeline với SiliconFlow API (Qwen3-32B)"
status: done
done: 2026-07-24
review_rounds: 1
priority: high
risk: normal
deadline: null
executor: "@claude-sonnet-high"
reviewer: "@antigravity"
result_ref: "siliconflow-orchestration-verified"
depends_on: [MVA-009]
files:
  - run.py
  - agent.py
  - config.py
  - database.py
  - prompts/agent_instructions.txt
  - tools/tts_tool.py
  - tools/video_tool.py
  - tools/edit_tool.py
  - tools/download_tool.py
flows: [main, __init__]
tests:
  - tests/test_simplified.py
dispatched: 2026-07-24
in_review: 2026-07-24
predicted_success: medium
prediction_factors:
  score: 0.6
  deductions:
    - "external API dependency — SiliconFlow có thể timeout/rate-limit (-0.2)"
    - "no existing tests for agent.py orchestration (-0.1)"
    - "hits hub nodes: create_agent (degree 11), VideoAgent.run (degree 11) (-0.1)"
confidence_interval: [0.4, 0.8]
created: 2026-07-24
updated: 2026-07-24

plan_approved: true
---

# MVA-010: Test orchestration pipeline với SiliconFlow API (Qwen3-32B)

> Dự án: [[projects/marketing-video-agent/marketing-video-agent]]

## Mục đích

Kiểm thử agent orchestration (LLM gọi tools) qua SiliconFlow API thay vì Ollama local. Chỉ test orchestration — KHÔNG refactor code, KHÔNG đụng engines, KHÔNG thay đổi bất cứ file nào.

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1:** Set env vars và chạy `python run.py "Tạo video TTS đơn giản nói Xin chào"` — ghi nhận agent có kết nối được LLM hay không (connection OK / FAIL + error message)
- [ ] **AC2:** Nếu AC1 connection OK: ghi nhận agent có nhận được plan từ LLM không (LLM response OK / FAIL)
- [ ] **AC3:** Nếu AC2 OK: ghi nhận agent có gọi được ít nhất 1 tool (TTSTool/EditTool/...) không (tool call OK / FAIL + lý do)
- [ ] **AC4:** Kiểm tra `jobs.db` — job mới được tạo với status phản ánh kết quả thực tế (completed hoặc failed + error message)
- [ ] **AC5:** Nếu SiliconFlow Qwen3-32B fail → thử lại với `zai-org/GLM-5.1` (cùng endpoint/key), ghi nhận kết quả
- [ ] **AC6:** Tổng hợp bảng kết quả: Model | Connection | LLM Response | Tool Calls | Job Status

## Verification

```bash
# Set env vars
export LLM_BASE_URL="https://api.siliconflow.com/v1"
export LLM_MODEL="Qwen/Qwen3-32B"
export LLM_API_KEY="$LLM_API_KEY"  # from .env

# AC1-AC3: Run orchestration
cd /data/projects/marketing-video-agent
.venv-light/bin/python run.py "Tạo video TTS đơn giản nói Xin chào"

# AC4: Check job DB
.venv-light/bin/python -c "from database import JobDB; db=JobDB(); print(db.get_all_jobs()[-1] if db.get_all_jobs() else 'empty')"

# AC5: Retry with GLM-5.1 if needed
export LLM_MODEL="zai-org/GLM-5.1"
.venv-light/bin/python run.py "Tạo video TTS đơn giản nói Xin chào"

# Existing tests still pass
.venv-light/bin/pytest tests/ -v
```

## Lưu ý quan trọng

- **KHÔNG thay đổi code** — đây là task kiểm thử thuần túy (test-only). Config đã hỗ trợ env vars (`LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY` trong `config.py`).
- `smolagents.OpenAIServerModel` trong `agent.py:create_agent` dùng OpenAI-compatible API — SiliconFlow cũng OpenAI-compatible nên lý thuyết sẽ hoạt động.
- Agent instructions (`prompts/agent_instructions.txt`) yêu cầu agent chọn tools theo brief — brief TTS đơn giản nên agent chỉ cần gọi TTSTool.
- Nếu tất cả đều fail → ghi nhận rõ error, KHÔNG tự fix. Kết quả test sẽ inform cho task tiếp theo (tích hợp SiliconFlow chính thức).

## Plan

1. Set 3 env vars: `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY` trỏ SiliconFlow
2. Chạy `python run.py "Tạo video TTS đơn giản nói Xin chào"` — quan sát output
3. Kiểm tra connection → LLM response → tool calls → job DB
4. Nếu Qwen3-32B fail → đổi `LLM_MODEL=zai-org/GLM-5.1`, chạy lại
5. Chạy `pytest tests/` xác nhận không regression
6. Tổng hợp bảng kết quả AC6

## Sub-tasks

- [ ] Set env vars SiliconFlow + chạy run.py với Qwen3-32B (AC1-AC3)
- [ ] Kiểm tra jobs.db (AC4)
- [ ] Retry với GLM-5.1 nếu cần (AC5)
- [ ] Tổng hợp bảng kết quả (AC6)
