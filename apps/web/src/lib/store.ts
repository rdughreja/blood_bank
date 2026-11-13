import { create } from "zustand";
import {
  clearTokens,
  decodeSessionUser,
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setTokens,
  type SessionUser,
} from "./auth";

interface AuthState {
  user: SessionUser | null;
  hydrated: boolean;
  /** Load any stored tokens into the store (called once on app mount). */
  hydrate: () => void;
  /** Store a fresh token pair after login / MFA. */
  setSession: (accessToken: string, refreshToken: string) => void;
  /** Replace only the access token (branch switch). */
  setAccessTokenOnly: (accessToken: string) => void;
  /** Clear tokens + session (logout). */
  clearSession: () => void;
}

export const useAuthStore = create<AuthState>()((set) => ({
  user: null,
  hydrated: false,
  hydrate: () => {
    const token = getAccessToken();
    set({ user: decodeSessionUser(token), hydrated: true });
  },
  setSession: (accessToken, refreshToken) => {
    setTokens(accessToken, refreshToken);
    set({ user: decodeSessionUser(accessToken) });
  },
  setAccessTokenOnly: (accessToken) => {
    setAccessToken(accessToken);
    set({ user: decodeSessionUser(accessToken) });
  },
  clearSession: () => {
    clearTokens();
    set({ user: null });
  },
}));

export function getStoredRefreshToken(): string | null {
  return getRefreshToken();
}
