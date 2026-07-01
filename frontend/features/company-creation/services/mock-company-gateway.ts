"use client";

import type { CompanyGateway } from "@/features/company-creation/services/company-gateway";
import { toCompanyDashboardData } from "@/features/company-creation/services/company-dashboard-mapper";
import { CompanyNotFoundError } from "@/features/company-creation/services/company-not-found-error";
import type {
  CompanyCreationInput,
  CompanyDashboardData,
  CompanyStatusResult,
  CreateCompanyResult,
  StartCompanyResult,
  WorkflowPreview,
} from "@/features/company-creation/types";

import { buildCreationEvents } from "./creation-events";

const MOCK_FAILURE_IDEA = "__operator_fail__";
const NETWORK_DELAY_MS = 650;

interface StoredCompany extends CreateCompanyResult {
  started: boolean;
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    globalThis.setTimeout(resolve, ms);
  });
}

function createId(prefix: string): string {
  return `${prefix}_${crypto.randomUUID()}`;
}

export class MockCompanyGateway implements CompanyGateway {
  private readonly companies = new Map<string, StoredCompany>();

  async createCompany(input: CompanyCreationInput): Promise<CreateCompanyResult> {
    await delay(NETWORK_DELAY_MS);

    const idea = input.idea.trim();
    if (!idea) {
      throw new Error("Business idea is required.");
    }

    if (idea === MOCK_FAILURE_IDEA) {
      throw new Error("Company creation failed.");
    }

    const timestamp = new Date().toISOString();
    const companyId = createId("company");
    const missionId = createId("mission");
    const workflowId = createId("workflow");
    const currentTaskId = createId("task");

    const currentTask = {
      id: currentTaskId,
      title: "Research niche and audience",
      status: "Ready to execute",
      description:
        "Validate audience demand and competitor landscape before downstream departments begin work.",
      department: "research",
    };

    const workflow: WorkflowPreview = {
      id: workflowId,
      title: "Mission execution workflow",
      currentTask,
      tasks: [
        currentTask,
        {
          id: createId("task"),
          title: "Define brand identity",
          status: "Queued",
          description: "Establish visual and verbal brand guidelines.",
          department: "brand",
        },
        {
          id: createId("task"),
          title: "Write content scripts",
          status: "Queued",
          description: "Produce scripts aligned with research and brand.",
          department: "scripts",
        },
      ],
    };

    const result: CreateCompanyResult = {
      companyId,
      missionId,
      missionTitle: idea,
      missionDescription: `Operator will assemble an AI company around: ${idea}`,
      missionStatus: "Active",
      ceo: {
        id: createId("ceo"),
        name: "AI CEO",
        status: "Planning",
        summary: "Mission analyzed. Departments assembled and ready to execute.",
      },
      departments: [
        {
          id: "research",
          name: "Research",
          status: "Ready",
          description: "Department operational",
        },
        {
          id: "brand",
          name: "Brand",
          status: "Ready",
          description: "Department operational",
        },
        {
          id: "scripts",
          name: "Scripts",
          status: "Ready",
          description: "Department operational",
        },
        {
          id: "video",
          name: "Video",
          status: "Ready",
          description: "Department operational",
        },
        {
          id: "publishing",
          name: "Publishing",
          status: "Ready",
          description: "Department operational",
        },
        {
          id: "growth",
          name: "Growth",
          status: "Ready",
          description: "Department operational",
        },
      ],
      workflow,
      currentTask,
      creationEvents: buildCreationEvents(timestamp),
    };

    this.companies.set(companyId, { ...result, started: false });
    return result;
  }

  async startCompany(companyId: string): Promise<StartCompanyResult> {
    await delay(400);

    const company = this.companies.get(companyId);
    if (!company) {
      throw new CompanyNotFoundError();
    }

    company.started = true;
    company.missionStatus = "Active";
    company.ceo = {
      ...company.ceo,
      status: "Executing",
      summary: "Strategic plan approved. Workflow execution is underway.",
    };

    this.companies.set(companyId, company);

    return {
      companyId,
      status: "started",
    };
  }

  async getCompanyStatus(companyId: string): Promise<CompanyStatusResult> {
    await delay(300);

    const company = this.companies.get(companyId);
    if (!company) {
      throw new CompanyNotFoundError();
    }

    return {
      companyId: company.companyId,
      missionId: company.missionId,
      missionTitle: company.missionTitle,
      missionDescription: company.missionDescription,
      missionStatus: company.missionStatus,
      ceo: company.ceo,
      departments: company.departments,
    };
  }

  async getWorkflowPreview(companyId: string): Promise<WorkflowPreview> {
    await delay(300);

    const company = this.companies.get(companyId);
    if (!company) {
      throw new CompanyNotFoundError();
    }

    return company.workflow;
  }

  async getCompanyDashboard(companyId: string): Promise<CompanyDashboardData> {
    await delay(300);

    const company = this.companies.get(companyId);
    if (!company) {
      throw new CompanyNotFoundError();
    }

    return toCompanyDashboardData(
      {
        companyId: company.companyId,
        missionId: company.missionId,
        missionTitle: company.missionTitle,
        missionDescription: company.missionDescription,
        missionStatus: company.missionStatus,
        ceo: company.ceo,
        departments: company.departments,
      },
      company.workflow,
    );
  }
}

export { MOCK_FAILURE_IDEA };
