---
id: CT-025
title: "Mandatory Tool Registry + Tool Preflight — bắt buộc dùng code-review-graph/OCR, không fallback manual, mở rộng bằng khai báo"
status: dispatched
priority: high
risk: high
deadline: null
executor: "@claude-opus"
reviewer: null
result_ref: null
depends_on: [CT-023]
files:
  - knowledge/tools/tool-registry.md
  - knowledge/decisions/ADR-009-mandatory-toolchain-registry.md
  - AGENTS-REFERENCE.md
  - .claude/skills/pm/SKILL.md
  - .claude/skills/pm/references/task-creation.md
  - .claude/skills/review-order/SKILL.md
  - .claude/skills/dispatch/SKILL.md
  - knowledge/guides/review-toolchain.md
flows: []
tests: []
dispatched: 2026-07-24
in_review: null
predicted_success: high
confidence_interval: [0.75, 0.95]
prediction_factors:
  score: 0.9
  deductions:
    - "no_tests: meta-project, markdown files only (-0.1)"
    - "blast_radius: 8 files (2 new) — at limit, coherent single architecture, no split (-0.0)"
created: 2026-07-24
updated: 2026-07-24
---

# CT-025: Mandatory Tool Registry + Tool Preflight

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (vì sao)

`code-review-graph` và `ocr` là 2 công cụ chính trong flow của CT (PLAN dùng graph để lấy `files:`/`tests:`/`flows:`; REVIEW dùng OCR + toolchain). Hiện tại nếu công cụ **chưa cài / lỗi / bash/CLI/MCP không gọi được**, các skill lại **âm thầm fallback về làm manual** (`pm`/`task-creation` step 8.5: *"skip silently"*; `dispatch`/`review-toolchain`: *"run /code-review as default"*). Manual thay công cụ → **giảm chất lượng sản phẩm**.

Task này biến việc dùng công cụ thành **bắt buộc**: nếu thiếu → **cài/sửa** trên control-tower hoặc trên repo đích rồi mới chạy tiếp; chỉ khi cài bất khả thi mới **BLOCK + escalate cho user**, KHÔNG bao giờ âm thầm làm manual. Đồng thời phải **mở rộng được**: thêm tool mới chỉ cần **khai báo 1 dòng** trong registry là CT (khi PLAN) và agent (khi dispatch/review) tự dùng được — không phải sửa code từng skill.

## Tiêu chí nghiệm thu (AC)

- [x] `knowledge/tools/tool-registry.md` tồn tại — **source of truth khai báo** cho mọi tool, mỗi tool 1 entry với tối thiểu các field: `id`, `scope` (`control-tower` | `target-repo` | `both`), `applies_to` (project/điều kiện áp dụng), `health_check` (lệnh kiểm tra), `install` (lệnh cài/sửa trên đúng scope), `required` (`hard` | `soft`), `used_by` (bước/skill dùng nó), `fallback` (`none` cho hard).
- [x] Registry chứa sẵn ít nhất 2 entry: `code-review-graph` (scope `control-tower`, applies_to = repo có Graph build ✅ trong PROJECT REGISTRY, health_check qua MCP/`list_repos_tool`, install theo `knowledge/guides/setup-code-review-graph.md`) và `ocr` (scope `target-repo`, applies_to = all, health_check `ocr --version`, install command cụ thể).
- [x] Registry có section **"Adding a new tool"**: thêm tool mới = thêm 1 row + điền các field trên; **không cần sửa bất kỳ skill nào** — skill đọc registry generic theo `used_by`. (tiêu chí mở rộng).
- [x] `AGENTS-REFERENCE.md` có section **"Tool Preflight"** định nghĩa thuật toán bắt buộc: chạy `health_check` → nếu fail thì chạy `install` (đúng `scope`: control-tower system hoặc target repo) → chạy lại `health_check` → nếu vẫn fail và `required: hard` thì **BLOCK gate + báo user** (kèm lệnh fail + output install đã thử); **cấm silent manual fallback**. Tool `soft` được phép skip nhưng **phải log** (không skip âm thầm).
- [x] `pm/SKILL.md` + `references/task-creation.md`: bước OCR pre-scan (step 8.5) thay *"skip silently"* bằng **preflight theo registry** (cài nếu thiếu; block/escalate nếu `hard` mà không cài được). Bước graph queries ghi rõ áp dụng preflight cho graph ở repo có Graph build ✅.
- [x] `dispatch/SKILL.md` step 5 (reviewer prompt): bỏ *"If file missing, run /code-review as default"*; reviewer phải **preflight/cài tool thiếu theo registry + `.claude/review-toolchain.md`**, KHÔNG được fallback manual, chỉ escalate/block khi install bất khả thi.
- [x] `knowledge/guides/review-toolchain.md`: bỏ silent fallback *"no toolchain → use /code-review as the default"*; nêu rõ mọi repo PHẢI khai báo toolchain, tool thiếu thì **cài theo registry**; `/code-review` là **baseline tool có trong registry**, không phải cửa thoát để bỏ qua tool khác.
- [x] `knowledge/decisions/ADR-009-mandatory-toolchain-registry.md` tồn tại (CT Project Gate: mọi thay đổi skill/AGENTS phải có ADR đi kèm) — ghi lại quyết định, alternatives, và migration.
- [x] KHÔNG đổi task lifecycle / states / four-eyes / gate semantics trong `AGENTS.md` — chỉ **thêm** hành vi enforce tool (preflight là bổ sung, không phải state/gate mới).

## Verification

