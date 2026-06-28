import { cva, type VariantProps } from "class-variance-authority";
import { type HTMLAttributes } from "react";

import { cn } from "@/lib/cn";

const pageContainerVariants = cva("mx-auto w-full px-4 sm:px-6 lg:px-8", {
  variants: {
    size: {
      sm: "max-w-[var(--width-container-sm)]",
      md: "max-w-[var(--width-container-md)]",
      lg: "max-w-[var(--width-container-lg)]",
      xl: "max-w-[var(--width-container-xl)]",
      "2xl": "max-w-[var(--width-container-2xl)]",
      full: "max-w-none",
    },
  },
  defaultVariants: {
    size: "xl",
  },
});

export interface PageContainerProps
  extends HTMLAttributes<HTMLDivElement>, VariantProps<typeof pageContainerVariants> {}

export function PageContainer({ className, size, ...props }: PageContainerProps) {
  return <div className={cn(pageContainerVariants({ size }), className)} {...props} />;
}

export { pageContainerVariants };
