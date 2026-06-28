"""Execution application service — orchestrates workflow and agent runtime."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.domain.decision import Decision
from app.domain.employee import Employee
from app.domain.execution_strategy import (
    DeterministicExecutionStrategy,
    ExecutionPlan,
    ExecutionStrategy,
)
from app.domain.mission import Mission
from app.domain.pipeline import Pipeline
from app.domain.plan import Plan
from app.domain.runtime import AgentExecution
from app.domain.task import Task
from app.domain.workflow import Workflow
from app.providers.registry import ProviderRegistry


@dataclass(frozen=True, slots=True)
class WorkflowSetup:
    """Plan and workflow produced from an approved decision."""

    plan: Plan
    workflow: Workflow


@dataclass(frozen=True, slots=True)
class FirstTaskExecutionResult:
    """Result of running the first available workflow task."""

    plan: Plan
    workflow: Workflow
    task: Task
    employee: Employee
    execution_plan: ExecutionPlan
    execution: AgentExecution


@dataclass(frozen=True, slots=True)
class ExecutionService:
    """Orchestrates workflow creation, execution preparation, and runtime."""

    pipeline: Pipeline = field(default_factory=Pipeline)
    strategy: ExecutionStrategy = field(default_factory=DeterministicExecutionStrategy)
    provider_registry: ProviderRegistry = field(default_factory=ProviderRegistry)

    def create_workflow(self, decision: Decision) -> WorkflowSetup:
        """Build a plan and workflow from an approved decision."""
        plan = self.pipeline.planner.create_plan(decision)
        workflow = self.pipeline.build(decision)
        return WorkflowSetup(plan=plan, workflow=workflow)

    def prepare_execution(self, task: Task, employee: Employee) -> ExecutionPlan:
        """Delegate execution preparation to the configured strategy."""
        return self.strategy.prepare_execution(task, employee)

    def run_first_task_demo(
        self,
        *,
        mission: Mission,
        decision: Decision,
        employee: Employee,
        started_at: datetime,
    ) -> FirstTaskExecutionResult:
        """Execute the first available workflow task using deterministic runtime."""
        workflow_setup = self.create_workflow(decision)
        workflow = workflow_setup.workflow

        available_tasks = workflow.next_available_tasks()
        if not available_tasks:
            msg = "Workflow has no available tasks to execute."
            raise ValueError(msg)

        first_task = available_tasks[0]
        execution_plan = self.prepare_execution(first_task, employee)

        workflow = workflow.assign_task(employee.id, first_task.id, started_at)

        execution = AgentExecution.create(first_task, employee.id)
        running = execution.start(started_at + timedelta(minutes=1))
        finished = running.succeed(
            title=_result_title(first_task, execution_plan),
            summary=_result_summary(mission, first_task, execution_plan),
            finished_at=started_at + timedelta(minutes=2),
        )

        result = finished.result
        if result is None:
            msg = "Succeeded execution must include a result."
            raise ValueError(msg)

        workflow = workflow.complete_task(
            first_task.id,
            result.artifact_reference,
            started_at + timedelta(minutes=3),
        )

        return FirstTaskExecutionResult(
            plan=workflow_setup.plan,
            workflow=workflow,
            task=workflow.get_task(first_task.id),
            employee=employee,
            execution_plan=execution_plan,
            execution=finished,
        )


def _result_title(task: Task, execution_plan: ExecutionPlan) -> str:
    return f"{execution_plan.artifact_type}: {task.title}"


def _result_summary(
    mission: Mission,
    task: Task,
    execution_plan: ExecutionPlan,
) -> str:
    return (
        f"Completed {task.department.value} work for mission '{mission.title}' "
        f"using {execution_plan.strategy_name} strategy "
        f"(mode={execution_plan.execution_mode.value})."
    )
