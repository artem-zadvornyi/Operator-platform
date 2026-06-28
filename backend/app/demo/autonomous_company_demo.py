"""Autonomous company demo — end-to-end domain execution without infrastructure."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.domain.ceo import AICEO, StrategyMode
from app.domain.decision import Decision, DecisionStatus
from app.domain.department import DepartmentName
from app.domain.employee import Employee, EmployeeStatus
from app.domain.execution_strategy import DeterministicExecutionStrategy, ExecutionPlan
from app.domain.mission import Mission, MissionPriority, MissionStatus
from app.domain.pipeline import Pipeline
from app.domain.plan import Plan
from app.domain.planner import Planner
from app.domain.runtime import AgentExecution
from app.domain.task import Task
from app.domain.workflow import Workflow

LogFn = Callable[[str], None]

DEMO_START = datetime(2026, 12, 1, 8, 0, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class AutonomousCompanyDemoResult:
    """Artifacts produced by a single autonomous company demo run."""

    mission: Mission
    ceo: AICEO
    decision: Decision
    plan: Plan
    workflow: Workflow
    first_task: Task
    employee: Employee
    execution_plan: ExecutionPlan
    execution: AgentExecution


def run_autonomous_company_demo(*, log: LogFn = print) -> AutonomousCompanyDemoResult:
    """Execute the full Operator domain flow and print a readable execution log."""
    timestamp = DEMO_START

    mission = _create_mission(timestamp)
    log(f"MISSION CREATED: {mission.title}")

    ceo = _create_and_assign_ceo(mission, timestamp + timedelta(minutes=1))
    log(f"CEO ASSIGNED: {ceo.name} → mission {mission.id}")

    ceo, decision, mission = _propose_decision(ceo, mission, timestamp + timedelta(minutes=2))
    log(f"DECISION CREATED: {decision.title} [{decision.status.value}]")

    approved_decision = decision.with_status(DecisionStatus.APPROVED)
    log(f"DECISION APPROVED: {approved_decision.id}")

    planner = Planner()
    plan = planner.create_plan(approved_decision)
    log(f"PLAN CREATED: {plan.title} ({len(plan.steps)} steps)")

    pipeline = Pipeline(planner=planner)
    workflow = pipeline.build(approved_decision)
    log(f"WORKFLOW CREATED: {workflow.id} ({len(workflow.tasks)} tasks)")

    available_tasks = workflow.next_available_tasks()
    if not available_tasks:
        msg = "Workflow has no available tasks after creation."
        raise RuntimeError(msg)

    first_task = available_tasks[0]
    log(
        f"FIRST TASK: {first_task.title} "
        f"[{first_task.department.value}] priority={first_task.priority.value}"
    )

    employee = _create_research_employee(timestamp + timedelta(minutes=3))
    log(f"EMPLOYEE READY: {employee.name} ({employee.department.value})")

    strategy = DeterministicExecutionStrategy()
    execution_plan = strategy.prepare_execution(first_task, employee)
    log(
        f"EXECUTION PLAN: {execution_plan.strategy_name} "
        f"mode={execution_plan.execution_mode.value} "
        f"artifact={execution_plan.artifact_type}"
    )

    workflow = workflow.assign_task(
        employee.id,
        first_task.id,
        timestamp + timedelta(minutes=4),
    )

    execution = AgentExecution.create(first_task, employee.id)
    running = execution.start(timestamp + timedelta(minutes=5))
    log(f"EXECUTION STARTED: {running.id} [{running.status.value}]")

    finished = running.succeed(
        title=_result_title(first_task, execution_plan),
        summary=_result_summary(mission, first_task, execution_plan),
        finished_at=timestamp + timedelta(minutes=6),
    )
    log(f"EXECUTION FINISHED: {finished.status.value}")

    result = finished.result
    if result is None:
        msg = "Succeeded execution must include a result."
        raise RuntimeError(msg)

    log(f"ARTIFACT CREATED: {result.artifact_reference}")

    workflow = workflow.complete_task(
        first_task.id,
        result.artifact_reference,
        timestamp + timedelta(minutes=7),
    )
    completed_task = workflow.get_task(first_task.id)
    log(f"TASK COMPLETED: {completed_task.title}")

    return AutonomousCompanyDemoResult(
        mission=mission,
        ceo=ceo,
        decision=approved_decision,
        plan=plan,
        workflow=workflow,
        first_task=completed_task,
        employee=employee,
        execution_plan=execution_plan,
        execution=finished,
    )


def _create_mission(timestamp: datetime) -> Mission:
    return Mission.create(
        title="Build a finance media business",
        description="Create a durable content company around personal finance education.",
        goal="Reach 100k subscribers and sustainable ad revenue within 18 months.",
        target_audience="Young professionals learning money management.",
        primary_platforms=("YouTube", "TikTok"),
        languages=("English",),
        priority=MissionPriority.HIGH,
        status=MissionStatus.ACTIVE,
        created_at=timestamp,
        updated_at=timestamp,
    )


def _create_and_assign_ceo(mission: Mission, timestamp: datetime) -> AICEO:
    return AICEO.create(
        "AI CEO",
        strategy_mode=StrategyMode.BALANCED,
        created_at=timestamp,
    ).assign_mission(mission, timestamp)


def _propose_decision(
    ceo: AICEO,
    mission: Mission,
    timestamp: datetime,
) -> tuple[AICEO, Decision, Mission]:
    updated_ceo, decision = ceo.propose_decision(mission, timestamp)
    updated_mission = mission.add_decision(decision.id, timestamp)
    return updated_ceo, decision, updated_mission


def _create_research_employee(timestamp: datetime) -> Employee:
    return Employee(
        id=uuid4(),
        name="Research Analyst",
        department=DepartmentName.RESEARCH,
        role="Audience Researcher",
        status=EmployeeStatus.IDLE,
        memory_reference="memory://employees/research-analyst",
        created_at=timestamp,
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


def main() -> None:
    """Run the autonomous company demo from the command line."""
    run_autonomous_company_demo()


if __name__ == "__main__":
    main()
