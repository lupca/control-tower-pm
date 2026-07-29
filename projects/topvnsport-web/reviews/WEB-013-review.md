---
id: WEB-013
task_path: projects/topvnsport-web/tasks/WEB-013-split-web-repo-gateway-cleanup.md
project: topvnsport-web
result_ref: 9599b4da
executor: @gpt-5.6-sol
reviewer: "@claude-opus"
status: passed
issued: 2026-07-29
verdict: pass
verdict_date: 2026-07-29
---

# Phiếu Review: WEB-013 — Split web to separate repo + gateway cleanup + CI/CD for new repo

- Dự án: topvnsport-web (`/home/lupca/projects/topvnsport.com`)
- Task gốc: `projects/topvnsport-web/tasks/WEB-013-split-web-repo-gateway-cleanup.md`
- Result-ref: 9599b4da
- Executor: @gpt-5.6-sol
- Reviewer: @claude-opus-4.5
- Ngày phát phiếu: 2026-07-29

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

### Part A: Gateway Cleanup (monorepo topvnsport)
- [ ] Remove `web_frontend` upstream from `gateway/nginx/conf.d/upstream.prod.conf` (lines 44-46)
- [ ] Update `gateway/nginx/conf.d/locations.prod.conf` — topvnsport.com server block: redirect to Vercel URL OR remove entirely (chọn redirect để không break bookmark)
- [ ] Update `gateway/nginx/conf.d/locations.http-prod.conf` — same: redirect topvnsport.com → Vercel
- [ ] Gateway restart không lỗi: `docker compose -f gateway/docker-compose.prod.yml config` pass

### Part B: CI Cleanup (monorepo topvnsport)
- [ ] Remove `web:` from paths-filter outputs in `.github/workflows/ci.yml` (line 35, 50-51)
- [ ] Remove `web-build` job (lines 283-320)
- [ ] Remove `web/docker-compose.prod.yml` validation (line 371)
- [ ] Remove `web-build` from `ci-success` job dependencies (lines 387, 399, 410)
- [ ] CI workflow runs without error on PR (no web/ path to trigger)

### Part C: New Repo CI/CD (topvnsport.com)
- [ ] Create `.github/workflows/ci.yml` với: lint (eslint), typecheck (tsc), test (vitest), build (vite)
- [ ] Vercel auto-deploy đã hoạt động (verify: push → preview deploy)
- [ ] Test workflow chạy pass trên PR

### Part D: Control-tower Registry Update
- [ ] Update `index.md` PROJECT REGISTRY: `topvnsport-web` repo_root → `/home/lupca/projects/topvnsport.com`

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: (none recorded)
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (xác nhận reviewer @claude-opus-4.5 ≠ executor @gpt-5.6-sol)

## Test gợi ý chạy trong repo code
- *(none recorded in task frontmatter)*

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict WEB-013 <pass|changes> --reviewer @claude-opus-4.5 [--commit <hash>] [--notes "..."]`
