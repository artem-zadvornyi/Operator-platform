import type {
  CompanyDashboardData,
  CompanyStatusResult,
  WorkflowPreview,
} from "@/features/company-creation/types";

export function toCompanyDashboardData(
  status: CompanyStatusResult,
  workflowPreview: WorkflowPreview,
): CompanyDashboardData {
  return {
    company: {
      companyId: status.companyId,
      missionId: status.missionId,
      missionTitle: status.missionTitle,
      missionDescription: status.missionDescription,
      missionStatus: status.missionStatus,
      ceo: status.ceo,
      departments: status.departments,
    },
    workflowPreview,
  };
}
