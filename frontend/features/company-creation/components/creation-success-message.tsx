"use client";

import { motion } from "framer-motion";

import { motionTransitions, motionVariants, reducedMotionTransition } from "@/lib/motion";

export interface CreationSuccessMessageProps {
  prefersReducedMotion: boolean;
}

export function CreationSuccessMessage({ prefersReducedMotion }: CreationSuccessMessageProps) {
  const transition = prefersReducedMotion ? reducedMotionTransition : motionTransitions.slow;

  return (
    <motion.div
      initial={motionVariants.fade.initial}
      animate={motionVariants.fade.animate}
      transition={transition}
      className="text-center"
      role="status"
    >
      <p className="text-h2 text-text-primary">Company successfully created.</p>
    </motion.div>
  );
}
