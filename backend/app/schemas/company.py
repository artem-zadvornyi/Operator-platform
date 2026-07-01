"""Pydantic schemas for the company API — aligned with frontend gateway types."""

from pydantic import BaseModel, ConfigDict, Field


class CompanyCreateRequest(BaseModel):
    idea: str


class CompanyCEOSchema(BaseModel):
    id: str
    name: str
    status: str
    summary: str


class CompanyDepartmentSchema(BaseModel):
    id: str
    name: str
    status: str
    description: str


class WorkflowTaskPreviewSchema(BaseModel):
    id: str
    title: str
    status: str
    description: str
    department: str


class WorkflowPreviewSchema(BaseModel):
    id: str
    title: str
    tasks: list[WorkflowTaskPreviewSchema]
    current_task: WorkflowTaskPreviewSchema = Field(alias="currentTask")

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)


class CreationEventSchema(BaseModel):
    id: str
    type: str
    title: str
    description: str
    status: str
    department: str | None = None
    timestamp: str | None = None


class CreateCompanyResponse(BaseModel):
    company_id: str = Field(alias="companyId")
    mission_id: str = Field(alias="missionId")
    mission_title: str = Field(alias="missionTitle")
    mission_description: str = Field(alias="missionDescription")
    mission_status: str = Field(alias="missionStatus")
    ceo: CompanyCEOSchema
    departments: list[CompanyDepartmentSchema]
    workflow: WorkflowPreviewSchema
    current_task: WorkflowTaskPreviewSchema = Field(alias="currentTask")
    creation_events: list[CreationEventSchema] = Field(alias="creationEvents")

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)


class StartCompanyResponse(BaseModel):
    company_id: str = Field(alias="companyId")
    status: str

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)


class CompanyDetailResponse(BaseModel):
    company_id: str = Field(alias="companyId")
    mission_id: str = Field(alias="missionId")
    mission_title: str = Field(alias="missionTitle")
    mission_description: str = Field(alias="missionDescription")
    mission_status: str = Field(alias="missionStatus")
    ceo: CompanyCEOSchema
    departments: list[CompanyDepartmentSchema]
    workflow: WorkflowPreviewSchema

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)
