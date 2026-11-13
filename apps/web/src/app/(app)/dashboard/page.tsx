"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { listBranches, listUsers } from "@/lib/api";
import { isApiError } from "@/lib/errors";
import { useAuthStore } from "@/lib/store";

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  const branchesQuery = useQuery({
    queryKey: ["branches", "count"],
    queryFn: () => listBranches(1, 1),
  });
  const usersQuery = useQuery({
    queryKey: ["users", "count"],
    queryFn: () => listUsers(1, 1),
  });

  const activeBranch =
    branchesQuery.data?.items.find((b) => b.id === user?.branchId) ?? null;

  function countCard(
    query: { data?: { meta: { total: number } }; error: unknown; isPending: boolean },
  ) {
    if (query.isPending) {
      return <p className="text-sm text-slate-500">Loading…</p>;
    }
    if (query.error) {
      if (isApiError(query.error) && query.error.code === "FORBIDDEN") {
        return (
          <p className="text-sm text-slate-500">
            Not visible for your role.
          </p>
        );
      }
      return (
        <p className="text-sm text-red-600">Could not load this count.</p>
      );
    }
    return <p className="text-3xl font-bold">{query.data?.meta.total ?? 0}</p>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">
          Welcome{user ? `, ${user.email}` : ""}.
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Role: <span className="font-medium text-slate-900">{user?.role ?? "—"}</span>
          {" · "}
          Active branch:{" "}
          <span className="font-medium text-slate-900">
            {activeBranch ? `${activeBranch.name} (${activeBranch.code})` : "—"}
          </span>
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Branches</CardTitle>
          </CardHeader>
          <CardContent>{countCard(branchesQuery)}</CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Users</CardTitle>
          </CardHeader>
          <CardContent>{countCard(usersQuery)}</CardContent>
        </Card>
      </div>
      <p className="text-sm text-slate-500">
        This is the Phase 1 foundation shell: branches, users, masters,
        settings, and the audit log. Donor, patient, and blood features arrive
        in later phases.
      </p>
    </div>
  );
}
