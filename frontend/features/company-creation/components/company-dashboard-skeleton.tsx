"use client";

import { Skeleton } from "@/components/ui/skeleton";

export function CompanyDashboardSkeleton() {
  return (
    <div aria-busy="true" aria-live="polite" className="space-y-12">
      <header className="space-y-3 text-center">
        <Skeleton className="mx-auto h-4 w-28" rounded="full" />
        <Skeleton className="mx-auto h-10 w-full max-w-lg" rounded="lg" />
      </header>

      <div className="grid gap-5 lg:grid-cols-2">
        <Skeleton className="h-44 w-full" rounded="lg" />
        <Skeleton className="h-44 w-full" rounded="lg" />
      </div>

      <div className="space-y-4">
        <Skeleton className="h-6 w-40" rounded="md" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <Skeleton key={index} className="h-28 w-full" rounded="lg" />
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <Skeleton className="h-6 w-48" rounded="md" />
        <Skeleton className="h-36 w-full" rounded="lg" />
      </div>
    </div>
  );
}
