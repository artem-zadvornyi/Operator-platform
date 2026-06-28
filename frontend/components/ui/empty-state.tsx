import { type LucideIcon } from "lucide-react";
import { type HTMLAttributes, type ReactNode } from "react";

import { Icon } from "@/components/icons";
import { cn } from "@/lib/cn";

export interface EmptyStateProps extends HTMLAttributes<HTMLDivElement> {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({
  className,
  icon,
  title,
  description,
  action,
  ...props
}: EmptyStateProps) {
  return (
    <div
      className={cn("flex flex-col items-center justify-center px-4 py-16 text-center", className)}
      {...props}
    >
      {icon ? (
        <div
          className={cn(
            "mb-4 flex size-12 items-center justify-center rounded-lg",
            "border-border bg-background-secondary border",
          )}
        >
          <Icon icon={icon} className="text-text-secondary size-5" />
        </div>
      ) : null}
      <h3 className="text-h3 text-text-primary">{title}</h3>
      {description ? (
        <p className="text-body text-text-secondary mt-2 max-w-sm">{description}</p>
      ) : null}
      {action ? <div className="mt-6">{action}</div> : null}
    </div>
  );
}
