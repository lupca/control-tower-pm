---
id: CT-028
task_path: projects/control-tower/tasks/CT-028-dispatch-review-order-scripts.md
project: control-tower
result_ref: 9bbf6f4
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
status: passed
issued: 2026-07-25
verdict: pass
verdict_date: 2026-07-25
round: 2
---

## Round 2 (re-review sau fix — ref b8ba2e2)
Round 1 (`9bbf6f4`) = CHANGES: AC3/AC4 pass; 3 fix cần. Executor fix ở `b8ba2e2` (suite 9/9). **Re-verify 3 điểm:** F1 — `ct-review-order.py` section() fence-aware (dựng task có `##` trong fenced block giữa các AC → phiếu copy ĐỦ, không cắt); F2 — `ct-dispatch.py --role review` refuse khi reviewer==executor (exit 1, 0 output/state); F3 — prompt shlex.quote, field chứa `$(...)`/backtick bị vô hiệu trong lệnh in ra (không execute khi chạy). Delta:
```
git diff 9bbf6f4..b8ba2e2 -- scripts/ct-dispatch.py scripts/ct-review-order.py scripts/test_ct_dispatch_review.py
```
Xác nhận không regress AC3/AC4 + 3 test regression mới thật sự cover.

# Phiếu Review: CT-028 — ct-dispatch.py + ct-review-order.py

- Dự án: control-tower (`/home/lupca/projects/control-tower`) — meta-project
- Task gốc: `projects/control-tower/tasks/CT-028-dispatch-review-order-scripts.md`
- Result-ref: commit `9bbf6f4` (branch `review/CT-028`) — diff so với `main`
- Executor: @gpt-5.6-luna-high
- Reviewer chỉ định: @gpt-5.6-sol (four-eyes: PHẢI ≠ @gpt-5.6-luna-high)
- Ngày phát phiếu: 2026-07-25

## Cách lấy diff (chỉ đọc)
```
cd /home/lupca/projects/control-tower
git diff main..9bbf6f4 -- scripts/ct-dispatch.py scripts/ct-review-order.py scripts/test_ct_dispatch_review.py .claude/skills/dispatch/SKILL.md .claude/skills/review-order/SKILL.md knowledge/decisions/ADR-010-dispatch-review-order-scripts.md
```

## Acceptance Criteria cần verify
- [ ] **AC1 (ct-dispatch.py):** `<ID> [--role execute|review] [--reviewer @id] [--print-only]` — đọc executor/reviewer từ task, tra `repo_root` từ PROJECT REGISTRY (index.md) + model/CLI từ `knowledge/agents/@<id>.md` + `knowledge/guides/spawn-patterns.md`, **dựng đúng lệnh** cho agy/codex/claude. Mặc định IN lệnh, **KHÔNG exec/spawn**. Không `--print-only` thì set status:dispatched + executor: vào task.
- [ ] **AC2 (ct-review-order.py):** `<ID> --ref <hash> --reviewer @id [--dry-run]` — **four-eyes hard refuse nếu reviewer==executor** (exit 1, không ghi); set frontmatter (status→in-review, result_ref, in_review/updated); sinh phiếu copy khối AC + DoD + tests từ task; JSON summary; `--dry-run` không ghi gì.
- [ ] **AC3:** Cả 2 script import `ct_common` (không lặp frontmatter/registry parse).
- [ ] **AC4:** `dispatch/SKILL.md` + `review-order/SKILL.md` gọi script (giữ phần LLM: chọn executor, câu hỏi rủi ro graph, log narrative; có manual-fallback). `ADR-010` tồn tại. `test_ct_dispatch_review.py` sandbox pass.

## Definition of Done
- [ ] Toàn bộ AC pass
- [ ] `scripts/test_ct_dispatch_review.py` xanh 100% (chạy thật trong /tmp)
- [ ] **KHÔNG regression skill:** SKILL sửa vẫn GIỮ phần Tool Preflight của CT-025 (registry/preflight, không silent fallback) — chỉ THÊM phần gọi script, không xoá enforce cũ; four-eyes/gate semantics không đổi
- [ ] Reviewer ≠ executor (bạn @gpt-5.6-sol ≠ @gpt-5.6-luna-high)

## Kiểm tra rủi ro riêng
- **ct-dispatch KHÔNG được tự exec** lệnh spawn — chỉ in ra. Xác nhận không có `subprocess.run`/`os.system` chạy lệnh đã dựng. Dựng lệnh đúng cú pháp cho cả 3 CLI (agy `--model/--print`, codex `-m/-c model_reasoning_effort/--dangerously-bypass...` positional prompt, claude `--model/-p/--dangerously-skip-permissions`).
- **ct-review-order four-eyes** phải refuse TRƯỚC khi ghi bất cứ gì (giống ct-verdict-apply). Test reviewer==executor → exit 1, 0 file đổi.
- Sinh phiếu: copy ĐÚNG khối "## Tiêu chí nghiệm thu (AC)" (không cắt nhầm sang section kế — kiểm tra fence-aware như ct_common? hay chỉ tới `## ` kế tiếp).
- Regression CT-025: `grep -c "preflight\|registry" .claude/skills/dispatch/SKILL.md` vẫn ≥1; không mất section Tool Preflight.
- Chạy ct-dispatch/ct-review-order thử trong /tmp sandbox (KHÔNG lên task thật).

## Review Toolchain
`cat .claude/review-toolchain.md` — theo registry (CT-025); meta-project markdown/python, không pytest CI → đọc script + chạy test sandbox.

## Trả kết quả
`/verdict CT-028 <pass|changes> --reviewer @gpt-5.6-sol [--commit 9bbf6f4] [--notes "..."]`
