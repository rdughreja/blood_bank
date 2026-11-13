/**
 * Generated API client (openapi-fetch) over the FastAPI OpenAPI spec.
 *
 * The TypeScript types come from `src/lib/api-generated/types.ts`, generated
 * by `npm run generate:api` from `../../openapi.json`. Never hand-edit the
 * generated file; change the backend schema and regenerate instead.
 *
 * Every response uses the envelope `{success, data, meta}` or
 * `{success, error: {code, message, details, requestId, timestamp}}`.
 * `unwrap` / `unwrapPage` unwrap `data` on success and throw a typed
 * `ApiError` carrying `error.code` on failure. The frontend branches on
 * `code`, never on message text.
 */
import createClient, { type Client } from "openapi-fetch";
import type { paths } from "./api-generated/types";
import { ApiError } from "./errors";
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setTokens,
} from "./auth";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface SuccessEnvelope<T> {
  success: true;
  data: T;
  meta: {
    requestId: string;
    timestamp: string;
    page?: number | null;
    pageSize?: number | null;
    total?: number | null;
    totalPages?: number | null;
  };
}

interface ErrorEnvelope {
  success: false;
  error: {
    code: string;
    message: string;
    details?: unknown;
    requestId?: string;
    timestamp?: string;
  };
}

type Envelope<T> = SuccessEnvelope<T> | ErrorEnvelope;

export interface PageMeta {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}

/** Refresh the access token once using the stored refresh token. */
async function tryRefresh(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;
  try {
    const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) return false;
    const body = (await res.json()) as Envelope<{
      access_token: string;
      refresh_token: string;
    }>;
    if (!body.success) return false;
    setTokens(body.data.access_token, body.data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

/**
 * fetch wrapper for openapi-fetch: injects the Bearer token, and on a 401
 * tries one refresh + retry. If the refresh fails, clears the session and
 * sends the user back to /login.
 *
 * NOTE: openapi-fetch calls this wrapper with a fully-built `Request`
 * object (headers + JSON body already set). Do NOT re-wrap it as
 * `fetch(input, { headers: new Headers(...) })` — a Headers init replaces
 * the request's header list, which silently drops the Content-Type (the API
 * then rejects the body with VALIDATION_ERROR) and the Authorization
 * header. Instead, normalise to a Request once and mutate its headers
 * in place. (Found by the Phase 1 Playwright E2E, 13 Nov 2026.)
 */
async function authFetch(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Response> {
  const request = new Request(input, init);
  const accessToken = getAccessToken();
  // Do not override an explicitly supplied Authorization header (used by
  // the MFA setup/confirm calls, which authenticate with the mfa_token).
  if (accessToken && !request.headers.has("Authorization")) {
    request.headers.set("Authorization", `Bearer ${accessToken}`);
  }
  // Keep a pristine copy for a single 401 retry (the first fetch consumes
  // the request body).
  const retryRequest = request.clone();
  let res = await fetch(request);
  if (res.status === 401) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      const newToken = getAccessToken();
      if (newToken) {
        retryRequest.headers.set("Authorization", `Bearer ${newToken}`);
      }
      res = await fetch(retryRequest);
    } else {
      clearTokens();
      if (
        typeof window !== "undefined" &&
        !window.location.pathname.startsWith("/login")
      ) {
        window.location.href = "/login";
      }
    }
  }
  return res;
}

export const client: Client<paths> = createClient<paths>({
  baseUrl: API_BASE_URL,
  fetch: authFetch,
});

/** Unwrap a single-item envelope, or throw ApiError with `error.code`. */
export function unwrap<T>(result: {
  data?: unknown;
  error?: unknown;
}): T {
  const body = (result.data ?? result.error) as Envelope<T> | undefined;
  if (!body || typeof body !== "object" || !("success" in body)) {
    throw new ApiError("UNKNOWN_ERROR", "Unexpected response from server.");
  }
  if (body.success) return body.data;
  throw new ApiError(body.error.code, body.error.message, body.error.details);
}

/** Unwrap a paginated list envelope into items + pagination meta. */
export function unwrapPage<T>(result: {
  data?: unknown;
  error?: unknown;
}): { items: T[]; meta: PageMeta } {
  const body = (result.data ?? result.error) as
    | Envelope<T[]>
    | undefined;
  if (!body || typeof body !== "object" || !("success" in body)) {
    throw new ApiError("UNKNOWN_ERROR", "Unexpected response from server.");
  }
  if (!body.success) {
    throw new ApiError(body.error.code, body.error.message, body.error.details);
  }
  return {
    items: body.data,
    meta: {
      page: body.meta.page ?? 1,
      pageSize: body.meta.pageSize ?? 20,
      total: body.meta.total ?? body.data.length,
      totalPages: body.meta.totalPages ?? 1,
    },
  };
}
