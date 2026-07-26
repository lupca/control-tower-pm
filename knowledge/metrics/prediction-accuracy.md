---
title: "Pre-Execution Prediction Accuracy & Metrics"
type: metric
tags: [metrics, prediction, control-tower, accuracy]
created: 2026-07-22
updated: 2026-07-24
---

# Pre-Execution Prediction Accuracy & Metrics

> Biểu đồ & Nhật ký theo dõi độ chính xác của hệ thống Pre-Execution Prediction (CT-001).

## 1. Overview & Scoring Formula

Hệ thống dự đoán khả năng hoàn thành thành công của task (`predicted_success`) trước khi dispatch, dựa trên công thức scoring:

- **Base Score**: `1.0`
- **Deductions**:
  - `blast_radius > 8 files`: `-0.3`
  - `blast_radius > 15 files`: `-0.2` (tổng cộng `-0.5`)
  - `Hits hub/bridge node`: `-0.2`
  - `Similar tasks in log.md success rate < 50%`: `-0.3`
  - `No existing tests (tests: [])`: `-0.1`

**Phân loại (Classification)**:
- `high`: Score >= 0.7 (Kì vọng pass cao)
- `medium`: 0.4 <= Score < 0.7 (Rủi ro trung bình)
- `low`: Score < 0.4 (Rủi ro cao, đề xuất split/enrich)

**Quy tắc đánh giá In-Interval (`In Interval?`)**:
- Cột `In Interval?` được tính độc lập với `Match?` dựa trên `confidence_interval: [lo, hi]` từ frontmatter của task.
- Quy đổi outcome thực tế từ verdict: `pass` → `outcome = 1.0`, `changes` → `outcome = 0.0`.
- Đánh giá: `✅` nếu `lo <= outcome <= hi`, `❌` nếu nằm ngoài khoảng, `—` nếu task không khai báo `confidence_interval`.

---

## 2. Summary Statistics

| Metric | Value |
|:---|:---|
| **Total Predicted Tasks** | 55 |
| **Pass Count (Actual Success)** | 53 |
| **Changes Count (Actual Rework/Fail)** | 2 |
| **Overall Prediction Accuracy** | 78% (43/55) |
| **High Prediction Precision** | 97% (28/29) |
| **Medium Prediction Precision** | 100% (14/14) |
| **Low Prediction Precision** | 50% (1/2) |

---

## 3. Log History (Task Predictions vs Actual Outcomes)

`Confidence Interval` / `In Interval?` columns added per `AGENTS.md` §16.4 (CT-006, Confidence Calibration) — populated only for tasks that recorded a `confidence_interval:` at Spec Gate; older rows leave them blank rather than backfilled.

