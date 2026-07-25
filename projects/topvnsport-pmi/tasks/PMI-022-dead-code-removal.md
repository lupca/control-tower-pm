---
id: PMI-022
title: "Dead code removal (~1,400 lines across all services)"
status: todo
priority: low
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - PMI/
  - OMS/
  - WMS/
  - web/
flows: []
tests: []
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "cross_project: -0.15"
created: 2026-07-25
updated: 2026-07-25
---

# PMI-022: Dead code removal (~1,400 lines across all services)

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

## Tiêu chí nghiệm thu (AC)

- [ ] Remove unused imports và variables (detected by linter)
- [ ] Remove backup files (*.bak, *.old, *_backup.*)
- [ ] Remove commented-out code blocks (> 10 lines)
- [ ] Remove unused dependencies từ package.json/requirements.txt
- [ ] All tests pass sau cleanup

## Verification

- `ruff check --select F401,F841 .` → no unused imports/vars
- `find . -name "*.bak" -o -name "*.old"` → empty
- `npm prune` / `pip-autoremove` → no removals needed
- `pytest` + `npm test` → pass

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Run linter để detect unused code
- [ ] Remove backup/old files
- [ ] Remove large commented blocks
- [ ] Audit và remove unused npm dependencies
- [ ] Audit và remove unused pip dependencies
- [ ] Verify tests pass

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/cleanup/01_dead_code_removal.md`
