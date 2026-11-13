"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ErrorAlert, FieldError } from "@/components/error-alert";
import { listBranches, listSettings, upsertSetting, type Setting } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { settingValueSchema } from "@/lib/validation";

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();
  const [branchFilter, setBranchFilter] = useState<string>("");
  const [editing, setEditing] = useState<Setting | null>(null);
  const [valueText, setValueText] = useState("");
  const [fieldError, setFieldError] = useState<string | undefined>();
  const [error, setError] = useState<unknown>(null);

  const isSuperAdmin = user?.role === "Super Admin";

  const settingsQuery = useQuery({
    queryKey: ["settings", branchFilter],
    queryFn: () => listSettings(branchFilter || undefined),
  });
  const branchesQuery = useQuery({
    queryKey: ["branches", "all"],
    queryFn: () => listBranches(1, 100),
  });

  const updateMutation = useMutation({
    mutationFn: () =>
      upsertSetting({
        key: editing?.key ?? "",
        value: JSON.parse(valueText) as unknown,
        scope: editing?.scope === "branch" ? "branch" : "global",
        branch_id: editing?.branch_id ?? null,
        confirm_with_mo: editing?.confirm_with_mo ?? false,
        label: editing?.label ?? null,
        description: editing?.description ?? null,
      }),
    onSuccess: () => {
      setEditing(null);
      setError(null);
      void queryClient.invalidateQueries({ queryKey: ["settings"] });
    },
    onError: setError,
  });

  /** Global-scope edits are Super Admin only; branch-scope rows may be edited by other roles (the API still enforces it). */
  function canEdit(setting: Setting): boolean {
    return setting.scope === "global" ? isSuperAdmin : true;
  }

  function submitEdit(e: React.FormEvent) {
    e.preventDefault();
    const parsed = settingValueSchema.safeParse({ valueText });
    if (!parsed.success) {
      setFieldError(
        parsed.error.issues[0]?.message ?? "Value must be valid JSON.",
      );
      return;
    }
    setFieldError(undefined);
    updateMutation.mutate();
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>
      <p className="text-sm text-slate-500">
        Configurable defaults for eligibility, gaps, shelf life, and alerts.
        Values marked below are defaults — confirm with the Medical Officer
        before go-live.
      </p>

      <ErrorAlert error={error} />
      {settingsQuery.error && <ErrorAlert error={settingsQuery.error} />}

      <div className="flex items-center gap-3">
        <Label htmlFor="branch-filter">Branch</Label>
        <Select
          id="branch-filter"
          className="w-64"
          value={branchFilter}
          onChange={(e) => setBranchFilter(e.target.value)}
        >
          <option value="">All (effective settings)</option>
          {(branchesQuery.data?.items ?? []).map((b) => (
            <option key={b.id} value={b.id}>
              {b.name} ({b.code})
            </option>
          ))}
        </Select>
      </div>

      {editing && (
        <Card>
          <CardHeader>
            <CardTitle>Edit setting {editing.key}</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={submitEdit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="value">Value (JSON)</Label>
                <Input
                  id="value"
                  value={valueText}
                  onChange={(e) => setValueText(e.target.value)}
                  placeholder='e.g. 72, true, or "text"'
                />
                <FieldError message={fieldError} />
              </div>
              <div className="flex gap-2">
                <Button type="submit" disabled={updateMutation.isPending}>
                  Save value
                </Button>
                <Button variant="outline" onClick={() => setEditing(null)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="pt-6">
          {settingsQuery.isPending ? (
            <p className="text-sm text-slate-500">Loading…</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Key</TableHead>
                  <TableHead>Value</TableHead>
                  <TableHead>Scope</TableHead>
                  <TableHead>Notes</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {(settingsQuery.data ?? []).map((s) => (
                  <TableRow key={s.id}>
                    <TableCell className="font-mono text-xs">{s.key}</TableCell>
                    <TableCell className="font-mono text-xs">
                      {JSON.stringify(s.value)}
                    </TableCell>
                    <TableCell>
                      {s.scope}
                      {s.branch_id ? ` (${s.branch_id.slice(0, 8)}…)` : ""}
                    </TableCell>
                    <TableCell>
                      {s.confirm_with_mo && (
                        <Badge variant="warning">
                          Default — confirm with Medical Officer before go-live
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={!canEdit(s)}
                        title={
                          canEdit(s)
                            ? "Edit value"
                            : "Global settings can only be edited by a Super Admin."
                        }
                        onClick={() => {
                          setEditing(s);
                          setValueText(JSON.stringify(s.value));
                          setFieldError(undefined);
                        }}
                      >
                        Edit
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
