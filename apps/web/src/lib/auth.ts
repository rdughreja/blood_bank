/**
 * Client-side auth storage + JWT decoding.
 *
 * Tokens are stored in localStorage for this Phase 1 demo. That is a
 * deliberate tradeoff: it keeps the demo simple, but tokens in localStorage
 * are readable by any script on the page, so a production build should move
 * them to httpOnly cookies (see apps/web/README.md).
 */

export interface SessionUser {
  sub: string;
  email: string;
  role: string;
  branchId: string | null;
  branches: string[];
}

const ACCESS_KEY = "bb.access_token";
const REFRESH_KEY = "bb.refresh_token";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(REFRESH_KEY);
}

export function setTokens(accessToken: string, refreshToken: string): void {
  window.localStorage.setItem(ACCESS_KEY, accessToken);
  window.localStorage.setItem(REFRESH_KEY, refreshToken);
}

export function setAccessToken(accessToken: string): void {
  window.localStorage.setItem(ACCESS_KEY, accessToken);
}

export function clearTokens(): void {
  window.localStorage.removeItem(ACCESS_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
}

/**
 * Decode the JWT payload client-side ONLY for menu visibility (which role,
 * which branch). The server enforces every permission; menu hiding is not
 * security. Returns null when the token is absent or malformed.
 */
export function decodeSessionUser(token: string | null): SessionUser | null {
  if (!token) return null;
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    const payload = JSON.parse(
      atob(parts[1].replace(/-/g, "+").replace(/_/g, "/")),
    ) as Record<string, unknown>;
    if (
      typeof payload.sub !== "string" ||
      typeof payload.email !== "string" ||
      typeof payload.role !== "string"
    ) {
      return null;
    }
    const branches = Array.isArray(payload.branches)
      ? (payload.branches as unknown[]).filter(
          (b): b is string => typeof b === "string",
        )
      : [];
    return {
      sub: payload.sub,
      email: payload.email,
      role: payload.role,
      branchId: typeof payload.branch_id === "string" ? payload.branch_id : null,
      branches,
    };
  } catch {
    return null;
  }
}
