"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import {
  ANIMATION_STEP_DELAY_MS,
  FINALIZE_DELAY_MS,
} from "@/features/company-creation/constants";
import type { CompanyGateway } from "@/features/company-creation/services/company-gateway";
import { companyGateway } from "@/features/company-creation/services";
import type { CreateCompanyResult, CreationEvent } from "@/features/company-creation/types";
import { usePrefersReducedMotion } from "@/hooks";

export type CreationPhase =
  | "input"
  | "loading"
  | "building"
  | "finalizing"
  | "error";

export function useCompanyCreationFlow(gateway: CompanyGateway = companyGateway) {
  const router = useRouter();
  const prefersReducedMotion = usePrefersReducedMotion();
  const [phase, setPhase] = useState<CreationPhase>("input");
  const [idea, setIdea] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [createResult, setCreateResult] = useState<CreateCompanyResult | null>(null);
  const [visibleEventCount, setVisibleEventCount] = useState(0);
  const finalizeStartedRef = useRef(false);
  const creatingRef = useRef(false);
  const flowGenerationRef = useRef(0);

  const isLoading = phase === "loading" || phase === "finalizing";
  const isAnimating = isLoading || phase === "building";
  const canSubmit = idea.trim().length > 0 && !isAnimating;

  const creationEvents: CreationEvent[] = createResult?.creationEvents ?? [];
  const stepDelay = prefersReducedMotion ? 0 : ANIMATION_STEP_DELAY_MS;
  const finalizeDelay = prefersReducedMotion ? 0 : FINALIZE_DELAY_MS;

  const resetFlow = useCallback(() => {
    flowGenerationRef.current += 1;
    creatingRef.current = false;
    finalizeStartedRef.current = false;
    setPhase("input");
    setIdea("");
    setErrorMessage(null);
    setCreateResult(null);
    setVisibleEventCount(0);
  }, []);

  const startCreation = useCallback(async () => {
    const trimmedIdea = idea.trim();
    if (!trimmedIdea || creatingRef.current) {
      return;
    }

    const generation = flowGenerationRef.current;
    creatingRef.current = true;
    setErrorMessage(null);
    setPhase("loading");
    setCreateResult(null);
    setVisibleEventCount(0);
    finalizeStartedRef.current = false;

    try {
      const result = await gateway.createCompany({ idea: trimmedIdea });
      if (generation !== flowGenerationRef.current) {
        return;
      }
      setCreateResult(result);
      setVisibleEventCount(1);
      setPhase("building");
    } catch (error) {
      if (generation !== flowGenerationRef.current) {
        return;
      }
      setErrorMessage(
        error instanceof Error ? error.message : "Company creation failed.",
      );
      setPhase("error");
    } finally {
      if (generation === flowGenerationRef.current) {
        creatingRef.current = false;
      }
    }
  }, [gateway, idea]);

  const retry = useCallback(() => {
    resetFlow();
  }, [resetFlow]);

  useEffect(() => {
    if (phase !== "building" || creationEvents.length === 0) {
      return;
    }

    if (visibleEventCount < creationEvents.length) {
      const timer = window.setTimeout(() => {
        setVisibleEventCount((current) => current + 1);
      }, stepDelay);
      return () => window.clearTimeout(timer);
    }

    const timer = window.setTimeout(() => {
      setPhase("finalizing");
    }, stepDelay);
    return () => window.clearTimeout(timer);
  }, [phase, creationEvents.length, visibleEventCount, stepDelay]);

  useEffect(() => {
    if (phase !== "finalizing" || !createResult || finalizeStartedRef.current) {
      return;
    }

    finalizeStartedRef.current = true;

    const generation = flowGenerationRef.current;

    const finalize = async () => {
      try {
        await gateway.startCompany(createResult.companyId);
        if (generation !== flowGenerationRef.current) {
          return;
        }

        if (finalizeDelay > 0) {
          await new Promise<void>((resolve) => {
            window.setTimeout(resolve, finalizeDelay);
          });
        }

        if (generation !== flowGenerationRef.current) {
          return;
        }

        router.push(`/companies/${createResult.companyId}`);
      } catch (error) {
        if (generation !== flowGenerationRef.current) {
          return;
        }
        setErrorMessage(
          error instanceof Error ? error.message : "Company creation failed.",
        );
        setPhase("error");
      }
    };

    void finalize();
  }, [phase, createResult, gateway, finalizeDelay, router]);

  return {
    phase,
    idea,
    setIdea,
    errorMessage,
    creationEvents,
    visibleEvents: creationEvents.slice(0, visibleEventCount),
    isLoading,
    isAnimating,
    canSubmit,
    startCreation,
    retry,
    resetFlow,
    prefersReducedMotion,
  };
}
