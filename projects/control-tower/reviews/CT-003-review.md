# Phiếu Review: CT-003 Causal Analysis

> **Task:** [[projects/control-tower/tasks/CT-003-causal-analysis]]
> **Executor:** @sonnet-5
> **Result Ref:** control-tower@main (commit 43caa5a)
> **Ngày phát phiếu:** 2026-07-22

---

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1:** Thêm `## Causal Analysis` section vào task template (sau verdict pass)
- [ ] **AC2:** Format causal_analysis đúng schema (root_cause, mechanism, counterfactual, pattern_id)
- [ ] **AC3:** `/verdict pass` prompts reviewer để fill causal analysis (required for high-risk tasks)
- [ ] **AC4:** Tạo `knowledge/patterns/` directory với initial patterns (n-plus-one, missing-index, race-condition, memory-leak)
- [ ] **AC5:** `/pm` auto-suggests "This looks like pattern X, see how [task] was fixed"
- [ ] **AC6:** `/lint` detects "same pattern exists elsewhere" — flags preventive tasks

---

## Definition of Done (DoD)

- [ ] Tất cả AC trên đều pass
- [ ] Pattern library có ít nhất 4 patterns với format chuẩn
- [ ] AGENTS.md §2.1 có causal analysis section template
- [ ] `reviewer:` khác `executor:` (four-eyes principle)

---

## Files cần review

| File | Thay đổi |
|------|----------|
| `AGENTS.md` §2.1 | Task template với `## Causal Analysis` section |
| `knowledge/patterns/_index.md` | Pattern registry |
| `knowledge/patterns/*.md` | 4 initial patterns |
| `.claude/skills/verdict/SKILL.md` | Causal analysis prompts |
| `.claude/skills/pm/SKILL.md` | Pattern matching suggestions |
| `.claude/skills/lint/SKILL.md` | Cross-reference detection |

---

## Test commands

```bash
# 1. Check patterns directory exists
ls -la knowledge/patterns/

# 2. Verify pattern format
cat knowledge/patterns/n-plus-one-query.md

# 3. Check AGENTS.md has causal analysis section
grep -n "Causal Analysis" AGENTS.md

# 4. Verify verdict skill has causal prompts
grep -n "causal\|pattern" .claude/skills/verdict/SKILL.md
```

---

## Verdict

> **Reviewer:** @claude
> **Kết quả:** `pass`
> **Ghi chú:** All 6 ACs verified. AGENTS.md §2.1b/§13 define causal analysis schema + pattern library. 4 patterns bootstrapped with proper format. verdict/pm/lint skills updated with causal prompts, pattern suggestions, and recurrence detection.
