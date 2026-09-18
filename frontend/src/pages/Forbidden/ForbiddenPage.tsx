import { ForbiddenView } from '@/components/auth/ForbiddenView';

/**
 * SYS02 — 403 / Forbidden System Page.
 *
 * Provides a first-class routed surface for HTTP 403 / unauthorized states,
 * allowing direct navigation to /403 while offering role-aware workplace return.
 */
export function ForbiddenPage() {
  return (
    <ForbiddenView
      reason="GENERIC"
      message="You do not have permission to access the requested resource or workspace."
    />
  );
}
