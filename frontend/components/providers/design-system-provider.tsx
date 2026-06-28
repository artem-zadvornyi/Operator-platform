"use client";

import { TooltipProvider } from "@/components/ui/tooltip";

export function DesignSystemProvider({ children }: { children: React.ReactNode }) {
  return (
    <TooltipProvider delayDuration={300} skipDelayDuration={0}>
      {children}
    </TooltipProvider>
  );
}
