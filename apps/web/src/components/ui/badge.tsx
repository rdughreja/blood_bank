import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "secondary" | "warning" | "destructive";
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold",
        variant === "default" && "border-slate-900 bg-slate-900 text-white",
        variant === "secondary" &&
          "border-slate-200 bg-slate-100 text-slate-900",
        variant === "warning" &&
          "border-amber-300 bg-amber-100 text-amber-900",
        variant === "destructive" &&
          "border-red-300 bg-red-100 text-red-900",
        className,
      )}
      {...props}
    />
  );
}

export { Badge };
