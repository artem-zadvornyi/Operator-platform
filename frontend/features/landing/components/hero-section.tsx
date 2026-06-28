import Link from "next/link";

import { Button } from "@/components/ui/button";
import { PageContainer } from "@/components/ui/page-container";
import { cn } from "@/lib/cn";

import { AiCompanyPreview } from "./ai-company-preview";
import { HeroNavigation } from "./hero-navigation";

export function HeroSection() {
  return (
    <div className="relative flex min-h-screen flex-col">
      <div
        aria-hidden
        className={cn(
          "pointer-events-none absolute inset-x-0 top-0 h-[520px]",
          "bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,color-mix(in_srgb,var(--color-accent)_18%,transparent),transparent)]",
        )}
      />

      <HeroNavigation />

      <main className="flex-1">
        <PageContainer size="2xl" className="relative py-16 sm:py-20 lg:py-28">
          <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16 xl:gap-20">
            <div className="flex flex-col items-start">
              <h1 className="text-display text-text-primary max-w-xl">
                Build a business.
                <span className="text-text-secondary block">Not just content.</span>
              </h1>

              <p className="text-body-large text-text-secondary mt-6 max-w-lg">
                Operator turns an idea into a managed content business using an AI CEO and
                specialized AI employees.
              </p>

              <div className="mt-8 flex w-full flex-col gap-3 sm:w-auto sm:flex-row sm:items-center">
                <Button size="lg" asChild>
                  <Link href="#start">Start building</Link>
                </Button>
                <Button variant="secondary" size="lg" asChild>
                  <Link href="#how-it-works">See how it works</Link>
                </Button>
              </div>

              <p className="text-caption text-text-secondary mt-10 tracking-wide uppercase">
                Your content company, operated by AI.
              </p>
            </div>

            <div className="w-full lg:pt-4">
              <AiCompanyPreview />
            </div>
          </div>
        </PageContainer>
      </main>
    </div>
  );
}
