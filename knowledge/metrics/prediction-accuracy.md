---
title: "Pre-Execution Prediction Accuracy & Metrics"
type: metric
tags: [metrics, prediction, control-tower, accuracy]
created: 2026-07-22
updated: 2026-07-24
---

# Pre-Execution Prediction Accuracy & Metrics

> Biểu đồ & Nhật ký theo dõi độ chính xác của hệ thống Pre-Execution Prediction (CT-001).

## 1. Overview & Scoring Formula

Hệ thống dự đoán khả năng hoàn thành thành công của task (`predicted_success`) trước khi dispatch, dựa trên công thức scoring:

- **Base Score**: `1.0`
- **Deductions**:
  - `blast_radius > 8 files`: `-0.3`
  - `blast_radius > 15 files`: `-0.2` (tổng cộng `-0.5`)
  - `Hits hub/bridge node`: `-0.2`
  - `Similar tasks in log.md success rate < 50%`: `-0.3`
  - `No existing tests (tests: [])`: `-0.1`

**Phân loại (Classification)**:
- `high`: Score >= 0.7 (Kì vọng pass cao)
- `medium`: 0.4 <= Score < 0.7 (Rủi ro trung bình)
- `low`: Score < 0.4 (Rủi ro cao, đề xuất split/enrich)

**Quy tắc đánh giá In-Interval (`In Interval?`)**:
- Cột `In Interval?` được tính độc lập với `Match?` dựa trên `confidence_interval: [lo, hi]` từ frontmatter của task.
- Quy đổi outcome thực tế từ verdict: `pass` → `outcome = 1.0`, `changes` → `outcome = 0.0`.
- Đánh giá: `✅` nếu `lo <= outcome <= hi`, `❌` nếu nằm ngoài khoảng, `—` nếu task không khai báo `confidence_interval`.

---

## 2. Summary Statistics

| Metric | Value |
|:---|:---|
| **Total Predicted Tasks** | 13 |
| **Pass Count (Actual Success)** | 11 |
| **Changes Count (Actual Rework/Fail)** | 2 |
| **Overall Prediction Accuracy** | 100% (13/13) |
| **High Prediction Precision** | 100% (10/10) |
| **Medium Prediction Precision** | 100% (1/1) |
| **Low Prediction Precision** | 100% (2/2) |

---

## 3. Log History (Task Predictions vs Actual Outcomes)

`Confidence Interval` / `In Interval?` columns added per `AGENTS.md` §16.4 (CT-006, Confidence Calibration) — populated only for tasks that recorded a `confidence_interval:` at Spec Gate; older rows leave them blank rather than backfilled.

| Date | Task ID | Predicted Level | Score | Factors / Deductions | Confidence Interval | Actual Verdict | Match? | In Interval? |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| 2026-07-22 | CT-001 | high | 0.9 | blast_radius: 3 (-0.0), hub_bridge: false (-0.0), no_tests: true (-0.1) | — | pass | ✅ | — |
| 2026-07-22 | MVA-001 | low | 0.2 | blast_radius: 168 (-0.5), hub_bridge: true (-0.2), no_tests: false (-0.1) | [0.1, 0.4] | changes | ✅ | ✅ |
| 2026-07-24 | MVA-002 | high | 0.8 | code cũ còn trong git history, chỉ cần port (-0.0), không chạm hub node nào (-0.0), chưa có test cho module mới (-0.2); note: text2img restore — scope nhỏ, plan rõ | [0.7, 0.9] | pass | ✅ | ✅ |
| 2026-07-24 | MVA-003 | medium | 0.5 | scope lớn: toàn bộ slideshow_engine (audio_sync, hook_outro, visuals, pipeline) (-0.3), phụ thuộc MVA-002 (cần gen ảnh) (-0.1), chưa có test (-0.1); note: under-estimated — plan rõ, executor mạnh | [0.3, 0.6] | pass | ✅ | ✅ |
| 2026-07-24 | MVA-004 | high | 0.75 | nhiều fix nhỏ phân tán (-0.15), MoviePy v2 migration cần cẩn thận (-0.1); note: most ACs already done by MVA-008, only 1 remaining bug | [0.6, 0.85] | pass | ✅ | ✅ |
| 2026-07-24 | CT-023 | high | 0.9 | no_tests: true (-0.1) | — | pass | ✅ | — |
| 2026-07-24 | CT-024 | high | 0.8 | code (không chỉ markdown) nhưng khu trú 1 file script (-0.1), no_tests: meta-project, chỉ validate bằng sandbox thủ công (-0.1); note: pass nhưng sau 3 round (2 reject) — predicted high hơi lạc quan, rework nhiều | [0.7, 0.9] | pass | ✅ | ❌ |
| 2026-07-24 | CT-026 | high | 0.8 | code khu trú 1 script, đã có test harness sẵn (CT-024) (-0.1), no_tests suite CI, chỉ chạy tay/sandbox (-0.1) | [0.7, 0.9] | pass | ✅ | ❌ |
| 2026-07-24 | CT-025 | high | 0.9 | no_tests: meta-project, markdown files only (-0.1), blast_radius: 8 files (2 new) — at limit, coherent single architecture, no split (-0.0) | [0.75, 0.95] | pass | ✅ | ❌ |
| 2026-07-24 | CT-027 | high | 0.8 | refactor thuần, có test harness sẵn (-0.1), đụng ct-verdict-apply.py — script mutate state thật, cần cẩn thận (-0.1) | [0.7, 0.9] | pass | ✅ | ❌ |
| 2026-07-25 | PMI-011 | low | 0.3 | blast_radius: 104 files impacted, >15 (-0.5 cumulative), hits hub/bridge node: calculate_discount (hub+bridge), eval_variant_promotion_match (hub) (-0.2) | — | changes | ✅ | — |
| 2026-07-25 | CT-029 | high | 1.0 | — | — | pass | ✅ | — |
| 2026-07-25 | CT-028 | high | 0.75 | 2 script mới + sửa 2 skill + ADR — blast rộng hơn CT-027 (-0.15), no CI, chỉ sandbox (-0.1) | [0.65, 0.85] | pass | ✅ | ❌ |
