---
id: MVA-005
title: "Gia cố TTS (retry/fallback) + cloud video fallback"
status: todo
priority: medium
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: [MVA-004]
files:
  - engines/tts.py
  - engines/text2video.py
  - config.py
flows: []
tests:
  - tests/test_simplified.py
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "cần API keys cho FPT.AI/SiliconFlow (-0.1)"
    - "retry logic cần test kỹ (-0.1)"
confidence_interval: [0.65, 0.9]
created: 2026-07-23
updated: 2026-07-23
plan_approved: false
---

# MVA-005: Gia cố TTS (retry/fallback) + cloud video fallback

> Dự án: [[projects/marketing-video-agent/marketing-video-agent]]

## Bối cảnh

Worker TTS cũ có retry 3 lần + voice fallback (HoaiMy ↔ NamMinh) khi Edge-TTS bị rate-limit. Engine mới không có, dễ crash. Thêm FPT.AI provider cho giọng Việt chất lượng cao. Text2video cũ có SiliconFlow cloud fallback khi ComfyUI local quá tải.

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1:** Edge-TTS auto-retry 3 lần khi fail
- [ ] **AC2:** Voice fallback tự động: HoaiMy fail → thử NamMinh (và ngược lại)
- [ ] **AC3:** Thêm provider FPT.AI TTS trong `engines/tts.py`
- [ ] **AC4:** `config.py` có `fptai_api_key`, `siliconflow_api_key`
- [ ] **AC5:** `engines/text2video.py` hỗ trợ `provider="siliconflow"` (Wan2.2 cloud API)
- [ ] **AC6:** Tests cho retry/fallback logic

## Plan

1. Port retry loop + voice fallback từ `git show 77bc43b^:worker_tts/engine.py`
2. Thêm FPT.AI provider (HTTP API call)
3. Thêm SiliconFlow T2V trong `engines/text2video.py`
4. Cập nhật `config.py` với API keys
5. Tạo tests

## Effort ước tính: 2-4 giờ
