---
id: WMS-003
title: "Fix CI Docker Compose network label mismatch for oms_default"
status: done
priority: high
risk: normal
deadline: null
executor: "@antigravity"
reviewer: "@claude"
result_ref: "topvnsport@main (commit 76aace1)"
depends_on: []
files:
  - start_all.sh
  - .github/workflows/e2e.yml
  - OMS/docker-compose.yml
  - OMS/docker-compose.prod.yml
  - WMS/docker-compose.yml
  - PMI/docker-compose.yml
  - gateway/docker-compose.yml
flows: []
tests:
  - e2e_tests/tests/test_full_flow.py
dispatched: 2026-07-22
in_review: 2026-07-22
created: 2026-07-22
updated: 2026-07-22
---

# WMS-003: Fix CI Docker Compose network label mismatch for oms_default

> Dự án: [[projects/topvnsport-wms/topvnsport-wms]]

## Bối cảnh (Context)

GitHub Actions E2E workflow fails with:

```
network oms_default was found but has incorrect label com.docker.compose.network set to "" (expected: "default")
Error: Process completed with exit code 1.
```

**Root cause:** `start_all.sh` (lines 73-79) pre-creates Docker networks using `docker network create`:

```bash
docker network create pmi_default || true
docker network create oms_default || true    # <-- Problem
docker network create wms_default || true
...
```

Networks created this way lack the `com.docker.compose.network` label that docker-compose expects. When docker-compose later tries to use the OMS project's implicit default network (also named `oms_default`), it finds the existing network but with incorrect/missing labels, causing the failure.

**Why it happens now:** This is a race condition that depends on CI runner state. If a previous run left stale networks or if compose files changed how networks are referenced, the conflict surfaces.

## Tiêu chí nghiệm thu (AC)

- [x] E2E workflow (`e2e.yml`) passes on a clean CI runner (no stale networks)
- [x] E2E workflow passes on a CI runner with pre-existing networks from a previous run
- [x] Local `./start_all.sh` still works correctly for dev environment
- [x] All subsystems (PMI, OMS, WMS, web, gateway) can communicate across their shared networks

## Plan

### Analysis

Current network declarations across compose files:

| Project | Default network | Declaration |
|---------|-----------------|-------------|
| PMI | `pmi_default` | `default: {name: pmi_default, external: true}` ✅ |
| WMS | `wms_default` | `default: {name: wms_default, external: true}` ✅ |
| OMS | `oms_default` | **Not declared** — compose tries to CREATE it ❌ |
| Gateway | (creates its own) | `gateway_network: {driver: bridge}` ✅ |

**Root cause:** OMS doesn't explicitly declare its default network as `external: true`, so compose expects to create/manage `oms_default` itself. But `start_all.sh` pre-creates it with `docker network create`, which lacks compose labels.

### Fix Strategy

**Option chosen:** Make OMS match PMI/WMS pattern — explicitly declare default network as external.

### Steps

1. **`OMS/docker-compose.yml`** (line ~81, networks section):
   ```yaml
   networks:
     default:
       name: oms_default
       external: true
     pmi_default:
       external: true
     wms_default:
       external: true
     gateway_network:
       external: true
   ```

2. **`OMS/docker-compose.prod.yml`** — apply same fix if network section differs.

3. **Verify `start_all.sh`** — no changes needed; pre-creation of all 5 networks is correct since all compose files now expect them as external.

4. **Test locally:**
   ```bash
   # Clean slate
   docker network rm oms_default pmi_default wms_default gateway_network identity_default 2>/dev/null || true
   
   # Run startup
   ./start_all.sh --no-watch
   
   # Verify all services up
   docker ps
   ```

5. **Test CI scenario** (simulate stale network):
   ```bash
   # Create network without compose labels (simulating stale state)
   docker network create oms_default
   
   # Run startup — should NOT fail now
   ./start_all.sh --no-watch
   ```

## Sub-tasks

- [x] Identify which networks are truly "external" (shared between multiple compose projects) vs. which are project-default networks managed by compose
- [x] Update `start_all.sh` to only pre-create truly external/shared networks, NOT project-default networks like `oms_default`
- [x] Verify docker-compose files correctly declare `external: true` only for cross-project networks
- [x] (Optional) Add network cleanup step in E2E workflow before starting services
- [x] Test locally with `./start_all.sh` and in CI

## Notes

- **No direct unit tests** for `start_all.sh` — validation is via E2E tests passing
- The issue is intermittent based on CI runner state — may need to force-clean networks in CI for reliable reproduction
- Related docker-compose files to audit: OMS, WMS, PMI, gateway, web — all reference external networks
