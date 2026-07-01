import type {
  CompanyCreationInput,
  CompanyDashboardData,
  CompanyStatusResult,
  CreateCompanyResult,
  StartCompanyResult,
  WorkflowPreview,
} from "@/features/company-creation/types";

export interface CompanyGateway {
  createCompany(input: CompanyCreationInput): Promise<CreateCompanyResult>;
  startCompany(companyId: string): Promise<StartCompanyResult>;
  getCompanyStatus(companyId: string): Promise<CompanyStatusResult>;
  getWorkflowPreview(companyId: string): Promise<WorkflowPreview>;
  getCompanyDashboard(companyId: string): Promise<CompanyDashboardData>;
}
