import { useAuth } from '@/auth/useAuth';
import { Button } from '@/components/ui/Button';
import type { AccountStatus as AccountStatusType } from '@/auth/types';
import './AccountStatus.css';

interface AccountStatusProps {
  status?: AccountStatusType;
}

/**
 * SYS04 — Suspended / Inactive Account System Page.
 *
 * Dedicated surface representing account lifecycle state boundaries.
 * Distinctly separates account lifecycle conditions (SUSPENDED vs INACTIVE)
 * from generic 403 authorization failures.
 *
 * Features:
 * - Clear distinction between SUSPENDED and INACTIVE
 * - Navigation to /contact for support recovery inquiry
 * - Explicit disclosure that contacting support does not automatically alter account status
 */
export function AccountStatus({ status: propStatus }: AccountStatusProps) {
  const { user, signOut } = useAuth();
  const effectiveStatus: AccountStatusType =
    propStatus || (user?.status as AccountStatusType) || 'INACTIVE';

  const isSuspended = effectiveStatus === 'SUSPENDED';

  const title = isSuspended ? 'Account Suspended' : 'Account Inactive';
  const badgeLabel = isSuspended
    ? 'Account Lifecycle Notice — Suspended'
    : 'Account Lifecycle Notice — Inactive';

  const message = isSuspended
    ? 'Your GrowFlow account has been suspended by platform administration. You cannot access workspaces while suspended.'
    : 'Your GrowFlow account is currently inactive. You must activate your account before accessing workspaces.';

  const resolutionHelp = isSuspended
    ? 'If you believe this suspension is in error or require further clarification, you may submit an inquiry to platform support. Please note that contacting support allows review of your account standing, but does not guarantee automatic reactivation.'
    : 'Please check your registered email address for an activation link. If you need assistance with account activation, you may contact support. Submitting an inquiry does not automatically modify your account status.';

  return (
    <div className="gf-account-status" role="main" aria-labelledby="account-status-title">
      <div className="gf-account-status__card">
        <span
          className={`gf-account-status__badge ${
            isSuspended
              ? 'gf-account-status__badge--suspended'
              : 'gf-account-status__badge--inactive'
          }`}
        >
          {badgeLabel}
        </span>

        <div
          className={`gf-account-status__graphic ${
            isSuspended
              ? 'gf-account-status__graphic--suspended'
              : 'gf-account-status__graphic--inactive'
          }`}
          aria-hidden="true"
        >
          <svg viewBox="0 0 120 120" width="84" height="84" fill="none" stroke="currentColor">
            <circle cx="60" cy="60" r="50" strokeWidth="2" strokeDasharray="6 6" className="gf-account-status__ring" />
            <path d="M60 38v28" strokeWidth="3" strokeLinecap="round" />
            <circle cx="60" cy="78" r="3.5" fill="currentColor" />
          </svg>
        </div>

        <h1 id="account-status-title" className="gf-account-status__title">
          {title}
        </h1>

        <p className="gf-account-status__message">{message}</p>
        <p className="gf-account-status__help">{resolutionHelp}</p>

        <div className="gf-account-status__actions">
          <Button as="link" to="/contact" variant="primary">
            Contact Platform Support
          </Button>

          <Button
            as="button"
            variant="secondary"
            onClick={() => {
              void signOut();
            }}
          >
            Sign In as Different User
          </Button>

          <Button as="link" to="/" variant="tertiary">
            Return Home
          </Button>
        </div>
      </div>
    </div>
  );
}
