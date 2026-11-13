import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "secondary" | "destructive" | "outline" | "ghost";
  size?: "sm" | "default";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", type = "button", ...props }, ref) => (
    <button
      ref={ref}
      type={type}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 disabled:pointer-events-none disabled:opacity-50",
        size === "sm" ? "h-8 px-3" : "h-10 px-4 py-2",
        variant === "default" &&
          "bg-slate-900 text-white hover:bg-slate-700",
        variant === "secondary" &&
          "bg-slate-100 text-slate-900 hover:bg-slate-200",
        variant === "destructive" &&
          "bg-red-600 text-white hover:bg-red-700",
        variant === "outline" &&
          "border border-slate-300 bg-white hover:bg-slate-100",
        variant === "ghost" && "hover:bg-slate-100",
        className,
      )}
      {...props}
    />
  ),
);
Button.displayName = "Button";

export { Button };
