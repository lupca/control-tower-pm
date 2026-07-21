---
type: decision
scope: general
created: 2026-07-22
updated: 2026-07-22
tags: [architecture, control-tower, paradigm-shift, research]
related: [[ADR-001-file-over-api]]
---

# ADR-002: Paradigm Shifts Roadmap — 10 hướng cải tiến đột phá cho control-tower

## Context

Sau khi hệ thống control-tower đã ổn định với Model B (PLAN/COORDINATE only, EXECUTE/REVIEW outside), cần xác định các hướng phát triển tiếp theo.

Nghiên cứu so sánh với các hệ thống đối thủ (Devin, OpenHands, MetaGPT, CrewAI, AutoGen, LangGraph) cho thấy control-tower đã implement đúng nhiều best practices (four-eyes, hybrid code graph, structured handoffs). Tuy nhiên, những cải tiến incremental (confidence scoring, event stream logging) không đủ đột phá.

Nghiên cứu mở rộng sang 10 paradigm areas:
1. Goal-Oriented Autonomous Planning
2. Continuous Monitoring → Auto-Remediation
3. Formal Methods + AI
4. Multi-Agent Emergent Behavior
5. Learning from Execution History
6. Intent-Based Systems
7. Human-AI Collaboration 2.0
8. Cross-Repository Intelligence
9. Temporal/Causal Reasoning
10. Economic/Game-Theoretic Models

## Decision

Chọn 10 paradigm shifts có tiềm năng biến đổi hoàn toàn control-tower, chia thành 3 tiers:

### Tier 1 — Quick wins, high impact (2 tasks)
| Task | Paradigm | Why prioritize |
|------|----------|----------------|
| CT-001 | Pre-execution prediction | Chỉ cần analyze log.md history, không đổi flow |
| CT-002 | Reputation system | Track metrics đã có, enable smarter routing |

### Tier 2 — Medium effort, foundational (4 tasks)
| Task | Paradigm | Why medium |
|------|----------|------------|
| CT-003 | Causal analysis | Thêm fields, không đổi core flow |
| CT-004 | Cross-repo intelligence | Mở rộng graph queries, có sẵn `cross_repo_search_tool` |
| CT-005 | LLM-Modulo verifier | New component, nhưng pluggable trước gates |
| CT-006 | Confidence calibration | Depends on CT-001, dynamic gates logic |

### Tier 3 — Paradigm shift lớn (4 tasks)
| Task | Paradigm | Why complex |
|------|----------|-------------|
| CT-007 | Goal-conditioned autonomy | New entity type (Goal), thay đổi cách define work |
| CT-008 | Stigmergic coordination | Remove explicit dispatch, emergent behavior |
| CT-009 | Auto-remediation + TNR | Monitoring integration, sandbox infra |
| CT-010 | Vericoding formal proofs | New toolchain (Dafny/Lean), different verification model |

### Dependency graph
```
CT-001 (prediction)
   ↓
CT-006 (confidence) ←── CT-005 (verifier)
   ↓
CT-007 (goal autonomy)

CT-002 (reputation)
   ↓
CT-008 (stigmergy)

CT-003 (causal)
   ↓
CT-009 (auto-remediation)

CT-004 (cross-repo) — standalone
CT-010 (vericoding) — standalone
```

## Consequences

### Dễ hơn
- Roadmap rõ ràng với priorities và dependencies
- Mỗi paradigm có research references (academic papers, industry implementations)
- Có thể implement từng tier độc lập

### Khó hơn
- Tier 3 tasks là paradigm shifts thật sự — có thể cần refactor fundamental assumptions
- Một số paradigms (formal proofs, stigmergy) chưa có production examples trong SE domain
- Cross-dependencies giữa tasks có thể gây chờ đợi

### Trade-offs chấp nhận
- Ưu tiên Tier 1 + 2 trước, Tier 3 như research/POC
- Không commit deadline cho Tier 3 — chúng là "north star" directions
- Mỗi task có thể evolve khi industry best practices phát triển

## Research Sources

### Academic Papers
- [LLM-Modulo Framework (ICML 2024)](https://proceedings.mlr.press/v235/kambhampati24a.html)
- [STRATUS (NeurIPS 2025)](https://neurips.cc/virtual/2025/poster/116834)
- [Vericoding (Tegmark 2025)](https://arxiv.org/pdf/2509.22908)
- [MIT Conformal Prediction (2025)](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00715)
- [Causal Software Engineering Vision (2025)](https://arxiv.org/pdf/2605.02454)

### Industry Implementations
- [Devin (Cognition AI)](https://docs.devin.ai)
- [OpenHands SDK](https://arxiv.org/html/2511.03690v2)
- [ERC-8004 AI Reputation Standard](https://rnwy.com/blog/ai-reputation-systems)
- [HolmesGPT (CNCF)](https://www.cncf.io/blog/2026/01/07/holmesgpt-agentic-troubleshooting-built-for-the-cloud-native-era/)

## Status
Accepted
