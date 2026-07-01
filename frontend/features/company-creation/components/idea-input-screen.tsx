"use client";

import { type FormEvent, useEffect, useRef } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";

export interface IdeaInputScreenProps {
  idea: string;
  canSubmit: boolean;
  isLoading: boolean;
  isAnimating: boolean;
  onIdeaChange: (value: string) => void;
  onSubmit: () => void;
}

export function IdeaInputScreen({
  idea,
  canSubmit,
  isLoading,
  isAnimating,
  onIdeaChange,
  onSubmit,
}: IdeaInputScreenProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <div className="mx-auto flex w-full max-w-xl flex-col items-center text-center">
      <h1 className="text-display text-text-primary">What do you want to build?</h1>
      <p className="text-body-large text-text-secondary mt-5 max-w-md">
        Describe your business idea. Operator will assemble an AI company around it.
      </p>

      <form
        onSubmit={handleSubmit}
        className="mt-14 flex w-full flex-col items-center gap-5"
        aria-busy={isLoading || isAnimating}
      >
        <Input
          ref={inputRef}
          inputSize="lg"
          value={idea}
          onChange={(event) => onIdeaChange(event.target.value)}
          placeholder="Luxury TikTok Brand"
          disabled={isLoading || isAnimating}
          aria-label="Business idea"
          className="h-14 text-center text-body-large"
        />
        <Button type="submit" size="lg" disabled={!canSubmit || isLoading} className="min-w-44">
          {isLoading ? (
            <>
              <Spinner size="sm" />
              Creating...
            </>
          ) : (
            "Create Company"
          )}
        </Button>
      </form>
    </div>
  );
}
