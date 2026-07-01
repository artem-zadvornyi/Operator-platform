"use client";

import { motion } from "framer-motion";

import { motionTransitions, motionVariants, reducedMotionTransition } from "@/lib/motion";

import type { CompanyDashboardData } from "../types";
import { CeoCard } from "./ceo-card";
import { DepartmentsGrid } from "./departments-grid";
import { MissionCard } from "./mission-card";
import { WorkflowPreviewCard } from "./workflow-preview";

export interface CompanyDashboardProps {
  data: CompanyDashboardData;
  prefersReducedMotion: boolean;
}

export function CompanyDashboard({ data, prefersReducedMotion }: CompanyDashboardProps) {
  const transition = prefersReducedMotion ? reducedMotionTransition : motionTransitions.slow;

  return (
    <motion.div
      initial={motionVariants.fade.initial}
      animate={motionVariants.fade.animate}
      transition={transition}
      className="space-y-12"
    >
      <div className="grid gap-5 lg:grid-cols-2">
        <MissionCard company={data.company} />
        <CeoCard ceo={data.company.ceo} />
      </div>

      <DepartmentsGrid
        departments={data.company.departments}
        prefersReducedMotion={prefersReducedMotion}
      />

      <WorkflowPreviewCard workflow={data.workflowPreview} />
    </motion.div>
  );
}
