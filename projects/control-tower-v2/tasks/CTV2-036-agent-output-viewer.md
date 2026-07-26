---
id: CTV2-036
title: "Frontend: Agent Output Viewer + SSE Hook"
status: done
priority: critical
risk: medium
deadline: 2026-07-29
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
depends_on: [CTV2-031]
files:
  - frontend/src/lib/sse/SSEManager.ts
  - frontend/src/lib/sse/useAgentStream.ts
  - frontend/src/components/agent/AgentOutputViewer.tsx
  - frontend/src/components/agent/RunStatusBadge.tsx
tests:
  - SSE connection establishes on mount
  - Lines render in realtime
  - Auto-reconnect on disconnect
  - Status badge updates correctly
created: 2026-07-26
effort: 8h
---

# CTV2-036: Agent Output Viewer

> Phase 1 từ Frontend Strategy (CTV2-035)

## Scope

Xây dựng SSE infrastructure + component xem agent output realtime.

## Components

### 1. SSEManager (singleton)
```typescript
// frontend/src/lib/sse/SSEManager.ts
- Quản lý EventSource connections
- Dedup subscriptions
- Auto-reconnect với Last-Event-ID
- Close khi done
```

### 2. useAgentStream hook
```typescript
// frontend/src/lib/sse/useAgentStream.ts
export function useAgentStream(runId: string | null) {
  return { lines: string[], status: 'pending'|'running'|'done'|'failed' }
}
```

### 3. AgentOutputViewer component
```typescript
// frontend/src/components/agent/AgentOutputViewer.tsx
- Renders lines trong <pre>
- Auto-scroll to bottom
- Max height với overflow
- Copy button
```

### 4. RunStatusBadge component
```typescript
// frontend/src/components/agent/RunStatusBadge.tsx
- queued: gray
- running: blue + pulse
- success: green
- failed: red
```

## AC

- [ ] AC1: SSEManager connects to `/api/runs/{id}/stream`
- [ ] AC2: useAgentStream hook returns lines + status
- [ ] AC3: AgentOutputViewer renders output với auto-scroll
- [ ] AC4: RunStatusBadge shows correct colors
- [ ] AC5: Auto-reconnect hoạt động khi disconnect
- [ ] AC6: Connection closes khi component unmount

## References

- Backend SSE: `backend/app/api/stream.py`
- Strategy: `docs/frontend-strategy.md` Appendix A, B
