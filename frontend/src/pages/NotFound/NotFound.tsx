import { useNavigate } from 'react-router';
import { useAuth } from '@/auth/useAuth';
import { Button } from '@/components/ui/Button';
import './NotFound.css';

export function NotFound() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  let destination = '/';
  let destinationLabel = 'Go to Homepage';

  if (isAuthenticated && user) {
    if (user.role === 'MENTOR') {
      destination = '/mentor/overview';
      destinationLabel = 'Return to Overview';
    } else if (user.role === 'ADMIN') {
      destination = '/admin/overview';
      destinationLabel = 'Return to Admin Overview';
    } else {
      destination = '/student/dashboard';
      destinationLabel = 'Return to Dashboard';
    }
  }

  return (
    <div className="gf-not-found" role="main" aria-labelledby="not-found-title">
      <div className="gf-not-found__card">
        <div className="gf-not-found__badge">404 — Not Found</div>

        <div className="gf-not-found__graphic" aria-hidden="true">
          <svg viewBox="0 0 120 120" width="84" height="84" fill="none" stroke="currentColor">
            <circle cx="60" cy="60" r="50" strokeWidth="2" strokeDasharray="6 6" className="gf-not-found__ring" />
            <path d="M40 70c5 8 15 12 20 12s15-4 20-12" strokeWidth="2.5" strokeLinecap="round" />
            <circle cx="45" cy="48" r="4" fill="currentColor" />
            <circle cx="75" cy="48" r="4" fill="currentColor" />
          </svg>
        </div>

        <h1 id="not-found-title" className="gf-not-found__title">
          Page Not Found
        </h1>

        <p className="gf-not-found__description">
          The view or resource you requested does not exist or may have been relocated. Check the URL or return to your active workspace.
        </p>

        <div className="gf-not-found__actions">
          <Button
            as="link"
            to={destination}
            variant="primary"
            className="gf-not-found__primary-btn"
          >
            {destinationLabel}
          </Button>

          <Button
            variant="secondary"
            onClick={() => navigate(-1)}
            className="gf-not-found__secondary-btn"
          >
            Go Back
          </Button>
        </div>
      </div>
    </div>
  );
}
