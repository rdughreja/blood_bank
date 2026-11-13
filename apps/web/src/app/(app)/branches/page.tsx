"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ErrorAlert, FieldError } from "@/components/error-alert";
import { Pagination } from "@/components/pagination";
import {
  createBranch,
  deleteBranch,
  listBranches,
  updateBranch,
  type Branch,
} from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { branchSchema, deleteReasonSchema } from "@/lib/validation";

interface BranchFormValues {
  code: string;
  name: string;
  address: string;
  licence_no: string;
  is_storage_centre: boolean;
}

const EMPTY_FORM: BranchFormValues = {
  code: "",
  name: "",
  address: "",
  licence_no: "",
  is_storage_centre: false,
};

export default function BranchesPage() {
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [form, setForm] = useState<BranchFormValues>(EMPTY_FORM);
  const [editing, setEditing] = useState<Branch | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [deleteTarget, setDeleteTarget] = useState<Branch | null>(null);
  const [deleteReason, setDeleteReason] = useState("");
  const [error, setError] = useState<unknown>(null);

  const isSuperAdmin = user?.role === "Super Admin";

  const branchesQuery = useQuery({
    queryKey: ["branches", page],
    queryFn: () => listBranches(page, 20),
  });

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["branches"] });

  const createMutation = useMutation({
    mutationFn: () =>
      createBranch({
        code: form.code,
        name: form.name,
        address: form.address || null,
        licence_no: form.licence_no || null,
        is_storage_centre: form.is_storage_centre,
      }),
    onSuccess: () => {
      setForm(EMPTY_FORM);
      setShowCreate(false);
      setError(null);
      void invalidate();
    },
    onError: setError,
  });

  const updateMutation = useMutation({
    mutationFn: () =>
      updateBranch(editing?.id ?? "", {
        name: form.name,
        address: form.address || null,
        licence_no: form.licence_no || null,
        is_storage_centre: form.is_storage_centre,
      }),
    onSuccess: () => {
      setEditing(null);
      setForm(EMPTY_FORM);
      setError(null);
      void invalidate();
    },
    onError: setError,
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteBranch(deleteTarget?.id ?? "", deleteReason),
    onSuccess: () => {
      setDeleteTarget(null);
      setDeleteReason("");
      setError(null);
      void invalidate();
    },
    onError: setError,
  });

  function startEdit(branch: Branch) {
    setEditing(branch);
    setShowCreate(false);
    setForm({
      code: branch.code,
      name: branch.name,
      address: branch.address ?? "",
      licence_no: branch.licence_no ?? "",
      is_storage_centre: branch.is_storage_centre,
    });
    setFieldErrors({});
  }

  function submitForm(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const parsed = branchSchema.safeParse(form);
    if (!parsed.success) {
      const errors: Record<string, string> = {};
      for (const issue of parsed.error.issues) {
        errors[String(issue.path[0])] = issue.message;
      }
      setFieldErrors(errors);
      return;
    }
    setFieldErrors({});
    if (editing) updateMutation.mutate();
    else createMutation.mutate();
  }

  function submitDelete(e: React.FormEvent) {
    e.preventDefault();
    const parsed = deleteReasonSchema.safeParse({ reason: deleteReason });
    if (!parsed.success) {
      setFieldErrors({
        reason: parsed.error.issues[0]?.message ?? "A reason is required.",
      });
      return;
    }
    setFieldErrors({});
    deleteMutation.mutate();
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Branches</h1>
        {isSuperAdmin && !showCreate && !editing && (
          <Button
            onClick={() => {
              setForm(EMPTY_FORM);
              setShowCreate(true);
            }}
          >
            New branch
          </Button>
        )}
      </div>

      <ErrorAlert error={error} />
      {branchesQuery.error && <ErrorAlert error={branchesQuery.error} />}

      {(showCreate || editing) && (
        <Card>
          <CardHeader>
            <CardTitle>{editing ? "Edit branch" : "New branch"}</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={submitForm} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="code">Code</Label>
                  <Input
                    id="code"
                    value={form.code}
                    disabled={!!editing}
                    onChange={(e) => setForm({ ...form, code: e.target.value })}
                  />
                  <FieldError message={fieldErrors.code} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                  />
                  <FieldError message={fieldErrors.name} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="address">Address</Label>
                  <Input
                    id="address"
                    value={form.address}
                    onChange={(e) => setForm({ ...form, address: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="licence_no">Licence no.</Label>
                  <Input
                    id="licence_no"
                    value={form.licence_no}
                    onChange={(e) => setForm({ ...form, licence_no: e.target.value })}
                  />
                </div>
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={form.is_storage_centre}
                  onChange={(e) =>
                    setForm({ ...form, is_storage_centre: e.target.checked })
                  }
                />
                Storage centre
              </label>
              <div className="flex gap-2">
                <Button
                  type="submit"
                  disabled={createMutation.isPending || updateMutation.isPending}
                >
                  {editing ? "Save changes" : "Create branch"}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setEditing(null);
                    setShowCreate(false);
                    setForm(EMPTY_FORM);
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="pt-6">
          {branchesQuery.isPending ? (
            <p className="text-sm text-slate-500">Loading…</p>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Code</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Storage centre</TableHead>
                    <TableHead>Active</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {branchesQuery.data?.items.map((branch) => (
                    <TableRow key={branch.id}>
                      <TableCell className="font-mono">{branch.code}</TableCell>
                      <TableCell>{branch.name}</TableCell>
                      <TableCell>
                        {branch.is_storage_centre ? (
                          <Badge>Yes</Badge>
                        ) : (
                          <Badge variant="secondary">No</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        {branch.is_active ? (
                          <Badge>Active</Badge>
                        ) : (
                          <Badge variant="destructive">Inactive</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => startEdit(branch)}
                          >
                            Edit
                          </Button>
                          {isSuperAdmin && (
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() => setDeleteTarget(branch)}
                            >
                              Delete
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {branchesQuery.data && (
                <Pagination meta={branchesQuery.data.meta} onPage={setPage} />
              )}
            </>
          )}
        </CardContent>
      </Card>

      {deleteTarget && (
        <Card>
          <CardHeader>
            <CardTitle>Delete branch {deleteTarget.name}?</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-slate-500">
              This is a soft delete. A reason is required and the action is
              written to the audit log.
            </p>
            <form onSubmit={submitDelete} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="delete-reason">Reason</Label>
                <Input
                  id="delete-reason"
                  value={deleteReason}
                  onChange={(e) => setDeleteReason(e.target.value)}
                  placeholder="Why is this branch being deleted?"
                />
                <FieldError message={fieldErrors.reason} />
              </div>
              <div className="flex gap-2">
                <Button
                  type="submit"
                  variant="destructive"
                  disabled={deleteMutation.isPending}
                >
                  Confirm delete
                </Button>
                <Button variant="outline" onClick={() => setDeleteTarget(null)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
