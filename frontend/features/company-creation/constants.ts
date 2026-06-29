import {
  Crown,
  FileText,
  Palette,
  Search,
  Send,
  TrendingUp,
  Video,
  type LucideIcon,
} from "lucide-react";

export const ANIMATION_STEP_DELAY_MS = 900;
export const SUCCESS_MESSAGE_DELAY_MS = 1200;

export type CreationStepKind = "ceo" | "department";

export interface CreationStep {
  id: string;
  kind: CreationStepKind;
  label: string;
  status: string;
  icon: LucideIcon;
}

export const CREATION_STEPS: readonly CreationStep[] = [
  {
    id: "ceo",
    kind: "ceo",
    label: "AI CEO",
    status: "Analyzing mission...",
    icon: Crown,
  },
  {
    id: "research",
    kind: "department",
    label: "Research Department",
    status: "Assembling team...",
    icon: Search,
  },
  {
    id: "brand",
    kind: "department",
    label: "Brand Department",
    status: "Assembling team...",
    icon: Palette,
  },
  {
    id: "scripts",
    kind: "department",
    label: "Script Department",
    status: "Assembling team...",
    icon: FileText,
  },
  {
    id: "video",
    kind: "department",
    label: "Video Department",
    status: "Assembling team...",
    icon: Video,
  },
  {
    id: "publishing",
    kind: "department",
    label: "Publishing Department",
    status: "Assembling team...",
    icon: Send,
  },
  {
    id: "growth",
    kind: "department",
    label: "Growth Department",
    status: "Assembling team...",
    icon: TrendingUp,
  },
] as const;

export interface DepartmentCardData {
  id: string;
  name: string;
  status: string;
  icon: LucideIcon;
}

export const DEPARTMENT_CARDS: readonly DepartmentCardData[] = [
  { id: "research", name: "Research", status: "Ready", icon: Search },
  { id: "brand", name: "Brand", status: "Ready", icon: Palette },
  { id: "scripts", name: "Scripts", status: "Ready", icon: FileText },
  { id: "video", name: "Video", status: "Ready", icon: Video },
  { id: "publishing", name: "Publishing", status: "Ready", icon: Send },
  { id: "growth", name: "Growth", status: "Ready", icon: TrendingUp },
] as const;

export const WORKFLOW_PREVIEW = {
  title: "Research niche and audience",
  status: "Ready to execute",
} as const;
