/**
 * GrowFlow Student Assessment Utility Functions.
 */

import type { AssessmentReadinessTier } from '@/lib/api/types';

export function getReadinessTierBadgeVariant(
  tier: AssessmentReadinessTier | string | undefined,
): 'success' | 'warning' | 'neutral' | 'danger' {
  switch (tier?.toUpperCase()) {
    case 'HIGH':
      return 'success';
    case 'MODERATE':
      return 'warning';
    case 'NEEDS_REFINEMENT':
      return 'danger';
    default:
      return 'neutral';
  }
}

export function formatDimensionLabel(key: string): string {
  return key
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

export function getSeverityBadgeVariant(
  severity: string | undefined,
): 'neutral' | 'warning' | 'danger' {
  switch (severity?.toUpperCase()) {
    case 'HIGH':
      return 'danger';
    case 'MEDIUM':
      return 'warning';
    case 'LOW':
    default:
      return 'neutral';
  }
}
