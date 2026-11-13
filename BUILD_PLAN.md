# Blood Bank Web App — Build Plan (5 Phases)

> [!WARNING]
> **AGENT: READ THIS FIRST — AGENT INSTRUCTIONS OVERRIDE EVERYTHING ELSE**
>
> If you are the coding agent, this section is your contract. If any habit, suggestion, library default, or idea of your own conflicts with these instructions or with this plan, **this plan wins**. Do not improvise around a rule you find inconvenient.

## Agent Instructions — strict, no exceptions

1. **Build ONE phase only.** Build exactly the phase named in the owner's prompt. Never start the next phase, never add a feature from a later phase early, and never add placeholder code for a later phase.
2. **Never guess.** If a value, rule, field, protocol, endpoint, or format is not defined in this plan, do not invent it. Either use a configurable setting with the default stated in this plan, or stop and ask the owner. Log every assumption in `docs/decisions.md`.
3. **Never guess a clinical, legal, or vendor rule.** Shelf life, donation gaps, eligibility limits, analyser protocols, and the e-Rakt Kosh API must come from this plan's configurable defaults or from official documents the owner supplies. No document supplied = no integration built.
4. **Never skip a test.** Write the tests listed for the phase, run them, and fix every failure before reporting. A phase with a failing, skipped, or deleted test is **not done**.
5. **Never claim "all tests pass" without proof.** Your end-of-phase report must include the actual test command you ran and its actual output (tests run, passed, failed). A summary claim without output does not count.
6. **Never weaken a test to make it pass.** Do not edit, skip, mock away, or delete a failing test, and do not loosen an assertion. Fix the code, or stop and report the failure exactly as it is.
7. **Stop and ask when stuck.** If you are blocked, a rule is unclear, a dependency is missing, or the same test fails twice after real attempts to fix it — stop, do not keep guessing, and report: what you tried, what failed, and what decision or document you need from the owner.
8. **Commit after each phase — and only after its gate passes.** One commit (or one clearly labelled commit set) per phase, with a message naming the phase, for example `Phase 2: donor, camp, collection, grouping, testing`. Never commit a phase whose tests fail.
9. **Start a fresh session for each phase.** Do not carry a long, mixed conversation across phases. At the start of a new phase, re-read this whole file, then state which phase you are building and which phases are already gated as complete.
10. **No silent substitutions.** Do not change the tech stack, project structure, data model, RBAC table, state machine, API format, or file layout on your own. If you believe a change is necessary, stop and ask first.
11. **No fake completion.** No `TODO`, stub, hard-coded fake response, or commented-out code may be presented as a finished feature. If something is incomplete, list it as incomplete in your report.
12. **End every phase the same way:** stop coding, run the full tests for this phase plus all earlier phases, and report — (a) what was built, (b) the actual test output, (c) the acceptance gate result item by item, (d) every assumption or skipped item in `docs/decisions.md`. Then wait. Do not continue on your own.
13. **PROGRESS.md is mandatory.** Every session starts by reading `PROGRESS.md` and ends by updating it (format in the PROGRESS.md section below). No session is complete until `PROGRESS.md` is updated.
14. **Test-first loop.** For each feature: write the failing test first, implement, make it pass, then re-run the entire suite for the current and all earlier phases.
15. **Small commits.** One logical change per commit. Message format: `phase<N>: <what>` — for example `phase1: add branch isolation tests`. Never mix two phases in one commit, and never commit a failing suite.
16. **No feature creep.** If you think of an improvement that is not in this plan, write it in `PROGRESS.md` under "Suggestions" — do not implement it unprompted.
17. **Third-party freeze.** Phases 1–3 contain no third-party integration code. Before Phase 4, integrations exist only as adapter interfaces with no-op / mock implementations. Implementing an integration early fails the phase.
18. **Read-then-write and dependency honesty.** Read a file fully before editing it. Before adding a dependency, verify the exact package name exists (PyPI / npm), is maintained, and is spelled correctly. If a command fails, report the real error — never claim success you did not observe.

### Rules for the owner — read before you hand this to an agent

- **Run the acceptance gate yourself. Do not trust the agent's "all tests pass" claim.** Open the app, run the phase's end-to-end flow with your own hands, and check the gate items one by one. The agent's report is a claim; your run is the proof.
- **Commit only after your own gate run passes.** If the gate fails, send the agent back to the same phase with the exact failure. Do not let it move on and "fix it later".
- **Give one phase prompt at a time**, using the copy-paste prompt at the end of that phase. Start a **fresh agent session** for each new phase and point it at this file again.
- **Never supply real donor or patient data** for testing, and never hand over a vendor or government protocol informally — supply the official document, or accept that the integration stays pending.

### Session starter checklist — agent, do this before writing any code

- [ ] I re-read this entire file in this session.
- [ ] I can name the one phase I am building, and I will build nothing outside it.
- [ ] I checked `docs/decisions.md` and the repo state for what earlier phases already built.
- [ ] Every value I need is either defined in this plan or will be a configurable setting. Anything missing, I will ask about — not invent.
- [ ] I read `PROGRESS.md` at the start of this session, and I will update it before I finish.
- [ ] I will work test-first and commit in small commits named `phase<N>: <what>`.

---

A step-by-step plan to give to any AI coding agent (Claude Code, Cursor, or similar). The agent builds **one phase at a time**, passes that phase's acceptance gate, and only then starts the next phase.

**Product in one line:** A web-based blood bank management system for hospital blood banks, standalone blood centres, multi-location networks, and accredited facilities in India — covering donor registration to transfusion, with full traceability.

**Phase order — do not change it:**

| Phase | Name | Third-party integrations? |
|---|---|---|
| 1 | Foundation | No |
| 2 | Donor side — donor, camp, collection, grouping, testing | No |
| 3 | Blood and patient side — components, inventory, crossmatch, issue, billing, reports | No |
| 4 | Hardening, deployment, SMS/WhatsApp, equipment interfacing | Yes — first integrations |
| 5 | e-Rakt Kosh, AI Auto Entry, UAT and go-live | Yes — final integrations |

Phases 1–3 are the complete core software. They must work, be tested, and be usable **without any third-party integration**. Phases 4–5 add integrations on top of the tested core.

---

## How to use this plan with a coding agent

1. Save this file in the project root as `BUILD_PLAN.md`.
2. Start the agent in that project folder.
3. Give the agent **only one phase prompt at a time** — copy-paste prompts are at the end of each phase and collected again at the end of this document. The standard owner prompt is: **"Read BUILD_PLAN.md and PROGRESS.md. Execute Phase N only."** (replace N with the phase number).
4. After each phase, **run the acceptance gate yourself — do not trust the agent's "all tests pass" claim.** Run the tests and the end-to-end flow with your own hands. Commit the code only when your own run passes.
5. Start a fresh agent session for each phase and point it at this file again. Never give the agent a prompt like "build the whole plan". It will skip tests, mix phases, and invent logic.

> [!WARNING]
> If any rule in this plan conflicts with a choice the agent wants to make on its own, this plan wins. If this plan does not define a value, the agent must add it as a **configurable setting with the default stated here** — never hard-code an invented value, and never invent a clinical, legal, or vendor protocol.

---

## PROGRESS.md — mandatory, every session

Create `PROGRESS.md` in the project root in Phase 1 and maintain it for the life of the project.

- **Every session starts by reading `PROGRESS.md`** and ends by updating it.
- The owner drives each session with: **"Read BUILD_PLAN.md and PROGRESS.md. Execute Phase N only."**
- `PROGRESS.md` never replaces the acceptance gate — the owner still runs the gate themselves.

Required format:

```markdown
# PROGRESS

## Status
- Phase 1: NOT STARTED / IN PROGRESS / COMPLETE
- Phase 2: NOT STARTED / IN PROGRESS / COMPLETE
- Phase 3: NOT STARTED / IN PROGRESS / COMPLETE
- Phase 4: NOT STARTED / IN PROGRESS / COMPLETE
- Phase 5: NOT STARTED / IN PROGRESS / COMPLETE

## Session Log
- [YYYY-MM-DD] Phase N: what changed, what is next

## Known Issues
- ...

## Decisions
- ... (mirror important entries in docs/decisions.md)

## Open Questions (blocking)
- ...

## Suggestions (do NOT implement unprompted)
- ...
```

---

## Global rules for the agent — read before every phase

1. **One phase at a time.** Do not write code for a later phase early. Do not add placeholder integrations.
2. **No invented clinical values.** Shelf life, donation gaps, eligibility limits, and alert thresholds in this plan are configurable defaults. Keep them in a settings table / config file, editable by an Admin, never hard-coded in business logic.
3. **No invented vendor or government protocols.** Analyser protocols (Phase 4) and the e-Rakt Kosh API (Phase 5) must come from official vendor / government documentation supplied by the project owner at that time. If the document is not supplied, build the adapter interface and a manual-entry fallback, and stop — do not guess the protocol.
4. **Server decides, frontend displays.** Eligibility, compatibility, expiry, stock status, and permissions are always computed on the server. The frontend never decides them.
5. **Nothing is ever hard-deleted.** Donors, units, patients, requests, and test results are soft-deleted or status-changed, with a reason. Every change writes an audit log entry.
6. **Every state change is timestamped automatically** by the server. Users never type in timestamps for workflow events. Turnaround time (TAT) is calculated only from these automatic timestamps.
7. **A blood unit's status changes only through the state machine** defined in Core logic. No direct status edits, no admin override that skips a state.
8. **Tests are part of the phase, not an extra.** A phase is not done until its listed tests pass and its acceptance gate passes.
9. **Stop and report at the end of each phase:** what was built, which tests pass, and the acceptance gate result. Do not continue to the next phase automatically.
10. **Money is integer paise.** Never store money as a float. Timestamps are stored in UTC; IST is applied only at UI display.
11. **Clinical defaults are not medical fact.** Where two sources disagree (see the clinical-conflicts note in Core logic §2 and §5), keep the value in Settings with a `rules_version`, label it "confirm with Medical Officer", and never present it in the UI as settled medical fact.
12. **Out of scope:** an online payments gateway is NOT a required feature of this plan. Billing in Phase 3 records bills and payment status manually. A gateway may be considered as optional future work only if the owner explicitly asks for it later.

