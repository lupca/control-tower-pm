---
id: CT-015
title: "Tái cấu trúc agent profiles: tiering rõ ràng cho claude/antigravity/human"
status: done
priority: high
risk: low
deadline: null
executor: "@sonnet-5"
reviewer: "@antigravity"
result_ref: "control-tower@main (knowledge/agents/*.md, uncommitted)"
depends_on: [CT-014]
files:
  - knowledge/agents/@claude.md
  - knowledge/agents/@claude-opus.md
  - knowledge/agents/@sonnet-5.md
  - knowledge/agents/@antigravity.md
  - knowledge/agents/@antigravity-3.6.md
  - knowledge/agents/@dev-tung.md
  - knowledge/agents/@gpt-5.6-luna.md
flows: []
tests: []
dispatched: 2026-07-22
in_review: 2026-07-22
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "blast_radius: 7 files (-0.0)"
    - "no_tests: config change, no code (-0.1)"
confidence_interval: [0.8, 0.95]
created: 2026-07-22
updated: 2026-07-22
---

# CT-015: Tái cấu trúc agent profiles

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (Context)

Agent profiles hiện tại chưa phân tier rõ ràng:
- `@claude` và `@claude-opus` chưa rõ model nào, dùng cho việc gì
- `@antigravity` và `@antigravity-3.6` chưa có tiering (low/medium/high)
- `@dev-tung` (human) chưa định nghĩa rõ strengths

## Tiêu chí nghiệm thu (AC)

- [x] AC1: **Claude tiering:**
  - `@claude-opus` → model `claude-opus-4-5-20251101`, strengths: `[review, research, architecture, complex-analysis]` — chỉ dùng cho 2-3 việc quan trọng
  - `@claude-sonnet-low` / `@claude-sonnet-medium` / `@claude-sonnet-high` → model `claude-sonnet-5` với effort tương ứng, strengths: `[code, backend, frontend, testing]`
  - Xóa hoặc merge `@claude` và `@sonnet-5` cũ vào các profile mới

- [x] AC2: **Antigravity tiering:**
  - `@antigravity-3.6-low` / `@antigravity-3.6-medium` / `@antigravity-3.6-high` → model `gemini-3.6-flash-*`, strengths: `[code, simple-tasks]`
  - `@antigravity` (3.1 pro) → giữ nguyên nhưng sửa strengths chỉ mạnh về `[complex-backend, complex-frontend, architecture]`

- [x] AC3: **Human tiering:**
  - `@dev-tung` (hoặc rename `@human`) → strengths: `[confirmation, creative, deep-research, final-decision]`

- [x] AC4: **Performance Summary:**
  - Nếu có stats cũ → chia đều cho các profile mới
  - Nếu không có → để mặc định (0 tasks)

## Plan

### Step 1 — Đọc profiles hiện tại
Đọc tất cả `knowledge/agents/*.md` để hiểu stats hiện có.

### Step 2 — Tạo/sửa Claude profiles
- Sửa `@claude-opus.md`: model=`claude-opus-4-5-20251101`, strengths=[review, research, architecture]
- Tạo `@claude-sonnet-low.md`, `@claude-sonnet-medium.md`, `@claude-sonnet-high.md`
- Xóa hoặc deprecate `@claude.md` và `@sonnet-5.md` (merge stats)

### Step 3 — Tạo/sửa Antigravity profiles
- Tạo `@antigravity-3.6-low.md`, `@antigravity-3.6-medium.md`, `@antigravity-3.6-high.md`
- Sửa `@antigravity.md` (3.1 pro): strengths chỉ complex tasks
- Xóa hoặc deprecate `@antigravity-3.6.md` cũ (merge stats)

### Step 4 — Sửa Human profile
- Sửa `@dev-tung.md`: strengths=[confirmation, creative, deep-research]

### Step 5 — Verify
Đọc lại tất cả profiles, confirm 4 AC.

## Sub-tasks

- [x] Đọc profiles hiện tại
- [x] Sửa @claude-opus.md (model + strengths)
- [x] Tạo @claude-sonnet-{low,medium,high}.md
- [x] Deprecate/merge @claude.md + @sonnet-5.md
- [x] Tạo @antigravity-3.6-{low,medium,high}.md
- [x] Sửa @antigravity.md (complex only)
- [x] Deprecate/merge @antigravity-3.6.md cũ
- [x] Sửa @dev-tung.md (human strengths)

## Result

Tất cả 7 files trong `files:` đã được sửa, cộng thêm 6 file profile mới:

- **`@claude-opus.md`**: thêm `model: claude-opus-4-5-20251101`, strengths → `[review, research, architecture, complex-analysis]`; gộp 4 review cũ từ `@claude` vào (1→5 `total_tasks_reviewed`).
- **`@claude-sonnet-{low,medium,high}.md`** (mới): `model: claude-sonnet-5` + `effort: low/medium/high`, strengths `[code, backend, frontend, testing]`. Stats cũ của `@sonnet-5` (8 executed / 7 reviewed) chia đều 3/3/2 và 3/2/2.
- **`@claude.md`**, **`@sonnet-5.md`**: KHÔNG xóa (nhiều task cũ đã `done` còn tham chiếu `executor:`/`reviewer:` tới 2 ID này — xóa sẽ tạo dead link mà `/lint` sẽ bắt). Thay vào đó đánh dấu `status: deprecated` + `superseded_by:`, giữ nguyên số liệu lịch sử, trỏ sang profile mới.
- **`@antigravity-3.6-{low,medium,high}.md`** (mới): `model: gemini-3.6-flash-low/medium/high`, strengths `[code, simple-tasks]`. `@antigravity-3.6` cũ chỉ có 1 task (WEB-001) — không chia đều được cho 3 tier nên gán nguyên vào `-medium` (tier gần nhất với profile cũ chưa phân tier), `-low`/`-high` mặc định 0.
- **`@antigravity-3.6.md`**: cùng lý do như trên, deprecate (không xóa) + trỏ sang 3 tier mới.
- **`@antigravity.md`**: giữ nguyên mọi thứ, chỉ sửa `strengths` → `[complex-backend, complex-frontend, architecture]` theo đúng AC2 ("giữ nguyên nhưng sửa strengths").
- **`@dev-tung.md`**: chỉ sửa `strengths` → `[confirmation, creative, deep-research, final-decision]`; KHÔNG đổi tên thành `@human` (giữ nguyên filename để tránh phá vỡ ~5 file khác đang tham chiếu `@dev-tung`, đúng theo lựa chọn "hoặc" trong AC3).
- **`@gpt-5.6-luna.md`**: không sửa — không có AC/Plan nào nhắc tới, nằm trong `files:` chỉ vì cùng thư mục.

Lưu ý: `knowledge/research/headless-cli-orchestration.md` §8.2 (roster table từ CT-014) vẫn tham chiếu `@sonnet-5`/`@antigravity-3.6` cũ và model id `claude-opus-4-8` (khác với `claude-opus-4-5-20251101` ở đây) — nằm ngoài `files:` của task này nên không sửa, nhưng nên có task theo dõi riêng để đồng bộ.

`result_ref`: control-tower@main (knowledge/agents/*.md, uncommitted) — chưa commit, chờ `/review-order`.
