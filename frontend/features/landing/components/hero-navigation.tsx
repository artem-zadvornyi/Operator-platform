import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Logo } from "@/components/ui/logo";
import { PageContainer } from "@/components/ui/page-container";
import { cn } from "@/lib/cn";

const navLinks = [
  { label: "Product", href: "#product" },
  { label: "Pricing", href: "#pricing" },
  { label: "Docs", href: "#docs" },
] as const;

export function HeroNavigation() {
  return (
    <header className="border-border/60 z-sticky bg-background-primary/80 sticky top-0 border-b backdrop-blur-md">
      <PageContainer size="2xl">
        <nav className="flex h-16 items-center justify-between gap-4" aria-label="Main navigation">
          <Link href="/" className="focus-ring rounded-md" aria-label="Operator home">
            <Logo />
          </Link>

          <div className="hidden items-center gap-1 md:flex">
            {navLinks.map((link) => (
              <Link
                key={link.label}
                href={link.href}
                className={cn(
                  "focus-ring rounded-md px-3 py-2",
                  "text-body text-text-secondary duration-fast transition-colors",
                  "hover:text-text-primary",
                )}
              >
                {link.label}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            <Button variant="ghost" size="sm" className="hidden sm:inline-flex" asChild>
              <Link href="#sign-in">Sign in</Link>
            </Button>
            <Button size="sm" asChild>
              <Link href="#create">Create</Link>
            </Button>
          </div>
        </nav>
      </PageContainer>
    </header>
  );
}
