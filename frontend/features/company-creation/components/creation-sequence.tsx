"use client";

import { motion } from "framer-motion";

import { motionTransitions, motionVariants, reducedMotionTransition } from "@/lib/motion";

import type { CreationEvent } from "../types";
import { CreationStepItem } from "./creation-step-item";

export interface CreationSequenceProps {
  events: CreationEvent[];
  prefersReducedMotion: boolean;
}

export function CreationSequence({ events, prefersReducedMotion }: CreationSequenceProps) {
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
        {events.map((event) => (
          <div key={event.id} role="listitem">
            <CreationStepItem event={event} prefersReducedMotion={prefersReducedMotion} />
          </div>
        ))}
      </div>
    </div>
  );
}
