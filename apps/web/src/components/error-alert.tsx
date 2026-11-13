"use client";

import { friendlyMessage, isApiError } from "@/lib/errors";

export function ErrorAlert({ error }: { error: unknown }) {
  if (!error) return null;
  return (
    <div
      role="alert"
      className="rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-900"
    >
      <p className="font-medium">{friendlyMessage(error)}</p>
      {isApiError(error) && (
        <p className="mt-1 font-mono text-xs text-red-700">
          Error code: {error.code}
        </p>
      )}
    </div>
  );
}

export function FieldError({ message }: { message?: string }) {
  if (!message) return null;
  return <p className="mt-1 text-xs text-red-600">{message}</p>;
}
