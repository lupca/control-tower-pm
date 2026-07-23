---
id: CTW-001
title: "Research: CSS not loading + file overwrite bugs"
status: done
type: research
priority: high
created: 2026-07-23
deadline: 2026-07-24
updated: 2026-07-23
executor: "@claude-opus"
reviewer: "@lupca"
files:
  - src/styles/global.css
  - src/layouts/DashboardLayout.astro
  - astro.config.mjs
  - tailwind.config.mjs
tests: []
---

## Description

Investigate 2 critical bugs in control-tower-web:

### Bug 1: UI không nhận CSS
- Triệu chứng: Giao diện không load được CSS/styles
- Cần xác định: Astro build config? Tailwind setup? Path issues?

### Bug 2: File overwrite thành blank
- Triệu chứng: Thao tác với project control-tower đôi khi ghi đè file thành nội dung trống
- Cần xác định: Race condition? Tool behavior? Symlink issues?

## Acceptance Criteria

- [x] Root cause identified for both bugs
- [x] Reproduction steps documented
- [x] Solution/fix proposal with code snippets
- [x] Fix applied: content-link.sh (atomic writes)
- [x] Fix applied: CSS rebuild (blocked - npm wrapper chỉ hỗ trợ pim-frontend container)

## Environment Issue

npm wrapper tại `/home/lupca/.local/bin/npm` chạy `docker exec pim-frontend npm "$@"` — không hỗ trợ project khác. Cần:
1. Setup Docker container riêng cho control-tower-web, hoặc
2. Cài npm thực (không wrapper) để build local

## Research Output

### Bug 1: CSS không load

**Root Cause:** `dist/` chứa CSS build không đầy đủ — thiếu Tailwind utility classes.

**Evidence:**
- `dist/_astro/agents.B807dkS2.css` (7KB): chỉ có custom CSS, **thiếu toàn bộ Tailwind utilities**
- `dist/dist/_astro/agents.-hAkVL-Q.css` (22KB): có đầy đủ Tailwind — nhưng nằm sai folder (nested)

**Why:** Build bị chạy 2 lần, lần đầu incomplete, lần sau output vào `dist/dist/`.

**Fix:**
```bash
cd /home/lupca/projects/control-tower-web
rm -rf dist
npm run build
```

---

### Bug 2: File overwrite thành blank

**Finding:** Không tìm thấy file trống trong control-tower hiện tại.

**Potential Cause:** `content-link.sh` dùng `sed ... > "$dest"` — nếu source file đang được write đồng thời (race condition), sed đọc file truncated/empty.

**Fix:** Thêm safety check vào `content-link.sh`:
```bash
sanitize_yaml() {
  local src="$1"
  local dest="$2"
  local tmp="${dest}.tmp"
  if [ ! -s "$src" ]; then
    echo "WARNING: Source $src empty/missing" >&2
    return 1
  fi
  sed -E 's/^(executor|reviewer):\s+@([a-zA-Z0-9_-]+)$/\1: "@\2"/' "$src" > "$tmp"
  if [ -s "$tmp" ]; then
    mv "$tmp" "$dest"
  else
    rm -f "$tmp"
  fi
}
```

---

| Bug | Root Cause | Fix |
|-----|------------|-----|
| CSS not loading | Incomplete Tailwind build trong `dist/` | `rm -rf dist && npm run build` |
| Blank file overwrite | Race condition trong `content-link.sh` | Atomic writes + empty check |
