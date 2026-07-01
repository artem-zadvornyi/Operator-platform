export type CreationEventStatus = "pending" | "in_progress" | "completed";

export type CreationEventType =
  | "CEO_ASSIGNED"
  | "RESEARCH_READY"
  | "BRAND_READY"
  | "SCRIPTS_READY"
  | "VIDEO_READY"
  | "PUBLISHING_READY"
  | "GROWTH_READY"
  | "WORKFLOW_CREATED"
  | "FIRST_TASK_READY";

export interface CreationEvent {
  id: string;
  type: CreationEventType;
  title: string;
  description: string;
  status: CreationEventStatus;
  department?: string;
  timestamp?: string;
}

export interface CompanyCreationInput {
  idea: string;
}

export interface CompanyCEO {
  id: string;
  name: string;
  status: string;
  summary: string;
}

export interface CompanyDepartment {
  id: string;
  name: string;
  status: string;
  description: string;
}

export interface WorkflowTaskPreview {
  id: string;
  title: string;
  status: string;
  description: string;
  department: string;
}

export interface WorkflowPreview {
  id: string;
  title: string;
  tasks: WorkflowTaskPreview[];
  currentTask: WorkflowTaskPreview;
}

export interface CreateCompanyResult {
  companyId: string;
  missionId: string;
  missionTitle: string;
  missionDescription: string;
  missionStatus: string;
  ceo: CompanyCEO;
  departments: CompanyDepartment[];
  workflow: WorkflowPreview;
  currentTask: WorkflowTaskPreview;
  creationEvents: CreationEvent[];
}

export interface CreatedCompany {
  companyId: string;
  missionId: string;
  missionTitle: string;
  missionDescription: string;
  missionStatus: string;
  ceo: CompanyCEO;
  departments: CompanyDepartment[];
}

export interface CompanyStatusResult {
  companyId: string;
  missionId: string;
  missionTitle: string;
  missionDescription: string;
  missionStatus: string;
  ceo: CompanyCEO;
  departments: CompanyDepartment[];
}

export interface StartCompanyResult {
  companyId: string;
  status: string;
}

export interface CompanyDashboardData {
  company: CreatedCompany;
  workflowPreview: WorkflowPreview;
}
