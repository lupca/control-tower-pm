---
id: PMI-022
title: "Dead code removal (~1,400 lines across all services)"
status: done
completed: 2026-07-29
result_ref: e0ed0a4c744baa40c5edc0cc27e13b588a6d2ff0
priority: low
risk: normal
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus-4.5"
result_ref: null
depends_on: []
dispatched: 2026-07-29
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
