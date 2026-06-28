import { type LucideIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/cn";

export interface EmployeeStatusCardProps {
  name: string;
  status: string;
  icon: LucideIcon;
  statusVariant?: "default" | "success" | "warning" | "outline";
  isLeader?: boolean;
}

export function EmployeeStatusCard({
  name,
  status,
  icon: Icon,
  statusVariant = "default",
  isLeader = false,
}: EmployeeStatusCardProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-3 rounded-lg border px-3 py-2.5",
        "duration-fast transition-colors",
        isLeader
          ? "border-accent/30 bg-accent/5 shadow-glow"
          : "border-border bg-background-secondary/50",
      )}
    >
      <div
        className={cn(
          "flex size-8 shrink-0 items-center justify-center rounded-md",
          isLeader ? "bg-accent/15 text-accent" : "bg-card text-text-secondary",
        )}
      >
        <Icon className="size-4 shrink-0" aria-hidden />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-body text-text-primary truncate font-medium">{name}</p>
      </div>
      <Badge variant={statusVariant} className="shrink-0">
        {status}
      </Badge>
    </div>
  );
}
