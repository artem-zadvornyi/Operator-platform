"use client";

import { motion } from "framer-motion";

import { motionTransitions, motionVariants, reducedMotionTransition } from "@/lib/motion";

import { DEPARTMENT_CARDS } from "../constants";
import { DepartmentCard } from "./department-card";

export interface DepartmentsGridProps {
  prefersReducedMotion: boolean;
}

export function DepartmentsGrid({ prefersReducedMotion }: DepartmentsGridProps) {
  const transition = prefersReducedMotion ? reducedMotionTransition : motionTransitions.normal;

  return (
    <section aria-labelledby="departments-heading">
      <h2 id="departments-heading" className="text-h3 text-text-primary mb-5">
        Departments
      </h2>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {DEPARTMENT_CARDS.map((department, index) => (
          <motion.div
            key={department.id}
            initial={motionVariants.slideUp.initial}
            animate={motionVariants.slideUp.animate}
            transition={{
              ...transition,
              delay: prefersReducedMotion ? 0 : index * 0.06,
            }}
          >
            <DepartmentCard
              name={department.name}
              status={department.status}
              icon={department.icon}
            />
          </motion.div>
        ))}
      </div>
    </section>
  );
}
