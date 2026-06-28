import { cva, type VariantProps } from "class-variance-authority";
import { type TextareaHTMLAttributes, forwardRef } from "react";

import { cn } from "@/lib/cn";

const textareaVariants = cva(
  [
    "flex min-h-20 w-full resize-y rounded-md border border-border bg-background-secondary px-3 py-2",
    "text-body text-text-primary placeholder:text-text-secondary",
    "transition-colors duration-fast ease-default",
    "focus-ring",
    "disabled:cursor-not-allowed disabled:opacity-50",
  ],
  {
    variants: {
      state: {
        default: "hover:border-border/80",
        error: "border-danger focus-visible:ring-danger",
      },
    },
    defaultVariants: {
      state: "default",
    },
  },
);

export interface TextareaProps
  extends TextareaHTMLAttributes<HTMLTextAreaElement>, VariantProps<typeof textareaVariants> {}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, state, "aria-invalid": ariaInvalid, ...props }, ref) => {
    const isError = state === "error" || ariaInvalid === true;

    return (
      <textarea
        ref={ref}
        aria-invalid={isError || undefined}
        className={cn(textareaVariants({ state: isError ? "error" : "default" }), className)}
        {...props}
      />
    );
  },
);

Textarea.displayName = "Textarea";

export { textareaVariants };
