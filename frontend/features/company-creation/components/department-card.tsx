import { type LucideIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export interface DepartmentCardProps {
  name: string;
  status: string;
  icon: LucideIcon;
}

export function DepartmentCard({ name, status, icon: Icon }: DepartmentCardProps) {
  return (
    <Card className="bg-background-secondary/40">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between gap-3">
          <div className="bg-card text-text-secondary flex size-9 items-center justify-center rounded-md">
            <Icon className="size-4" aria-hidden />
          </div>
          <Badge variant="success">{status}</Badge>
        </div>
        <CardTitle className="text-body-large pt-2">{name}</CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <p className="text-caption text-text-secondary">Department operational</p>
      </CardContent>
    </Card>
  );
}
