import { cva, type VariantProps } from "class-variance-authority";
import { type HTMLAttributes } from "react";

import { cn } from "@/lib/cn";

const sectionContainerVariants = cva("w-full", {
  variants: {
    spacing: {
      sm: "py-8",
      md: "py-12",
      lg: "py-16",
      xl: "py-24",
    },
  },
  defaultVariants: {
    spacing: "md",
  },
});

export interface SectionContainerProps
  extends HTMLAttributes<HTMLElement>, VariantProps<typeof sectionContainerVariants> {
  as?: "section" | "div";
}

export function SectionContainer({
  className,
  spacing,
  as: Component = "section",
  ...props
}: SectionContainerProps) {
  return <Component className={cn(sectionContainerVariants({ spacing }), className)} {...props} />;
}

export { sectionContainerVariants };
