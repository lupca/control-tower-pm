---
id: CT-001
title: "Pre-Execution Prediction — Dự đoán task fail trước khi execute"
status: dispatched
priority: high
risk: normal
deadline: null
executor: "@antigravity"
reviewer: null
result_ref: null
depends_on: []
files:
  - .claude/skills/pm/SKILL.md
  - .claude/skills/pm/references/task-creation.md
  - log.md
flows: [pm-create, dispatch]
tests: []
dispatched: 2026-07-22
in_review: null
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "blast_radius: 3 (-0.0)"
    - "hub_bridge: false (-0.0)"
    - "no_tests: true (-0.1)"
created: 2026-07-22
updated: 2026-07-22
tier: 1
paradigm_source: "Can We Predict Before Executing ML Agents? (2025)"
---

# CT-001: Pre-Execution Prediction — Dự đoán task fail trước khi execute

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (Context)

Hiện tại: dispatch task → executor cố làm → có thể fail sau nhiều giờ effort.

Research cho thấy có thể **predict success/failure BEFORE execution** bằng cách dùng LLM như implicit world model, "compressing hours of execution into seconds of inference."

## Tiêu chí nghiệm thu (AC)

- [ ] AC1: Thêm field `predicted_success: high|medium|low` vào task frontmatter template (AGENTS.md §2.1)
- [ ] AC2: `/pm` tự động tính prediction dựa trên:
  - Complexity từ `get_impact_radius_tool` (blast radius)
  - Hub/bridge node involvement từ `get_hub_nodes_tool`
  - Historical similarity: query log.md cho tasks tương tự (same files/flows) và outcome
- [ ] AC3: Nếu `predicted_success: low`, `/pm` auto-suggest enrichments:
  - "Consider adding more context about X"
  - "Similar task PMI-003 failed due to Y — address this"
  - "Split into smaller tasks (blast radius > 8 files)"
- [ ] AC4: Track actual outcomes để improve prediction over time:
  - Sau `/verdict`, so sánh prediction vs actual
  - Log accuracy metrics trong `knowledge/metrics/prediction-accuracy.md`

## Plan

### Phase 1: Schema Update
1. **AGENTS.md §2.1** — Thêm vào Standard Task Syntax:
   ```yaml
   predicted_success: high    # high | medium | low (computed by /pm)
   prediction_factors:        # transparency - why this score?
     blast_radius: 5
     hub_node_hit: false
     similar_tasks_success_rate: 0.85
   ```

### Phase 2: Prediction Logic (pm/SKILL.md)
2. **Scoring formula:**
   ```
   Score = 1.0
   - IF blast_radius > 8 files: Score -= 0.3
   - IF blast_radius > 15 files: Score -= 0.2 (thêm)
   - IF hits hub/bridge node: Score -= 0.2
   - IF similar tasks (same files/flows) had < 50% success: Score -= 0.3
   - IF no existing tests for impacted files: Score -= 0.1
   
   high:   Score >= 0.7
   medium: Score 0.4-0.7
   low:    Score < 0.4
   ```

3. **Historical similarity lookup:**
   - Parse `log.md` entries với `verdict` operation
   - Extract task files/flows từ linked task file
   - Match against current task's files/flows
   - Calculate success rate (pass / total)

### Phase 3: Suggestion Generator
4. **Khi `predicted_success: low`**, generate suggestions:
   - Blast radius lớn → "Consider splitting: files A,B,C thành task riêng"
   - Hub node hit → "High-risk: touches ProductService (hub). Add extra test coverage"
   - Similar task failed → "PMI-003 failed with same files. Root cause: X. Address this"
   - No tests → "Missing test coverage for services/payment.py"

### Phase 4: Accuracy Tracking
5. **verdict/SKILL.md** — sau mỗi verdict, log vào `knowledge/metrics/prediction-accuracy.md`

### Phase 5: Integration
6. **pm/SKILL.md flow update:**
   ```
   Existing: graph queries → generate AC → Spec Gate
   New:      graph queries → compute prediction → generate AC + prediction → Spec Gate
                                    ↓
                            if low: show warnings + suggestions
   ```

## Sub-tasks

- [ ] Thêm `predicted_success:` field vào AGENTS.md §2.1 Standard Task Syntax
- [ ] Update `pm/SKILL.md` để compute prediction score
- [ ] Tạo function parse log.md cho historical task outcomes
- [ ] Implement suggestion generator khi prediction thấp
- [ ] Tạo `knowledge/metrics/prediction-accuracy.md` template
- [ ] Update `/verdict` để log prediction vs actual

## Research References

- [Can We Predict Before Executing ML Agents? (2025)](https://arxiv.org/html/2601.05930)
- [Complexity-Aware Reasoning and Execution (2025)](https://arxiv.org/html/2607.13034v1)
