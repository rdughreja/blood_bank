"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
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
import { ErrorAlert } from "@/components/error-alert";
import { Pagination } from "@/components/pagination";
import { listAuditLogs } from "@/lib/api";

function formatTime(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" });
}

export default function AuditPage() {
  const [page, setPage] = useState(1);
  const [entity, setEntity] = useState("");
  const [action, setAction] = useState("");
  const [applied, setApplied] = useState({ entity: "", action: "" });

  const auditQuery = useQuery({
    queryKey: ["audit-logs", page, applied],
    queryFn: () => listAuditLogs(page, 20, applied),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Audit Log</h1>
      <p className="text-sm text-slate-500">
        Append-only record of creates, updates, and deletes. Read-only — there
        is no edit or delete API for audit entries.
      </p>

      {auditQuery.error && <ErrorAlert error={auditQuery.error} />}

      <form
        className="flex flex-wrap items-end gap-4"
        onSubmit={(e) => {
          e.preventDefault();
          setPage(1);
          setApplied({ entity, action });
        }}
      >
        <div className="space-y-2">
          <Label htmlFor="entity">Entity</Label>
          <Input
            id="entity"
            value={entity}
            onChange={(e) => setEntity(e.target.value)}
            placeholder="e.g. Branch"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="action">Action</Label>
          <Input
            id="action"
            value={action}
            onChange={(e) => setAction(e.target.value)}
            placeholder="e.g. create"
          />
        </div>
        <Button type="submit">Filter</Button>
        <Button
          variant="outline"
          onClick={() => {
            setEntity("");
            setAction("");
            setApplied({ entity: "", action: "" });
            setPage(1);
          }}
        >
          Clear
        </Button>
      </form>

      <Card>
        <CardContent className="pt-6">
          {auditQuery.isPending ? (
            <p className="text-sm text-slate-500">Loading…</p>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Time (IST)</TableHead>
                    <TableHead>User</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Entity</TableHead>
                    <TableHead>Entity ID</TableHead>
                    <TableHead>IP</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {auditQuery.data?.items.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell className="whitespace-nowrap">
                        {formatTime(log.created_at)}
                      </TableCell>
                      <TableCell>{log.user_email ?? "—"}</TableCell>
                      <TableCell>{log.action}</TableCell>
                      <TableCell>{log.entity}</TableCell>
                      <TableCell className="font-mono text-xs">
                        {log.entity_id ? `${log.entity_id.slice(0, 8)}…` : "—"}
                      </TableCell>
                      <TableCell>{log.ip_address ?? "—"}</TableCell>
                    </TableRow>
                  ))}
                  {(auditQuery.data?.items.length ?? 0) === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} className="text-slate-500">
                        No audit entries match these filters.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
              {auditQuery.data && (
                <Pagination meta={auditQuery.data.meta} onPage={setPage} />
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
