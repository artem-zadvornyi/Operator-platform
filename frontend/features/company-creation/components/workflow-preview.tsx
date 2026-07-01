import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

import { getDepartmentIcon } from "../constants";
import type { WorkflowPreview } from "../types";

export interface WorkflowPreviewCardProps {
  workflow: WorkflowPreview;
}

export function WorkflowPreviewCard({ workflow }: WorkflowPreviewCardProps) {
  const currentTask = workflow.currentTask;
  const TaskIcon = getDepartmentIcon(currentTask.department);

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
                <TaskIcon className="size-4" aria-hidden />
              </div>
              <div>
                <CardTitle className="text-body-large">{currentTask.title}</CardTitle>
                <CardDescription>{workflow.title}</CardDescription>
              </div>
            </div>
            <Badge variant="outline">{currentTask.status}</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-body text-text-secondary">{currentTask.description}</p>
        </CardContent>
      </Card>
    </section>
  );
}
