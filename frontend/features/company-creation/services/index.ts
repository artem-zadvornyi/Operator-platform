"use client";

import type { CompanyGateway } from "@/features/company-creation/services/company-gateway";
import type {
  CompanyCreationInput,
  CompanyStatusResult,
  CreateCompanyResult,
  StartCompanyResult,
  WorkflowPreview,
} from "@/features/company-creation/types";

import { MockCompanyGateway } from "./mock-company-gateway";

export const companyGateway: CompanyGateway = new MockCompanyGateway();

export type { CompanyGateway };
export { MockCompanyGateway, MOCK_FAILURE_IDEA } from "./mock-company-gateway";
export { buildCreationEvents } from "./creation-events";

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
