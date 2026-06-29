"use client";

import { motion } from "framer-motion";

import { motionTransitions, motionVariants, reducedMotionTransition } from "@/lib/motion";

import { CeoCard } from "./ceo-card";
import { DepartmentsGrid } from "./departments-grid";
import { MissionCard } from "./mission-card";
import { WorkflowPreview } from "./workflow-preview";

export interface CompanyDashboardProps {
  idea: string;
  prefersReducedMotion: boolean;
}

export function CompanyDashboard({ idea, prefersReducedMotion }: CompanyDashboardProps) {
  const transition = prefersReducedMotion ? reducedMotionTransition : motionTransitions.slow;

  return (
    <motion.div
      initial={motionVariants.fade.initial}
      animate={motionVariants.fade.animate}
      transition={transition}
      className="space-y-12"
    >
      <div className="grid gap-5 lg:grid-cols-2">
        <MissionCard idea={idea} />
        <CeoCard />
      </div>

      <DepartmentsGrid prefersReducedMotion={prefersReducedMotion} />

      <WorkflowPreview />
    </motion.div>
  );
}
