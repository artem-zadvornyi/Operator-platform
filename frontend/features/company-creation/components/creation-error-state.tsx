"use client";

import { AlertCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export interface CreationErrorStateProps {
  message?: string | null;
  onRetry: () => void;
}

export function CreationErrorState({
  message,
  onRetry,
}: CreationErrorStateProps) {
  return (
    <div className="mx-auto w-full max-w-md">
      <Card className="border-danger/20">
        <CardHeader className="text-center">
          <div className="bg-danger/10 text-danger mx-auto mb-2 flex size-12 items-center justify-center rounded-full">
            <AlertCircle className="size-6" aria-hidden />
          </div>
          <CardTitle>Company creation failed</CardTitle>
          <CardDescription>
            {message ?? "Something went wrong while assembling your company."}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center pb-8">
          <Button onClick={onRetry} size="lg" className="min-w-36">
            Try again
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
