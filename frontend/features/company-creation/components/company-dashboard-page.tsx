"use client";

import { PageContainer } from "@/components/ui/page-container";
import { usePrefersReducedMotion } from "@/hooks";

import { useCompanyDashboard } from "../hooks/use-company-dashboard";
import { CompanyDashboard } from "./company-dashboard";
import { CompanyDashboardErrorState } from "./company-dashboard-error-state";
import { CompanyDashboardSkeleton } from "./company-dashboard-skeleton";
import { CompanyNotFoundPage } from "./company-not-found-page";

export interface CompanyDashboardPageProps {
  companyId: string;
}

export function CompanyDashboardPage({ companyId }: CompanyDashboardPageProps) {
  const prefersReducedMotion = usePrefersReducedMotion();
  const { loadState, dashboardData, errorMessage, reload } = useCompanyDashboard(companyId);

  return (
    <main className="min-h-screen py-20 sm:py-28">
      <PageContainer size="lg">
        {loadState === "loading" ? <CompanyDashboardSkeleton /> : null}

        {loadState === "not-found" ? <CompanyNotFoundPage /> : null}

        {loadState === "error" ? (
          <CompanyDashboardErrorState
            message={errorMessage}
            onRetry={() => {
              void reload();
            }}
          />
        ) : null}

        {loadState === "ready" && dashboardData ? (
          <div className="space-y-10">
            <header className="space-y-2 text-center">
              <p className="text-caption text-text-secondary tracking-wide uppercase">
                Your company
              </p>
              <h1 className="text-h1 text-text-primary">{dashboardData.company.missionTitle}</h1>
            </header>
            <CompanyDashboard data={dashboardData} prefersReducedMotion={prefersReducedMotion} />
          </div>
        ) : null}
      </PageContainer>
    </main>
  );
}
