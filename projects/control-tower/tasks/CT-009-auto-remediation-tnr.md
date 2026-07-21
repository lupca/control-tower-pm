---
id: CT-009
title: "Auto-Remediation với TNR Safety — Closed-loop tự động"
status: todo
priority: low
risk: high
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: [CT-003, CT-005]
files:
  - AGENTS.md
flows: []
tests: []
dispatched: null
in_review: null
created: 2026-07-22
updated: 2026-07-22
tier: 3
paradigm_source: "STRATUS (NeurIPS 2025)"
---

# CT-009: Auto-Remediation với TNR Safety — Closed-loop tự động

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (Context)

Hiện tại: Bug detected → human tạo task → executor fix → reviewer check.

Research: STRATUS introduces **Transactional No-Regression (TNR)** — AI can explore fixes autonomously if it can prove no regression. "82% incidents resolved without human intervention, MTTR -70%."

## Tiêu chí nghiệm thu (AC)

- [ ] AC1: Integration với monitoring/alerting:
  - Webhook từ Sentry/Datadog/custom monitoring
  - Alert → auto-create task với `source: auto-detected`
- [ ] AC2: Auto-diagnosis:
  - Parse error logs/stack traces
  - Query causal patterns (từ CT-003) cho likely root cause
  - Generate hypothesis với confidence
- [ ] AC3: TNR Sandbox:
  ```yaml
  tnr_spec:
    invariants:
      - "All existing tests must pass"
      - "No new critical/high severity issues"
      - "Response time p99 not increase > 10%"
    rollback_trigger: "Any invariant violated"
  ```
- [ ] AC4: Auto-remediation flow:
  ```
  Alert detected
      ↓
  AI diagnoses + generates fix
      ↓
  TNR sandbox runs fix:
    - Deploy to staging
    - Run full test suite
    - Compare metrics
      ↓
  If all invariants hold:
    - Auto-commit + auto-verdict (với flag `auto_remediated: true`)
    - Human notified but không block
  If any invariant fails:
    - Rollback
    - Escalate to human với diagnosis + attempted fix
  ```
- [ ] AC5: Audit trail đầy đủ cho mọi auto-remediation

## Plan

*(Điền khi Plan Gate)*

## Sub-tasks

- [ ] Design alert webhook integration
- [ ] Auto-diagnosis từ stack traces
- [ ] TNR spec format và checker
- [ ] Sandbox environment setup (staging deploy)
- [ ] Auto-commit flow với proper audit
- [ ] Escalation logic

## Research References

- [STRATUS: Multi-Agent Autonomous SRE (NeurIPS 2025)](https://neurips.cc/virtual/2025/poster/116834)
- [HolmesGPT — Agentic SRE (CNCF 2025)](https://www.cncf.io/blog/2026/01/07/holmesgpt-agentic-troubleshooting-built-for-the-cloud-native-era/)
- [GitHub Copilot Coding Agent](https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/)
