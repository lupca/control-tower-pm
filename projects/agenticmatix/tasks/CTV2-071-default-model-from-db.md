---
id: CTV2-071
title: "Fix Chat Page: Load Default Model from DB"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@claude-opus"
result_ref: "bf047f0"
depends_on: []
files:
  - frontend/src/components/chat/ChatPanel.tsx
  - frontend/src/components/chat/ModelSelector.tsx
flows: []
tests:
  - frontend/src/components/chat/ModelSelector.test.tsx
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "blast_radius: 2 (-0.0)"
    - "frontend state timing (-0.05)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-071: Fix Chat Page: Load Default Model from DB

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)
- [x] Chat page waits for API fetch before initializing model state
- [x] Default agent from DB is used (không fallback to hardcoded claude-sonnet-4)
- [x] User không cần re-select model khi vào chat page
- [x] Clear chat vẫn giữ default agent từ DB

## Verification
- Set kimi-k3 as default agent in DB
- Refresh chat page → model selector shows kimi-k3 immediately
- No error toast about retired claude-sonnet-4 model
- Clear chat → still shows kimi-k3

## Plan

**Root cause**: `ChatPanel.tsx` initializes state with hardcoded `DEFAULT_COORDINATOR_MODEL` before async fetch completes. Lines 61, 131-132, 218 reference this constant.

1. **Remove hardcoded fallback** in `ModelSelector.tsx`:
   - Remove `export const DEFAULT_COORDINATOR_MODEL = 'claude-sonnet-4-20250514'`
   - Export nothing as default, let it be `null` until fetched

2. **Update ChatPanel.tsx state initialization**:
   - Initialize `selectedModel` as `null` (not hardcoded)
   - Initialize `selectedProvider` as `null`
   - Show loading state while model is null

3. **Handle clear chat correctly**:
   - Line 131-132: Instead of `setSelectedModel(DEFAULT_COORDINATOR_MODEL)`, keep current model or re-fetch default

4. **Guard sendMessage()**:
   - Line 218: Don't send if `selectedModel` is null, show error instead

5. **Update tests**:
   - Update `ModelSelector.test.tsx` to remove `DEFAULT_COORDINATOR_MODEL` references
   - Test loading state before API fetch completes

## Sub-tasks
- [ ] Remove `DEFAULT_COORDINATOR_MODEL` export from ModelSelector.tsx
- [ ] Update ChatPanel state initialization to null
- [ ] Add loading/disabled state while model is null
- [ ] Fix clear chat to preserve or re-fetch default
- [ ] Guard sendMessage against null model
- [ ] Update tests
