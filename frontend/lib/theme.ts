export const breakpoints = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  "2xl": 1536,
} as const;

export type Breakpoint = keyof typeof breakpoints;

export const containers = {
  sm: "var(--width-container-sm)",
  md: "var(--width-container-md)",
  lg: "var(--width-container-lg)",
  xl: "var(--width-container-xl)",
  "2xl": "var(--width-container-2xl)",
} as const;

export type ContainerSize = keyof typeof containers;

export const zIndex = {
  base: "var(--z-base)",
  raised: "var(--z-raised)",
  dropdown: "var(--z-dropdown)",
  sticky: "var(--z-sticky)",
  overlay: "var(--z-overlay)",
  modal: "var(--z-modal)",
  popover: "var(--z-popover)",
  tooltip: "var(--z-tooltip)",
  toast: "var(--z-toast)",
} as const;

export const durations = {
  instant: "var(--duration-instant)",
  fast: "var(--duration-fast)",
  normal: "var(--duration-normal)",
  slow: "var(--duration-slow)",
  slower: "var(--duration-slower)",
} as const;

export const easings = {
  default: "var(--ease-default)",
  in: "var(--ease-in)",
  out: "var(--ease-out)",
  inOut: "var(--ease-in-out)",
  spring: "var(--ease-spring)",
} as const;
