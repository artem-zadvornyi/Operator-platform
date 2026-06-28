import { cva, type VariantProps } from "class-variance-authority";
import { type InputHTMLAttributes, forwardRef } from "react";

import { cn } from "@/lib/cn";

const inputVariants = cva(
  [
    "flex w-full rounded-md border border-border bg-background-secondary px-3 py-2",
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
      inputSize: {
        sm: "h-8 text-small",
        md: "h-9 text-body",
        lg: "h-10 text-body-large",
      },
    },
    defaultVariants: {
      state: "default",
      inputSize: "md",
    },
  },
);

export interface InputProps
  extends InputHTMLAttributes<HTMLInputElement>, VariantProps<typeof inputVariants> {}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, state, inputSize, type = "text", "aria-invalid": ariaInvalid, ...props }, ref) => {
    const isError = state === "error" || ariaInvalid === true;

    return (
      <input
        ref={ref}
        type={type}
        aria-invalid={isError || undefined}
        className={cn(
          inputVariants({ state: isError ? "error" : "default", inputSize }),
          className,
        )}
        {...props}
      />
    );
  },
);

Input.displayName = "Input";

export { inputVariants };
