import {
  Crown,
  FileText,
  GitBranch,
  Palette,
  Search,
  Send,
  TrendingUp,
  Video,
  type LucideIcon,
} from "lucide-react";

import type { CreationEventType } from "@/features/company-creation/types";

export const ANIMATION_STEP_DELAY_MS = 900;
export const SUCCESS_MESSAGE_DELAY_MS = 1200;
export const FINALIZE_DELAY_MS = 500;

export const DEPARTMENT_ICON_MAP: Record<string, LucideIcon> = {
  research: Search,
  brand: Palette,
  scripts: FileText,
  video: Video,
  publishing: Send,
  growth: TrendingUp,
};

export const EVENT_ICON_MAP: Record<CreationEventType, LucideIcon> = {
  CEO_ASSIGNED: Crown,
  RESEARCH_READY: Search,
  BRAND_READY: Palette,
  SCRIPTS_READY: FileText,
  VIDEO_READY: Video,
  PUBLISHING_READY: Send,
  GROWTH_READY: TrendingUp,
  WORKFLOW_CREATED: GitBranch,
  FIRST_TASK_READY: Search,
};

export function getDepartmentIcon(departmentId: string): LucideIcon {
  return DEPARTMENT_ICON_MAP[departmentId] ?? Search;
}

export function getEventIcon(eventType: CreationEventType): LucideIcon {
  return EVENT_ICON_MAP[eventType];
}

export function isCeoEvent(eventType: CreationEventType): boolean {
  return eventType === "CEO_ASSIGNED";
}
