"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState, type ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { listBranches, logout, switchBranch } from "@/lib/api";
import { getStoredRefreshToken, useAuthStore } from "@/lib/store";
import { visibleMenuItems } from "@/lib/menu";
import { cn } from "@/lib/utils";
import { ApiError } from "@/lib/errors";

export function Shell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const queryClient = useQueryClient();
  const user = useAuthStore((s) => s.user);
  const hydrated = useAuthStore((s) => s.hydrated);
  const clearSession = useAuthStore((s) => s.clearSession);
  const setAccessTokenOnly = useAuthStore((s) => s.setAccessTokenOnly);
  const [switching, setSwitching] = useState(false);
  const [switchError, setSwitchError] = useState<string | null>(null);

  // All branches the user may switch to. Super Admin has branches ["*"]:
  // fall back to the full branch list in that case.
  const branchesQuery = useQuery({
    queryKey: ["branches", "all-for-switcher"],
    queryFn: () => listBranches(1, 100),
    enabled: hydrated && !!user,
  });

  if (hydrated && !user) {
    router.replace("/login");
    return null;
  }
  if (!hydrated || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center text-slate-500">
        Loading…
      </div>
    );
  }

  const menuItems = visibleMenuItems(user.role);
  const allBranches = branchesQuery.data?.items ?? [];
  const switchableBranches =
    user.branches.includes("*") || user.branches.length === 0
      ? allBranches
      : allBranches.filter((b) => user.branches.includes(b.id));
  const showSwitcher = switchableBranches.length > 1;
  const activeBranch =
    allBranches.find((b) => b.id === user.branchId) ?? null;

  async function handleSwitch(branchId: string) {
    if (!branchId || branchId === user?.branchId) return;
    setSwitching(true);
    setSwitchError(null);
    try {
      const result = await switchBranch(branchId);
      setAccessTokenOnly(result.access_token);
      await queryClient.invalidateQueries();
      window.location.reload();
    } catch (error) {
      setSwitchError(
        error instanceof ApiError
          ? error.message
          : "Could not switch branch.",
      );
    } finally {
      setSwitching(false);
    }
  }

  async function handleLogout() {
    const refreshToken = getStoredRefreshToken();
    if (refreshToken) {
      try {
        await logout(refreshToken);
      } catch {
        // Logout is best-effort; the local session is cleared regardless.
      }
    }
    clearSession();
    router.push("/login");
  }

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      <aside className="flex w-60 shrink-0 flex-col border-r border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-5 py-4">
          <p className="text-lg font-bold">Blood Bank</p>
          <p className="text-xs text-slate-500">Phase 1 — Foundation</p>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-4">
          {menuItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "block rounded-md px-3 py-2 text-sm font-medium",
                pathname === item.href || pathname.startsWith(`${item.href}/`)
                  ? "bg-slate-900 text-white"
                  : "text-slate-700 hover:bg-slate-100",
              )}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="border-t border-slate-200 px-5 py-4 text-xs text-slate-500">
          <p className="truncate font-medium text-slate-900">{user.email}</p>
          <p>{user.role}</p>
          {activeBranch && <p>Branch: {activeBranch.name}</p>}
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between gap-4 border-b border-slate-200 bg-white px-6 py-3">
          <p className="text-sm font-medium">
            {menuItems.find((i) => i.href === pathname)?.label ?? "Blood Bank"}
          </p>
          <div className="flex items-center gap-3">
            {showSwitcher && (
              <label className="flex items-center gap-2 text-sm">
                <span className="text-slate-500">Branch</span>
                <Select
                  value={user.branchId ?? ""}
                  disabled={switching}
                  onChange={(e) => void handleSwitch(e.target.value)}
                  className="w-56"
                  aria-label="Switch branch"
                >
                  {switchableBranches.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.name} ({b.code})
                    </option>
                  ))}
                </Select>
              </label>
            )}
            {switchError && (
              <p className="text-xs text-red-600">{switchError}</p>
            )}
            <Button variant="outline" size="sm" onClick={() => void handleLogout()}>
              Log out
            </Button>
          </div>
        </header>
        <main className="flex-1 px-6 py-6">{children}</main>
      </div>
    </div>
  );
}
