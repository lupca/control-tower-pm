---
id: CT-025
task_path: projects/control-tower/tasks/CT-025-mandatory-tool-registry-preflight.md
project: control-tower
result_ref: "control-tower@main (commit 95d126f)"
executor: "@claude-opus"
reviewer: "@antigravity"
status: passed
issued: 2026-07-24
verdict: pass
verdict_date: 2026-07-24
---

# Phiếu Review: CT-025 — Mandatory Tool Registry + Tool Preflight

- Dự án: control-tower (`/home/lupca/projects/control-tower`) — meta-project, no code graph
- Task gốc: `projects/control-tower/tasks/CT-025-mandatory-tool-registry-preflight.md`
- Result-ref: `control-tower@main (commit 95d126f)`
- Executor: @claude-opus
- Reviewer dự kiến: @antigravity (four-eyes: PHẢI khác executor @claude-opus)
- Ngày phát phiếu: 2026-07-24

## Acceptance Criteria cần verify

- [ ] `knowledge/tools/tool-registry.md` tồn tại — **source of truth khai báo** cho mọi tool, mỗi tool 1 entry với tối thiểu các field: `id`, `scope` (`control-tower` | `target-repo` | `both`), `applies_to`, `health_check`, `install`, `required` (`hard` | `soft`), `used_by`, `fallback` (`none` cho hard).
- [ ] Registry chứa sẵn ít nhất 2 entry: `code-review-graph` (scope `control-tower`, applies_to = repo có Graph build ✅, health_check qua MCP/`list_repos_tool`, install theo `setup-code-review-graph.md`) và `ocr` (scope `target-repo`, applies_to = all, health_check `ocr --version`, install cụ thể).
- [ ] Registry có section **"Adding a new tool"**: thêm tool mới = thêm 1 row, không cần sửa skill nào (tiêu chí mở rộng).
- [ ] `AGENTS-REFERENCE.md` có section **"Tool Preflight"**: `health_check` → fail → `install` (đúng scope) → re-check → `hard` vẫn fail ⇒ **BLOCK + escalate**; cấm silent manual fallback; `soft` skip nhưng **phải log**.
- [ ] `pm/SKILL.md` + `references/task-creation.md`: OCR pre-scan (step 8.5) thay *"skip silently"* bằng preflight; graph note cho repo có Graph build ✅.
- [ ] `dispatch/SKILL.md` step 5: bỏ *"If file missing, run /code-review as default"*; reviewer preflight/cài tool theo registry, không fallback manual.
- [ ] `knowledge/guides/review-toolchain.md`: bỏ silent fallback *"no toolchain → use /code-review as the default"*; mọi repo PHẢI khai báo toolchain; `/code-review` là baseline tool trong registry.
- [ ] `knowledge/decisions/ADR-009-mandatory-toolchain-registry.md` tồn tại (CT Project Gate: thay đổi skill/AGENTS phải có ADR).
- [ ] KHÔNG đổi task lifecycle / states / four-eyes / gate semantics trong `AGENTS.md` — chỉ thêm hành vi enforce tool.

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Verification 100% pass (meta-project markdown — không có pytest; test = các lệnh grep/test bên dưới)
- [ ] Không regression (không phá vỡ skill/gate hiện có; đọc lướt các skill đã sửa)
- [ ] Reviewer khác executor — xác nhận bạn ≠ @claude-opus

## Test gợi ý chạy trong repo code

`control-tower` là meta-project (Markdown, không pytest). Chạy đúng khối `## Verification` của task tại `repo_root`:

```bash
cd /home/lupca/projects/control-tower
test -f knowledge/tools/tool-registry.md && echo "registry OK"
grep -ci "code-review-graph" knowledge/tools/tool-registry.md   # ≥1
grep -ci "ocr" knowledge/tools/tool-registry.md                 # ≥1
grep -ciE "health_check|health-check" knowledge/tools/tool-registry.md  # ≥1
grep -ci "install" knowledge/tools/tool-registry.md             # ≥1
grep -ci "adding a new tool" knowledge/tools/tool-registry.md   # ≥1
grep -ci "preflight" AGENTS-REFERENCE.md                        # ≥1
grep -c "skip silently" .claude/skills/pm/references/task-creation.md   # 0
grep -ciE "preflight|registry|install" .claude/skills/pm/references/task-creation.md  # ≥1
grep -c "run /code-review as default" .claude/skills/dispatch/SKILL.md  # 0
grep -ciE "preflight|registry|install" .claude/skills/dispatch/SKILL.md # ≥1
grep -c "use /code-review as the default" knowledge/guides/review-toolchain.md  # 0
test -f knowledge/decisions/ADR-009-mandatory-toolchain-registry.md && echo "ADR-009 OK"
```

Verify against `95d126f`: `git show --stat 95d126f` (8 files, disjoint from CT-024).

## Câu hỏi rủi ro (tĩnh — không thay thế việc bạn tự đọc diff)

Meta-project không có code graph nên không có `get_suggested_questions_tool` output. Điểm rủi ro cần soi thủ công:

1. **Preflight có thực sự chặn không?** Đọc AGENTS-REFERENCE §8: đường `hard` fail sau install PHẢI dừng gate + escalate, KHÔNG có nhánh nào lặng lẽ quay về manual. Kiểm mọi skill đã sửa không còn câu chữ "skip silently"/"/code-review as default".
2. **Tính mở rộng có thật không?** Thêm 1 tool tưởng tượng (vd `eslint`) chỉ bằng 1 row registry — các skill (`pm`/`dispatch`/`review-order`) có đọc registry generic theo `used_by` không, hay vẫn hardcode tên `ocr`/`graph`? Nếu còn hardcode thì AC "mở rộng" chưa đạt.
3. **Không phá four-eyes/gate:** xác nhận `AGENTS.md` không bị đổi lifecycle/gate; preflight chỉ là lớp bổ sung.
4. **Scope `soft` vs `hard`:** OCR pre-scan trong `pm` là bước optional — kiểm nó vẫn attempt-install và **log khi skip**, không skip âm thầm.

## Review Toolchain

Chạy review theo repo's toolchain:
  `cat .claude/review-toolchain.md`
Repo PHẢI khai báo toolchain. Với mỗi tool trong pipeline:
  - Preflight theo `knowledge/tools/tool-registry.md` (health_check → install nếu cần → re-check)
  - Tool `required=hard` mà preflight fail sau install → BLOCK + escalate, không review với partial tools
  - `/code-review` là baseline tool trong registry, chạy cùng (không thay thế) các tools khác

Lưu ý: `control-tower` hiện CHƯA có `.claude/review-toolchain.md` (chính task này định nghĩa convention). Nếu file chưa tồn tại ở repo meta này, dùng `/code-review` làm baseline + chạy khối verification grep/test ở trên. Aggregate kết quả rồi verify từng AC.

## Trả kết quả

Sau khi review xong, báo lại cho control-tower:
`/verdict CT-025 <pass|changes> --reviewer @antigravity [--commit <hash>] [--notes "..."]`
