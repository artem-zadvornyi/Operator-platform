"use client";

import type { CompanyGateway } from "@/features/company-creation/services/company-gateway";
import type {
  CompanyCreationInput,
  CompanyDashboardData,
  CompanyStatusResult,
  CreateCompanyResult,
  StartCompanyResult,
  WorkflowPreview,
} from "@/features/company-creation/types";

import { ApiCompanyGateway } from "./api-company-gateway";
import { MockCompanyGateway, MOCK_FAILURE_IDEA } from "./mock-company-gateway";

function createCompanyGateway(): CompanyGateway {
  const useMock = process.env.NEXT_PUBLIC_USE_MOCK_GATEWAY !== "false";
  return useMock ? new MockCompanyGateway() : new ApiCompanyGateway();
}

export const companyGateway: CompanyGateway = createCompanyGateway();

export type { CompanyGateway };
export { ApiCompanyGateway, MockCompanyGateway, MOCK_FAILURE_IDEA };
export { buildCreationEvents } from "./creation-events";
export { CompanyNotFoundError, isCompanyNotFoundError } from "./company-not-found-error";
export { toCompanyDashboardData } from "./company-dashboard-mapper";

export async function createCompany(input: CompanyCreationInput): Promise<CreateCompanyResult> {
  return companyGateway.createCompany(input);
}

export async function startCompany(companyId: string): Promise<StartCompanyResult> {
  return companyGateway.startCompany(companyId);
}

export async function getCompanyStatus(companyId: string): Promise<CompanyStatusResult> {
  return companyGateway.getCompanyStatus(companyId);
}

export async function getWorkflowPreview(companyId: string): Promise<WorkflowPreview> {
  return companyGateway.getWorkflowPreview(companyId);
}

export async function getCompanyDashboard(companyId: string): Promise<CompanyDashboardData> {
  return companyGateway.getCompanyDashboard(companyId);
}
