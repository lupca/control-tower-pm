# Phiếu Review: CT-002 Reputation System

> **Task:** [[projects/control-tower/tasks/CT-002-reputation-system]]
> **Executor:** @antigravity
> **Result Ref:** control-tower@main (commit 9183f6a)
> **Ngày phát phiếu:** 2026-07-22

---

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1:** Tạo `knowledge/agents/` directory với profile file cho mỗi executor/reviewer
- [ ] **AC2:** Profile format đúng schema (agent_id, type, success_rate, strengths, trend, etc.)
- [ ] **AC3:** `/verdict` auto-updates profile sau mỗi verdict
- [ ] **AC4:** `/pm` suggests executor based on task's `files:` matching agent strengths
- [ ] **AC5:** Warning nếu assign task to agent với low success_rate trong domain đó

---

## Definition of Done (DoD)

- [ ] Tất cả AC trên đều pass
- [ ] Profiles được bootstrap từ historical log.md
- [ ] AGENTS.md có §12 định nghĩa schema
- [ ] `reviewer:` khác `executor:` (four-eyes principle)

---

## Files cần review

| File | Thay đổi |
|------|----------|
| `AGENTS.md` §12 | Agent Reputation & Profile schema |
| `knowledge/agents/*.md` | 5 bootstrapped profiles |
| `.claude/skills/verdict/SKILL.md` | Auto-update profiles |
| `.claude/skills/pm/references/task-execution.md` | Executor suggestions |

---

## Test commands

```bash
# 1. Check agents directory exists with profiles
ls -la knowledge/agents/

# 2. Verify profile format
cat knowledge/agents/@antigravity.md

# 3. Check AGENTS.md has §12
grep -n "§12\|Agent Reputation" AGENTS.md
```

---

## Verdict

> **Reviewer:** @claude
> **Kết quả:** `pass`
> **Ghi chú:** All 5 ACs verified. 5 profiles bootstrapped, AGENTS.md §12 schema defined, verdict auto-updates, pm executor suggestions with warnings.
