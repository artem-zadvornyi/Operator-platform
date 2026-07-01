import { type LucideIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import type { CompanyDepartment } from "../types";

export interface DepartmentCardProps {
  department: CompanyDepartment;
  icon: LucideIcon;
}

export function DepartmentCard({ department, icon: Icon }: DepartmentCardProps) {
  return (
    <Card className="bg-background-secondary/40">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between gap-3">
          <div className="bg-card text-text-secondary flex size-9 items-center justify-center rounded-md">
            <Icon className="size-4" aria-hidden />
          </div>
          <Badge variant="success">{department.status}</Badge>
        </div>
        <CardTitle className="text-body-large pt-2">{department.name}</CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <p className="text-caption text-text-secondary">{department.description}</p>
      </CardContent>
    </Card>
  );
}
