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
import { Pagination } from "@/components/pagination";
import {
  createUser,
  deleteUser,
  listBranches,
  listRoles,
  listUsers,
  resetUserPassword,
  updateUser,
  type User,
} from "@/lib/api";
import { isApiError } from "@/lib/errors";
import {
  PASSWORD_HINT,
  deleteReasonSchema,
  passwordSchema,
  userCreateSchema,
  userUpdateSchema,
} from "@/lib/validation";

export default function UsersPage() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<User | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [error, setError] = useState<unknown>(null);
  const [deleteTarget, setDeleteTarget] = useState<User | null>(null);
  const [deleteReason, setDeleteReason] = useState("");
  const [resetTarget, setResetTarget] = useState<User | null>(null);
  const [resetPassword, setResetPassword] = useState("");

  const [createForm, setCreateForm] = useState({
    email: "",
    full_name: "",
    mobile: "",
    password: "",
    role_id: "",
    branch_ids: [] as string[],
    primary_branch_id: "",
  });
  const [editForm, setEditForm] = useState({
    full_name: "",
    mobile: "",
    role_id: "",
    branch_ids: [] as string[],
    primary_branch_id: "",
    is_active: true,
  });

  const usersQuery = useQuery({
    queryKey: ["users", page],
    queryFn: () => listUsers(page, 20),
  });
  const rolesQuery = useQuery({
    queryKey: ["roles"],
    queryFn: listRoles,
  });
  const branchesQuery = useQuery({
    queryKey: ["branches", "all"],
    queryFn: () => listBranches(1, 100),
  });

  const roles = rolesQuery.data ?? [];
  const branches = branchesQuery.data?.items ?? [];
  const rolesUnavailable =
    isApiError(rolesQuery.error) && rolesQuery.error.code === "FORBIDDEN";

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["users"] });

  const createMutation = useMutation({
    mutationFn: () =>
      createUser({
        email: createForm.email,
        full_name: createForm.full_name,
        mobile: createForm.mobile || null,
        password: createForm.password,
        role_id: createForm.role_id,
        branch_ids: createForm.branch_ids,
        primary_branch_id: createForm.primary_branch_id || null,
      }),
    onSuccess: () => {
      setShowCreate(false);
      setCreateForm({
        email: "",
        full_name: "",
        mobile: "",
        password: "",
        role_id: "",
        branch_ids: [],
        primary_branch_id: "",
      });
      setError(null);
      void invalidate();
    },
    onError: setError,
  });

  const updateMutation = useMutation({
    mutationFn: () =>
      updateUser(editing?.id ?? "", {
        full_name: editForm.full_name,
        mobile: editForm.mobile || null,
        role_id: editForm.role_id,
        branch_ids: editForm.branch_ids,
        primary_branch_id: editForm.primary_branch_id || null,
        is_active: editForm.is_active,
      }),
    onSuccess: () => {
      setEditing(null);
      setError(null);
      void invalidate();
    },
    onError: setError,
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteUser(deleteTarget?.id ?? "", deleteReason),
    onSuccess: () => {
      setDeleteTarget(null);
      setDeleteReason("");
      setError(null);
      void invalidate();
    },
    onError: setError,
  });

  const resetMutation = useMutation({
    mutationFn: () =>
      resetUserPassword(resetTarget?.id ?? "", resetPassword),
    onSuccess: () => {
      setResetTarget(null);
      setResetPassword("");
      setError(null);
    },
    onError: setError,
  });

  function toggleBranch(
    list: string[],
    branchId: string,
    set: (next: string[]) => void,
  ) {
    set(
      list.includes(branchId)
        ? list.filter((id) => id !== branchId)
        : [...list, branchId],
    );
  }

  function submitCreate(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const parsed = userCreateSchema.safeParse(createForm);
    if (!parsed.success) {
      const errors: Record<string, string> = {};
      for (const issue of parsed.error.issues) {
        errors[String(issue.path[0])] = issue.message;
      }
      setFieldErrors(errors);
      return;
    }
    setFieldErrors({});
    createMutation.mutate();
  }

  function startEdit(user: User) {
    setEditing(user);
    setShowCreate(false);
    setEditForm({
      full_name: user.full_name,
      mobile: user.mobile ?? "",
      role_id: user.role_id,
      branch_ids: user.branches.map((b) => b.id),
      primary_branch_id: user.branches[0]?.id ?? "",
      is_active: user.is_active,
    });
    setFieldErrors({});
  }

  function submitEdit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const parsed = userUpdateSchema.safeParse(editForm);
    if (!parsed.success) {
      const errors: Record<string, string> = {};
      for (const issue of parsed.error.issues) {
        errors[String(issue.path[0])] = issue.message;
      }
      setFieldErrors(errors);
      return;
    }
    setFieldErrors({});
    updateMutation.mutate();
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

  function submitReset(e: React.FormEvent) {
    e.preventDefault();
    const parsed = passwordSchema.safeParse(resetPassword);
    if (!parsed.success) {
      setFieldErrors({
        reset_password: parsed.error.issues[0]?.message ?? "Invalid password.",
      });
      return;
    }
    setFieldErrors({});
    resetMutation.mutate();
  }

  const branchCheckboxes = (
    selected: string[],
    onToggle: (branchId: string) => void,
  ) => (
    <div className="flex flex-wrap gap-3">
      {branches.map((b) => (
        <label key={b.id} className="flex items-center gap-1.5 text-sm">
          <input
            type="checkbox"
            checked={selected.includes(b.id)}
            onChange={() => onToggle(b.id)}
          />
          {b.name} ({b.code})
        </label>
      ))}
      {branches.length === 0 && (
        <p className="text-sm text-slate-500">No branches loaded.</p>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Users</h1>
        {!showCreate && !editing && (
          <Button
            onClick={() => setShowCreate(true)}
            disabled={rolesUnavailable}
          >
            New user
          </Button>
        )}
      </div>

      <ErrorAlert error={error} />
      {usersQuery.error && <ErrorAlert error={usersQuery.error} />}
      {rolesUnavailable && (
        <p className="text-sm text-slate-500">
          The roles list is not readable for your role, so new users cannot
          be created from here.
        </p>
      )}

      {showCreate && (
        <Card>
          <CardHeader>
            <CardTitle>New user</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={submitCreate} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={createForm.email}
                    onChange={(e) =>
                      setCreateForm({ ...createForm, email: e.target.value })
                    }
                  />
                  <FieldError message={fieldErrors.email} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="full_name">Full name</Label>
                  <Input
                    id="full_name"
                    value={createForm.full_name}
                    onChange={(e) =>
                      setCreateForm({ ...createForm, full_name: e.target.value })
                    }
                  />
                  <FieldError message={fieldErrors.full_name} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="mobile">Mobile</Label>
                  <Input
                    id="mobile"
                    value={createForm.mobile}
                    onChange={(e) =>
                      setCreateForm({ ...createForm, mobile: e.target.value })
                    }
                  />
                  <FieldError message={fieldErrors.mobile} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="role_id">Role</Label>
                  <Select
                    id="role_id"
                    value={createForm.role_id}
                    onChange={(e) =>
                      setCreateForm({ ...createForm, role_id: e.target.value })
                    }
                  >
                    <option value="">Choose a role…</option>
                    {roles.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.name}
                      </option>
                    ))}
                  </Select>
                  <FieldError message={fieldErrors.role_id} />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    autoComplete="new-password"
                    value={createForm.password}
                    onChange={(e) =>
                      setCreateForm({ ...createForm, password: e.target.value })
                    }
                  />
                  <p className="text-xs text-slate-500">{PASSWORD_HINT}</p>
                  <FieldError message={fieldErrors.password} />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <Label>Branches</Label>
                  {branchCheckboxes(createForm.branch_ids, (id) =>
                    toggleBranch(createForm.branch_ids, id, (next) =>
                      setCreateForm({ ...createForm, branch_ids: next }),
                    ),
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="primary_branch_id">Primary branch</Label>
                  <Select
                    id="primary_branch_id"
                    value={createForm.primary_branch_id}
                    onChange={(e) =>
                      setCreateForm({
                        ...createForm,
                        primary_branch_id: e.target.value,
                      })
                    }
                  >
                    <option value="">None</option>
                    {branches
                      .filter((b) => createForm.branch_ids.includes(b.id))
                      .map((b) => (
                        <option key={b.id} value={b.id}>
                          {b.name}
                        </option>
                      ))}
                  </Select>
                </div>
              </div>
              <div className="flex gap-2">
                <Button type="submit" disabled={createMutation.isPending}>
                  Create user
                </Button>
                <Button variant="outline" onClick={() => setShowCreate(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {editing && (
        <Card>
          <CardHeader>
            <CardTitle>Edit user {editing.email}</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={submitEdit} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="edit_full_name">Full name</Label>
                  <Input
                    id="edit_full_name"
                    value={editForm.full_name}
                    onChange={(e) =>
                      setEditForm({ ...editForm, full_name: e.target.value })
                    }
                  />
                  <FieldError message={fieldErrors.full_name} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit_mobile">Mobile</Label>
                  <Input
                    id="edit_mobile"
                    value={editForm.mobile}
                    onChange={(e) =>
                      setEditForm({ ...editForm, mobile: e.target.value })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit_role_id">Role</Label>
                  <Select
                    id="edit_role_id"
                    value={editForm.role_id}
                    onChange={(e) =>
                      setEditForm({ ...editForm, role_id: e.target.value })
                    }
                  >
                    {roles.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.name}
                      </option>
                    ))}
                  </Select>
                  <FieldError message={fieldErrors.role_id} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit_primary_branch_id">Primary branch</Label>
                  <Select
                    id="edit_primary_branch_id"
                    value={editForm.primary_branch_id}
                    onChange={(e) =>
                      setEditForm({
                        ...editForm,
                        primary_branch_id: e.target.value,
                      })
                    }
                  >
                    <option value="">None</option>
                    {branches
                      .filter((b) => editForm.branch_ids.includes(b.id))
                      .map((b) => (
                        <option key={b.id} value={b.id}>
                          {b.name}
                        </option>
                      ))}
                  </Select>
                </div>
                <div className="space-y-2 md:col-span-2">
                  <Label>Branches</Label>
                  {branchCheckboxes(editForm.branch_ids, (id) =>
                    toggleBranch(editForm.branch_ids, id, (next) =>
                      setEditForm({ ...editForm, branch_ids: next }),
                    ),
                  )}
                </div>
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={editForm.is_active}
                  onChange={(e) =>
                    setEditForm({ ...editForm, is_active: e.target.checked })
                  }
                />
                Active
              </label>
              <div className="flex gap-2">
                <Button type="submit" disabled={updateMutation.isPending}>
                  Save changes
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
          {usersQuery.isPending ? (
            <p className="text-sm text-slate-500">Loading…</p>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Branches</TableHead>
                    <TableHead>MFA</TableHead>
                    <TableHead>Active</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {usersQuery.data?.items.map((u) => (
                    <TableRow key={u.id}>
                      <TableCell>{u.full_name}</TableCell>
                      <TableCell>{u.email}</TableCell>
                      <TableCell>{u.role}</TableCell>
                      <TableCell>
                        {u.branches.map((b) => b.code).join(", ") || "—"}
                      </TableCell>
                      <TableCell>
                        {u.mfa_enabled ? (
                          <Badge>On</Badge>
                        ) : (
                          <Badge variant="secondary">Off</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        {u.is_active ? (
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
                            onClick={() => startEdit(u)}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setResetTarget(u)}
                          >
                            Reset password
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => setDeleteTarget(u)}
                          >
                            Delete
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {usersQuery.data && (
                <Pagination meta={usersQuery.data.meta} onPage={setPage} />
              )}
            </>
          )}
        </CardContent>
      </Card>

      {deleteTarget && (
        <Card>
          <CardHeader>
            <CardTitle>Delete user {deleteTarget.email}?</CardTitle>
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

      {resetTarget && (
        <Card>
          <CardHeader>
            <CardTitle>Reset password for {resetTarget.email}</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={submitReset} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="reset-password">New password</Label>
                <Input
                  id="reset-password"
                  type="password"
                  autoComplete="new-password"
                  value={resetPassword}
                  onChange={(e) => setResetPassword(e.target.value)}
                />
                <p className="text-xs text-slate-500">{PASSWORD_HINT}</p>
                <FieldError message={fieldErrors.reset_password} />
              </div>
              <div className="flex gap-2">
                <Button type="submit" disabled={resetMutation.isPending}>
                  Reset password
                </Button>
                <Button variant="outline" onClick={() => setResetTarget(null)}>
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
