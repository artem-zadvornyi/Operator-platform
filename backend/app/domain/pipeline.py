"""Execution pipeline domain service connecting decisions to workflows."""

from dataclasses import dataclass, field
from datetime import datetime

from app.domain.decision import Decision
from app.domain.plan import Plan, PlanStep
from app.domain.planner import Planner
from app.domain.task import Task, TaskStatus
from app.domain.workflow import Workflow


@dataclass(frozen=True, slots=True)
class Pipeline:
    """Orchestrates decision planning and workflow initialization."""

    planner: Planner = field(default_factory=Planner)

    def build(self, decision: Decision) -> Workflow:
        """Convert an approved decision into a fully initialized workflow."""
        plan = self.planner.create_plan(decision)
        return self._build_workflow_from_plan(plan)

    def _build_workflow_from_plan(self, plan: Plan) -> Workflow:
        workflow = Workflow.create(created_at=plan.created_at)

        for step in plan.steps:
            task = _plan_step_to_task(step, plan.created_at)
            workflow = workflow.add_task(task)

        _validate_plan_task_alignment(plan, workflow)
        workflow.validate_dependencies()
        return workflow


def _plan_step_to_task(step: PlanStep, created_at: datetime) -> Task:
    """Map a plan step to a workflow task preserving identity and dependencies."""
    return Task.create(
        task_id=step.id,
        title=step.title,
        description=step.description,
        department=step.target_department,
        priority=step.priority,
        depends_on=step.depends_on,
        status=TaskStatus.CREATED,
        created_at=created_at,
    )


def _validate_plan_task_alignment(plan: Plan, workflow: Workflow) -> None:
    if len(workflow.tasks) != len(plan.steps):
        msg = "Workflow must contain exactly one task for every plan step."
        raise ValueError(msg)

    step_by_id = {step.id: step for step in plan.steps}

    for task in workflow.tasks:
        step = step_by_id.get(task.id)
        if step is None:
            msg = f"Workflow task {task.id} has no matching plan step."
            raise ValueError(msg)

        if task.department is not step.target_department:
            msg = (
                f"Task {task.id} department {task.department.value} does not match "
                f"plan step department {step.target_department.value}."
            )
            raise ValueError(msg)

        if task.priority is not step.priority:
            msg = f"Task {task.id} priority does not match plan step priority."
            raise ValueError(msg)

        if task.depends_on != step.depends_on:
            msg = f"Task {task.id} dependencies do not match plan step dependencies."
            raise ValueError(msg)