---

## API response and error format — exact contract, never change it

Every API in every phase uses exactly these shapes. Frontend and backend must never invent a different shape for one endpoint. If a new field is needed, add it inside `data` — never change the outer shape.

### Success — single item

```json
{
  "success": true,
  "data": { "id": "d_01HXYZ", "name": "Example Donor", "bloodGroup": "A+" },
  "meta": { "requestId": "req_01HXYZ", "timestamp": "2026-01-15T10:30:00.000Z" }
}
```

### Success — list (always paginated)

```json
{
  "success": true,
  "data": [],
  "meta": {
    "requestId": "req_01HXYZ",
    "timestamp": "2026-01-15T10:30:00.000Z",
    "page": 1,
    "pageSize": 20,
    "total": 0,
    "totalPages": 0
  }
}
```

Query parameters for every list endpoint: `?page=1&pageSize=20` plus that endpoint's documented filters only. Default `pageSize` is 20, maximum is 100.

### Error — every error, no exceptions

```json
{
  "success": false,
  "error": {
    "code": "DONOR_NOT_ELIGIBLE",
    "message": "Donor is inside the minimum donation gap.",
    "details": { "nextEligibleDate": "2026-04-10", "reason": "MIN_GAP_WHOLE_BLOOD" },
    "requestId": "req_01HXYZ",
    "timestamp": "2026-01-15T10:30:00.000Z"
  }
}
```

Rules:

- `error.code` is a stable, uppercase, machine-readable string from a shared error-code list defined in the backend (`apps/api/app/core/errors.py`) and mirrored in the API contract. The frontend branches on `code`, never on the human-readable `message` text.
- `message` is for humans and may be reworded. `details` carries only the extra fields a screen needs to explain the error — never a stack trace, SQL, or internal path.
- Never return a raw framework error, an HTML error page, or a bare string from any endpoint.
- IDs are strings. Dates are `YYYY-MM-DD`. Timestamps are ISO 8601 UTC strings ending in `Z` (stored in UTC; IST only at UI display). **Money is an integer in paise, everywhere — never a float, never a decimal string.**
- This envelope is the Pydantic response schema in FastAPI (`success`, `data`, `meta` / `error`), so it appears in the OpenAPI spec and in the generated frontend client. Do not bypass it with a bare model return.
- `null` means "no value". Never use `""`, `0`, or `"N/A"` as a substitute for `null`.

| HTTP status | Use it only for |
|---|---|
| 200 | Successful read or update |
| 201 | Successful create |
| 400 | Validation failed — `code: VALIDATION_ERROR`, `details` lists the field errors |
| 401 | Not logged in, or token expired/invalid |
| 403 | Logged in but role or branch does not allow this action |
| 404 | Entity does not exist **in the caller's branch scope** — never reveal another branch's record exists |
| 409 | Illegal state transition, duplicate, or concurrent change — for example reserving a unit that is not `AVAILABLE` |
| 422 | Business rule blocked a well-formed request — for example `DONOR_NOT_ELIGIBLE`, incompatible crossmatch |
| 429 | Rate limit exceeded |
| 500 | Unexpected server error — log it server-side with `requestId`, return no internal detail |

---

## Tech stack — fixed, do not substitute without approval

| Layer | Choice | Notes |
|---|---|---|
| Frontend | Next.js (App Router) + TypeScript + Tailwind CSS + shadcn/ui | Web-based, responsive, works on desktop and tablet. **Next.js is locked — do not substitute React + Vite.** |
| Backend | FastAPI (Python 3.12+) | Modular — one router + service package per domain area below; Pydantic schemas for every request/response |
| Database | PostgreSQL | One database, every record carries `branch_id` |
| ORM / migrations | SQLAlchemy 2.x (or SQLModel) + Alembic | Models in Python; migrations are versioned and committed; Alembic is the only migration tool |
| Auth | JWT access token + refresh token, passwords hashed with bcrypt or argon2 (via `passlib` / `argon2-cffi`) | See Security |
| Cache / jobs | Redis + Celery (Celery Beat for schedules) | Expiry checks, alert jobs, report jobs, notification retries, sync retries — Phases 3–5 |
| Files | Local storage first, S3-compatible storage behind an interface | Certificates, reports, uploads |
| Barcode | Server-generated unique IDs, rendered as Code128 barcodes | Printed labels + USB barcode scanner input (keyboard mode) |
| Frontend data | React Query (server state) + Zustand (UI state only) | No server data in Zustand; no UI state faked through React Query |
| Frontend validation | Zod | Form validation on the frontend; Pydantic remains the server authority |
| Testing | Pytest + httpx (backend unit/API), Playwright (end-to-end, drives the Next.js frontend), k6 (load, Phase 4) | See Master testing plan |
| Lint / types (CI gates) | Ruff (lint + format) + `mypy --strict` (backend), TypeScript strict + ESLint (frontend) | All Python fully type-hinted; `mypy --strict` and Ruff must pass — see CI pipeline |
| Deployment | Docker + docker-compose | Same setup runs on cloud and on-premise |