| Date | Task ID | Predicted Level | Score | Factors / Deductions | Confidence Interval | Actual Verdict | Match? | In Interval? |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| 2026-07-22 | CT-001 | high | 0.9 | blast_radius: 3 (-0.0), hub_bridge: false (-0.0), no_tests: true (-0.1) | — | pass | ✅ | — |
| 2026-07-22 | MVA-001 | low | 0.2 | blast_radius: 168 (-0.5), hub_bridge: true (-0.2), no_tests: false (-0.1) | [0.1, 0.4] | changes | ✅ | ✅ |
| 2026-07-24 | MVA-002 | high | 0.8 | code cũ còn trong git history, chỉ cần port (-0.0), không chạm hub node nào (-0.0), chưa có test cho module mới (-0.2); note: text2img restore — scope nhỏ, plan rõ | [0.7, 0.9] | pass | ✅ | ✅ |
| 2026-07-24 | MVA-003 | medium | 0.5 | scope lớn: toàn bộ slideshow_engine (audio_sync, hook_outro, visuals, pipeline) (-0.3), phụ thuộc MVA-002 (cần gen ảnh) (-0.1), chưa có test (-0.1); note: under-estimated — plan rõ, executor mạnh | [0.3, 0.6] | pass | ✅ | ✅ |
| 2026-07-24 | MVA-004 | high | 0.75 | nhiều fix nhỏ phân tán (-0.15), MoviePy v2 migration cần cẩn thận (-0.1); note: most ACs already done by MVA-008, only 1 remaining bug | [0.6, 0.85] | pass | ✅ | ✅ |
| 2026-07-24 | CT-023 | high | 0.9 | no_tests: true (-0.1) | — | pass | ✅ | — |
| 2026-07-24 | CT-024 | high | 0.8 | code (không chỉ markdown) nhưng khu trú 1 file script (-0.1), no_tests: meta-project, chỉ validate bằng sandbox thủ công (-0.1); note: pass nhưng sau 3 round (2 reject) — predicted high hơi lạc quan, rework nhiều | [0.7, 0.9] | pass | ✅ | ❌ |
| 2026-07-24 | CT-026 | high | 0.8 | code khu trú 1 script, đã có test harness sẵn (CT-024) (-0.1), no_tests suite CI, chỉ chạy tay/sandbox (-0.1) | [0.7, 0.9] | pass | ✅ | ❌ |
| 2026-07-24 | CT-025 | high | 0.9 | no_tests: meta-project, markdown files only (-0.1), blast_radius: 8 files (2 new) — at limit, coherent single architecture, no split (-0.0) | [0.75, 0.95] | pass | ✅ | ❌ |
| 2026-07-24 | CT-027 | high | 0.8 | refactor thuần, có test harness sẵn (-0.1), đụng ct-verdict-apply.py — script mutate state thật, cần cẩn thận (-0.1) | [0.7, 0.9] | pass | ✅ | ❌ |
| 2026-07-25 | PMI-011 | low | 0.3 | blast_radius: 104 files impacted, >15 (-0.5 cumulative), hits hub/bridge node: calculate_discount (hub+bridge), eval_variant_promotion_match (hub) (-0.2); note: pass sau 3 round (2 reject) — predicted low, cuối cùng pass sau khi thu hẹp scope (descope NLP parser theo quyết định User) | — | pass | ❌ | — |
| 2026-07-25 | CT-029 | high | 1.0 | — | — | pass | ✅ | — |
| 2026-07-25 | CT-028 | high | 0.75 | 2 script mới + sửa 2 skill + ADR — blast rộng hơn CT-027 (-0.15), no CI, chỉ sandbox (-0.1) | [0.65, 0.85] | pass | ✅ | ❌ |
| 2026-07-25 | CT-030 | high | 1.0 | có test, blast nhỏ (5 file, 2 new), không hub/bridge (-0.0) | [0.8, 0.98] | pass | ✅ | ❌ |
| 2026-07-25 | PMI-012 | medium | 0.5 | blast_radius: 142 files impacted (2-hop), >15 (-0.5 cumulative); note: root cause thật của báo cáo gốc user (PMI-011+WEB-005 pass nhưng không đủ) — verify độc lập qua browser thật xác nhận fix đúng | — | pass | ✅ | — |
| 2026-07-25 | WEB-006 | high | 0.7 | hits hub/bridge node not applicable (verification task, no core logic change expected) | — | pass | ✅ | — |
| 2026-07-25 | OMS-006 | medium | 0.5 | risk_high: -0.2 (security), multiple_files: -0.05, unresolved root cause: -0.15 (2 competing hypotheses for the live 500 — Fernet key mismatch vs system_configs.config_value schema drift — needs live diagnosis on both envs before fix), possible prod DB schema change: -0.1 (Project Gate: needs explicit User confirm before executor runs any ALTER/migrate, independent of bypass mode) | [0.35, 0.65] | pass | ✅ | ❌ |
| 2026-07-25 | OMS-010 | medium | 0.5 | blast_radius > 8: -0.3 (get_impact_radius: 128 file bị ảnh hưởng trong 2 hop), blast_radius > 15: -0.2 (cộng dồn -0.5), blast radius bị phóng đại: main.py là FastAPI entrypoint import toàn bộ routers, nên 2-hop traversal chạm gần hết OMS backend. Diện sửa thực tế nhỏ (bỏ create_all + ensure_zalo_otp_schema, thêm alembic scaffold)., không trừ hub/bridge: không file nào trong files: nằm trong get_hub_nodes(top_n=50)/get_bridge_nodes(top_n=50). Nhưng 2 bridge test NẰM TRÊN flow bị ảnh hưởng (test_storefront_otp_checkout_flow betweenness 0.0109, test_oms_admin_zalo_settings 0.0041) → đã đưa vào tests:., không trừ no-tests: đã có test hiện hữu cho SystemConfig/OTP., không trừ past-failure: OMS-001..006 đều pass. | [0.35, 0.65] | pass | ✅ | ❌ |
| 2026-07-25 | OMS-011 | medium | 0.5 | blast_radius > 8: -0.3 (get_impact_radius trên deploy_prod.sh + OMS/docker-compose.prod.yml: 49 file bị ảnh hưởng), blast_radius > 15: -0.2 (cộng dồn -0.5), không trừ hub/bridge: không file nào trong files: nằm trong get_hub_nodes/get_bridge_nodes(top_n=50)., không trừ no-tests: đã có test cho GET/PUT /api/configs/sms., rủi ro thật của task này KHÔNG nằm ở code mà ở dữ liệu prod (ciphertext không giải mã được nếu đổi key) — xem Project Gate. | [0.35, 0.65] | pass | ✅ | ❌ |
| 2026-07-25 | DEVOPS-001 | medium | 0.6 | IaC repo mới, chưa có test coverage (-0.1), Nhiều bước migration thủ công (-0.2), Ảnh hưởng production (-0.1) | — | pass | ✅ | — |
| 2026-07-25 | DEVOPS-002 | high | 0.75 | Ảnh hưởng production data (-0.15), Cần test với real data (-0.1) | — | pass | ✅ | — |
| 2026-07-25 | DEVOPS-003 | high | 0.8 | Production verification (-0.1), Multiple services to check (-0.1) | — | pass | ✅ | — |
| 2026-07-25 | WEB-011 | high | 0.85 | risk_high: -0.15 (sửa CORS gateway + app, ảnh hưởng mọi service; sai là chặn toàn bộ storefront), root cause đã VERIFY trực tiếp trên prod (đếm được header ACAO = 2), không phải giả thuyết ⇒ diện sửa rõ., không trừ blast_radius: sửa config CORS, không đụng logic., web frontend KHÔNG cần sửa dòng nào — đừng để executor đi lạc vào code web. | [0.7, 0.95] | pass | ✅ | ❌ |
| 2026-07-25 | OMS-015 | medium | 0.4 | blast_radius > 8 (110 files in graph, but fix is scoped to 1-2 files): -0.3, blast_radius > 15: -0.2, no existing tests for customers.py: -0.1 | — | pass | ✅ | — |
| 2026-07-25 | WEB-012 | high | 0.8 | no existing tests for index.ts: -0.1, simple cleanup, low risk: -0.0, depends_on OMS-015 (must deploy first): -0.1 | — | pass | ✅ | — |
| 2026-07-26 | CTV2-001 | high | 0.85 | Greenfield project, no legacy constraints (+0.1), Standard SQLAlchemy patterns (+0.0) | — | pass | ✅ | — |
| 2026-07-26 | CTV2-006 | high | 0.8 | Chainlit well-documented (+0.05), LangGraph native integration (+0.1), UI customization may need work (-0.1) | — | pass | ✅ | — |
| 2026-07-26 | CTV2-008 | high | 0.85 | Standard Docker patterns (+0.05) | — | pass | ✅ | — |
| 2026-07-26 | CTV2-002 | high | 0.85 | Standard FastAPI patterns (+0.0) | — | pass | ✅ | — |
| 2026-07-26 | CTV2-003 | medium | 0.7 | New framework (LangGraph) learning curve (-0.15), Complex state management (-0.1), Well-documented framework (+0.05) | — | pass | ✅ | — |
| 2026-07-26 | CTV2-004 | medium | 0.65 | Core business logic (-0.15), LLM integration needed for some gates (-0.1), Four-eyes enforcement critical (-0.1) | — | pass | ✅ | — |
| 2026-07-26 | CTV2-005 | medium | 0.7 | MCP protocol complexity (-0.15), Existing MCP server available (+0.1), Network/subprocess handling (-0.1) | — | pass | ✅ | — |
| 2026-07-26 | CTV2-007 | high | 0.85 | Streamlit very simple (+0.1), View-only, no complex state (+0.05) | — | pass | ✅ | — |
| 2026-07-26 | CTV2-009 | medium | 0.7 | E2E tests complex (-0.15), LLM mocking needed (-0.1) | — | pass | ✅ | — |
| 2026-07-26 | OMS-007 | medium | 0.65 | risk_high: -0.2 (concurrency), complex_logic: -0.15 | — | pass | ✅ | — |
| 2026-07-26 | WMS-004 | medium | 0.65 | risk_high: -0.2 (concurrency), complex_logic: -0.15 | — | pass | ✅ | — |
| 2026-07-26 | OMS-008 | high | 0.8 | — | — | pass | ✅ | — |
| 2026-07-26 | OMS-009 | high | 0.85 | schema_change: -0.15 | — | pass | ✅ | — |
| 2026-07-26 | CTV2-041 | — | — | — | — | pass | — | — |
| 2026-07-26 | CTV2-037 | — | — | — | — | pass | — | — |
| 2026-07-26 | CTV2-043 | — | — | — | — | pass | — | — |
| 2026-07-26 | CTV2-042 | — | — | — | — | pass | — | — |
| 2026-07-26 | CTV2-045 | — | — | — | — | pass | — | — |
| 2026-07-26 | CTV2-044 | — | — | — | — | pass | — | — |
| 2026-07-26 | CTV2-046 | — | — | — | — | pass | — | — |
| 2026-07-26 | CTV2-047 | — | — | — | — | pass | — | — |
| 2026-07-26 | CTV2-051 | — | — | — | — | pass | — | — |
| 2026-07-26 | CTV2-052 | — | — | — | — | pass | — | — |
| 2026-07-26 | CTV2-053 | medium | 0.65 | cross-cutting concern, touches coordinator core (-0.15), requires LLM API changes for cache_control (-0.1), needs token measurement instrumentation (-0.1) | [0.5, 0.7] | pass | ✅ | ❌ |
| 2026-07-27 | CTV2-056 | high | 0.75 | touches Session model (-0.15), migration complexity (-0.1) | — | pass | ✅ | — |
| 2026-07-27 | CTV2-057 | high | 0.75 | new UI components (-0.15), state management (-0.1) | — | pass | ✅ | — |
| 2026-07-27 | CTV2-059 | high | 0.9 | research task, no code blast radius (-0.0), greenfield project, no existing patterns to conflict (-0.0), no tests required for research (-0.1) | — | pass | ✅ | — |
| 2026-07-27 | CTV2-063 | high | 0.9 | research task, no code changes (-0.0), external library evaluation (-0.1) | — | pass | ✅ | — |
| 2026-07-27 | CTV2-061 | high | 0.9 | no deductions — blast_radius: 7, within limit | — | pass | ✅ | — |
| 2026-07-27 | CTV2-065 | high | 1.0 | — | — | changes | ❌ | — |
