import { Crown, FileText, Palette, Search, Send, TrendingUp, Video } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/cn";

import { EmployeeStatusCard } from "./employee-status-card";

const employees = [
  {
    name: "AI CEO",
    status: "Planning strategy",
    icon: Crown,
    statusVariant: "success" as const,
    isLeader: true,
  },
  {
    name: "Research Employee",
    status: "Researching niche",
    icon: Search,
    statusVariant: "default" as const,
  },
  {
    name: "Brand Employee",
    status: "Creating brand",
    icon: Palette,
    statusVariant: "default" as const,
  },
  {
    name: "Script Employee",
    status: "Writing scripts",
    icon: FileText,
    statusVariant: "default" as const,
  },
  {
    name: "Video Employee",
    status: "Producing videos",
    icon: Video,
    statusVariant: "default" as const,
  },
  {
    name: "Publishing Employee",
    status: "Waiting for approval",
    icon: Send,
    statusVariant: "warning" as const,
  },
  {
    name: "Growth Employee",
    status: "Finding growth opportunities",
    icon: TrendingUp,
    statusVariant: "outline" as const,
  },
];

export function AiCompanyPreview() {
  return (
    <div className="relative w-full">
      <div
        aria-hidden
        className={cn("pointer-events-none absolute -inset-4 rounded-2xl", "bg-accent/10 blur-3xl")}
      />
      <Card
        className={cn(
          "border-border/80 relative overflow-hidden shadow-lg",
          "bg-card/80 backdrop-blur-sm",
        )}
        aria-label="AI company preview"
      >
        <CardHeader className="border-border border-b pb-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <span className="bg-success size-2 rounded-full" aria-hidden />
              <CardTitle className="text-body font-medium">Content Business</CardTitle>
            </div>
            <span className="text-caption text-text-secondary">Live preview</span>
          </div>
          <div className="mt-3 flex gap-1.5" aria-hidden>
            <span className="bg-border size-2.5 rounded-full" />
            <span className="bg-border size-2.5 rounded-full" />
            <span className="bg-border size-2.5 rounded-full" />
          </div>
        </CardHeader>
        <CardContent className="space-y-2 pt-4">
          {employees.map((employee) => (
            <EmployeeStatusCard key={employee.name} {...employee} />
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
