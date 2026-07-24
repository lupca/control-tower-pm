---
id: CT-030
title: "Skill-health validation trong /lint + bổ sung frontmatter cho dispatch/SKILL.md"
status: done
priority: medium
risk: normal
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
result_ref: "a3306db"
depends_on: []
files:
  - scripts/ct-validate-skills.py
  - scripts/test_ct_validate_skills.py
  - .claude/skills/lint/SKILL.md
  - .claude/skills/dispatch/SKILL.md
  - knowledge/decisions/ADR-011-skill-validation-in-lint.md
flows: []
tests:
  - scripts/test_ct_validate_skills.py
dispatched: 2026-07-25
in_review: 2026-07-25
predicted_success: high
confidence_interval: [0.8, 0.98]
prediction_factors:
  score: 1.0
  deductions:
    - "có test, blast nhỏ (5 file, 2 new), không hub/bridge (-0.0)"
created: 2026-07-25
updated: 2026-07-25
---

# CT-030: Skill-health validation trong /lint

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (vì sao)

CT vận hành hoàn toàn bằng skill (`.claude/skills/*/SKILL.md`) nhưng `/lint` chỉ soi backlog task, **không kiểm chính các skill điều hành hệ thống**. Thực tế đã có defect lọt: `dispatch/SKILL.md` **thiếu hẳn YAML frontmatter** (8/9 skill khác có `name`/`description`/`allowed-tools`). Bộ `docs/opensource` (skill-creator của Anthropic) có sẵn `quick_validate.py` — tận dụng để tự động bắt loại lỗi này.

*Phạm vi đã điều chỉnh:* bug spawn flag `-m`→`--model` **đã được CT-028 sửa** (dispatch nay dùng `claude --model … -p`) → KHÔNG làm lại ở task này. Chỉ còn: (1) validator + wire vào `/lint`, (2) bổ sung frontmatter cho `dispatch/SKILL.md`.

## Tiêu chí nghiệm thu (AC)

- [x] `scripts/ct-validate-skills.py` tồn tại — loop TẤT CẢ `.claude/skills/*/SKILL.md`, kiểm: (a) có YAML frontmatter, (b) có `name` + `description`, (c) `name` khớp tên thư mục skill, (d) cấu trúc frontmatter hợp lệ. Chạy được `python3 scripts/ct-validate-skills.py [--json]` → in danh sách findings; `--json` xuất mảng JSON `[{skill, severity, issue}]`. Exit code ≠ 0 nếu có finding (để CI/lint dùng).
- [x] Dựa trên `docs/opensource/quick_validate.py` (không chép mù — chấp nhận field mở rộng của CT như `argument-hint`/`allowed-tools`, không báo lỗi vì chúng).
- [x] `scripts/test_ct_validate_skills.py` — test: skill hợp lệ → pass; skill thiếu frontmatter → bị flag; `name` lệch thư mục → bị flag.
- [x] `.claude/skills/lint/SKILL.md` — thêm 1 check mới (đánh số tiếp, ví dụ 14 **Skill health**): chạy `python3 scripts/ct-validate-skills.py --json`, đưa mỗi finding vào bảng output của `/lint` (severity 🔴/🟡). Read-only, không tự sửa skill.
- [x] `dispatch/SKILL.md` được **bổ sung YAML frontmatter** (`name: dispatch`, `description:` mô tả rõ + "Activate on /dispatch", `argument-hint`, `allowed-tools`) theo đúng format các skill khác — sau đó validator KHÔNG còn flag dispatch.
- [x] `knowledge/decisions/ADR-011-skill-validation-in-lint.md` tồn tại (CT Project Gate: đổi skill cần ADR). *(ADR-010 đã bị CT-028 chiếm — dùng 011.)*
- [x] KHÔNG đổi lifecycle/gate/four-eyes; validator chỉ read-only, `/lint` vẫn chỉ report (không tự sửa).

## Verification

- `test -f scripts/ct-validate-skills.py` → exit 0
- `python3 scripts/ct-validate-skills.py --json` → chạy được, in JSON hợp lệ
- `head -1 .claude/skills/dispatch/SKILL.md` → `---` (đã có frontmatter)
- `grep -cE "^name: dispatch" .claude/skills/dispatch/SKILL.md` → 1
- `python3 scripts/ct-validate-skills.py` sau khi fix → **0 finding cho dispatch** (exit 0 nếu toàn bộ skill sạch)
- `python3 -m pytest scripts/test_ct_validate_skills.py -q` → pass
- `grep -ciE "ct-validate-skills|skill health|skill.*validat" .claude/skills/lint/SKILL.md` → ≥1
- `test -f knowledge/decisions/ADR-011-skill-validation-in-lint.md` → exit 0

## Plan

### 1. `scripts/ct-validate-skills.py` (MỚI)
- Refactor `docs/opensource/quick_validate.py` thành 1 hàm `validate_skill(dir)` + `main()` loop `.claude/skills/*/`.
- Check: frontmatter (`^---`), `name:`/`description:` có mặt, `name` == basename thư mục, không vỡ vì field CT (`argument-hint`,`allowed-tools`).
- `--json` → `json.dumps([{skill,severity,issue}])`; mặc định → in người-đọc. Exit 1 nếu có finding.

### 2. `scripts/test_ct_validate_skills.py` (MỚI)
- Tạo tmp skill hợp lệ / thiếu frontmatter / name lệch → assert kết quả validate.

### 3. `dispatch/SKILL.md` — thêm frontmatter
- Chèn block `---\nname: dispatch\ndescription: ...Activate on /dispatch.\nargument-hint: "<task-id> @<agent-id> [--review]"\nallowed-tools: Read, Edit, Write, Glob, Grep, Bash\n---` ngay đầu file, trên dòng `# /dispatch`.

### 4. `.claude/skills/lint/SKILL.md` — wire check 14
- Thêm mục "14. **Skill health**": chạy `python3 scripts/ct-validate-skills.py --json`, map findings vào bảng output (🔴 thiếu frontmatter/`name`, 🟡 name lệch). Read-only.

### 5. `ADR-011`
- Context (skill là code vận hành nhưng chưa được lint), Decision (validator dựa quick_validate + wire /lint), Consequences, Alternatives, liên kết `docs/opensource` skill-creator.

## Sub-tasks
- [ ] `scripts/ct-validate-skills.py` — validator loop + `--json` + exit code
- [ ] `scripts/test_ct_validate_skills.py` — 3 case
- [ ] Thêm frontmatter cho `dispatch/SKILL.md`
- [ ] Wire check "Skill health" vào `lint/SKILL.md`
- [ ] `ADR-011-skill-validation-in-lint.md`
