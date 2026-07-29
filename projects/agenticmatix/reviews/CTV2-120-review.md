---
id: CTV2-120
task_path: projects/control-tower-v2/tasks/CTV2-120-fix-high-severity-bugs-prescan.md
project: control-tower-v2
result_ref: 912db309ca18f802eb42203e27fe9e67ebd7e6c3
executor: "@gpt-5.6-luna-high"
reviewer: "@gemini-3.1-pro-high"
status: passed
issued: 2026-07-28
verdict: pass
verdict_date: 2026-07-28
---

# Phiếu Review: CTV2-120 — Fix High-Severity Bugs from Pre-scan

- Dự án: Control Tower V2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-120-fix-high-severity-bugs-prescan.md`
- Result-ref: 912db309ca18f802eb42203e27fe9e67ebd7e6c3
- Executor: @gpt-5.6-luna-high
- Reviewer: @gemini-3.1-pro-high
- Ngày phát phiếu: 2026-07-28

## Acceptance Criteria cần verify

- [ ] `AgentDetail.tsx:82-83`: filter task theo executor/reviewer phải guard `t.id != null` (tránh null dereference).
- [ ] `AgentDetail.tsx:114-116`: bỏ fallback capabilities hard-code, hoặc lấy từ agent thật; không hiển thị dữ liệu giả khi `agent.capabilities` rỗng/không hợp lệ.
- [ ] `ProjectDetail.tsx:46-52`: khi fetch tasks lỗi, set `tasksError` state hiển thị banner cho user thay vì chỉ `console.warn`.
- [ ] `ProjectDetail.tsx:192`: khi `created_at` null, hiển thị "Unknown" thay vì fallback `Date.now()`.
- [ ] `Dashboard.tsx:133`: khi API lỗi, hiển thị banner lỗi cho user (không chỉ log console).
- [ ] Test `AgentDetail.test.tsx` khẳng định: với `tasks` chứa item `id: null`, component không throw và không hiển thị task đó trong executor/reviewer list.

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: `frontend/src/pages/__tests__/AgentDetail.test.tsx`
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @gpt-5.6-luna-high)

## Test gợi ý chạy trong repo code
```
cd /home/lupca/projects/control-tower-v2/frontend
npm test -- AgentDetail
npm test -- ProjectDetail
```

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc bạn tự đọc diff)
- `get_affected_flows_tool` trên 3 file (`AgentDetail.tsx`, `ProjectDetail.tsx`, `Dashboard.tsx`): 0 flow được graph track trực tiếp cho các page này — không loại trừ rủi ro, chỉ nghĩa là graph chưa map flow cấp UI; vẫn cần tự verify bằng test/tay.
- **⚠️ CẢNH BÁO QUAN TRỌNG (control-tower phát hiện trước khi review)**: executor báo cáo "Build blocked by existing `node_modules` permission issue" — nghĩa là executor **không tự chạy `npm run build` để xác nhận** thay đổi không vỡ build. Bắt buộc bạn tự chạy build.
- **⚠️ Nghi ngờ AC #5 (`Dashboard.tsx:133`) CHƯA được sửa**: commit `912db309` chỉ đổi `AgentDetail.tsx` + `ProjectDetail.tsx` + thêm test — không có `Dashboard.tsx` trong diff. Xác nhận rõ bằng `git show --stat 912db309ca18f802eb42203e27fe9e67ebd7e6c3` — nếu đúng là thiếu, verdict phải là `changes`.

## Review Toolchain
Chạy review theo repo's toolchain:
```
cat .claude/review-toolchain.md
```
Repo PHẢI khai báo toolchain. Với mỗi tool trong pipeline:
  - Preflight theo `knowledge/tools/tool-registry.md` (health_check → install nếu cần → re-check)
  - Tool required=hard mà preflight fail sau install → BLOCK + escalate, không review với partial tools
  - `/code-review` là baseline tool trong registry, chạy cùng (không thay thế) các tools khác
Chạy tất cả tools trong pipeline, aggregate kết quả, rồi verify từng AC item.

## Trả kết quả
Sau khi review xong, báo lại cho control-tower bằng lệnh:
`/verdict CTV2-120 <pass|changes> --reviewer @gemini-3.1-pro-high [--commit 912db309ca18f802eb42203e27fe9e67ebd7e6c3] [--notes "..."]`
