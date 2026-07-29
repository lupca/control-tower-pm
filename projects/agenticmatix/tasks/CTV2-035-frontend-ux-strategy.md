---
id: CTV2-035
title: "Frontend UX Strategy - Research & Architecture"
status: done
priority: critical
risk: low
deadline: 2026-07-28
executor: "@claude-opus"
reviewer:
type: research
files: []
created: 2026-07-26
---

# CTV2-035: Frontend UX Strategy - Research

## Mục tiêu

**Research task** - Nghiên cứu và đề xuất chiến lược frontend, KHÔNG implement.

## Phạm vi nghiên cứu

### 1. Kiến trúc hiện tại
- [ ] Audit frontend components hiện có
- [ ] Audit backend API endpoints
- [ ] Audit background services (Dramatiq, Redis, SSE)
- [ ] Map data flow: API → Store → Components

### 2. Gap Analysis
- [ ] So sánh với mục tiêu (giảm token, tăng chất lượng)
- [ ] Liệt kê features thiếu
- [ ] Liệt kê bugs/issues hiện tại

### 3. Library Evaluation
- [ ] SSE/Streaming: native EventSource vs libraries
- [ ] State management: Zustand hiện tại có đủ?
- [ ] UI components: cần thêm gì?

### 4. Đề xuất
- [ ] Component architecture mới
- [ ] API changes cần thiết
- [ ] Priority order cho implementation

## Output

Deliverable: `projects/control-tower-v2/docs/frontend-strategy.md`

Nội dung:
1. Current State Analysis
2. Gap Analysis  
3. Proposed Architecture
4. Implementation Roadmap (ordered tasks)
5. Library Recommendations

## AC

- [ ] AC1: Document phân tích kiến trúc hiện tại
- [ ] AC2: Document gap analysis
- [ ] AC3: Document đề xuất architecture + roadmap
- [ ] AC4: Tạo sub-tasks cho implementation (CTV2-036, 037, ...)
