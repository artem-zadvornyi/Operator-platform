"use client";

import type { CompanyGateway } from "@/features/company-creation/services/company-gateway";
import type {
  CompanyCreationInput,
  CompanyStatusResult,
  CreateCompanyResult,
  StartCompanyResult,
  WorkflowPreview,
} from "@/features/company-creation/types";

interface CompanyDetailResponse extends CompanyStatusResult {
  workflow: WorkflowPreview;
}

function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let detail = "Request failed.";
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === "string") {
        detail = body.detail;
      }
    } catch {
      // Keep default detail when error body is not JSON.
    }
    throw new Error(detail);
  }

  return (await response.json()) as T;
}

export class ApiCompanyGateway implements CompanyGateway {
  async createCompany(input: CompanyCreationInput): Promise<CreateCompanyResult> {
    return request<CreateCompanyResult>("/companies", {
      method: "POST",
      body: JSON.stringify(input),
    });
  }

  async startCompany(companyId: string): Promise<StartCompanyResult> {
    return request<StartCompanyResult>(`/companies/${companyId}/start`, {
      method: "POST",
    });
  }

  async getCompanyStatus(companyId: string): Promise<CompanyStatusResult> {
    const { workflow, ...status } = await this.fetchCompanyDetail(companyId);
    void workflow;
    return status;
  }

  async getWorkflowPreview(companyId: string): Promise<WorkflowPreview> {
    const detail = await this.fetchCompanyDetail(companyId);
    return detail.workflow;
  }

  private fetchCompanyDetail(companyId: string): Promise<CompanyDetailResponse> {
    return request<CompanyDetailResponse>(`/companies/${companyId}`);
  }
}