*(meta-project markdown — verify bằng grep/test, không có pytest)*
- `test -f knowledge/tools/tool-registry.md` → exit 0
- `grep -ci "code-review-graph" knowledge/tools/tool-registry.md` → ≥1
- `grep -ci "ocr" knowledge/tools/tool-registry.md` → ≥1
- `grep -ciE "health_check|health-check" knowledge/tools/tool-registry.md` → ≥1
- `grep -ci "install" knowledge/tools/tool-registry.md` → ≥1
- `grep -ci "adding a new tool" knowledge/tools/tool-registry.md` → ≥1
- `grep -ci "preflight" AGENTS-REFERENCE.md` → ≥1
- `grep -c "skip silently" .claude/skills/pm/references/task-creation.md` → 0
- `grep -ciE "preflight|registry|install" .claude/skills/pm/references/task-creation.md` → ≥1
- `grep -c "run /code-review as default" .claude/skills/dispatch/SKILL.md` → 0
- `grep -ciE "preflight|registry|install" .claude/skills/dispatch/SKILL.md` → ≥1
- `grep -c "use /code-review as the default" knowledge/guides/review-toolchain.md` → 0
- `test -f knowledge/decisions/ADR-009-mandatory-toolchain-registry.md` → exit 0

## Plan

Kiến trúc: **1 registry khai báo (source of truth) + 1 rule preflight (thuật toán enforce) + rewire các điểm hiện đang silent-fallback**. Thứ tự implement:

### 1. `knowledge/tools/tool-registry.md` (MỚI) — declarative source of truth
- Bảng/entry-per-tool với field: `id`, `scope`, `applies_to`, `health_check`, `install`, `required`, `used_by`, `fallback`.
- Seed 2 tool:
  - `code-review-graph`: scope `control-tower`; applies_to = repos có `Graph build ✅` (PROJECT REGISTRY index.md §2); health_check = gọi `list_repos_tool`/`list_graph_stats_tool` với `repo_root`; install = theo `knowledge/guides/setup-code-review-graph.md` (venv + `.mcp.json`) → nếu graph chưa build thì `build_or_update_graph_tool`; required `hard`; used_by = `pm` graph queries; fallback `none`.
  - `ocr`: scope `target-repo`; applies_to = all; health_check = `cd <repo> && ocr --version`; install = lệnh cài trên repo đích; required `hard` (khi repo có toolchain khai báo ocr) / `soft` (pm pre-scan optional — nhưng vẫn attempt-install, chỉ skip khi bản thân bước là optional); used_by = `pm` pre-scan + `review`; fallback `none`.
- Section **"Adding a new tool"**: điền 1 row → xong. Skill KHÔNG hardcode tên tool, đọc registry theo `used_by`.

### 2. `knowledge/decisions/ADR-009-mandatory-toolchain-registry.md` (MỚI)
- Context (manual fallback làm giảm chất lượng), Decision (registry + mandatory preflight, no silent manual fallback, extensible-by-declaration), Consequences, Alternatives (giữ silent skip — rejected), Migration (CT-023 toolchain nay tham chiếu registry).

### 3. `AGENTS-REFERENCE.md` — thêm section "Tool Preflight"
- Thuật toán: `health_check` → fail → `install` (đúng scope) → re-check → `hard` still-fail ⇒ **BLOCK + escalate** (kèm command + install output); `soft` ⇒ skip **có log**. Cấm silent manual fallback. Trỏ registry là nguồn khai báo.

### 4. `.claude/skills/pm/SKILL.md` + `references/task-creation.md` — rewire step 8.5 (+ graph note)
- Thay *"skip silently"* bằng preflight (đọc registry → health_check ocr → install nếu thiếu → chạy `ocr scan` → hard-fail-uninstallable ⇒ block/escalate).
- Graph queries: note preflight cho `code-review-graph` ở repo có Graph build ✅ (đã có MCP; nếu graph lỗi/chưa build → rebuild theo registry install, không tự bịa `files:`/`tests:`).

### 5. `.claude/skills/dispatch/SKILL.md` — reviewer prompt step 5
- Bỏ *"If file missing, run /code-review as default"*. Prompt reviewer: đọc `knowledge/tools/tool-registry.md` + `.claude/review-toolchain.md`, **preflight/cài** tool thiếu theo registry, chạy pipeline, KHÔNG fallback manual; chỉ escalate khi install bất khả thi.

### 6. `.claude/skills/review-order/SKILL.md` — review sheet toolchain section
- Section toolchain trong review sheet trỏ registry + hướng dẫn preflight/install; bỏ ngôn ngữ "bỏ qua nếu thiếu".

### 7. `knowledge/guides/review-toolchain.md` — bỏ silent fallback
- Xóa *"no toolchain → use /code-review as the default"*; mọi repo PHẢI khai báo toolchain; tool thiếu ⇒ cài theo registry; `/code-review` là baseline tool trong registry (không phải escape hatch).

## Sub-tasks
- [x] Tạo `knowledge/tools/tool-registry.md` — schema + seed `code-review-graph`, `ocr` + section "Adding a new tool"
- [x] Tạo `knowledge/decisions/ADR-009-mandatory-toolchain-registry.md`
- [x] Thêm section "Tool Preflight" vào `AGENTS-REFERENCE.md`
- [x] Sửa `pm/SKILL.md` + `references/task-creation.md` step 8.5 → preflight (bỏ "skip silently") + graph note
- [x] Sửa `dispatch/SKILL.md` step 5 reviewer prompt → preflight/install, bỏ "/code-review as default"
- [x] Sửa `review-order/SKILL.md` toolchain section → trỏ registry + preflight
- [x] Sửa `knowledge/guides/review-toolchain.md` → bỏ silent fallback, cài theo registry
