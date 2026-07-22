# Token Baseline — Manual Flow (Pre-Model A)

**Task:** CT-013  
**Date:** 2026-07-22  
**Mốc so sánh:** AGENTS.md split cf9886f (636→152 dòng core)

---

## 1. Baseline Chi Phí Đọc File (AC1)

### Core Rules (bắt buộc đọc mỗi session)

| File | Lines | Reads/Cycle | Purpose |
|------|-------|-------------|---------|
| CLAUDE.md | 35 | 1 | Entry point, Model B definition |
| AGENTS.md | 152 | 1 | Core rules (§1-§4) |
| AGENTS-REFERENCE.md | 84 | 0-1 | On-demand: §5-§7 |
| AGENTS-PLAYBOOK.md | 105 | 0-1 | On-demand: §8-§11 |
| AGENTS-EXPERIMENTAL.md | 270 | 0-1 | On-demand: §12-§20 |
| index.md | 77 | 1 | Project registry |
| **Subtotal (mandatory)** | **264** | **3** | |
| **Subtotal (on-demand)** | **459** | **0-3** | |

### Skills (đọc khi invoke macro)

| Skill | Lines | Invoked When |
|-------|-------|--------------|
| pm/SKILL.md | 36 | `/pm` |
| pm/references/task-creation.md | 55 | `/pm` |
| pm/references/task-execution.md | 32 | `/pm` dispatch |
| ingest/SKILL.md | 27 | `/ingest` |
| report/SKILL.md | 23 | `/report` |
| lint/SKILL.md | 37 | `/lint` |
| review-order/SKILL.md | 79 | `/review-order` |
| verdict/SKILL.md | 68 | `/verdict` |
| goal/SKILL.md | 33 | `/goal` |
| **Total skills** | **390** | |

### Project + Tasks

| Category | Lines | Notes |
|----------|-------|-------|
| control-tower.md | 45 | Project overview |
| tasks/*.md (13 files) | 1144 | All tasks combined |
| **Total project** | **1189** | Grows with task count |

### Log (growing file)

| Metric | Value | Projection |
|--------|-------|------------|
| Current lines | 640 | 2026-07-22 |
| Growth rate | ~20-30 lines/task cycle | |
| 1 month (30 tasks) | ~1500 lines | |
| 3 months (90 tasks) | ~3300 lines | |
| 6 months (180 tasks) | ~6000 lines | Need archival strategy |

---

## 2. Full Task Cycle Token Estimate

A complete task cycle: `/pm` → dispatch → executor → `/review-order` → reviewer → `/verdict` → `/report`

| Step | Files Read | Est. Lines | Token Est. (~1.3 tok/line) |
|------|-----------|-----------|---------------------------|
| `/pm` (Spec Gate) | CLAUDE+AGENTS+index+pm/SKILL+refs | ~400 | ~520 |
| `/pm` (Plan Gate) | Same + project file | ~450 | ~585 |
| Dispatch | task-execution.md + log | ~700 | ~910 |
| `/review-order` | review-order/SKILL + task | ~250 | ~325 |
| `/verdict` | verdict/SKILL + task + log | ~750 | ~975 |
| `/report` | report/SKILL + project + index | ~200 | ~260 |
| **Total per cycle** | | **~2750** | **~3575 tokens (reading only)** |

**Note:** This is INPUT tokens only. LLM reasoning/output adds 2-10x depending on task complexity.

---

## 3. Model A Impact Estimate

With headless CLI orchestration (CT-012):
- Executor runs in separate context → 0 token in planner
- Reviewer runs in separate context → 0 token in planner
- Control-tower only: `/pm` + dispatch + `/review-order` + `/verdict` + `/report`

| Model B (current) | Model A (projected) | Savings |
|------------------|--------------------|---------| 
| Planner reads executor context | Planner sends 1 spawn command | ~30-50% |
| Planner reads reviewer context | Planner sends 1 spawn command | ~30-50% |

**Actual savings depend on:** how much context executor/reviewer would have added. For simple tasks: minimal. For complex multi-file tasks: significant.

---

## 4. Recommendations

1. **Archive log.md** every 3 months (move to `knowledge/archive/log-YYYY-Qn.md`)
2. **Lazy-load detail files** (already implemented: AGENTS-REFERENCE, PLAYBOOK, EXPERIMENTAL)
3. **Model A for batch tasks** — biggest win when running many tasks sequentially

---

## 5. Data Points for Future Comparison

| Metric | Pre-Model A (2026-07-22) |
|--------|-------------------------|
| Core rules lines | 264 (mandatory) + 459 (on-demand) |
| Skills lines | 390 |
| Project lines | 1189 |
| Log lines | 640 |
| Est. tokens/cycle | ~3575 (input reading) |

After Model A implementation, re-measure same metrics to calculate actual savings.
