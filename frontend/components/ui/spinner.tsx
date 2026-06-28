import { type HTMLAttributes } from "react";

import { cn } from "@/lib/cn";

export interface SpinnerProps extends HTMLAttributes<HTMLDivElement> {
  size?: "sm" | "md" | "lg";
}

const sizeClasses = {
  sm: "size-4 border-2",
  md: "size-5 border-2",
  lg: "size-6 border-[2.5px]",
} as const;

export function Spinner({ className, size = "md", ...props }: SpinnerProps) {
  return (
    <div
      role="status"
      aria-label="Loading"
      className={cn(
        "border-border border-t-accent animate-spin rounded-full",
        sizeClasses[size],
        className,
      )}
      {...props}
    />
  );
}
