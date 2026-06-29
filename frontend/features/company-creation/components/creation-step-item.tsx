"use client";

import { motion } from "framer-motion";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/cn";
import { motionTransitions, motionVariants, reducedMotionTransition } from "@/lib/motion";

import { type CreationStep } from "../constants";

export interface CreationStepItemProps {
  step: CreationStep;
  prefersReducedMotion: boolean;
}

export function CreationStepItem({ step, prefersReducedMotion }: CreationStepItemProps) {
  const Icon = step.icon;
  const transition = prefersReducedMotion ? reducedMotionTransition : motionTransitions.slow;

  return (
    <motion.div
      layout
      initial={motionVariants.slideUp.initial}
      animate={motionVariants.slideUp.animate}
      transition={transition}
      className={cn(
        "flex items-center gap-4 rounded-lg border px-4 py-3.5",
        step.kind === "ceo"
          ? "border-accent/25 bg-accent/5"
          : "border-border bg-background-secondary/60",
      )}
    >
      <div
        className={cn(
          "flex size-10 shrink-0 items-center justify-center rounded-md",
          step.kind === "ceo" ? "bg-accent/15 text-accent" : "bg-card text-text-secondary",
        )}
      >
        <Icon className="size-5" aria-hidden />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-body-large text-text-primary font-medium">{step.label}</p>
      </div>
      <Badge variant={step.kind === "ceo" ? "outline" : "default"} className="shrink-0">
        {step.status}
      </Badge>
    </motion.div>
  );
}
