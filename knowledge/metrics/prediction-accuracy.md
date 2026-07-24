---
title: "Pre-Execution Prediction Accuracy & Metrics"
type: metric
tags: [metrics, prediction, control-tower, accuracy]
created: 2026-07-22
updated: 2026-07-22
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

---

## 2. Summary Statistics

| Metric | Value |
|:---|:---|
| **Total Predicted Tasks** | 2 |
| **Pass Count (Actual Success)** | 1 |
| **Changes Count (Actual Rework/Fail)** | 1 |
| **Overall Prediction Accuracy** | 100% (2/2) |
| **High Prediction Precision** | 100% (1/1) |
| **Medium Prediction Precision** | N/A |
| **Low Prediction Precision** | 100% (1/1) |

---

## 3. Log History (Task Predictions vs Actual Outcomes)

`Confidence Interval` / `In Interval?` columns added per `AGENTS.md` §16.4 (CT-006, Confidence Calibration) — populated only for tasks that recorded a `confidence_interval:` at Spec Gate; older rows leave them blank rather than backfilled.

| Date | Task ID | Predicted Level | Score | Factors / Deductions | Confidence Interval | Actual Verdict | Match? | In Interval? |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| 2026-07-22 | CT-001 | high | 0.9 | blast_radius: 3 (-0.0), hub_bridge: false (-0.0), no_tests: true (-0.1) | — | pass | ✅ | — |
| 2026-07-22 | MVA-001 | low | 0.2 | blast_radius: 168 (-0.5), hub_bridge: true (-0.2), no_tests: false (-0.1) | [0.1, 0.4] | changes | ✅ | ✅ |
<!-- Updated automatically by /verdict -->
| MVA-003 | medium (0.5) | pass (round 1) | ✅ under-estimated | slideshow restore — scope lớn nhưng plan rõ, executor mạnh |
| MVA-002 | high (0.8) | pass (round 1) | ✅ accurate | text2img restore — scope nhỏ, plan rõ |
| MVA-004 | high (0.75) | pass (round 1) | ✅ accurate | most ACs already done by MVA-008, only 1 remaining bug |
