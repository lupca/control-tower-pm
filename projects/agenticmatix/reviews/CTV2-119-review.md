---
id: CTV2-119
task_path: projects/control-tower-v2/tasks/CTV2-119-shadcn-ui-core-primitives.md
project: control-tower-v2
result_ref: eac9006b010f1615e93d16d9a99df6c88093f819
executor: "@gemini-3.6-flash"
reviewer: "@gemini-3.1-pro-high"
status: changes-requested
issued: 2026-07-28
verdict: changes
verdict_date: 2026-07-28
---

# Phiếu Review: CTV2-119 — Install shadcn/ui and Extract Core Primitives

- Dự án: Control Tower V2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-119-shadcn-ui-core-primitives.md`
- Result-ref: eac9006b010f1615e93d16d9a99df6c88093f819
- Executor: @gemini-3.6-flash
- Reviewer: @gemini-3.1-pro-high
- Ngày phát phiếu: 2026-07-28

## Acceptance Criteria cần verify

- [ ] Chạy shadcn/ui CLI để scaffold `frontend/src/components/ui/`, cấu hình đúng `tailwind.config.js` hiện có (không phá vỡ theme/dark-mode hiện tại).
- [ ] Tạo `StatCard` (icon, label, value, trend) tại `components/ui/stat-card.tsx`.
- [ ] Tạo `AlertBanner` (severity error/warning/info, message, retry action) tại `components/ui/alert-banner.tsx`.
- [ ] Tạo `StatusBadge` (status → color mapping) tại `components/ui/status-badge.tsx`.
- [ ] Test `stat-card.test.tsx` khẳng định: render đúng `label`/`value` truyền vào, và render đúng icon khi có prop `icon`.
- [ ] Không có regression: build frontend (`npm run build`) pass, không file page nào bị sửa trong task này (chỉ tạo primitives, chưa migrate — migrate ở CTV2-126/127).

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: `frontend/src/components/ui/__tests__/stat-card.test.tsx`
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @gemini-3.6-flash)

## Test gợi ý chạy trong repo code
```
cd /home/lupca/projects/control-tower-v2/frontend
npm test -- stat-card
npm run build
```

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc bạn tự đọc diff)
- `get_affected_flows_tool` trên 5 file (`package.json`, `tailwind.config.js`, `stat-card.tsx`, `alert-banner.tsx`, `status-badge.tsx`): 0 flow bị ảnh hưởng — component mới, chưa được page nào import/sử dụng, rủi ro thấp.
- Ghi chú thực thi quan trọng: executor **không sửa `package.json`/`tailwind.config.js` trực tiếp** như kế hoạch ban đầu, mà tạo `frontend/components.json` (config chuẩn của shadcn CLI) + `frontend/src/lib/utils.ts` (helper `cn()`). Hãy xác nhận đây là cách scaffold shadcn/ui hợp lệ (không phải executor lách AC), và rằng Tailwind/theme hiện tại thực sự không bị đổi (AC yêu cầu "không phá vỡ theme/dark-mode hiện tại").
- Task cố tình giới hạn "chưa migrate page nào" (migrate ở CTV2-126/127) — verify diff KHÔNG đụng vào bất kỳ file trong `frontend/src/pages/` hay `components/agents|projects|tasks|chat` nào.

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
`/verdict CTV2-119 <pass|changes> --reviewer @gemini-3.1-pro-high [--commit eac9006b010f1615e93d16d9a99df6c88093f819] [--notes "..."]`
