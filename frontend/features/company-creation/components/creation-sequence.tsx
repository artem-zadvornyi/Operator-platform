"use client";

import { motion } from "framer-motion";

import { motionTransitions, motionVariants, reducedMotionTransition } from "@/lib/motion";

import { CREATION_STEPS } from "../constants";
import { CreationStepItem } from "./creation-step-item";

export interface CreationSequenceProps {
  buildStep: number;
  prefersReducedMotion: boolean;
}

export function CreationSequence({ buildStep, prefersReducedMotion }: CreationSequenceProps) {
  const visibleSteps = CREATION_STEPS.slice(0, buildStep + 1);
  const transition = prefersReducedMotion ? reducedMotionTransition : motionTransitions.normal;

  return (
    <div className="mx-auto w-full max-w-lg">
      <motion.p
        initial={motionVariants.fade.initial}
        animate={motionVariants.fade.animate}
        transition={transition}
        className="text-caption text-text-secondary mb-8 text-center tracking-wide uppercase"
      >
        Building your company
      </motion.p>
      <div className="flex flex-col gap-3" role="list" aria-live="polite" aria-relevant="additions">
        {visibleSteps.map((step) => (
          <div key={step.id} role="listitem">
            <CreationStepItem step={step} prefersReducedMotion={prefersReducedMotion} />
          </div>
        ))}
      </div>
    </div>
  );
}
