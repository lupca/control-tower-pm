---
id: CT-030
task_path: projects/control-tower/tasks/CT-030-skill-validation-in-lint.md
project: control-tower
result_ref: a3306db
executor: @gpt-5.6-luna-high
reviewer: "@claude-opus"
status: passed
issued: 2026-07-25
verdict: pass
verdict_date: 2026-07-25
---

# Phiếu Review: CT-030 — Skill-health validation trong /lint + bổ sung frontmatter cho dispatch/SKILL.md

- Dự án: control-tower (`/home/lupca/projects/control-tower`)
- Task gốc: `projects/control-tower/tasks/CT-030-skill-validation-in-lint.md`
- Result-ref: a3306db
- Executor: @gpt-5.6-luna-high
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-25

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [ ] `scripts/ct-validate-skills.py` tồn tại — loop TẤT CẢ `.claude/skills/*/SKILL.md`, kiểm: (a) có YAML frontmatter, (b) có `name` + `description`, (c) `name` khớp tên thư mục skill, (d) cấu trúc frontmatter hợp lệ. Chạy được `python3 scripts/ct-validate-skills.py [--json]` → in danh sách findings; `--json` xuất mảng JSON `[{skill, severity, issue}]`. Exit code ≠ 0 nếu có finding (để CI/lint dùng).
- [ ] Dựa trên `docs/opensource/quick_validate.py` (không chép mù — chấp nhận field mở rộng của CT như `argument-hint`/`allowed-tools`, không báo lỗi vì chúng).
- [ ] `scripts/test_ct_validate_skills.py` — test: skill hợp lệ → pass; skill thiếu frontmatter → bị flag; `name` lệch thư mục → bị flag.
- [ ] `.claude/skills/lint/SKILL.md` — thêm 1 check mới (đánh số tiếp, ví dụ 14 **Skill health**): chạy `python3 scripts/ct-validate-skills.py --json`, đưa mỗi finding vào bảng output của `/lint` (severity 🔴/🟡). Read-only, không tự sửa skill.
- [ ] `dispatch/SKILL.md` được **bổ sung YAML frontmatter** (`name: dispatch`, `description:` mô tả rõ + "Activate on /dispatch", `argument-hint`, `allowed-tools`) theo đúng format các skill khác — sau đó validator KHÔNG còn flag dispatch.
- [ ] `knowledge/decisions/ADR-011-skill-validation-in-lint.md` tồn tại (CT Project Gate: đổi skill cần ADR). *(ADR-010 đã bị CT-028 chiếm — dùng 011.)*
- [ ] KHÔNG đổi lifecycle/gate/four-eyes; validator chỉ read-only, `/lint` vẫn chỉ report (không tự sửa).

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: scripts/test_ct_validate_skills.py
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @gpt-5.6-luna-high)

## Test gợi ý chạy trong repo code
- `scripts/test_ct_validate_skills.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CT-030 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`
