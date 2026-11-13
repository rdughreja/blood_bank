"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
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
  createMaster,
  deleteMaster,
  listMasterTypes,
  listMasters,
  updateMaster,
  type Master,
} from "@/lib/api";
import { deleteReasonSchema, masterSchema } from "@/lib/validation";

const FALLBACK_TYPES = [
  "blood_group",
  "component_type",
  "test_name",
  "deferral_reason",
  "discard_reason",
  "hospital",
  "ward",
  "charge",
];

export default function MastersPage() {
  const queryClient = useQueryClient();
  const [type, setType] = useState<string>(FALLBACK_TYPES[0]);
  const [page, setPage] = useState(1);
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<Master | null>(null);
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [error, setError] = useState<unknown>(null);
  const [deleteTarget, setDeleteTarget] = useState<Master | null>(null);
  const [deleteReason, setDeleteReason] = useState("");

  const typesQuery = useQuery({
    queryKey: ["master-types"],
    queryFn: listMasterTypes,
  });
  const types =
    typesQuery.data && typesQuery.data.length > 0
      ? typesQuery.data
      : FALLBACK_TYPES;

  useEffect(() => {
    if (typesQuery.data && typesQuery.data.length > 0 && !types.includes(type)) {
      setType(types[0]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [typesQuery.data]);

  const mastersQuery = useQuery({
    queryKey: ["masters", type, page],
    queryFn: () => listMasters(type, page, 20),
  });

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["masters", type] });

  const createMutation = useMutation({
    mutationFn: () => createMaster(type, { code, name }),
    onSuccess: () => {
      setShowCreate(false);
      setCode("");
      setName("");
      setError(null);
      void invalidate();
    },
    onError: setError,
  });

  const updateMutation = useMutation({
    mutationFn: () => updateMaster(editing?.id ?? "", { name }),
    onSuccess: () => {
      setEditing(null);
      setCode("");
      setName("");
      setError(null);
      void invalidate();
    },
    onError: setError,
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteMaster(deleteTarget?.id ?? "", deleteReason),
    onSuccess: () => {
      setDeleteTarget(null);
      setDeleteReason("");
      setError(null);
      void invalidate();
    },
    onError: setError,
  });

  function submitForm(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (editing) {
      if (!name.trim()) {
        setFieldErrors({ name: "Name is required." });
        return;
      }
      setFieldErrors({});
      updateMutation.mutate();
      return;
    }
    const parsed = masterSchema.safeParse({ code, name });
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
        <h1 className="text-2xl font-bold">Masters</h1>
        {!showCreate && !editing && (
          <Button
            onClick={() => {
              setCode("");
              setName("");
              setShowCreate(true);
            }}
          >
            New entry
          </Button>
        )}
      </div>

      <ErrorAlert error={error} />
      {mastersQuery.error && <ErrorAlert error={mastersQuery.error} />}

      <div className="flex items-center gap-3">
        <Label htmlFor="master-type">Type</Label>
        <Select
          id="master-type"
          className="w-64"
          value={type}
          onChange={(e) => {
            setType(e.target.value);
            setPage(1);
          }}
        >
          {types.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </Select>
      </div>

      {(showCreate || editing) && (
        <Card>
          <CardHeader>
            <CardTitle>
              {editing ? `Edit ${type} entry` : `New ${type} entry`}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={submitForm} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="code">Code</Label>
                  <Input
                    id="code"
                    value={code}
                    disabled={!!editing}
                    onChange={(e) => setCode(e.target.value)}
                  />
                  <FieldError message={fieldErrors.code} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                  <FieldError message={fieldErrors.name} />
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  type="submit"
                  disabled={createMutation.isPending || updateMutation.isPending}
                >
                  {editing ? "Save changes" : "Create entry"}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setEditing(null);
                    setShowCreate(false);
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
          {mastersQuery.isPending ? (
            <p className="text-sm text-slate-500">Loading…</p>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Code</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Active</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mastersQuery.data?.items.map((m) => (
                    <TableRow key={m.id}>
                      <TableCell className="font-mono">{m.code}</TableCell>
                      <TableCell>{m.name}</TableCell>
                      <TableCell>
                        {m.is_active ? (
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
                            onClick={() => {
                              setEditing(m);
                              setShowCreate(false);
                              setCode(m.code);
                              setName(m.name);
                            }}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => setDeleteTarget(m)}
                          >
                            Delete
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {mastersQuery.data && (
                <Pagination meta={mastersQuery.data.meta} onPage={setPage} />
              )}
            </>
          )}
        </CardContent>
      </Card>

      {deleteTarget && (
        <Card>
          <CardHeader>
            <CardTitle>Delete master entry {deleteTarget.name}?</CardTitle>
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
    </div>
  );
}
