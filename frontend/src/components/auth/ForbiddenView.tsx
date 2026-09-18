import { Button } from '@/components/ui/Button';
import { useAuth } from '@/auth/useAuth';
import './ForbiddenView.css';

interface ForbiddenViewProps {
  reason?: 'ROLE_MISMATCH' | 'SUSPENDED' | 'INACTIVE' | 'GENERIC';
  message?: string;
}

export function ForbiddenView({
  reason = 'ROLE_MISMATCH',
  message,
}: ForbiddenViewProps) {
  const { user, isAuthenticated, signOut } = useAuth();

  let displayTitle = 'Access Restricted';
  let displayMessage =
    message ||
    "You don't have access to this workspace with your current account.";

  if (reason === 'SUSPENDED') {
    displayTitle = 'Account Suspended';
    displayMessage =
      message ||
      'Your GrowFlow account has been suspended. Please contact platform support for assistance.';
  } else if (reason === 'INACTIVE') {
    displayTitle = 'Account Inactive';
    displayMessage =
      message ||
      'Your account is currently inactive. Please check your email or contact support to activate your account.';
  }

  // Determine authorized workplace destination
  let destination = '/';
  let destinationLabel = 'Return Home';

  if (isAuthenticated && user) {
    if (user.role === 'MENTOR') {
      destination = '/mentor/overview';
      destinationLabel = 'Return to Overview';
    } else if (user.role === 'ADMIN') {
      destination = '/admin/overview';
      destinationLabel = 'Return to Admin Overview';
    } else if (user.role === 'STUDENT') {
      destination = '/student/dashboard';
      destinationLabel = 'Return to Dashboard';
    }
  }

  return (
    <div className="gf-forbidden" role="alert" aria-labelledby="forbidden-title">
      <span className="gf-forbidden__badge">403 — Unauthorized</span>
      <h1 id="forbidden-title" className="gf-forbidden__title">
        {displayTitle}
      </h1>
      <p className="gf-forbidden__message">{displayMessage}</p>
      <div className="gf-forbidden__actions">
        <Button as="link" to={destination} variant="secondary">
          {destinationLabel}
        </Button>
        <Button
          as="button"
          variant="primary"
          onClick={() => {
            void signOut();
          }}
        >
          Sign In as Different User
        </Button>
      </div>
    </div>
  );
}
