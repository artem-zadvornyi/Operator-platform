import type { Metadata } from "next";

import { CompanyCreationPage } from "@/features/company-creation";

export const metadata: Metadata = {
  title: "Create Company — Operator",
  description: "Describe your business idea. Operator will assemble an AI company around it.",
};

export default function CreatePage() {
  return <CompanyCreationPage />;
}
