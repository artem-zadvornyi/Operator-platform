import { Target } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export interface MissionCardProps {
  idea: string;
}

export function MissionCard({ idea }: MissionCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-accent/10 text-accent flex size-10 items-center justify-center rounded-md">
              <Target className="size-5" aria-hidden />
            </div>
            <div>
              <CardTitle>Mission</CardTitle>
              <CardDescription>Strategic objective</CardDescription>
            </div>
          </div>
          <Badge variant="success">Active</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-body-large text-text-primary">{idea}</p>
      </CardContent>
    </Card>
  );
}
