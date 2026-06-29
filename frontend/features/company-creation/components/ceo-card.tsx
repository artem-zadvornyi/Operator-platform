import { Crown } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function CeoCard() {
  return (
    <Card className="border-accent/20">
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-accent/10 text-accent flex size-10 items-center justify-center rounded-md">
              <Crown className="size-5" aria-hidden />
            </div>
            <div>
              <CardTitle>AI CEO</CardTitle>
              <CardDescription>Strategic leadership</CardDescription>
            </div>
          </div>
          <Badge variant="outline">Planning</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-body text-text-secondary">
          Mission analyzed. Departments assembled and ready to execute.
        </p>
      </CardContent>
    </Card>
  );
}