> **Two languages, one contract — generated client is mandatory.** Types live in both TypeScript (frontend) and Python (backend, as Pydantic models). They are **not** shared code. The API contract in this plan — endpoint paths, the exact response/error shapes above, field names, and enums — is the single source of truth. **The frontend API client must be GENERATED from the FastAPI OpenAPI spec using `openapi-typescript` (plus the project's fetch client setup). Never hand-write frontend API types.** CI regenerates the client on every backend change and fails the frontend build if it does not compile against the new spec. The response envelope above is defined as a Pydantic schema so generation carries it through unchanged. Never hand-duplicate business logic (eligibility, compatibility, expiry, FEFO) in TypeScript — that logic lives only in Python on the server.

### Typing and code-generation rules (mandatory)

1. All Python code is fully type-hinted; **`mypy --strict` must pass** — CI fails otherwise.
2. Ruff (lint + format) must pass. No `# type: ignore` without an inline justification comment.
3. Generated client code lives in `apps/web/src/lib/api-generated/` (or the Phase 1 documented equivalent) and is **never hand-edited**. To change a type, change the Pydantic schema, regenerate, and fix the frontend compile errors.
4. Frontend forms validate with Zod; the server re-validates everything with Pydantic. A Zod pass is never a substitute for server validation.

### CI pipeline — set up in Phase 1, merge blocked on failure

GitHub Actions, in this order:

```text
ruff (lint + format check)
  -> mypy --strict
  -> pytest (unit + API)
  -> regenerate OpenAPI client (openapi-typescript)
  -> frontend type-check + build
  -> Playwright E2E (at each phase Definition of Done)
```

**Merge is blocked on any failing check.** Also run `pip-audit` and a ZAP baseline scan in CI / at phase gates — zero high-severity findings to merge (see Security).

If the agent's environment cannot use one of these, it must say so and ask — not silently switch stacks.

## Architecture

- **Monorepo, modular monolith.** One FastAPI backend, one Next.js frontend, one database. Do not build microservices. Multi-branch is handled by data scoping, not by separate deployments.
- **Multi-location from day one:** every business table has `branch_id`. A user sees only their branch by default. Head Office / Admin roles can see all branches for centralized reporting and inventory visibility. A standalone centre is simply a setup with one branch.
- **Module boundaries:** Python packages under `app/modules/`: `auth`, `branches`, `users_roles`, `masters`, `donors`, `camps`, `collections`, `grouping`, `testing`, `components`, `inventory`, `patients_requests`, `crossmatch_issue`, `apheresis`, `billing`, `reports`, `alerts`, `audit`, and in later phases `integrations/sms_whatsapp`, `integrations/analysers`, `integrations/eraktkosh`, `integrations/ai_auto_entry`. Each module has its own `router.py`, `schemas.py` (Pydantic), `models.py` (SQLAlchemy/SQLModel), and `service.py`. Modules talk through services, never by querying another module's tables directly from a router.
- **Integration adapter pattern (Phases 4–5 only):** every external system sits behind an adapter interface (a Python `Protocol` / abstract base class) with three implementations over time — `manual` (staff type the result), `mock` / no-op (for tests and for Phases 1–3), and the real vendor/government adapter. Core code never calls a vendor directly. **Every integration is feature-flagged per branch**, and every integration ships with a provider-outage test proving the core still works when the provider is down.
- **Environments:** dev → staging (seeded demo data) → production, using identical Docker images. Health endpoints: `GET /health` and `GET /health/db`. Logs are structured JSON.

## Project structure

```text
blood-bank-app/
  BUILD_PLAN.md                # this plan
  PROGRESS.md                  # mandatory session log — read first, update last
  .github/workflows/ci.yml     # ruff -> mypy --strict -> pytest -> regenerate
                               # client -> frontend build -> Playwright
  docker-compose.yml           # web, api, worker, postgres, redis
  .env.example                 # every env var, no real secrets
  apps/
    web/                       # Next.js frontend (TypeScript)
      src/app/                 # routes: login, dashboard, donors, camps,
                               # collections, testing, components,
                               # inventory, patients, requests, billing,
                               # reports, settings, admin
      src/components/          # shared UI: tables, forms, barcode, status badges
      src/lib/                 # api client, auth helpers, formatters
        api-generated/         # GENERATED by openapi-typescript from the
                               # FastAPI OpenAPI spec — never hand-edit
    api/                       # FastAPI backend (Python)
      app/
        main.py                # FastAPI app factory, router registration
        core/                  # config, security, errors, deps, audit dep
        db/                    # SQLAlchemy engine, session, base model
        modules/               # one package per module listed above
                               # each: router.py, schemas.py, models.py,
                               #       service.py
        workers/               # Celery app, tasks (expiry, alerts, reports)
      alembic/                 # Alembic migrations (versioned, committed)
        versions/
      tests/                   # Pytest: unit + API (httpx) tests
      pyproject.toml           # deps: fastapi, uvicorn, sqlalchemy,
                               # alembic, pydantic, celery, redis, pytest
      seed.py                  # roles, masters, one demo branch, admin user
  docs/
    decisions.md               # agent records every assumption here
    runbook.md                 # backup, restore, deploy steps (Phase 4)
  openapi.json                 # exported FastAPI spec (commit it)
```

---

## Data model — core entities

Build these entities across the phases as noted. Every entity has `id`, `branch_id` (where applicable), `created_at`, `created_by`, `updated_at`, and `deleted_at` (soft delete).

| Entity | Phase | Key fields and rules |
|---|---|---|
| Branch | 1 | Name, code, address, licence details, storage-centre flag |
| User, Role, Permission | 1 | See RBAC table; a user belongs to one or more branches |
| Setting | 1 | Key–value, per branch with global fallback; holds all thresholds |
| AuditLog | 1 | User, action, entity, entity id, old value, new value, timestamp, IP |
| Master data | 1 | Blood groups, component types, test names, deferral reasons, discard reasons, hospitals/wards, charges |
| Donor | 2 | Unique donor ID, name, date of birth, gender, blood group, contact, address, ID proof reference; duplicate check on mobile + date of birth |
| DonorDeferral | 2 | Donor, reason, type (temporary/permanent), from date, until date, decided by |
| Camp | 2 | Organizer, venue, date, target units, linked branch, status |
| Donation / Collection | 2 | Donor, camp or in-house, bag number (barcode), volume, collected by, collected at, donation type (whole blood / apheresis) |
| Sample | 2 | Linked to collection, sample barcode, received at lab timestamp |
| GroupingResult | 2 | Forward/reverse grouping, final blood group, optional subphenotype fields (E, e, K, k, Kell — used fully in Phase 3), done by, verified by |
| TestResult | 2 | Sample, test (TTD panel), method, result (reactive / non-reactive), done by, verified by |
| BloodUnit | 2–3 | Unit barcode, source collection, component type, blood group, status (state machine), expiry at — **computed by the system, never typed by a user** |
| ComponentSplit | 3 | Parent unit, child units created, prepared by, prepared at |
| QuarantineRecord | 3 | Unit, reason, released/discarded by, at, remarks |
| InventoryTransfer | 3 | Unit, from branch/storage centre, to branch/storage centre, status |
| Patient | 3 | Patient ID, name, age/gender, hospital, ward, diagnosis reference |
| BloodRequest | 3 | Patient, component, group, units needed, urgency, needed by, status |
| Crossmatch | 3 | Request, unit, method, result (compatible / incompatible), done by |
| Issue | 3 | Request, unit, issued to, issued by, issued at, receiver acknowledgement |
| TransfusionRecord | 3 | Issue, start/end time, reaction (none / details), recorded by |
| ApheresisSession | 3 | Donor, procedure type, yield, eligibility check result, machine reference (manual in Phase 3) |
| Bill, BillLine | 3 | Patient or storage centre, request/issue link, charge, amount, payment status |
| Alert | 3 | Type, entity, message, severity, status (open / seen / resolved), created at |
| DonorCard, Certificate | 3 | Donor, public verification token, generated at |
| NotificationLog | 4 | Channel, recipient, template, status — written by integrations, read by core |
| ExternalSyncLog | 4–5 | System, entity, direction, payload reference, status, error |
| DonorEligibility / Deferral (extends DonorDeferral) | 2 | Type (permanent / temporary), reason, from/till date, decided by, **`rules_version`** — every eligibility check stores which rules version was applied |
| TATEvent | 2–3 | Entity, entity type, stage, automatic timestamp, branch, actor — one row per workflow stage; source for all TAT reporting |
| AlertEvent | 3 | Type (expiry / testing / eligibility / low_stock / test_failure / temp_excursion), severity, payload, created at, resolved at, resolved by |
| InventoryLocation | 3 | Branch, type (fridge / freezer / platelet agitator), temperature sensor reference, `temp_min`, `temp_max` |
| TemperatureLog | 3 | Location, recorded temperature, recorded at, in-range flag |
| StockTransfer (extends InventoryTransfer) | 3 | From branch, to branch, component/unit ids, status (`draft` / `in_transit` / `received`) |
| Crossmatch (extends row above) | 3 | Adds `allocated_at` and **`expires_at` — allocation hold defaults to 72 hours**, configurable in Settings |
| Setting / Config (extends Setting) | 1 | Key, JSON value, scope (global / branch), versioned — eligibility rules, expiry days, thresholds, TAT SLAs and the crossmatch hold live here |

### Mandatory database-level safety (non-negotiable)

- **Unique indexes:** `donor` donor ID / donor number, unit `barcode`, component code, patient ID / UHID. Barcodes are unique across all branches and never reused.
- **Foreign-key integrity everywhere.** No orphan records are allowed.
- **AVAILABLE safety rule at the database level:** implement a CHECK constraint, trigger, or database verification function (with tests) so that a component / unit with status `AVAILABLE` cannot exist unless **all mandatory TTI TestResults for its donation are non-reactive (negative) AND verified**. Application code enforces this too — the database rule is the second line of defence, not a replacement.
- **Data-integrity assertion script** (run in tests and at every phase gate): orphan-record scan, barcode-uniqueness check, and a scan proving no `AVAILABLE` component exists without verified negative tests. Any finding fails the gate.

## Roles and permissions (RBAC)

Enforce permissions on the **server on every API call**, not only by hiding buttons in the frontend.

| Role | Can do | Cannot do |
|---|---|---|
| Super Admin | All branches, settings, users, roles, masters | — |
| Branch Admin | Own branch setup, users, masters, reports | Other branches' data, global settings |
| Medical Officer | Approve/reject donor eligibility, deferrals, quarantine release, discard approval | Billing changes, user management |
| Donor Staff / Counsellor | Donor registration, camps, donor screening forms | Lab results, issue |
| Phlebotomist / Collection Staff | Collection entry, bag labelling | Test results, inventory release |
| Lab Technician | Grouping, TTD testing entry, component preparation | Issue, billing |
| Lab In-charge | Verify grouping/testing results, quarantine decisions with Medical Officer | User management |
| Issue / Store Staff | Crossmatch, reservation, issue, transfers, stock view | Donor/lab data entry |
| Billing Staff | Bills, payments, storage-centre billing | Clinical / lab actions |
| Viewer / Auditor | Read-only, reports, audit trail | Any create, edit, or status change |

Rules: a result is final only after **verification by a second authorised user** where this plan says "verified by". The same user cannot enter and verify the same result. Deny by default: if a role is not listed for an action, the API returns 403.

---

## Core logic — the agent must implement exactly this

### 1. Blood unit state machine

A unit moves only in this order. Any other transition is rejected by the API with an error.

```text
COLLECTED
  -> IN_TESTING
  -> QUARANTINED        (if any TTD result is reactive, grouping is unresolved,
                         or verification is pending)
  -> AVAILABLE          (only if grouping is verified AND all TTD results are
                         non-reactive AND verified)
  -> RESERVED           (linked to one approved request via crossmatch)
  -> ISSUED
  -> TRANSFUSED         (transfusion record completed)
Terminal states, reachable from AVAILABLE / QUARANTINED / RESERVED with a
recorded reason and authorised approval:
  -> DISCARDED, EXPIRED, TRANSFERRED_OUT (then received as stock at the
     destination branch through a transfer record)
```

- `EXPIRED` is set by a scheduled system job when `expiry_at` passes — never by a user clicking a button, and an expired unit can never be reserved or issued. **Expired units move to `DISCARD_PENDING` for the discard workflow — they are never auto-destroyed.** Discard requires an authorised role, a recorded reason, and a witness (see Phase 3).
- **Two-person quarantine release [CRITICAL]:** the user who prepared / quarantined a unit cannot be the user who authorises its release — preparer ≠ authorizer. Both identities are audit-logged.
- **Crossmatch allocation hold:** a reserved / allocated unit is held for **72 hours by default** (configurable in Settings, stored as `Crossmatch.expires_at`). On expiry of the hold, the reservation auto-releases per §1.
- A reactive unit can never become `AVAILABLE`. There is no override for this.
- Reservation auto-releases if the request is cancelled or the reservation timeout in Settings passes.

### 2. Donor eligibility — server-side check at registration and before collection

Configurable defaults (Admin-editable in Settings; the agent must seed these defaults and label them as defaults to confirm with the blood bank's Medical Officer before go-live):

- Minimum age 18, maximum age 65; weight at least 50 kg; haemoglobin at least 12.5 g/dL.

> **Clinical-conflict flag — confirm, do not assume:** sources differ on some values — for example female haemoglobin is stated as **11.5 g/dL in one source and 12.5 g/dL in another**. Neither value is presented here as medical fact. Seed one value as a configurable default in Settings, store the `rules_version` with every eligibility check, label the settings screen "Confirm with Medical Officer before go-live", and use whichever value the Medical Officer signs off. The same rule applies to every shelf-life and gap value in §5.
- Minimum gap: whole blood 3 months, platelet apheresis 48 hours with a monthly cap, plasma apheresis 2 weeks — all values from Settings, not hard-coded.
- A donor with an active temporary deferral, any permanent deferral, or a donation inside the minimum gap is **blocked from collection**. The system shows the reason and the next eligible date.
- Repeat donor recognition: search by mobile number and date of birth before creating a new donor. If a match exists, open the existing donor — never create a duplicate silently.

### 3. Testing and release rule

- TTD panel (seed as master data, editable): HIV, Hepatitis B, Hepatitis C, Syphilis, Malaria — plus any test the branch adds.
- Every test needs a result **and** a verifier before it counts. Pending or unverified results keep the unit in `IN_TESTING` / `QUARANTINED`.
- One reactive result quarantines the unit and raises an alert. Release from quarantine for a non-reactive reason (for example pending verification now completed) needs Lab In-charge or Medical Officer approval, recorded with a reason, **and must follow the two-person rule in §1: preparer ≠ authorizer, both audit-logged.**

### 4. Compatibility matrix — encode once, in Python on the server, use everywhere

Red cell compatibility (donor group → patient groups it can supply):

| Donor | Can supply red cells to |
|---|---|
| O− | All groups |
| O+ | O+, A+, B+, AB+ |
| A− | A−, A+, AB−, AB+ |
| A+ | A+, AB+ |
| B− | B−, B+, AB−, AB+ |
| B+ | B+, AB+ |
| AB− | AB−, AB+ |
| AB+ | AB+ only |

Plasma compatibility is the inverse pattern (AB is the universal plasma donor, O patients can receive from any group). Encode plasma, platelet, and cryoprecipitate rules as separate explicit tables in the same Python module — `apps/api/app/core/compatibility.py` — each covered by Pytest unit tests. Crossmatch and issue must call these tables via the API — no group logic written inside a frontend page, a TypeScript file, or a router. The frontend only displays the server's compatible / incompatible result; it must not duplicate the matrix.

### 5. Expiry — system-computed

`expiry_at` = collection (or preparation) time + shelf life from Settings for that component type. Seed shelf-life defaults per component (whole blood, PRBC, FFP, platelets, cryoprecipitate, SDP) as configurable values to be confirmed by the Medical Officer — the agent must not present seeded defaults as medical fact in the UI; label the settings screen "Confirm all values with your Medical Officer before go-live."

Configurable defaults to seed (confirm with Medical Officer — not medical fact): **WB / PRBC 35 days, FFP / Cryoprecipitate 1 year, Platelets / SDP 5 days.** If the Medical Officer confirms different values, change Settings only — never code.

- A **Celery Beat job runs every 30 minutes**: it flags units expiring within **≤ 7 days** (alert threshold, configurable) and moves expired units to `DISCARD_PENDING` (never auto-destroy).

### 6. Issue order — FEFO

When staff pick a unit for a compatible request, the system lists matching `AVAILABLE` units **first-expiry-first-out (FEFO)** by default. Staff can pick a different compatible unit only by recording a reason. Incompatible or non-available units are never offered.

### 7. TAT (turnaround time)

Every workflow step writes its timestamp automatically (as `TATEvent` rows): registered, collected, sample received, grouping done, testing verified, component ready, available, reserved, crossmatched, issued, transfused. TAT reports and bottleneck views are computed only from these timestamps. No manual time entry anywhere in the workflow. **Reports compute p50 and p90 stage-wise TAT and flag bottlenecks against configurable SLAs in Settings.**

### 8. Barcoding and traceability

- The server generates every barcode ID (donor card, sample, bag, unit, component). IDs are unique across all branches and never reused.
- Scanning a barcode anywhere opens that entity's full trace: donor → collection → tests → components → crossmatch → issue → transfusion. This trace view is a required screen, not a nice-to-have.
- Labels print from the browser print view in Phase 2; a dedicated label printer is a Phase 4 hardware item, not a core dependency.
- **HARD REQUIREMENT — 3-click trace:** any component must be traceable **forward to the transfused patient and backward to the donor within 3 clicks** from the dedicated Trace page. This is covered by an end-to-end test in Phase 3; if the trace takes more than 3 clicks, the test fails.

## Worked examples — copy this logic exactly

Do not re-derive these rules from the prose. Follow the worked example; if your code produces a different result for the same inputs, your code is wrong.

### Example 1 — Donor eligibility

Settings used (defaults from Core logic §2): minimum age 18, maximum age 65, weight at least 50 kg, haemoglobin at least 12.5 g/dL, whole-blood gap 3 months.

Donor: age 24, weight 54 kg, haemoglobin 13.2 g/dL, no deferral, last whole-blood donation 10 January 2026. Collection attempted 15 April 2026.

| Check | Input | Result |
|---|---|---|
| Age | 24, allowed 18–65 | Pass |
| Weight | 54 kg, minimum 50 kg | Pass |
| Haemoglobin | 13.2 g/dL, minimum 12.5 g/dL | Pass |
| Deferral | None active | Pass |
| Donation gap | Last donation 10 Jan 2026 + 3 months = next eligible 10 Apr 2026; today is 15 Apr 2026 | Pass |

**Result: ELIGIBLE.** The server returns eligible, with every check listed.

Same donor, collection attempted 20 February 2026 instead: the gap check fails — 20 Feb 2026 is before 10 Apr 2026.

**Result: BLOCKED.** The API returns HTTP 422, `code: DONOR_NOT_ELIGIBLE`, `details.nextEligibleDate: "2026-04-10"`. No collection record is created. The frontend shows the reason and the next eligible date; it does not decide eligibility itself.

### Example 2 — Expiry calculation

Setting used for this example only: PRBC shelf life in Settings = 35 days. This is an example value taken from Settings, not a medical fact — the real value is whatever the Medical Officer confirms in Settings.

- Collection time (server timestamp, never typed by a user): `2026-01-01T10:00:00.000Z`
- Computation: `expiry_at = collection time + shelf life` = 1 Jan 2026, 10:00 UTC + 35 days
- **Stored `expiry_at`: `2026-02-05T10:00:00.000Z`**

The user never types, edits, or overrides `expiry_at`. At `2026-02-05T10:00:00.000Z` the unit is no longer issuable, and the scheduled job moves it to `EXPIRED`. A request to reserve or issue it after that moment returns HTTP 409.

### Example 3 — FEFO pick for a request

Request: 1 unit of PRBC for a patient with blood group A+. Compatible red-cell donor groups (from the matrix): A+, A−, O+, O−.

Units in the branch:

| Unit | Group | Expiry | Offered? |
|---|---|---|---|
| U-103 | A+ | 2026-02-20 | Yes — 2nd |
| U-101 | O+ | 2026-02-08 | **Yes — 1st, picked by default** |
| U-102 | A− | 2026-02-12 | Yes — 3rd |
| U-104 | B+ | 2026-02-06 | No — incompatible, never offered |
| U-105 | A+ | 2026-02-05 | No — status is `RESERVED`, not `AVAILABLE` |

**Default pick: U-101** — compatible, `AVAILABLE`, and earliest expiry (FEFO). Staff may pick U-102 or U-103 instead only by recording a reason. U-104 and U-105 must not appear as selectable options at all.

---

## Security — applies from Phase 1

- Passwords hashed with bcrypt or argon2 (`passlib` / `argon2-cffi`), never stored or logged in plain text. Minimum password policy and login rate-limiting from Phase 1. **Account locks after 5 failed login attempts** (threshold configurable in Settings).
- **MFA (TOTP) is required for Admin and Medical Officer roles** (Super Admin, Branch Admin, Medical Officer, Lab In-charge). Other roles may enable it voluntarily.
- JWT access tokens are **15 minutes** (issued with `PyJWT`), refresh tokens are **7 days, rotating** — each refresh issues a new refresh token and revokes the old one. A server-side **revocation list** is checked on refresh/logout; logout invalidates the refresh token.
- **Column-level encryption** for contact details (mobile, email, address) and medical notes, on top of transport encryption (TLS 1.2+ / HTTPS only) and database-at-rest encryption where the deployment supports it.
- **Strict CORS allowlist** — only the configured frontend origin(s); never `*` in any environment that holds real data.
- **Rate limiting** on auth endpoints and on write endpoints (429 per the API contract).
- **OWASP Top-10 review at every phase Definition of Done**, recorded in `PROGRESS.md`. `pip-audit` and a ZAP baseline scan must show **zero high-severity findings to merge**.
- **DPDP Act (India):** donor consent is captured at registration; retention periods live in Settings; consent and retention behaviour are never hard-coded without a Settings entry.
- All APIs require authentication except login and the public donor-card verification link (token-based, read-only, shows no contact details).
- Server-side RBAC check on every route (FastAPI dependencies); branch scoping on every query. A user must never receive another branch's records by changing an ID in a request — API tests must prove this.
- Validate and sanitise all input on the server with Pydantic schemas on every endpoint; parameterised queries only via SQLAlchemy — no raw SQL string building or f-string SQL.
- Encrypt sensitive fields at rest where the database supports it, serve only over HTTPS in deployment, and keep secrets only in environment variables — never in code, never committed. `.env` is git-ignored; `.env.example` carries names only.
- Audit log is append-only for normal users: no edit or delete API for audit entries.
- Daily automated database backup from Phase 4 deployment, with a tested restore — a backup that was never restored does not count.
- No real donor or patient data in seeds, tests, or screenshots. Test data is clearly fake.

---

## Phase 1 — Foundation

**Goal:** A running, secure, empty system: login, roles, branches, masters, settings, and audit — ready for business modules. No donor, patient, or blood features in this phase.

### Sub-steps (build in this order, check each one off in PROGRESS.md)

- **1A — Repo and runtime:** monorepo, Docker, Postgres, Redis, FastAPI skeleton, Next.js skeleton, `.env.example`.
- **1B — Auth and RBAC:** login / refresh / logout, users, roles, branch scoping, MFA and lockout.
- **1C — Platform masters:** branches, masters, Settings, audit log, barcode service.
- **1D — Contract pipeline:** OpenAPI export, generated frontend client, CI pipeline green end to end.

### Build

- Monorepo, Docker setup, database, migrations, and seed as per Project structure.
- **`PROGRESS.md` created** in the required format, and the **CI pipeline** (ruff → mypy --strict → pytest → regenerate OpenAPI client → frontend type-check + build → Playwright) running in GitHub Actions with merge blocked on any failure.
- **Seed script (training / UAT dataset):** all roles, master defaults, **3 demo branches, 200 fake donors, and sample camps** — clearly fake data only, used for training, staging and UAT. (Donor records are seeded as demo data for staging; no donor features are built in this phase.)
- Auth: login, logout, refresh, password policy, rate limiting, inactive-user block.
- Users, roles, and permissions exactly as the RBAC table; branch assignment per user.
- Branch CRUD and storage-centre flag; branch switching for multi-branch users.
- Masters CRUD: blood groups, component types, test names, deferral reasons, discard reasons, hospitals/wards, charges.
- Settings screen and settings API holding every configurable default from Core logic (eligibility, gaps, shelf life, reservation timeout, alert thresholds), each labelled as a default to confirm before go-live.
- Audit log: automatic logging via a FastAPI dependency / middleware and service-layer helper on create/update/status change, plus an audit viewer screen for Admin/Auditor.
- Barcode foundation: a server service that generates unique, never-reused IDs in one documented format, with a unit test for uniqueness across branches.
- Frontend shell: login page, layout with role-based menu (menu hides what the role cannot use **and** the API still blocks it), dashboard placeholder, branches, users, masters, settings, and audit screens.
- Seed: all roles, master defaults, demo branches and one Super Admin per the seed script above. Fake data only.

### Key APIs

`POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, CRUD for `/branches`, `/users`, `/roles`, `/masters/:type`, `GET/PUT /settings`, `GET /audit-logs`, `GET /barcodes/next` (internal service, not a public free-for-all).

### DO NOT — Phase 1

- Do NOT build any donor, patient, blood, billing, or integration feature in this phase.
- Do NOT hard-delete anything. There is no delete that removes a row — only soft delete with a reason.
- Do NOT enforce permissions only in the frontend. Hiding a menu is not security; every API route checks role and branch on the server.
- Do NOT put any secret, password, token, or API key in code, in a seed, or in git. Secrets live only in environment variables.
- Do NOT seed or test with real people's data. Fake names, fake numbers, fake records only.
- Do NOT change the tech stack, folder layout, or API response format to suit a library you prefer.
- Do NOT skip the branch-isolation tests. They are the most important tests in this phase.

### Tests for this phase

- Unit: password hashing, token expiry, barcode uniqueness, settings fallback (branch → global). **100% of the state-machine definition that exists so far is declared as data and unit-tested for legal vs illegal transitions as later phases add states.**
- Type and lint gates: `mypy --strict` and Ruff pass with zero errors; the generated frontend client regenerates and the frontend compiles against it.
- Security: `pip-audit` clean of high-severity findings; lockout after 5 failed attempts and MFA enforcement for admin/medical roles are tested.
- API: login success/failure, 403 for every role/action pair the RBAC table forbids, branch isolation (user of Branch A gets no Branch B records), audit entry written on create and update.
- End-to-end: login → create branch → create user → that user logs in and sees only permitted menus.

### Acceptance gate — all must pass before Phase 2

- App runs from `docker-compose up` on a clean machine using only `.env.example` as the guide.
- All tests above pass. RBAC and branch-isolation tests are mandatory, not optional.
- No business module (donor/patient/blood) exists yet, and no third-party code or API key exists anywhere in the repo.
- CI is green on the full pipeline, `PROGRESS.md` exists and is current, and the OWASP Top-10 review for this phase is recorded.

### Copy-paste prompt — Phase 1

> Read BUILD_PLAN.md and PROGRESS.md. Execute Phase 1 only — Foundation. Do not build any donor, patient, blood, billing, or integration features. Follow the tech stack, project structure, RBAC table, and security rules exactly. Set up PROGRESS.md and the CI pipeline (ruff → mypy --strict → pytest → regenerate OpenAPI client → frontend build → Playwright) in this phase. Seed only fake data. Work test-first, commit small with `phase1: <what>` messages, write and run the tests listed for Phase 1, fix all failures, update PROGRESS.md, then stop and report: what you built, test results, and the acceptance gate result. Do not start Phase 2.

---

## Phase 2 — Donor side: donor, camp, collection, grouping, testing

**Goal:** The complete donor-to-tested-unit flow with manual lab entry: register a donor, collect blood at a camp or in-house, group it, test it, and land the unit in the correct state. No components, no patient features yet.

### Sub-steps (build in this order, check each one off in PROGRESS.md)

- **2A — Donor:** donor management, eligibility engine, deferral registry (with `rules_version`).
- **2B — Camp and collection:** camp CRUD, collection session, bag + sample barcodes, TAT stamps.
- **2C — Grouping:** forward/reverse grouping, second-user verification.
- **2D — Testing:** sample registry, manual TTI entry, verification, reactive → quarantine path.
- **2E — Domain review gate (below)** before any Phase 3 detail work starts.

### Build

- **Donor Management:** registration form (identity, contact, blood group if known, medical screening questionnaire as configurable master questions), duplicate check, donor profile with full donation history, eligibility check result shown with reasons, deferral recording (temporary/permanent, reason, until date, decided by Medical Officer), repeat-donor search.
- **Camp Management:** camp create/plan (organizer, venue, date, target), camp status (planned / active / closed), donor registration and collection linked to a camp, camp summary (registered, collected, deferred).
- **Collection:** eligibility re-check at collection (blocked donors cannot proceed), bag number generated and label printed, volume and collection time recorded automatically, donation creates one `BloodUnit` in `COLLECTED` and one linked `Sample`, each with its own barcode.
- **Grouping (Collection & Grouping module):** forward/reverse grouping entry, final group confirmation, second-user verification. A unit with unverified or conflicting grouping stays out of `AVAILABLE`. Advanced subphenotype fields (E, e, K, k, Kell) exist on the grouping record from this phase as optional fields, used fully in Phase 3 apheresis/antibody workflows.
- **Testing & Screening (manual entry):** TTD panel entry per sample, method field, result + separate verifier, reactive handling per Core logic §3. This phase is **manual entry only** — analyser interfacing is Phase 4. The result-entry API must be shaped so a Phase 4 adapter can call it unchanged.
- **Trace view v1:** scanning or entering a bag/sample barcode shows donor → collection → grouping → test status.
- **Frontend screens:** donor list/search, donor registration, donor profile, deferral form, camp list/detail, collection form, grouping worklist, testing worklist, verification queues, trace view. Worklists show oldest first and flag items waiting longest (TAT timestamps already recorded, reporting comes in Phase 3).

### Key APIs

CRUD + actions for `/donors`, `/donors/:id/eligibility`, `/donors/:id/deferrals`, `/camps`, `/collections`, `/grouping`, `/grouping/:id/verify`, `/testing`, `/testing/:id/verify`, `GET /trace/:barcode`.

### DO NOT — Phase 2

- Do NOT let the frontend decide eligibility. The frontend displays the server's eligibility result and reasons — it never computes them.
- Do NOT create a duplicate donor silently. A mobile + date-of-birth match opens the existing donor.
- Do NOT let the same user enter and verify the same grouping or test result. Verification is always a second authorised user.
- Do NOT ever make a reactive or unverified unit `AVAILABLE`. There is no override, no admin shortcut, and no direct status edit.
- Do NOT let a user type a workflow timestamp. Collection, grouping, and testing times are server timestamps.
- Do NOT auto-release a quarantined unit. Release needs the authorised approval and recorded reason defined in Core logic §3.
- Do NOT add any analyser, SMS, WhatsApp, e-Rakt Kosh, or AI code in this phase. Testing entry is manual only.

### Tests for this phase

- Unit: eligibility rules (under-age, low weight, low haemoglobin, inside gap, active deferral), duplicate detection, state transitions `COLLECTED → IN_TESTING → QUARANTINED / AVAILABLE`. **State-machine coverage rule: 100% of transitions — every legal transition works and every illegal transition is rejected — in this and every later phase.**
- Data integrity: the assertion script passes (no orphans, barcodes unique, no `AVAILABLE` unit without verified negative tests); the database-level AVAILABLE rule is tested by attempting a direct invalid state and proving it is rejected.
- API: collection blocked for a deferred donor; a reactive result can never produce `AVAILABLE`; same user cannot verify their own entry; unverified results keep the unit unavailable.
- End-to-end: camp created → donor registered → collected → grouped → tested non-reactive and verified → unit `AVAILABLE`; and a second flow where one test is reactive → unit `QUARANTINED` with an alert record created (alert display is Phase 3; the record is created now).

### Acceptance gate — all must pass before Phase 3

- **⛔ DOMAIN REVIEW GATE:** a human / Medical Officer sign-off is required on the testing and quarantine logic built in this phase (reactive handling, verification, quarantine release) **before Phase 3 starts**. Record the sign-off in `PROGRESS.md`. No sign-off = Phase 3 does not start.
- Both end-to-end flows above pass on a clean database.
- There is **no code path** — UI, API, or direct service call in tests — that makes a reactive or unverified unit available.
- No patient, component, inventory, billing, or integration features exist yet.

### Copy-paste prompt — Phase 2

> Read BUILD_PLAN.md and PROGRESS.md. Phase 1 is complete and its gate passed. Implement Phase 2 only — Donor Management, Camp Management, Collection, Grouping, and manual Testing & Screening, following the state machine, eligibility, and testing rules in Core logic exactly. Analyser interfacing is NOT in this phase; testing is manual entry shaped so an adapter can call the same API later. Do not build components, patients, inventory, billing, or integrations. Write and run all Phase 2 tests, fix failures, then stop and report results against the Phase 2 acceptance gate. Do not start Phase 3.

---

## Phase 3 — Blood and patient side, billing, reports, dashboards

**Goal:** The complete core application, still with **zero third-party integrations**: components, quarantine, live inventory, patient requests, crossmatch, issue, transfusion, apheresis, billing, registers, reports, TAT, in-app alerts, dashboards, and digital donor cards. After this phase the software is fully usable on its own.

### Sub-steps (build in this order, check each one off in PROGRESS.md)

- **3A — Components:** component preparation and per-type expiry.
- **3B — Inventory:** storage locations, temperature logs, two-person quarantine release, expiry scanner, discard workflow, stock dashboard.
- **3C — Patients and requests:** patient registry, requests (routine / urgent / emergency).
- **3D — Crossmatch and issue:** compatibility, 72-hour allocation hold, issue, returns, emergency issue — **⛔ domain review gate applies inside this sub-step (see Acceptance gate).**
- **3E — Multi-branch operations:** inter-branch transfers, consolidated reporting.
- **3F — Billing and reports:** rate cards, invoices (amounts in integer paise), statutory registers, CSV/PDF export.
- **3G — Intelligence (in-app only):** Live Stock Dashboard, TAT dashboards (p50/p90), Alert & Notification Desk, digital donor card / certificate, Trace page.

### Build

- **Components & Quarantine:** split one whole-blood unit into child components (PRBC, FFP, platelets, cryoprecipitate, plasma — from master data) with child barcodes and system-computed expiry per component; quarantine list with reasons, authorised release/discard workflow under the **two-person rule (preparer ≠ authorizer, both audit-logged)**, and discard recording (reason, approval, witness, method) — discarded units are terminal and audited.
- **Inventory Management:** live stock by branch, component, and group; states from the state machine only; expiry watch (units expiring within the Settings threshold), the 30-minute Celery Beat expiry scan from Core logic §5, expired units moving to `DISCARD_PENDING` (never auto-destroyed — discard needs an authorised role, a reason, and a witness); **storage locations (`InventoryLocation`) with temperature logs — a temperature out of range beyond the configurable threshold quarantines the affected units and raises an `AlertEvent`**; **low-stock thresholds per branch × component type × blood group**, with a breach raising an `AlertEvent`; inter-branch and storage-centre transfers (`draft` / `in_transit` / `received`) with dispatch/receive confirmation; stock ledger so every stock change can be explained from records.
- **Patient & Requests:** patient registration, blood request (component, group, units, urgency, needed-by), request approval, request status flow (requested → approved → reserved → issued → completed / cancelled).
- **Crossmatch & Issue:** compatibility check using the server-side Python compatibility matrix, crossmatch entry + result, FEFO unit suggestion with reason-required override, reservation with the **72-hour allocation hold (`expires_at`, configurable)**, issue with receiver details, return/cancel handling, and transfusion record (start/end, reaction). An incompatible crossmatch result blocks issue for that unit–request pair **on the server**.
- **Apheresis Management:** session recording for SDP, plasma, PBSC, and granulocyte procedures; donor eligibility check specific to procedure type (gap and caps from Settings); yield calculation (entered values, system-computed yield field); suitability tracking on the donor profile. Machine interfacing is **not** here — values are manual until Phase 4.
- **Billing & Reports:** charge master–based billing for patients and for storage centres, bill linked to issue, payment status, receipts; registers (donor register, collection register, testing register, component register, issue register, discard register) as filterable, exportable (CSV/PDF) reports; operational reports by branch and consolidated across branches for Head Office roles.
- **Live Stock Dashboard:** stock of Whole Blood, PRBC, FFP, Platelets, Cryo, SDP, and Plasma by group and branch, auto-refreshing, with expiry and shortage indicators against Settings thresholds.
- **TAT monitoring and analytics:** per-stage and end-to-end (registration → issue) TAT from automatic timestamps, **p50 and p90 per stage**, delay/bottleneck view flagging stages that breach configurable SLAs, filterable by branch, date range, and camp.
- **Alert & Notification Desk (in-app only in this phase):** alerts for expiring/expired units, low stock, reactive results, pending verifications, and eligibility events, on an alerts screen with open/seen/resolved flow. SMS and WhatsApp delivery of these alerts is Phase 4 — in this phase alerts exist only inside the app, and the alert service must expose one `notify()` interface that Phase 4 plugs delivery channels into.
- **Digital Donor Experience:** digital donor card (mobile-friendly page via a secure token link: donor name, group, donor ID, donation history) and a printable donation certificate (PDF) generated per donation.
- **Trace view complete (Trace page):** barcode scan shows the full chain including components, crossmatch, issue, and transfusion, meeting the **3-click hard requirement** in Core logic §8 (donor ↔ patient, both directions), covered by an E2E test.

### Key APIs

`/components/split`, `/quarantine`, `/quarantine/:id/release`, `/quarantine/:id/discard`, `/inventory`, `/inventory/transfers`, `/patients`, `/requests`, `/requests/:id/approve`, `/crossmatch`, `/issues`, `/transfusions`, `/apheresis`, `/bills`, `/reports/:type`, `/dashboard/stock`, `/reports/tat`, `/alerts`, `/donors/:id/card`, `/donations/:id/certificate`.

### DO NOT — Phase 3

- Do NOT offer, reserve, or issue an incompatible, expired, quarantined, discarded, or already-reserved unit. Incompatible and non-`AVAILABLE` units are not shown as selectable options.
- Do NOT write compatibility or FEFO logic inside a frontend page, a TypeScript file, or a FastAPI router. Use only the server-side Python compatibility matrix (`app/core/compatibility.py`) and the FEFO rule in Core logic, and follow Worked example 3.
- Do NOT allow a manual stock edit. Stock changes only through collection, split, transfer, issue, discard, and expiry records — so every number can be explained from the ledger.
- Do NOT discard a unit without an authorised approval, a recorded reason, and an audit entry. Discarded is terminal.
- Do NOT let a user type or edit `expiry_at`, or override the system-computed expiry. Follow Worked example 2.
- Do NOT issue more units than a request was approved for, and do NOT skip crossmatch to issue faster.
- Do NOT add any SMS, WhatsApp, analyser, e-Rakt Kosh, or AI code in this phase. Alerts stay in-app behind the `notify()` interface.

### Tests for this phase

- Unit: compatibility matrices (red cell and plasma tables, every row), FEFO ordering, expiry computation per component, split rules (child expiry never exceeds parent rules), yield calculation.
- API: incompatible unit cannot be reserved/issued; expired unit cannot be issued; discarded unit is terminal; transfer keeps stock totals consistent across branches; bill total equals charge master lines; a request cannot be issued more units than approved.
- End-to-end: full journey — donor → collection → testing → component split → available → patient request → crossmatch → FEFO issue → transfusion → bill — plus a quarantine-discard journey and an inter-branch transfer journey.

### Acceptance gate — all must pass before Phase 4

- **⛔ DOMAIN REVIEW GATE:** a human / Medical Officer sign-off is required on the crossmatch and issue logic (compatibility enforcement, 72-hour hold, emergency issue) **before that logic is treated as complete and before Phase 4 starts**. Record the sign-off in `PROGRESS.md`.
- The full-journey end-to-end test passes on a clean database, and the trace view shows every step of it from one barcode scan **within 3 clicks in each direction**.
- Dashboard stock numbers match a hand-checked count from the test data; TAT figures match the recorded timestamps.
- The app contains **no** SMS, WhatsApp, analyser, e-Rakt Kosh, or AI code, keys, or endpoints. A staff member could run a blood bank on this build with manual entry alone.

### Copy-paste prompt — Phase 3

> Read BUILD_PLAN.md and PROGRESS.md. Phases 1–2 are complete and their gates passed. Implement Phase 3 only — Components & Quarantine, Inventory, Patient & Requests, Crossmatch & Issue, Apheresis (manual), Billing & Reports, stock dashboard, TAT, in-app Alert Desk, and digital donor cards/certificates. Use the compatibility matrix, FEFO, expiry, and state machine rules from Core logic exactly. Do NOT add any third-party integration: no SMS, WhatsApp, analyser, e-Rakt Kosh, or AI code. Alerts stay in-app behind the notify() interface. Write and run all Phase 3 tests including the full-journey end-to-end test, fix failures, then stop and report against the Phase 3 acceptance gate. Do not start Phase 4.

---

## Phase 4 — Hardening, deployment, and first third-party integrations

**Goal:** First prove the core in Phases 1–3 is safe and deployable, **then** add the first integrations — SMS/WhatsApp notifications and lab analyser interfacing — one at a time, each behind its adapter, each removable without breaking the core.

**Order inside this phase is fixed:** 4A hardening and deployment first, gate it, then 4B notifications, then 4C analysers one by one.

### Sub-steps (check each one off in PROGRESS.md)

- **4A — Hardening and deployment:** full regression, security pass, k6 load test, backup/restore proof, dev → staging → production deployment.
- **4B — Notifications:** SMS / WhatsApp behind `NotificationAdapter`, feature-flagged per branch, with provider-outage test.
- **4C — Equipment:** generic analyser framework, then one analyser at a time, each behind its adapter, feature-flagged per branch, with provider-outage test.
- **4D — Buffer:** fixes from UAT of Phases 1–3; no new core features.

### 4A — Testing hardening, security, deployment (no integrations yet)

- Full regression run of every Phase 1–3 test; add load sanity checks (concurrent issue of the same unit must succeed only once) and negative tests for every state-machine transition not allowed.
- **Load test with k6:** 200 concurrent users, plus a camp-day burst of 500 registrations in 4 hours. Record results in `PROGRESS.md`; a failed load target is reported honestly, not hidden.
- **Security re-check:** `pip-audit` + ZAP baseline with zero high-severity findings; OWASP Top-10 review recorded for this phase.
- Security pass: dependency audit, secrets scan of the repo, HTTPS setup, headers, upload validation, session/refresh-token review, penetration-style API checks (ID tampering across branches and roles).
- Backup and restore: **nightly automated database backup (RPO ≤ 24 hours)**, a documented restore runbook in `docs/runbook.md`, a **weekly restore drill**, and an actually-performed restore test onto a clean environment. Always back up before running Alembic migrations in production.
- Deployment: Docker deployment for cloud and for on-premise (same compose, different `.env`), promoted **dev → staging (seeded demo) → production with identical Docker images**; health endpoints `/health` and `/health/db` verified; structured JSON logs in place; environment checklist, admin training material outline and implementation checklist (roles setup, masters confirmation, settings confirmation with the Medical Officer).

### 4B — Smart Notifications: SMS and WhatsApp

- Plug delivery into the Phase 3 `notify()` interface. Core alert behaviour must not change.
- Provider: use **one** SMS provider and the WhatsApp Business API (or one aggregator that covers both) chosen by the project owner; credentials only in environment variables; provider sits behind a `NotificationAdapter` with `mock` mode for tests, **feature-flagged per branch**, and a **provider-outage test** proving registrations, issues and all core flows still work when the provider is down.
- Message types: donor donation reminders, appointment reminders, next-eligibility alerts, emergency / urgent stock requests to eligible donors, and request-status messages where the branch enables them. Templates are master data, editable, with placeholders — no message text hard-coded in code.
- Every send writes a `NotificationLog` (channel, recipient, template, provider status). Failures retry via Celery and never block the underlying workflow — a failed SMS must not fail an issue or a registration.
- Donor communication preferences and opt-out are respected; no marketing messages in this system.

### 4C — Equipment interfacing (lab analysers)

Build a generic analyser framework first, then **one analyser at a time**, in the owner's priority order. Known target devices from the reference feature list:

| Device | Used for |
|---|---|
| Diagast | Blood grouping and antibody screening |
| Immucor NEO | Blood grouping and antibody screening |
| Ortho Vision | Blood grouping, antibody screening, and crossmatching |
| Abbott Architect | ELISA |
| Tulip Euphoreia | ELISA |
| Vitros 3600 | ELISA |
| Electra FA | CLIA |
| Roche Cobas | NAT |

Rules for every analyser:

- Before coding any device, the project owner supplies that vendor's official interfacing document (protocol such as ASTM/HL7/file-based, as the vendor specifies). **If the document is not available, skip that device and record it in `docs/decisions.md` — never reverse-engineer or guess a protocol.**
- Each device gets an `AnalyserAdapter` (serial / ASTM / file-watch only as its official document specifies — for example `pyserial` where the vendor protocol is serial) that parses its output and calls the **same grouping/testing APIs built in Phase 2**, so verification rules, quarantine rules, and audit apply identically to machine and manual results. Each adapter is **feature-flagged per branch** and ships with a **provider-outage test**: the lab keeps working by manual entry when the analyser or its link is down. Apheresis-machine yield capture, where a device is in scope, follows the same adapter + manual-fallback rule.
- Machine results land as **unverified** and still need human verification. No analyser result auto-releases a unit.
- Test each adapter with recorded/sample vendor files in `mock` mode before any live connection, then with the real device in a supervised session.
- Manual entry remains fully available for every analyser-covered test, forever — it is the fallback, not a legacy mode.

### DO NOT — Phase 4

- Do NOT start 4B or 4C before 4A hardening, deployment, and the restore test have passed their gate.
- Do NOT guess, reverse-engineer, or invent an analyser protocol. No official vendor document from the owner = that device is skipped and recorded as pending in `docs/decisions.md`.
- Do NOT auto-release a unit from a machine result. Analyser results land as unverified and need human verification, exactly like manual results.
- Do NOT remove or bypass manual entry. Manual entry is the permanent fallback for every analyser-covered test.
- Do NOT let an integration failure block core work. A failed SMS, WhatsApp message, or analyser import must never fail a registration, an issue, or any other workflow.
- Do NOT hard-code message text, provider endpoints, or credentials in code. Templates are master data; credentials live only in environment variables.
- Do NOT claim a backup works because it is scheduled. A backup counts only after a restore to a clean environment has actually been performed and verified.

### Tests for this phase

- Regression: all Phase 1–3 tests still pass with integrations enabled **and** with integrations disabled (feature flags off).
- Notification tests in mock mode: correct template rendering, opt-out respected, failure does not block workflow, log written.
- Analyser tests per device: sample files parse to correct results, malformed files are rejected safely, machine result still requires verification, reactive machine result quarantines the unit.
- Restore test evidence and security checklist recorded in `docs/runbook.md`.

### Acceptance gate — all must pass before Phase 5

- Core works identically with all integrations switched off.
- At least the notification integration runs end-to-end in mock mode and, with the owner's credentials, one real test message per channel is delivered and logged.
- Each connected analyser passes its sample-file tests; any analyser without an official vendor document is listed as pending, not faked.
- Backup restore has been demonstrated, not just configured.

### Copy-paste prompt — Phase 4

> Read BUILD_PLAN.md and PROGRESS.md. Phases 1–3 are complete and their gates passed. Implement Phase 4 in its fixed internal order: 4A hardening, security, backup/restore and deployment first; then 4B SMS/WhatsApp notifications behind the NotificationAdapter plugged into the existing notify() interface; then 4C analyser interfacing, framework first and then one device at a time in my priority order. For each analyser, use only the official vendor interfacing document I supply — if I have not supplied it, skip that device, record it in docs/decisions.md, and do not guess a protocol. Machine results must call the existing Phase 2 APIs and stay unverified until a human verifies them. Manual entry must keep working throughout. Run the full Phase 1–3 regression plus all Phase 4 tests, with integrations on and off, then stop and report against the Phase 4 acceptance gate. Do not start Phase 5.

---

## Phase 5 — Final third-party integrations and go-live

**Goal:** Add the two integrations that depend on everything else being stable — e-Rakt Kosh sync and AI-based Auto Entry — then run user acceptance, training, and go-live. Nothing new is built after this phase except fixes.

### Sub-steps (check each one off in PROGRESS.md)

- **5A — e-Rakt Kosh:** adapter, sync queue, reconciliation, feature-flagged per branch, provider-outage test.
- **5B — AI Auto Entry:** OCR / extraction behind `AutoEntryAdapter`, review-first only, feature-flagged per branch, provider-outage test (feature hides, manual entry unaffected).
- **5C — Go-live:** UAT sign-off, validated data import, training, Medical Officer Settings sign-off, hypercare.

### 5A — e-Rakt Kosh integration

- Prerequisite: the project owner supplies the current official e-Rakt Kosh integration documentation and the centre's credentials/registration details. **Without that documentation, build the sync framework and field mapping as configurable configuration, mark the integration as pending, and do not invent endpoints, payloads, or reporting formats.**
- Scope once documented: sync of donor data, stock availability, and mandatory reporting data required by the portal; support for the reporting formats the documentation specifies for Indian regulatory and NABH-aligned record keeping.
- Design: an `ERaktKoshAdapter` with `mock` mode, **feature-flagged per branch**; a Celery-backed sync queue with retry; an `ExternalSyncLog` entry for every push/pull with status and error; a sync status screen where staff can see what synced, what failed, and retry manually; and a **provider-outage test** proving local work continues when the portal is unavailable.
- Sync failures never block local work. The local system is the source of truth for operations; e-Rakt Kosh is a reporting/sync destination.
- Reconciliation report: local counts vs last-synced counts for stock and donations, so staff can spot a silent sync gap.

### 5B — AI-based Auto Entry

- Purpose: reduce manual typing by extracting fields from the sources the owner actually provides — for example a photographed/scanned donor form or a patient request document — and pre-filling the existing donor registration and blood request forms. This is intentionally in the Python backend: OCR, document extraction, and AI/LLM libraries (for example the OpenAI Python SDK or LangChain) integrate directly in FastAPI services without a second backend language.
- Hard rules:
  - AI output is a **draft suggestion only**. It pre-fills a form; a staff member reviews, corrects, and submits it through the normal Phase 2/3 APIs. AI never writes directly to the database, never approves eligibility, and never verifies a result.
  - Show extracted values side by side with the source image/document so review is a comparison, not a memory test. Log that a record was AI-assisted, with the model/provider used.
  - The AI provider and its API key are the owner's choice, held only in environment variables, behind an `AutoEntryAdapter` with `mock` mode. If no provider is configured, the feature is hidden and manual entry is unaffected.
  - Do not claim accuracy numbers in the UI or reports. Measure real correction rates in UAT (fields changed by staff ÷ fields pre-filled) and report that measured number to the owner.
  - Donor/patient documents are personal data: send to the AI provider only the document the staff member explicitly uploads for extraction, keep no extra copies, and record the processing in the audit log.

### 5C — UAT, training, and go-live

- User acceptance testing with the blood bank's own staff on scripted scenarios covering every phase: a camp day, a reactive unit, an emergency request, a transfer, a discard, a month-end register export, and an e-Rakt Kosh sync check.
- Data migration if the owner has existing records: import donors and opening stock through a validated import tool with a dry-run report — never by direct database inserts.
- Training sessions per role, a short user manual per role (from the screens as built), and the confirmed Settings sign-off by the Medical Officer (eligibility, shelf life, thresholds).
- Go-live checklist: production `.env` reviewed, backups running, roles and users created, masters confirmed, integrations on/off decided per integration, support contact and issue log started.
- Hypercare: two weeks of monitored use, daily sync/backup checks, and a fix-only change rule during this period.

### DO NOT — Phase 5

- Do NOT invent e-Rakt Kosh endpoints, payloads, field mappings presented as official, or reporting formats. No official documentation from the owner = framework and configurable mapping only, integration marked pending.
- Do NOT let AI write directly to the database, approve eligibility, verify a result, or submit a form. AI output is a draft pre-fill for a staff member to review, correct, and submit through the normal APIs — nothing else.
- Do NOT present an AI accuracy number you have not measured. Report only the correction rate actually measured in UAT.
- Do NOT let a sync failure block local work. The local system is the source of truth for operations; e-Rakt Kosh is a sync destination.
- Do NOT migrate existing data by direct database inserts. Use the validated import tool with a dry-run report.
- Do NOT go live without the Medical Officer's signed-off Settings values, working backups, and signed-off UAT scenarios. If any one is missing, go-live waits.

### Tests for this phase

- e-Rakt Kosh in mock mode: payloads match the supplied official documentation examples, failures retry and log, reconciliation report is accurate against test data.
- Auto Entry in mock mode: draft pre-fill only, no direct database write path exists (test attempts it and fails), staff edits are what gets saved, audit records AI assistance.
- Full regression of Phases 1–4 with all integrations on and off.
- UAT scenario scripts all signed off by the owner's staff.

### Acceptance gate — go-live requires all of these

- All regression tests pass; UAT scenarios signed off.
- e-Rakt Kosh is either syncing successfully against the real portal with the owner's credentials, or is explicitly recorded as pending official documentation — with manual reporting continuing meanwhile.
- Auto Entry is either live as review-first draft assistance with a measured correction rate reported, or disabled — it is never live as unattended data entry.
- Medical Officer has signed off the production Settings values. Backups, training, and manuals are done.

### Copy-paste prompt — Phase 5

> Read BUILD_PLAN.md and PROGRESS.md. Phases 1–4 are complete and their gates passed. Implement Phase 5: 5A e-Rakt Kosh sync behind an adapter, using only the official documentation and credentials I supply — if I have not supplied them, build the framework and field mapping as configuration, mark it pending in docs/decisions.md, and do not invent endpoints or payloads. Then 5B AI Auto Entry as review-first draft pre-fill only, behind an adapter — it must never write directly to the database or bypass any existing form, validation, or verification. Then 5C: UAT scenario support, validated data import with dry-run, training/manual material, and the go-live checklist. Run the full regression with integrations on and off, then stop and report against the Phase 5 acceptance gate.

---

## Master testing plan — applies to every phase

| Test level | What it covers | When |
|---|---|---|
| Unit tests | Eligibility, state machine, compatibility matrices, expiry, FEFO, settings fallback, barcode uniqueness, calculations. **State machine: 100% of transitions — legal transitions pass, illegal transitions are rejected** | Every phase, for that phase's logic |
| Type / lint / generation gates | `mypy --strict`, Ruff, frontend client regenerated from OpenAPI + frontend type-check and build | Every phase, in CI — merge blocked on failure |
| Data-integrity tests | Assertion script: orphan scan, barcode uniqueness, no `AVAILABLE` component without verified negative TTI tests | Every phase gate |
| Load tests | k6: 200 concurrent users; camp-day burst 500 registrations / 4 hours | Phase 4 |
| API tests | Every endpoint: success, validation failure, 403 per role, branch isolation, illegal state transitions | Every phase |
| End-to-end tests | The named user journeys in each phase, on a clean seeded database | End of every phase |
| Integration tests (mock) | Notifications, each analyser, e-Rakt Kosh, AI Auto Entry — all in mock mode first | Phases 4–5 |
| Regression | All earlier phases' tests re-run before a new phase is accepted | Start of Phases 3, 4, 5 acceptance |
| Security tests | ID tampering across branches/roles, token expiry, rate limiting, secrets scan, `pip-audit`, ZAP baseline (zero high-severity to merge), OWASP Top-10 review at each phase DoD | Phases 1, 4, and before go-live |
| Restore test | Backup taken, restored to a clean environment, data verified; nightly backup, weekly restore drill, RPO ≤ 24 hours | Phase 4, repeated before go-live |

Testing rules: tests use fake data only; a failing test blocks the phase gate; the agent reports actual test output, not a summary claim; manual exploratory testing by the owner happens at each gate, not only at UAT.

## Definition of done — for every phase

- All features listed for the phase are built; nothing from a later phase is built.
- Nothing on that phase's DO NOT list was done, and every endpoint follows the exact API response and error format in this plan.
- All tests listed for the phase pass, and earlier phases' regression tests still pass — with the actual test output included in the agent's report, and the owner has re-run the acceptance gate themselves before committing.
- Every new screen works for the roles allowed to use it and is blocked (UI and API) for the roles that are not.
- Every new status change writes an audit entry and an automatic timestamp.
- Every new configurable value lives in Settings, not in code.
- `docs/decisions.md` records every assumption the agent made and every item skipped for missing documentation, and **`PROGRESS.md` is updated** with status, session log, known issues, decisions, open questions, and any suggestions (not implemented).
- OpenAPI spec is regenerated, the frontend client is regenerated from it, and the frontend compiles; `mypy --strict` and Ruff pass; the data-integrity assertion script passes; the phase's OWASP Top-10 review is recorded.
- Human checkpoints: the Phase 2 domain review (testing/quarantine) and the Phase 3 domain review (crossmatch/issue) are signed off where they apply — no sign-off, no next phase.
- Definition of Done per phase, in one line: **code + all tests passing + OpenAPI regenerated + frontend client regenerated + seed data updated + PROGRESS.md updated with a "what changed & what's next" summary.**
- The agent has stopped, reported against the acceptance gate, and waited for approval to start the next phase.

## All copy-paste phase prompts — quick reference

**Phase 1:** Read BUILD_PLAN.md and PROGRESS.md. Implement Phase 1 only — Foundation. Do not build any donor, patient, blood, billing, or integration features. Follow the tech stack, project structure, RBAC table, and security rules exactly. Seed only fake data. Write and run the unit, API, and end-to-end tests listed for Phase 1, fix all failures, then stop and report: what you built, test results, and the acceptance gate result. Do not start Phase 2.

**Phase 2:** Read BUILD_PLAN.md and PROGRESS.md. Phase 1 is complete and its gate passed. Implement Phase 2 only — Donor Management, Camp Management, Collection, Grouping, and manual Testing & Screening, following the state machine, eligibility, and testing rules in Core logic exactly. Analyser interfacing is NOT in this phase; testing is manual entry shaped so an adapter can call the same API later. Do not build components, patients, inventory, billing, or integrations. Write and run all Phase 2 tests, fix failures, then stop and report results against the Phase 2 acceptance gate. Do not start Phase 3.

**Phase 3:** Read BUILD_PLAN.md and PROGRESS.md. Phases 1–2 are complete and their gates passed. Implement Phase 3 only — Components & Quarantine, Inventory, Patient & Requests, Crossmatch & Issue, Apheresis (manual), Billing & Reports, stock dashboard, TAT, in-app Alert Desk, and digital donor cards/certificates. Use the compatibility matrix, FEFO, expiry, and state machine rules from Core logic exactly. Do NOT add any third-party integration: no SMS, WhatsApp, analyser, e-Rakt Kosh, or AI code. Alerts stay in-app behind the notify() interface. Write and run all Phase 3 tests including the full-journey end-to-end test, fix failures, then stop and report against the Phase 3 acceptance gate. Do not start Phase 4.

**Phase 4:** Read BUILD_PLAN.md and PROGRESS.md. Phases 1–3 are complete and their gates passed. Implement Phase 4 in its fixed internal order: 4A hardening, security, backup/restore and deployment first; then 4B SMS/WhatsApp notifications behind the NotificationAdapter plugged into the existing notify() interface; then 4C analyser interfacing, framework first and then one device at a time in my priority order. For each analyser, use only the official vendor interfacing document I supply — if I have not supplied it, skip that device, record it in docs/decisions.md, and do not guess a protocol. Machine results must call the existing Phase 2 APIs and stay unverified until a human verifies them. Manual entry must keep working throughout. Run the full Phase 1–3 regression plus all Phase 4 tests, with integrations on and off, then stop and report against the Phase 4 acceptance gate. Do not start Phase 5.

**Phase 5:** Read BUILD_PLAN.md and PROGRESS.md. Phases 1–4 are complete and their gates passed. Implement Phase 5: 5A e-Rakt Kosh sync behind an adapter, using only the official documentation and credentials I supply — if I have not supplied them, build the framework and field mapping as configuration, mark it pending in docs/decisions.md, and do not invent endpoints or payloads. Then 5B AI Auto Entry as review-first draft pre-fill only, behind an adapter — it must never write directly to the database or bypass any existing form, validation, or verification. Then 5C: UAT scenario support, validated data import with dry-run, training/manual material, and the go-live checklist. Run the full regression with integrations on and off, then stop and report against the Phase 5 acceptance gate.

## Feature coverage check

Every feature from the reference list is owned by exactly one phase:

- **Phase 1:** web-based cloud/on-premise setup, RBAC, encrypted/secure data handling, backups (configured in Phase 4, foundation here), multi-location support, centralized visibility, standalone-to-chain scaling, masters and settings.
- **Phase 2:** Donor Management, Camp Management, Collection & Grouping, donor registration/eligibility/history/repeat donors, TTD testing workflow, end-to-end barcoding (starts here, completed in Phase 3), audit trail (starts in Phase 1, used everywhere).
- **Phase 3:** Components & Quarantine, Inventory Management, Patient & Requests, crossmatch and issue, transfusion, Billing & Reports and registers, Live Stock Dashboard, TAT monitoring and analytics, advanced grouping subphenotypes in use, Apheresis Management (manual), Alert & Notification Desk (in-app), digital donor cards and certificates, full traceability.
- **Phase 4:** implementation/deployment hardening, training checklist, Smart Notifications (SMS/WhatsApp), Equipment Interfacing and automated analyser result capture for Diagast, Abbott Architect, Immucor NEO, Tulip Euphoreia, Ortho Vision, Vitros 3600, Roche Cobas, and Electra FA — each only with its official vendor document.
- **Phase 5:** e-Rakt Kosh integration/sync and regulatory reporting support, AI-based Auto Entry (review-first), real-time sync status and reconciliation, UAT, training delivery, and go-live.
- **Explicitly out of scope:** an online payments gateway. Phase 3 billing records bills and payment status; gateway collection is optional future work only on the owner's explicit request. Advanced phenotype matching (E, e, K, k, Kell) beyond the Phase 2 fields and Phase 3 antibody workflows is likewise enabled only through the compatibility data layer — the base ABO/Rh matrix never changes to add it.
