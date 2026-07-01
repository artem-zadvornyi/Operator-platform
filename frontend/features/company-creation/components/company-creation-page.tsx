"use client";

import { type MutableRefObject, useRef } from "react";

import { AnimatePresence, motion } from "framer-motion";

import { PageContainer } from "@/components/ui/page-container";
import { Spinner } from "@/components/ui/spinner";
import { cn } from "@/lib/cn";
import { motionTransitions, motionVariants, reducedMotionTransition } from "@/lib/motion";

import type { CreationPhase } from "../hooks/use-company-creation-flow";
import { useCompanyCreationFlow } from "../hooks/use-company-creation-flow";
import type { CompanyDashboardData } from "../types";
import { CompanyDashboard } from "./company-dashboard";
import { CreationErrorState } from "./creation-error-state";
import { CreationSequence } from "./creation-sequence";
import { CreationSuccessMessage } from "./creation-success-message";
import { IdeaInputScreen } from "./idea-input-screen";

interface PhaseContentProps {
  phase: CreationPhase;
  idea: string;
  canSubmit: boolean;
  isLoading: boolean;
  isAnimating: boolean;
  errorMessage: string | null;
  visibleEvents: ReturnType<typeof useCompanyCreationFlow>["visibleEvents"];
  dashboardData: CompanyDashboardData | null;
  prefersReducedMotion: boolean;
  onIdeaChange: (value: string) => void;
  onSubmit: () => void;
  onRetry: () => void;
}

function PhaseContent({
  phase,
  idea,
  canSubmit,
  isLoading,
  isAnimating,
  errorMessage,
  visibleEvents,
  dashboardData,
  prefersReducedMotion,
  onIdeaChange,
  onSubmit,
  onRetry,
}: PhaseContentProps) {
  switch (phase) {
    case "input":
    case "loading":
      return (
        <IdeaInputScreen
          idea={idea}
          canSubmit={canSubmit}
          isLoading={isLoading}
          isAnimating={isAnimating}
          onIdeaChange={onIdeaChange}
          onSubmit={onSubmit}
        />
      );
    case "building":
      return <CreationSequence events={visibleEvents} prefersReducedMotion={prefersReducedMotion} />;
    case "finalizing":
      return (
        <div
          className="flex min-h-[40vh] flex-col items-center justify-center gap-4 py-16"
          role="status"
          aria-live="polite"
        >
          <Spinner size="lg" />
          <p className="text-body text-text-secondary">Starting your company...</p>
        </div>
      );
    case "success":
      return (
        <div className="flex min-h-[40vh] items-center justify-center py-16">
          <CreationSuccessMessage prefersReducedMotion={prefersReducedMotion} />
        </div>
      );
    case "dashboard":
      if (!dashboardData) {
        return (
          <div
            className="flex min-h-[40vh] flex-col items-center justify-center gap-4 py-16"
            role="status"
            aria-live="polite"
          >
            <Spinner size="lg" />
            <p className="text-body text-text-secondary">Loading your company...</p>
          </div>
        );
      }
      return (
        <div className="space-y-10">
          <header className="space-y-2 text-center">
            <p className="text-caption text-text-secondary tracking-wide uppercase">
              Your company
            </p>
            <h1 className="text-h1 text-text-primary">{dashboardData.company.missionTitle}</h1>
          </header>
          <CompanyDashboard data={dashboardData} prefersReducedMotion={prefersReducedMotion} />
        </div>
      );
    case "error":
      return <CreationErrorState message={errorMessage} onRetry={onRetry} />;
    default: {
      const exhaustiveCheck: never = phase;
      return exhaustiveCheck;
    }
  }
}

function getPhaseLayoutKey(phase: CreationPhase): string {
  switch (phase) {
    case "input":
    case "loading":
      return "idea";
    case "building":
      return "building";
    case "finalizing":
      return "finalizing";
    case "success":
      return "success";
    case "dashboard":
      return "dashboard";
    case "error":
      return "error";
    default: {
      const exhaustiveCheck: never = phase;
      return exhaustiveCheck;
    }
  }
}

function getPhaseInitial(
  layoutKey: string,
  initialByKeyRef: MutableRefObject<
    Map<string, false | (typeof motionVariants.fade.initial)>
  >,
): false | typeof motionVariants.fade.initial {
  const stored = initialByKeyRef.current.get(layoutKey);
  if (stored !== undefined) {
    return stored;
  }

  const initial = initialByKeyRef.current.size === 0 ? false : motionVariants.fade.initial;
  initialByKeyRef.current.set(layoutKey, initial);
  return initial;
}

export function CompanyCreationPage() {
  const initialByKeyRef = useRef<
    Map<string, false | (typeof motionVariants.fade.initial)>
  >(new Map());

  const {
    phase,
    idea,
    setIdea,
    errorMessage,
    visibleEvents,
    dashboardData,
    isLoading,
    isAnimating,
    canSubmit,
    startCreation,
    retry,
    prefersReducedMotion,
  } = useCompanyCreationFlow();

  const transition = prefersReducedMotion ? reducedMotionTransition : motionTransitions.normal;

  const isDashboard = phase === "dashboard";
  const isCenteredPhase =
    phase === "input" ||
    phase === "loading" ||
    phase === "finalizing" ||
    phase === "success" ||
    phase === "error";

  const layoutKey = getPhaseLayoutKey(phase);
  const phaseInitial = getPhaseInitial(layoutKey, initialByKeyRef);

  return (
    <main className="min-h-screen py-20 sm:py-28">
      <PageContainer size={isDashboard ? "lg" : "md"}>
        <div
          className={cn(
            "relative w-full",
            !isDashboard && "min-h-[calc(100dvh-10rem)]",
          )}
        >
          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={layoutKey}
              initial={phaseInitial}
              animate={motionVariants.fade.animate}
              exit={motionVariants.fade.exit}
              transition={transition}
              className={cn(
                "w-full",
                isDashboard
                  ? undefined
                  : cn(
                      "absolute inset-x-0 top-0",
                      isCenteredPhase &&
                        "flex min-h-[calc(100dvh-10rem)] items-center justify-center",
                      phase === "building" && "py-8",
                    ),
              )}
            >
              <PhaseContent
                phase={phase}
                idea={idea}
                canSubmit={canSubmit}
                isLoading={isLoading}
                isAnimating={isAnimating}
                errorMessage={errorMessage}
                visibleEvents={visibleEvents}
                dashboardData={dashboardData}
                prefersReducedMotion={prefersReducedMotion}
                onIdeaChange={setIdea}
                onSubmit={() => {
                  void startCreation();
                }}
                onRetry={retry}
              />
            </motion.div>
          </AnimatePresence>
        </div>
      </PageContainer>
    </main>
  );
}
