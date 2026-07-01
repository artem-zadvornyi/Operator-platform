import type { Transition, Variants } from "framer-motion";

import { easings } from "@/lib/theme";

// Seconds for Framer Motion (mirrors styles/tokens/animation.css).
const motionDurations = {
  fast: 0.15,
  normal: 0.2,
  slow: 0.3,
} as const;

export const motionTransitions = {
  fast: {
    duration: motionDurations.fast,
    ease: [0.4, 0, 0.2, 1],
  },
  normal: {
    duration: motionDurations.normal,
    ease: [0.4, 0, 0.2, 1],
  },
  slow: {
    duration: motionDurations.slow,
    ease: [0.4, 0, 0.2, 1],
  },
  spring: {
    type: "spring",
    stiffness: 400,
    damping: 30,
  },
} as const satisfies Record<string, Transition>;

export const motionVariants = {
  fade: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
  },
  scale: {
    initial: { opacity: 0, scale: 0.96 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.96 },
  },
  slideUp: {
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 8 },
  },
} as const satisfies Record<string, Variants>;

export const reducedMotionTransition: Transition = {
  duration: 0,
};

export { easings };
