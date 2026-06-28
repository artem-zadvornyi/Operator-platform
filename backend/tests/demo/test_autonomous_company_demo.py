from app.demo.autonomous_company_demo import run_autonomous_company_demo
from app.domain import (
    DecisionStatus,
    DepartmentName,
    ExecutionMode,
    ExecutionStatus,
    MissionStatus,
    TaskStatus,
)


def test_autonomous_company_demo_completes_full_domain_flow() -> None:
    logs: list[str] = []
    result = run_autonomous_company_demo(log=logs.append)

    assert result.mission.status is MissionStatus.ACTIVE
    assert result.decision.status is DecisionStatus.APPROVED
    assert len(result.plan.steps) == 6
    assert len(result.workflow.tasks) == 6

    assert result.first_task.department is DepartmentName.RESEARCH
    assert result.first_task.status is TaskStatus.COMPLETED
    assert result.first_task.result_reference == result.execution.result.artifact_reference

    assert result.employee.department is result.first_task.department
    assert result.execution_plan.task_id == result.first_task.id
    assert result.execution_plan.employee_id == result.employee.id
    assert result.execution_plan.execution_mode is ExecutionMode.DETERMINISTIC

    assert result.execution.status is ExecutionStatus.SUCCEEDED
    assert result.execution.result is not None
    assert result.execution.result.task_id == result.first_task.id

    completed_count = sum(1 for task in result.workflow.tasks if task.is_completed)
    assert completed_count == 1

    next_task = result.workflow.next_available_tasks()[0]
    assert next_task.id != result.first_task.id
    assert next_task.department is DepartmentName.BRAND

    assert logs == [
        "MISSION CREATED: Build a finance media business",
        f"CEO ASSIGNED: AI CEO → mission {result.mission.id}",
        "DECISION CREATED: Advance mission: Build a finance media business [proposed]",
        f"DECISION APPROVED: {result.decision.id}",
        "PLAN CREATED: Plan: Advance mission: Build a finance media business (6 steps)",
        f"WORKFLOW CREATED: {result.workflow.id} (6 tasks)",
        "FIRST TASK: Research niche and audience [Research] priority=high",
        "EMPLOYEE READY: Research Analyst (Research)",
        "EXECUTION PLAN: deterministic mode=deterministic artifact=research_brief",
        f"EXECUTION STARTED: {result.execution.id} [running]",
        "EXECUTION FINISHED: succeeded",
        f"ARTIFACT CREATED: {result.execution.result.artifact_reference}",
        "TASK COMPLETED: Research niche and audience",
    ]
