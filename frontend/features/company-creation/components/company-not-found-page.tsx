"use client";

import Link from "next/link";
import { Building2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function CompanyNotFoundPage() {
  return (
    <div className="mx-auto w-full max-w-lg">
      <Card className="border-border/80">
        <CardHeader className="text-center">
          <div className="bg-background-secondary mx-auto mb-2 flex size-12 items-center justify-center rounded-full">
            <Building2 className="text-text-secondary size-6" aria-hidden />
          </div>
          <CardTitle>Company not found</CardTitle>
          <CardDescription>
            This company does not exist or may have been removed. Check the URL or create a new
            company to get started.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center gap-3 pb-8">
          <Button asChild size="lg" className="min-w-36">
            <Link href="/create">Create company</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
