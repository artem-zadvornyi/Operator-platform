import { Crown } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

import type { CompanyCEO } from "../types";

export interface CeoCardProps {
  ceo: CompanyCEO;
}

export function CeoCard({ ceo }: CeoCardProps) {
  return (
    <Card className="border-accent/20">
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-accent/10 text-accent flex size-10 items-center justify-center rounded-md">
              <Crown className="size-5" aria-hidden />
            </div>
            <div>
              <CardTitle>{ceo.name}</CardTitle>
              <CardDescription>Strategic leadership</CardDescription>
            </div>
          </div>
          <Badge variant="outline">{ceo.status}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-body text-text-secondary">{ceo.summary}</p>
      </CardContent>
    </Card>
  );
}
