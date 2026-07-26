---
id: CTV2-052
task_path: projects/control-tower-v2/tasks/CTV2-052-coordinator-model-selector.md
project: control-tower-v2
result_ref: 65c5af4
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
status: passed
issued: 2026-07-26
verdict: pass
verdict_date: 2026-07-26
---

# Phiếu Review: CTV2-052 — Coordinator Model Selector UI

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-052-coordinator-model-selector.md`
- Result-ref: 65c5af4
- Executor: @gpt-5.6-luna-high
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-26

## Acceptance Criteria cần verify

- [ ] AC1: ModelSelector dropdown shows 4 model options
- [ ] AC2: Current session model displayed as selected
- [ ] AC3: Changing model calls PATCH /api/sessions/{id} with selected_model
- [ ] AC4: Chat messages sent with new model after switch
- [ ] AC5: Model switch persists across page refresh
- [ ] AC6: Provider icon shown next to model name
- [ ] AC7: Loading state shown during model switch API call

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: ModelSelector.test.tsx
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @gpt-5.6-luna-high)

## Files changed

- `frontend/src/components/chat/ModelSelector.tsx` (new)
- `frontend/src/components/chat/ModelSelector.test.tsx` (new)
- `frontend/src/components/chat/ChatInput.tsx` (modified)
- `frontend/src/components/chat/ChatPanel.tsx` (modified)
- `frontend/src/hooks/useChat.ts` (new)

## Test gợi ý chạy trong repo code

```bash
cd /home/lupca/projects/control-tower-v2/frontend
npm test -- ModelSelector.test.tsx
npm run build  # verify no TS errors
```

## Review Toolchain

Chạy review theo repo's toolchain:
```bash
cat .claude/review-toolchain.md
```

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:
```
/verdict CTV2-052 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]
```
