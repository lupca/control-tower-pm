---
id: CTV2-068
title: "Research: OCR Integration Design for LangGraph Gates"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: medium
risk: normal
deadline: null
executor: "@claude-opus"
reviewer: "@antigravity"
result_ref: "docs/design/ocr-integration.md"
depends_on: []
files: []
flows: []
tests: []
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "research task, no code changes (-0.0)"
    - "clear V1 reference available (-0.1)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-068: Research: OCR Integration Design for LangGraph Gates

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)
- [x] Xác nhận V1 OCR usage: PM pre-scan step 8.5 + Review toolchain (từ tool-registry.md)
- [x] Đánh giá đề xuất V2: review_order_gate (chính) + spec_gate (optional pre-scan)
- [x] Output design doc với: integration points, API design, preflight logic
- [x] Recommendation: PROCEED / NEEDS CHANGES với rationale

## Verification
- Design doc chứa đầy đủ 4 mục trong AC
- V1 reference có link/quote từ tool-registry.md và AGENTS-REFERENCE.md
- V2 proposal có mapping rõ ràng từ V1 concepts

## Context từ User

**V1 OCR Usage (từ tool-registry.md):**
1. PM Agent: pre-scan step 8.5 (quét lỗi trước khi lên kế hoạch)
2. Review Agent: review toolchain (soi lỗi ở khâu cuối)

**V2 Proposed Integration:**
1. Chính: `review_order_gate` - chuẩn bị Review, đính kèm findings vào Review Sheet
2. Optional: `spec_gate`/`plan_gate` - pre-scan sớm để ép AI đưa việc sửa lỗi vào Plan

## Plan

### Phase 1: V1 Analysis
1. Read tool-registry.md → confirm OCR `used_by: pm (step 8.5), review (toolchain)`
2. Read AGENTS-REFERENCE.md §8 → understand preflight algorithm
3. Read pm/references/task-creation.md step 8.5 → understand pre-scan flow

### Phase 2: V2 Mapping
4. Map V1 PM pre-scan → V2 `spec_gate` or `plan_gate` (optional, soft-required)
5. Map V1 Review toolchain → V2 `review_order_gate` (mandatory, hard-required)
6. Identify differences: V1 spawns CLI, V2 calls Python service

### Phase 3: Design
7. Design `OcrService` class with async `scan()` method
8. Design preflight logic (health_check, install, fallback)
9. Design integration points in LangGraph nodes

### Phase 4: Output
10. Write design doc with: architecture, API, integration code samples

## Sub-tasks
- [x] Read V1 tool-registry.md + AGENTS-REFERENCE.md §8 để xác nhận OCR usage
- [x] Map V1 concepts → V2 LangGraph gates
- [x] Design OCR service wrapper cho V2 (async, preflight logic)
- [x] Write design doc với integration proposal
