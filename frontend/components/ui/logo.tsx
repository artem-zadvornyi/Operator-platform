import { type HTMLAttributes } from "react";

import { cn } from "@/lib/cn";

export interface LogoProps extends HTMLAttributes<HTMLDivElement> {
  showWordmark?: boolean;
}

export function Logo({ className, showWordmark = true, ...props }: LogoProps) {
  return (
    <div className={cn("inline-flex items-center gap-2.5", className)} {...props}>
      <div
        aria-hidden
        className={cn(
          "flex size-7 items-center justify-center rounded-md",
          "bg-accent shadow-glow",
        )}
      >
        <div className="bg-text-primary size-3 rounded-sm" />
      </div>
      {showWordmark ? (
        <span className="text-body text-text-primary font-semibold tracking-tight">Operator</span>
      ) : null}
    </div>
  );
}
