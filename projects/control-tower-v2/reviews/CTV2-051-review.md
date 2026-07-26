---
id: CTV2-051
task_path: projects/control-tower-v2/tasks/CTV2-051-cli-coordinator.md
project: control-tower-v2
result_ref: 27ea213
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
status: passed
issued: 2026-07-26
verdict: pass
verdict_date: 2026-07-26
---

# Phiếu Review: CTV2-051 — Refactor Coordinator to CLI Dispatch

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-051-cli-coordinator.md`
- Result-ref: 27ea213
- Executor: @gpt-5.6-luna-high
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-26

## Acceptance Criteria cần verify

- [ ] AC1: CLIDispatcher spawns CLI with formatted prompt
- [ ] AC2: Session history loaded from PostgreSQL before each spawn
- [ ] AC3: CLI output parsed and saved back to PostgreSQL
- [ ] AC4: SSE streaming works with CLI output
- [ ] AC5: Model switching works (claude ↔ agy)
- [ ] AC6: No API key required (uses account login)
- [ ] AC7: Session ID preserved across CLI spawns
- [ ] AC8: Tests verify session continuity

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: test_cli_coordinator.py
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @gpt-5.6-luna-high)

## Test gợi ý chạy trong repo code

```bash
cd /home/lupca/projects/control-tower-v2
pytest backend/tests/test_cli_coordinator.py -v
pytest backend/tests/ -v  # full suite
```

## Files changed

- `backend/app/services/cli_dispatcher.py` (new)
- `backend/app/services/coordinator.py` (modified)
- `backend/tests/test_cli_coordinator.py` (new)

## Review Toolchain

Chạy review theo repo's toolchain:
```bash
cat .claude/review-toolchain.md
```

Repo PHẢI khai báo toolchain. Với mỗi tool trong pipeline:
- Preflight theo knowledge/tools/tool-registry.md (health_check → install nếu cần → re-check)
- Tool required=hard mà preflight fail sau install → BLOCK + escalate, không review với partial tools
- /code-review là baseline tool trong registry, chạy cùng (không thay thế) các tools khác

Chạy tất cả tools trong pipeline, aggregate kết quả, rồi verify từng AC item.

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:
```
/verdict CTV2-051 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]
```
