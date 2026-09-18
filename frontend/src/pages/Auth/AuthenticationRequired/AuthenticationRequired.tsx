import { useSearchParams } from 'react-router';
import { Button } from '@/components/ui/Button';
import { sanitizeReturnTo, DEFAULT_STUDENT_DESTINATION } from '@/auth/returnTo';
import './AuthenticationRequired.css';

/**
 * SYS03 — 401 / Authentication Required System Page.
 *
 * Provides a dedicated routed surface for unauthenticated users attempting
 * to access protected resources or encountering session expiration.
 *
 * Security:
 * - Sanitizes returnTo parameter using sanitizeReturnTo to strictly allow internal paths.
 * - Rejects/ignores absolute external URLs, javascript:, protocol-relative //, and control characters.
 */
export function AuthenticationRequired() {
  const [searchParams] = useSearchParams();
  const rawReturnTo = searchParams.get('returnTo');

  // Verify and sanitize returnTo: if valid internal path, preserve; otherwise null
  const sanitized = rawReturnTo ? sanitizeReturnTo(rawReturnTo, '') : '';
  const safeReturnTo = sanitized && sanitized !== DEFAULT_STUDENT_DESTINATION ? sanitized : (rawReturnTo === DEFAULT_STUDENT_DESTINATION ? DEFAULT_STUDENT_DESTINATION : null);

  const signInUrl = safeReturnTo
    ? `/auth/student/sign-in?returnTo=${encodeURIComponent(safeReturnTo)}`
    : '/auth/student/sign-in';

  return (
    <div className="gf-auth-required" role="main" aria-labelledby="auth-req-title">
      <div className="gf-auth-required__card">
        <span className="gf-auth-required__badge">401 — Authentication Required</span>

        <div className="gf-auth-required__graphic" aria-hidden="true">
          <svg viewBox="0 0 120 120" width="84" height="84" fill="none" stroke="currentColor">
            <circle cx="60" cy="60" r="50" strokeWidth="2" strokeDasharray="6 6" className="gf-auth-required__ring" />
            <rect x="44" y="52" width="32" height="26" rx="4" strokeWidth="2.5" />
            <path d="M50 52V42a10 10 0 0 1 20 0v10" strokeWidth="2.5" strokeLinecap="round" />
            <circle cx="60" cy="65" r="3" fill="currentColor" />
          </svg>
        </div>

        <h1 id="auth-req-title" className="gf-auth-required__title">
          Authentication Required
        </h1>

        <p className="gf-auth-required__description">
          Your session has expired or authentication is required to access this workspace resource. Please sign in to continue your work.
        </p>

        {safeReturnTo && (
          <div className="gf-auth-required__context">
            <span className="gf-auth-required__context-label">Intended Destination:</span>
            <code className="gf-auth-required__context-path">{safeReturnTo}</code>
          </div>
        )}

        <div className="gf-auth-required__actions">
          <Button
            as="link"
            to={signInUrl}
            variant="primary"
            className="gf-auth-required__primary-btn"
          >
            Sign In to Continue
          </Button>

          <Button
            as="link"
            to="/"
            variant="secondary"
            className="gf-auth-required__secondary-btn"
          >
            Return Home
          </Button>
        </div>
      </div>
    </div>
  );
}
