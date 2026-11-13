# Blood Bank — Web Frontend (Phase 1: Foundation)

Next.js (App Router) + TypeScript (strict) + Tailwind CSS + hand-written
shadcn/ui-style components. Server state via React Query, UI/session state
via Zustand, form validation via Zod.

## Screens (Phase 1 only)

`/login` (with MFA setup/verify steps), `/dashboard`, `/branches`,
`/users`, `/masters`, `/settings`, `/audit`. No donor, patient, blood,
billing, or integration screens exist in this phase.

## API client — generated, never hand-written

Types are generated from `../../openapi.json` (the FastAPI OpenAPI spec):

```sh
npm run generate:api
```

That writes `src/lib/api-generated/types.ts`. The openapi-fetch client and
the envelope-unwrapping fetch wrapper live in `src/lib/api-client.ts`;
typed resource functions live in `src/lib/api.ts`. Never hand-edit the
generated file — change the backend schema and regenerate.

All API responses use the envelope `{success, data, meta}` or
`{success, error: {code, message, details, requestId, timestamp}}`. The
wrapper unwraps `data` on success and throws a typed `ApiError` carrying
`error.code` on failure; the UI branches on `code`, never on message text.

## Auth

- `POST /auth/login` returns tokens, or `{mfa_required, mfa_setup_required,
  mfa_token}`. MFA setup: `POST /auth/mfa/setup` (Bearer mfa_token) shows
  the TOTP secret + provisioning URI, then `POST /auth/mfa/confirm {code}`
  (Bearer mfa_token). MFA already enabled: `POST /auth/mfa/verify
  {mfa_token, code}`.
- On a 401 the client tries `POST /auth/refresh` once with the stored
  refresh token and retries; if the refresh fails it clears the session and
  redirects to `/login`. `POST /auth/logout` is called on logout.
- The JWT `role` claim is decoded client-side ONLY for menu visibility. The
  server enforces every permission; hiding a menu item is not security.

## Token storage tradeoff (Phase 1 demo)

Access + refresh tokens are stored in `localStorage`. That keeps the demo
simple, but any script running on the page can read `localStorage`, so a
production deployment should move tokens to `httpOnly` cookies (set by the
backend) instead. Do not ship the `localStorage` approach to production
without that change.

## Config

```sh
cp .env.example .env.local   # then edit if the API is not on localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Scripts

```sh
npm run dev           # dev server on http://localhost:3000
npm run generate:api  # regenerate the API client from ../../openapi.json
npm run type-check    # tsc --noEmit
npm run lint          # next lint
npm run build         # production build
```
