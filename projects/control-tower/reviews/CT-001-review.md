# Phiếu Review: CT-001 Pre-Execution Prediction

> **Task:** [[projects/control-tower/tasks/CT-001-pre-execution-prediction]]
> **Executor:** @antigravity
> **Result Ref:** control-tower@main (commit 7477570)
> **Ngày phát phiếu:** 2026-07-22

---

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1:** Thêm field `predicted_success: high|medium|low` vào task frontmatter template (AGENTS.md §2.1)
- [ ] **AC2:** `/pm` tự động tính prediction dựa trên:
  - Complexity từ `get_impact_radius_tool` (blast radius)
  - Hub/bridge node involvement từ `get_hub_nodes_tool`
  - Historical similarity: query log.md cho tasks tương tự (same files/flows) và outcome
- [ ] **AC3:** Nếu `predicted_success: low`, `/pm` auto-suggest enrichments
- [ ] **AC4:** Track actual outcomes để improve prediction over time (verdict logs to metrics file)

---

## Definition of Done (DoD)

- [ ] Tất cả AC trên đều pass
- [ ] Không có regression trong các skill khác (`/pm`, `/verdict`, `/ingest`, `/report`, `/lint`)
- [ ] Files mới/sửa đều syntactically correct (YAML parse OK)
- [ ] `reviewer:` khác `executor:` (four-eyes principle)

---

## Files cần review

| File | Thay đổi |
|------|----------|
| `AGENTS.md` §2.1 | Thêm `predicted_success:` + `prediction_factors:` fields |
| `.claude/skills/pm/SKILL.md` | Prediction logic, scoring formula |
| `.claude/skills/pm/references/task-creation.md` | Template update |
| `.claude/skills/verdict/SKILL.md` | Log prediction vs actual |
| `knowledge/metrics/prediction-accuracy.md` | New file — metrics template |
| `knowledge/_index.md` | Register metrics file |

---

## Test commands

```bash
# 1. Verify YAML syntax in AGENTS.md
python3 -c "import yaml; yaml.safe_load(open('AGENTS.md').read().split('---')[1])" 2>/dev/null || echo "Check AGENTS.md manually"

# 2. Check prediction-accuracy.md exists
ls -la knowledge/metrics/prediction-accuracy.md

# 3. Verify skill files are valid
head -50 .claude/skills/pm/SKILL.md
head -50 .claude/skills/verdict/SKILL.md

# 4. Check git log for commit
git log --oneline -3
```

---

## Câu hỏi rủi ro

1. **Scoring formula:** Các deduction weights (-0.3, -0.2, -0.1) có hợp lý không? Có edge case nào bị score quá thấp/cao sai?
2. **Historical lookup:** Logic parse log.md có handle được format cũ (trước khi có prediction) không?
3. **Backward compatibility:** Tasks cũ không có `predicted_success:` field — các skill có handle được không?

---

## Verdict

> **Reviewer:** @claude
> **Kết quả:** `pass`
> **Ghi chú:** All 4 ACs verified. Schema, prediction logic, suggestion generator, và accuracy tracking đều implemented đúng. Code quality tốt, backward compatible.
