"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import type { CompanyGateway } from "@/features/company-creation/services/company-gateway";
import {
  companyGateway,
  isCompanyNotFoundError,
} from "@/features/company-creation/services";
import { isValidCompanyId } from "@/features/company-creation/lib/company-id";
import type { CompanyDashboardData } from "@/features/company-creation/types";

export type CompanyDashboardLoadState = "loading" | "ready" | "not-found" | "error";

export function useCompanyDashboard(
  companyId: string,
  gateway: CompanyGateway = companyGateway,
) {
  const [loadState, setLoadState] = useState<CompanyDashboardLoadState>("loading");
  const [dashboardData, setDashboardData] = useState<CompanyDashboardData | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const requestGenerationRef = useRef(0);

  const reload = useCallback(async () => {
    const generation = requestGenerationRef.current + 1;
    requestGenerationRef.current = generation;

    if (!isValidCompanyId(companyId)) {
      setDashboardData(null);
      setErrorMessage(null);
      setLoadState("not-found");
      return;
    }

    setLoadState("loading");
    setErrorMessage(null);
    setDashboardData(null);

    try {
      const data = await gateway.getCompanyDashboard(companyId);
      if (generation !== requestGenerationRef.current) {
        return;
      }
      setDashboardData(data);
      setLoadState("ready");
    } catch (error) {
      if (generation !== requestGenerationRef.current) {
        return;
      }
      if (isCompanyNotFoundError(error)) {
        setLoadState("not-found");
        return;
      }
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to load this company.",
      );
      setLoadState("error");
    }
  }, [companyId, gateway]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return {
    loadState,
    dashboardData,
    errorMessage,
    reload,
  };
}
