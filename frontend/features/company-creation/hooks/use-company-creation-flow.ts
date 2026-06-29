"use client";

import { useCallback, useEffect, useState } from "react";

import {
  ANIMATION_STEP_DELAY_MS,
  CREATION_STEPS,
  SUCCESS_MESSAGE_DELAY_MS,
} from "@/features/company-creation/constants";
import { usePrefersReducedMotion } from "@/hooks";

export type CreationPhase = "input" | "building" | "success" | "dashboard";

export function useCompanyCreationFlow() {
  const prefersReducedMotion = usePrefersReducedMotion();
  const [phase, setPhase] = useState<CreationPhase>("input");
  const [idea, setIdea] = useState("");
  const [buildStep, setBuildStep] = useState(-1);

  const isAnimating = phase === "building" || phase === "success";
  const canSubmit = idea.trim().length > 0 && !isAnimating;

  const startCreation = useCallback(() => {
    if (!idea.trim() || isAnimating) {
      return;
    }
    setPhase("building");
    setBuildStep(0);
  }, [idea, isAnimating]);

  const stepDelay = prefersReducedMotion ? 0 : ANIMATION_STEP_DELAY_MS;
  const successDelay = prefersReducedMotion ? 100 : SUCCESS_MESSAGE_DELAY_MS;
  const totalSteps = CREATION_STEPS.length;

  useEffect(() => {
    if (phase !== "building" || buildStep < 0) {
      return;
    }

    if (buildStep < totalSteps - 1) {
      const timer = window.setTimeout(() => {
        setBuildStep((current) => current + 1);
      }, stepDelay);
      return () => window.clearTimeout(timer);
    }

    const timer = window.setTimeout(() => {
      setPhase("success");
    }, stepDelay);
    return () => window.clearTimeout(timer);
  }, [phase, buildStep, stepDelay, totalSteps]);

  useEffect(() => {
    if (phase !== "success") {
      return;
    }

    const timer = window.setTimeout(() => {
      setPhase("dashboard");
    }, successDelay);
    return () => window.clearTimeout(timer);
  }, [phase, successDelay]);

  return {
    phase,
    idea,
    setIdea,
    buildStep,
    isAnimating,
    canSubmit,
    startCreation,
    prefersReducedMotion,
  };
}
