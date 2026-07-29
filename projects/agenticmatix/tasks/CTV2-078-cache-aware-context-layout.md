---
id: CTV2-078
title: "Cache-aware context layout: tách snapshot khỏi prefix, bỏ cache_control Anthropic"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "46e2aee"
depends_on: []
files:
  - backend/app/services/context_hierarchy.py
  - backend/app/services/coordinator.py
flows: []
tests:
  - backend/tests/test_context_hierarchy.py
  - backend/tests/test_coordinator.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "budget_messages có edge case truncation (-0.1)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-078: Cache-aware Context Layout (ADR-001 Phase 1b)

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Thiết kế: `docs/adr/ADR-001-unified-tool-architecture.md` §D4, fix P2

## Bối cảnh

Snapshot động đang bị nối vào cuối message Global tier-1 trong `build_messages` → mỗi mutation project/task làm vỡ OpenAI prefix cache của toàn bộ phần sau (tool schemas + project context ≤25KB). `cache_control: ephemeral` là Anthropic-only, OpenAI adapter drop, nhưng `budget_messages` đang dùng sự hiện diện của nó để pin prefix.

## Tiêu chí nghiệm thu (AC)

- [x] Snapshot không còn append vào message Global; phát thành message riêng đặt SAU Project tier, TRƯỚC Task tier
- [x] Thứ tự volatility tăng dần: global (static) → project (semi-stable) → snapshot (dynamic) → task/session (dynamic)
- [x] Bỏ phát `cache_control` trong `build_messages`; prefix pinning trong `budget_messages` chuyển sang flag tường minh `pinned: True` trên message
- [x] Messages gửi tới OpenAI adapter không chứa key `cache_control`/`pinned` (adapter strip hoặc build strip)
- [x] Hành vi compact/budget giữ nguyên với test hiện có

## Verification

- `pytest backend/tests/test_context_hierarchy.py backend/tests/test_coordinator.py -v` → xanh
- Test mới: gọi `build_messages` 2 lần với mutation task ở giữa → message Global + Project bytes không đổi (prefix ổn định), chỉ message snapshot đổi

## Plan

1. `build_messages`: tách `get_context_snapshot` thành message `{"role":"system","content":snapshot}` sau project tier.
2. Đánh dấu `pinned: True` cho global/project messages; sửa `budget_messages` check `pinned` thay vì `cache_control`.
3. Xoá phát `cache_control`; đảm bảo render adapter strip metadata.
4. Test prefix-stability như Verification.

## Sub-tasks

- [ ] Tách snapshot message
- [ ] pinned flag + budget_messages
- [ ] Bỏ cache_control
- [ ] Test prefix stability
