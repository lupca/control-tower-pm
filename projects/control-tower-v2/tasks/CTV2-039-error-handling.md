---
id: CTV2-039
title: "Frontend: Error Handling + Toast Notifications"
status: done
priority: high
risk: low
deadline: 2026-07-30
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
depends_on: []
files:
  - frontend/src/components/ErrorBoundary.tsx
  - frontend/src/lib/toast.ts
  - frontend/src/lib/api.ts
  - frontend/src/App.tsx
  - frontend/package.json
tests:
  - Error boundary catches component crashes
  - Toast appears on API errors
  - Retry logic works for transient failures
  - User can dismiss toasts
created: 2026-07-26
effort: 6h
---

# CTV2-039: Error Handling + Notifications

> Phase 4 từ Frontend Strategy (CTV2-035)

## Scope

Add proper error handling và user notifications.

## Components

### 1. Install react-hot-toast
```bash
cd frontend && npm install react-hot-toast
```

### 2. Toast setup
```typescript
// frontend/src/lib/toast.ts
import toast from 'react-hot-toast';

export const showSuccess = (msg: string) => toast.success(msg);
export const showError = (msg: string) => toast.error(msg);
```

### 3. API client retry logic
```typescript
// frontend/src/lib/api.ts
// Add retry with exponential backoff
// Show toast on final failure
```

### 4. ErrorBoundary component
```typescript
// frontend/src/components/ErrorBoundary.tsx
// Catch React errors
// Show friendly error UI
// Report to console
```

### 5. App.tsx integration
```typescript
// Wrap routes in ErrorBoundary
// Add <Toaster /> at root
```

## AC

- [ ] AC1: react-hot-toast installed + Toaster in App
- [ ] AC2: API errors show toast
- [ ] AC3: Dispatch success shows toast
- [ ] AC4: ErrorBoundary wraps app
- [ ] AC5: Retry logic (3 attempts) in API client
