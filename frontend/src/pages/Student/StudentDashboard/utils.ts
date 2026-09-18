/**
 * S01 Student Dashboard Utility Functions & Canonical Mappings
 *
 * Requirements:
 * - Real canonical lifecycle stages (IDEA -> COMPLETED, 8 stages)
 * - Deterministic Next Action mapped strictly to lifecycle phase
 * - Health indicator semantic mapping
 * - Safe greeting and date formatters
 * - NO fake metrics or artificial predictions
 */

import type { ProjectPhase } from '@/lib/api/types';

export interface LifecycleStageMeta {
  phase: ProjectPhase;
  stage: number;
  label: string;
}

export const CANONICAL_LIFECYCLE_STAGES: readonly LifecycleStageMeta[] = [
  { phase: 'IDEA', stage: 1, label: 'Idea' },
  { phase: 'ASSESSMENT', stage: 2, label: 'Assessment' },
  { phase: 'BLUEPRINT', stage: 3, label: 'Blueprint' },
  { phase: 'PLANNING', stage: 4, label: 'Planning' },
  { phase: 'IMPLEMENTATION', stage: 5, label: 'Implementation' },
  { phase: 'TESTING', stage: 6, label: 'Testing' },
  { phase: 'DEPLOYMENT', stage: 7, label: 'Deployment' },
  { phase: 'COMPLETED', stage: 8, label: 'Completed' },
] as const;

export function getStageNumber(phase: string): number {
  const normalized = phase?.toUpperCase();
  const match = CANONICAL_LIFECYCLE_STAGES.find((s) => s.phase === normalized);
  return match ? match.stage : 1;
}

export interface DeterministicActionMeta {
  action: string;
  description: string;
  guidance: string;
}

/**
 * Derives the deterministic recommended action strictly from canonical lifecycle phase.
 * Does NOT invoke AI or claim unavailable subsystem operations.
 */
export function getDeterministicNextAction(phase: string): DeterministicActionMeta {
  const normalized = phase?.toUpperCase();
  switch (normalized) {
    case 'IDEA':
      return {
        action: 'Refine your project definition and profile.',
        description:
          'Detail the problem statement, target users, and proposed technical solution before advancing to assessment.',
        guidance:
          'Clarify the primary problem and expected technical scope to establish a solid foundation.',
      };
    case 'ASSESSMENT':
      return {
        action: 'Continue through the assessment.',
        description:
          'Review project feasibility criteria and ensure readiness for architecture evaluation.',
        guidance:
          'Assess technical complexity, prerequisites, and resource requirements.',
      };
    case 'BLUEPRINT':
      return {
        action: 'Review the project blueprint.',
        description:
          'Examine the system architectural specification and technical requirements.',
        guidance:
          'Inspect the system architecture diagram and technical specifications before planning work.',
      };
    case 'PLANNING':
      return {
        action: 'Prepare the execution plan.',
        description:
          'Establish milestones, task dependencies, and implementation sequencing.',
        guidance:
          'Structure work into ordered, measurable deliverables to maintain momentum.',
      };
    case 'IMPLEMENTATION':
      return {
        action: 'Continue project implementation.',
        description:
          'Execute build milestones and track progress against core deliverables.',
        guidance:
          'Work through active implementation deliverables systematically.',
      };
    case 'TESTING':
      return {
        action: 'Continue validating the project.',
        description:
          'Verify system behavior, run test suites, and resolve defects.',
        guidance:
          'Execute unit and integration validation to ensure robust functionality.',
      };
    case 'DEPLOYMENT':
      return {
        action: 'Prepare or continue deployment.',
        description:
          'Configure runtime environments, verify deployment configurations, and launch services.',
        guidance:
          'Verify environment configurations and runtime dependencies for production release.',
      };
    case 'COMPLETED':
      return {
        action: 'Review your completed project.',
        description:
          'Conduct final review, verify project objectives, and document findings.',
        guidance:
          'Review outcomes against original project objectives and archive deliverables.',
      };
    default:
      return {
        action: 'Review project workspace.',
        description:
          'Check active project parameters and current lifecycle status.',
        guidance:
          'Ensure project status and health accurately reflect ongoing work.',
      };
  }
}

export interface HealthDisplayMeta {
  label: string;
  variant: 'success' | 'warning' | 'danger' | 'neutral';
  tone: 'success' | 'warning' | 'danger' | 'default';
  description: string;
}

export function getHealthDisplay(health: string): HealthDisplayMeta {
  const normalized = health?.toUpperCase();
  switch (normalized) {
    case 'HEALTHY':
      return {
        label: 'Healthy',
        variant: 'success',
        tone: 'success',
        description: 'Project is progressing with no blocking anomalies reported.',
      };
    case 'WARNING':
      return {
        label: 'Warning',
        variant: 'warning',
        tone: 'warning',
        description: 'Attention needed. Review timeline and constraints to maintain schedule.',
      };
    case 'CRITICAL':
      return {
        label: 'Critical',
        variant: 'danger',
        tone: 'danger',
        description: 'Immediate intervention required. Blocker or severe deadline risk.',
      };
    default:
      return {
        label: health || 'Not Specified',
        variant: 'neutral',
        tone: 'default',
        description: 'Health status has not been recorded.',
      };
  }
}

/**
 * Returns a calm, contextually appropriate greeting based on time of day.
 * Falls back gracefully to email local part or neutral greeting.
 */
export function getStudentGreeting(fullName?: string | null, email?: string | null): string {
  const hour = new Date().getHours();
  let timeSalutation = 'Good morning';
  if (hour >= 12 && hour < 17) {
    timeSalutation = 'Good afternoon';
  } else if (hour >= 17 || hour < 5) {
    timeSalutation = 'Good evening';
  }

  if (fullName && fullName.trim().length > 0) {
    const firstName = fullName.trim().split(/\s+/)[0];
    return `${timeSalutation}, ${firstName}`;
  }

  if (email && email.includes('@')) {
    const localPart = email.split('@')[0];
    return `${timeSalutation}, ${localPart}`;
  }

  return `${timeSalutation}, Student`;
}

/**
 * Formats an ISO date string cleanly without external dependencies.
 */
export function formatDate(isoString: string | null | undefined): string {
  if (!isoString) return 'No deadline set';
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return isoString;
  }
}

/**
 * Formats an ISO date-time string for recent transition logs.
 */
export function formatDateTime(isoString: string | null | undefined): string {
  if (!isoString) return '';
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return isoString;
  }
}
