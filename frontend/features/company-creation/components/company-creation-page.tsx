"use client";

import { AnimatePresence, motion } from "framer-motion";

import { PageContainer } from "@/components/ui/page-container";
import { motionTransitions, motionVariants, reducedMotionTransition } from "@/lib/motion";

import { useCompanyCreationFlow } from "../hooks/use-company-creation-flow";
import { CompanyDashboard } from "./company-dashboard";
import { CreationSequence } from "./creation-sequence";
import { CreationSuccessMessage } from "./creation-success-message";
import { IdeaInputScreen } from "./idea-input-screen";

export function CompanyCreationPage() {
  const {
    phase,
    idea,
    setIdea,
    buildStep,
    isAnimating,
    canSubmit,
    startCreation,
    prefersReducedMotion,
  } = useCompanyCreationFlow();

  const transition = prefersReducedMotion ? reducedMotionTransition : motionTransitions.normal;

  return (
    <main className="min-h-screen py-20 sm:py-28">
      <PageContainer size={phase === "dashboard" ? "lg" : "md"}>
        <AnimatePresence mode="wait">
          {phase === "input" && (
            <motion.div
              key="input"
              initial={motionVariants.fade.initial}
              animate={motionVariants.fade.animate}
              exit={motionVariants.fade.exit}
              transition={transition}
            >
              <IdeaInputScreen
                idea={idea}
                canSubmit={canSubmit}
                isAnimating={isAnimating}
                onIdeaChange={setIdea}
                onSubmit={startCreation}
              />
            </motion.div>
          )}

          {phase === "building" && (
            <motion.div
              key="building"
              initial={motionVariants.fade.initial}
              animate={motionVariants.fade.animate}
              exit={motionVariants.fade.exit}
              transition={transition}
              className="py-8"
            >
              <CreationSequence buildStep={buildStep} prefersReducedMotion={prefersReducedMotion} />
            </motion.div>
          )}

          {phase === "success" && (
            <motion.div
              key="success"
              initial={motionVariants.fade.initial}
              animate={motionVariants.fade.animate}
              exit={motionVariants.fade.exit}
              transition={transition}
              className="flex min-h-[40vh] items-center justify-center py-16"
            >
              <CreationSuccessMessage prefersReducedMotion={prefersReducedMotion} />
            </motion.div>
          )}

          {phase === "dashboard" && (
            <motion.div
              key="dashboard"
              initial={motionVariants.fade.initial}
              animate={motionVariants.fade.animate}
              exit={motionVariants.fade.exit}
              transition={transition}
              className="space-y-10"
            >
              <header className="space-y-2 text-center">
                <p className="text-caption text-text-secondary tracking-wide uppercase">
                  Your company
                </p>
                <h1 className="text-h1 text-text-primary">{idea}</h1>
              </header>
              <CompanyDashboard idea={idea} prefersReducedMotion={prefersReducedMotion} />
            </motion.div>
          )}
        </AnimatePresence>
      </PageContainer>
    </main>
  );
}
