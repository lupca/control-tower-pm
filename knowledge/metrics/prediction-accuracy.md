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
| **Total Predicted Tasks** | 0 |
| **Pass Count (Actual Success)** | 0 |
| **Changes Count (Actual Rework/Fail)** | 0 |
| **Overall Prediction Accuracy** | N/A |
| **High Prediction Precision** | N/A |
| **Medium Prediction Precision** | N/A |
| **Low Prediction Precision** | N/A |

---

## 3. Log History (Task Predictions vs Actual Outcomes)

| Date | Task ID | Predicted Level | Score | Factors / Deductions | Actual Verdict | Match? |
|:---|:---|:---|:---|:---|:---|:---|
<!-- Updated automatically by /verdict -->
