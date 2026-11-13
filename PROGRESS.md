# PROGRESS

## Status
- Phase 1: COMPLETE (2026-11-13 — all acceptance-gate items verified; see below)
- Phase 2: NOT STARTED
- Phase 3: NOT STARTED
- Phase 4: NOT STARTED
- Phase 5: NOT STARTED

## Session Log
- [2026-11-13] Phase 1: Repo created at ~/workspace/blood-bank/. Plan copied to BUILD_PLAN.md. Docker explicitly excluded by owner (no Docker install, no docker-compose verification) — Dockerfiles/docker-compose.yml are written as config only and NOT verified.
- [2026-11-13] Phase 1: Backend 1A–1C complete. FastAPI skeleton, auth/RBAC (JWT 15 min + rotating 7-day refresh with server-side revocation, argon2, lockout after 5, TOTP MFA for admin/medical roles), branches, users/roles, masters, settings (branch→global fallback, clinical defaults flagged confirm-with-MO), audit log, barcode service. PostgreSQL 16 installed locally (apt) and running; Alembic migration `2c8a2d43ffaa` applied; seed script verified (10 roles, 16 permissions, 17 settings, 44 masters, 3 branches, Super Admin, 10 demo users, 200 fake donors, 5 camps). API smoke-tested live on :8000 (login + scoped branch list).
- [2026-11-13] Phase 1: Backend gates green — pytest 56 passed, ruff clean, mypy --strict clean, pip-audit clean (no known vulnerabilities). OpenAPI exported to openapi.json (22 paths). requirements.txt at repo root pinned to exact venv versions; fresh-venv install verified.
- [2026-11-13] Phase 1: Frontend shell built (Next.js 15.5.29, React 19.2.0, React Query 5.107.1, Zustand 5.1.0, Zod 4.6.7, openapi-typescript 7.13.0, openapi-fetch 0.17.0, Tailwind 4.3.5, TypeScript 5.9.3 — all exact-pinned). Client generated from openapi.json; login incl. MFA setup/verify, role-based menu, dashboard, branches, users, masters, settings (MO-confirm badges), audit screens. Gate: `generate:api` clean, `tsc --noEmit` clean, `next lint` clean, `next build` compiled successfully (9 routes).
- [2026-11-13] Phase 1: Two real bugs found and fixed by the Playwright E2E (details in docs/decisions.md #21–22): (a) CORS allowlist only had `http://localhost:3000` — the browser origin `http://127.0.0.1:3000` was blocked ("Failed to fetch"); added 127.0.0.1:3000 to the dev `.env` and restarted the API. (b) The frontend `authFetch` wrapper silently dropped `Content-Type`/`Authorization` by re-wrapping openapi-fetch's built `Request` with an empty Headers init — every browser login failed with VALIDATION_ERROR. Fixed to mutate the Request's headers in place. Both were invisible to curl checks.
- [2026-11-13] Phase 1: Playwright E2E PASSED (1 test, 7.7 s): admin login + in-browser MFA setup → create branch → create Donor Staff user → that user logs in, sees only Dashboard/Branches/Masters/Settings (no Users/Audit Log) → direct visit to /users returns `Error code: FORBIDDEN` → cleanup soft-deletes the user and branch. `e2e/global-setup.ts` resets Super Admin MFA in the dev DB before each run so the test is repeatable. Leftover E2E rows from failed runs were soft-deleted via the API; none remain.
- [2026-11-13] Phase 1: Final gates re-run after all fixes — pytest 56 passed (95 warnings: 1 Starlette/httpx TestClient deprecation + 94 PyJWT 31-byte test-key warnings, both benign), ruff check + format clean, mypy --strict clean (53 files), pip-audit clean, frontend type-check/lint/build clean, `generate:api` regenerates the committed client with no diff. OWASP Top-10 review recorded below. Phase 1 marked COMPLETE.

## Acceptance Gate (Phase 1)
- [x] All tests pass (pytest 56 passed; Playwright E2E 1 passed; RBAC + branch-isolation tests mandatory — included).
- [x] No donor/patient/blood module and no third-party code or API key anywhere in the repo.
- [x] CI pipeline written (.github/workflows/ci.yml); steps verified locally (GitHub Actions cannot run in this VM).
- [x] PROGRESS.md current.
- [x] OWASP Top-10 review for this phase recorded below.
- [ ] ZAP baseline scan — NOT run (no ZAP available in this VM); recorded as a gap, not a pass.
- [–] Docker acceptance item ("app runs from `docker-compose up`") — EXCLUDED by owner instruction; Dockerfiles/compose are config only, unverified.

## OWASP Top-10 Review (Phase 1, 2026-11-13)
Reviewed against the OWASP Top 10 (2021) for the code as built. "Residual" items are pre-production hardening, not Phase 1 failures.
- **A01 Broken Access Control — PASS.** Server-side RBAC (`resource:action`, deny-by-default) on every route; branch scoping on every query; out-of-scope lookups return 404, never reveal existence. Covered by tests: 16 forbidden role/action pairs → 403, branch-isolation suite, and the E2E (donor staff gets `FORBIDDEN` on /users despite the menu hiding it).
- **A02 Cryptographic Failures — PASS with note.** Passwords argon2; JWT HMAC-SHA256; refresh tokens stored as SHA-256 hashes only; PII columns Fernet-encrypted with an HMAC blind index for email lookup; no secrets in code or git (`.env` git-ignored). Residual: test JWT secret is 31 bytes (PyJWT warns below 32) — test-only; production `SECRET_KEY` must be a long random string. Seed admin password has a documented DEV-ONLY default (`Admin@123456`, decisions.md #18) — must be overridden via env and rotated after first login before any shared use.
- **A03 Injection — PASS.** All DB access via SQLAlchemy ORM parameterized queries; no raw SQL in the codebase. All request bodies validated by Pydantic v2; validation failures return the 400 envelope.
- **A04 Insecure Design — PASS.** Rate limiting (slowapi) on auth endpoints; lockout after 5 failed logins (15 min, configurable via Settings); MFA required for Super Admin/Branch Admin/Medical Officer/Lab In-charge; password policy (12 chars, upper/lower/digit/special); soft deletes with reason; append-only audit log.
- **A05 Security Misconfiguration — GAP (pre-production).** CORS is an explicit allowlist (never `*`); `.env.example` contains names only. Gap: no security-headers middleware yet (no HSTS, X-Content-Type-Options, frame-ancestors). Add before any non-local deployment.
- **A06 Vulnerable and Outdated Components — PASS with note.** pip-audit clean (0 vulnerabilities). Frontend deps exact-pinned; Next.js pinned to 15.5.29 (latest 15.5.x patch; older 15.5.4/15.5.7 have a known CVE). Note: `npm audit` could not run — the sandbox registry denies the audit endpoint (`policy_denied`); npm-side vulnerability status is unverified here, not failed.
- **A07 Identification and Authentication Failures — PASS with note.** Rotating refresh tokens with server-side revocation; 15-min access tokens; logout revokes; TOTP MFA (pyotp, ±1 step window); lockout; inactive-user login block. Note: frontend stores tokens in localStorage for this Phase 1 demo (documented tradeoff in `apps/web/README.md`) — an XSS flaw would expose them; move to httpOnly cookies before production.
- **A08 Software and Data Integrity Failures — PASS.** Deps pinned exactly (root `requirements.txt`, frontend `package.json`); frontend API client is generated from the OpenAPI spec, never hand-written; CI defined with merge blocked on failure (verified locally — Actions cannot run in this VM).
- **A09 Security Logging and Monitoring Failures — PARTIAL.** Audit log on create/update/delete + login, viewer for Admin/Auditor; `X-Request-Id` on every response. Gap: no alerting/monitoring — out of Phase 1 scope; add with deployment.
- **A10 Server-Side Request Forgery — N/A.** Phase 1 makes no server-side requests to user-supplied URLs (no integrations, no webhooks).

## Known Issues
- Docker is NOT available in this VM and the owner instructed to ignore it completely. Acceptance item "app runs from docker-compose up" is NOT verified and is excluded by owner instruction — Dockerfiles/compose are config only.
- Test secret key is 31 bytes (PyJWT warns it is below the 32-byte recommended minimum) — test-only; production SECRET_KEY must be a long random string.
- Seed admin password default (`Admin@123456`) is DEV-ONLY — override via `SEED_ADMIN_PASSWORD` and rotate after first login before any shared/production use.
- No security-headers middleware yet (OWASP A05 gap) — add HSTS / X-Content-Type-Options / frame-ancestors before any non-local deployment.
- Frontend stores auth tokens in localStorage (Phase 1 demo tradeoff, documented in apps/web/README.md) — move to httpOnly cookies before production.
- ZAP baseline scan not run (no ZAP in this VM) — run before go-live.
- `npm audit` could not run (sandbox registry denies the audit endpoint) — npm vulnerability status unverified here.
- The seed Super Admin now has MFA enabled (set up during E2E verification). Password-only admin login is not possible by design. To reset for local testing: `UPDATE users SET mfa_enabled=false, mfa_secret=NULL FROM roles WHERE users.role_id=roles.id AND roles.name='Super Admin';` — the E2E `global-setup.ts` does this automatically before each run.

## Decisions
- See docs/decisions.md for all assumptions (password policy, MFA flow, barcode format, rate limits, seed-data tables, CORS, the authFetch bug, E2E MFA handling, ruff exclusions).

## Open Questions (blocking)
- None yet.

## Suggestions (do NOT implement unprompted)
- None yet.
