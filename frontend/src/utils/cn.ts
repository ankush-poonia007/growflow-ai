/* ==========================================================================
   Utility Hooks & Helpers
   ========================================================================== */

/**
 * Merge class names conditionally.
 * cn('base', condition && 'active', undefined, 'always')
 * → 'base active always'
 */
export function cn(
  ...classes: (string | boolean | undefined | null)[]
): string {
  return classes.filter(Boolean).join(' ');
}
