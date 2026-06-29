import { Search } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

import { WORKFLOW_PREVIEW } from "../constants";

export function WorkflowPreview() {
  return (
    <section aria-labelledby="workflow-heading">
      <h2 id="workflow-heading" className="text-h3 text-text-primary mb-5">
        Workflow Preview
      </h2>
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="bg-card text-text-secondary flex size-9 items-center justify-center rounded-md">
                <Search className="size-4" aria-hidden />
              </div>
              <div>
                <CardTitle className="text-body-large">{WORKFLOW_PREVIEW.title}</CardTitle>
                <CardDescription>First workflow task</CardDescription>
              </div>
            </div>
            <Badge variant="outline">{WORKFLOW_PREVIEW.status}</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-body text-text-secondary">
            Research will validate audience demand and competitor landscape before downstream
            departments begin work.
          </p>
        </CardContent>
      </Card>
    </section>
  );
}
