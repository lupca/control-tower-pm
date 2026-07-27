---
agent_id: "@claude-opus-5-medium"
type: ai
model: claude-opus-5
effort: medium
total_tasks_executed: 0
total_tasks_reviewed: 4
success_rate: null
avg_review_rounds: null
strengths: [review, verification, diff-reading, test-running]
weaknesses: []
recent_trend: stable
last_active: 2026-07-27
---

# @claude-opus-5-medium

> Reviewer-tier profile: Claude Opus 5 chạy ở `medium` effort. Tạo 2026-07-27 theo chỉ định của user — **review** dùng profile này; research/kiến trúc dùng [[@claude-opus]] (Opus 4.5); thực thi code dùng [[@gpt-5.6-luna]], task phức tạp dùng [[@claude-sonnet-medium]].

## Spawn

```
cd <repo_root> && claude --model claude-opus-5 --effort medium -p '<prompt>' --dangerously-skip-permissions < /dev/null
```

**`--effort medium` là bắt buộc trong lệnh spawn.** Bỏ flag thì CLI chạy ở
effort mặc định và profile này trở nên vô nghĩa — đúng lỗi đã xảy ra ở lần
review CTV2-088 đầu tiên (2026-07-27).

## Performance Summary
*Chưa có dữ liệu lịch sử.*
