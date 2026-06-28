import { breakpoints, type Breakpoint } from "@/lib/theme";

export function minWidth(breakpoint: Breakpoint): string {
  return `(min-width: ${breakpoints[breakpoint]}px)`;
}

export function maxWidth(breakpoint: Breakpoint): string {
  return `(max-width: ${breakpoints[breakpoint] - 1}px)`;
}

export function between(min: Breakpoint, max: Breakpoint): string {
  return `(min-width: ${breakpoints[min]}px) and (max-width: ${breakpoints[max] - 1}px)`;
}

export const responsive = {
  sm: minWidth("sm"),
  md: minWidth("md"),
  lg: minWidth("lg"),
  xl: minWidth("xl"),
  "2xl": minWidth("2xl"),
} as const;
