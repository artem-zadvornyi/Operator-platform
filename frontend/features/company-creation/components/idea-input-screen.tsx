"use client";

import { type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export interface IdeaInputScreenProps {
  idea: string;
  canSubmit: boolean;
  isAnimating: boolean;
  onIdeaChange: (value: string) => void;
  onSubmit: () => void;
}

export function IdeaInputScreen({
  idea,
  canSubmit,
  isAnimating,
  onIdeaChange,
  onSubmit,
}: IdeaInputScreenProps) {
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
        aria-busy={isAnimating}
      >
        <Input
          inputSize="lg"
          value={idea}
          onChange={(event) => onIdeaChange(event.target.value)}
          placeholder="Luxury TikTok Brand"
          disabled={isAnimating}
          aria-label="Business idea"
          className="h-14 text-center text-body-large"
          autoFocus
        />
        <Button type="submit" size="lg" disabled={!canSubmit} className="min-w-44">
          Create Company
        </Button>
      </form>
    </div>
  );
}
