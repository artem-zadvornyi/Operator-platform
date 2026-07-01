import type { Metadata } from "next";

import { CompanyDashboardPage } from "@/features/company-creation/components/company-dashboard-page";

interface CompanyPageProps {
  params: Promise<{ companyId: string }>;
}

export async function generateMetadata({ params }: CompanyPageProps): Promise<Metadata> {
  const { companyId } = await params;
  return {
    title: `Company — Operator`,
    description: `View company ${companyId} on Operator.`,
  };
}

export default async function CompanyPage({ params }: CompanyPageProps) {
  const { companyId } = await params;
  return <CompanyDashboardPage companyId={companyId} />;
}
