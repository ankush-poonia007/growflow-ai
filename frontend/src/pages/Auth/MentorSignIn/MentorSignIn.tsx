import { useState, type FormEvent } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router';
import { useAuth } from '@/auth/useAuth';
import { getSafeReturnTo, sanitizeReturnTo, DEFAULT_MENTOR_DESTINATION } from '@/auth/returnTo';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import './MentorSignIn.css';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function MentorSignIn() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const rawReturnTo = searchParams.get('returnTo');
  const safeReturnTo = rawReturnTo ? sanitizeReturnTo(rawReturnTo, '') : '';
  const recoverUrl = safeReturnTo
    ? `/auth/mentor/recover?returnTo=${encodeURIComponent(safeReturnTo)}`
    : '/auth/mentor/recover';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const [emailError, setEmailError] = useState<string | undefined>();
  const [passwordError, setPasswordError] = useState<string | undefined>();
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = (): boolean => {
    let isValid = true;
    setEmailError(undefined);
    setPasswordError(undefined);
    setFormError(null);

    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      setEmailError('Email is required.');
      isValid = false;
    } else if (!EMAIL_REGEX.test(trimmedEmail)) {
      setEmailError('Please enter a valid email address.');
      isValid = false;
    }

    if (!password) {
      setPasswordError('Password is required.');
      isValid = false;
    }

    return isValid;
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (isSubmitting) return;

    if (!validate()) {
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    try {
      const result = await signIn({ email, password });

      if (result.success) {
        // Enforce canonical backend authorization boundaries
        if (result.user?.status === 'SUSPENDED') {
          setFormError('Your account has been suspended. Please contact platform support.');
          return;
        }

        if (result.user?.status === 'INACTIVE') {
          setFormError('Your account is currently inactive. Please check your email or contact support.');
          return;
        }

        if (result.user?.role && result.user.role !== 'MENTOR') {
          setFormError('This account is registered as a Student. Please sign in through the Student workspace.');
          return;
        }

        const destination = getSafeReturnTo(searchParams, DEFAULT_MENTOR_DESTINATION);
        navigate(destination, { replace: true });
      } else {
        setFormError(
          result.error ||
            'Sign-in details could not be verified. Check your email and password and try again.',
        );
      }
    } catch {
      setFormError('Unable to reach GrowFlow right now. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="gf-mentor-signin">
      <div className="gf-mentor-signin__container">
        {/* Left / Primary Sign-In Form Area */}
        <div className="gf-mentor-signin__form-area">
          <span className="gf-mentor-signin__eyebrow">
            <span className="gf-mentor-signin__context-badge-dot" aria-hidden="true" />
            SUPERVISE — MENTOR WORKSPACE
          </span>
          <h1 className="gf-mentor-signin__title">Guide projects with clarity.</h1>
          <p className="gf-mentor-signin__subtitle">
            Sign in to review student progress, provide feedback, and keep projects moving.
          </p>

          {/* Form-level Error Alert */}
          {formError && (
            <div className="gf-mentor-signin__alert" role="alert" aria-live="polite">
              <svg
                className="gf-mentor-signin__alert-icon"
                viewBox="0 0 20 20"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <circle cx="10" cy="10" r="9" />
                <line x1="10" y1="7" x2="10" y2="11" />
                <line x1="10" y1="14" x2="10.01" y2="14" />
              </svg>
              <span>{formError}</span>
            </div>
          )}

          <form className="gf-mentor-signin__form" onSubmit={handleSubmit} noValidate>
            <Input
              id="mentor-email"
              label="Email"
              type="email"
              inputMode="email"
              autoComplete="email"
              required
              placeholder="mentor@university.edu"
              value={email}
              error={emailError}
              disabled={isSubmitting}
              onChange={(e) => {
                setEmail(e.target.value);
                if (emailError) setEmailError(undefined);
              }}
            />

            <div>
              <Input
                id="mentor-password"
                label="Password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                required
                value={password}
                error={passwordError}
                disabled={isSubmitting}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (passwordError) setPasswordError(undefined);
                }}
                rightAddon={
                  <button
                    type="button"
                    className="gf-mentor-signin__pwd-toggle"
                    onClick={() => setShowPassword((v) => !v)}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    disabled={isSubmitting}
                    tabIndex={0}
                  >
                    {showPassword ? (
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        aria-hidden="true"
                      >
                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                        <line x1="1" y1="1" x2="23" y2="23" />
                      </svg>
                    ) : (
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        aria-hidden="true"
                      >
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                        <circle cx="12" cy="12" r="3" />
                      </svg>
                    )}
                  </button>
                }
              />
              <div className="gf-mentor-signin__password-meta">
                <Link to={recoverUrl} className="gf-mentor-signin__forgot-link">
                  Forgot password?
                </Link>
              </div>
            </div>

            <div className="gf-mentor-signin__actions">
              <Button
                as="button"
                type="submit"
                variant="primary"
                size="lg"
                fullWidth
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Signing in...' : 'Sign in'}
              </Button>
            </div>
          </form>

          <div className="gf-mentor-signin__footer">
            Don&apos;t have a Mentor account?
            <Link to="/auth/mentor/register" className="gf-mentor-signin__register-link">
              Create one.
            </Link>
          </div>
        </div>

        {/* Right / Secondary Contextual Information Area */}
        <aside
          className="gf-mentor-signin__context-area"
          aria-label="Mentor Workspace Context"
        >
          <div className="gf-mentor-signin__context-header">
            <div className="gf-mentor-signin__context-badge">
              <span className="gf-mentor-signin__context-badge-dot" aria-hidden="true" />
              SUPERVISE WORKPLACE
            </div>
            <h2 className="gf-mentor-signin__context-heading">
              Structured project oversight.
            </h2>
            <p className="gf-mentor-signin__context-desc">
              Designed specifically for mentors and faculty advisors supervising
              capstone engineering teams and student project milestones.
            </p>

            <ul className="gf-mentor-signin__features">
              <li className="gf-mentor-signin__feature-item">
                <svg
                  className="gf-mentor-signin__feature-icon"
                  viewBox="0 0 20 20"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                <span>Real-time student progress tracking & milestone verification</span>
              </li>
              <li className="gf-mentor-signin__feature-item">
                <svg
                  className="gf-mentor-signin__feature-icon"
                  viewBox="0 0 20 20"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                <span>Project health monitoring & early risk indicator alerts</span>
              </li>
              <li className="gf-mentor-signin__feature-item">
                <svg
                  className="gf-mentor-signin__feature-icon"
                  viewBox="0 0 20 20"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                <span>Direct feedback loops and technical architecture reviews</span>
              </li>
            </ul>
          </div>

          <div className="gf-mentor-signin__context-footer">
            GrowFlow Soft Intelligence Foundation · All sessions protected with cryptographic identity
          </div>
        </aside>
      </div>
    </div>
  );
}
