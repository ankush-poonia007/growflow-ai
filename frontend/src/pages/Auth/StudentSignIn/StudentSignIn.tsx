import { useState, type FormEvent } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router';
import { useAuth } from '@/auth/useAuth';
import { getSafeReturnTo, sanitizeReturnTo, DEFAULT_STUDENT_DESTINATION } from '@/auth/returnTo';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import './StudentSignIn.css';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function StudentSignIn() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const rawReturnTo = searchParams.get('returnTo');
  const safeReturnTo = rawReturnTo ? sanitizeReturnTo(rawReturnTo, '') : '';
  const recoverUrl = safeReturnTo
    ? `/auth/student/recover?returnTo=${encodeURIComponent(safeReturnTo)}`
    : '/auth/student/recover';

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
        const destination = getSafeReturnTo(searchParams, DEFAULT_STUDENT_DESTINATION);
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
    <div className="gf-signin">
      <div className="gf-signin__container">
        {/* Left / Primary Sign-In Form Area */}
        <div className="gf-signin__form-area">
          <span className="gf-signin__eyebrow">
            <span className="gf-signin__context-badge-dot" aria-hidden="true" />
            BUILD — STUDENT WORKSPACE
          </span>
          <h1 className="gf-signin__title">Welcome back.</h1>
          <p className="gf-signin__subtitle">Sign in to continue building with GrowFlow.</p>

          {/* Form-level Error Alert */}
          {formError && (
            <div className="gf-signin__alert" role="alert" aria-live="polite">
              <svg
                className="gf-signin__alert-icon"
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

          <form className="gf-signin__form" onSubmit={handleSubmit} noValidate>
            <Input
              id="student-email"
              label="Email"
              type="email"
              inputMode="email"
              autoComplete="email"
              required
              placeholder="student@university.edu"
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
                id="student-password"
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
                    className="gf-signin__pwd-toggle"
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
              <div className="gf-signin__password-meta">
                <Link to={recoverUrl} className="gf-signin__forgot-link">
                  Forgot password?
                </Link>
              </div>
            </div>

            <div className="gf-signin__actions">
              <Button
                as="button"
                type="submit"
                variant="primary"
                size="lg"
                fullWidth
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Signing in...' : 'Sign In'}
              </Button>
            </div>
          </form>

          <div className="gf-signin__footer">
            Don&apos;t have a Student account?
            <Link to="/auth/student/register" className="gf-signin__register-link">
              Create one.
            </Link>
          </div>
        </div>

        {/* Right / Secondary Contextual Information Area */}
        <aside
          className="gf-signin__context-area"
          aria-label="Student Workspace Context"
        >
          <div className="gf-signin__context-header">
            <div className="gf-signin__context-badge">
              <span className="gf-signin__context-badge-dot" aria-hidden="true" />
              BUILD WORKPLACE
            </div>
            <h2 className="gf-signin__context-heading">
              Structured engineering execution.
            </h2>
            <p className="gf-signin__context-desc">
              Designed specifically for university engineering students transforming
              ambitious ideas into milestone-driven capstone projects.
            </p>

            <ul className="gf-signin__features">
              <li className="gf-signin__feature-item">
                <svg
                  className="gf-signin__feature-icon"
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
                <span>Automated architectural breakdown & milestone roadmaps</span>
              </li>
              <li className="gf-signin__feature-item">
                <svg
                  className="gf-signin__feature-icon"
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
                <span>Verified technical progress tracking and submission</span>
              </li>
              <li className="gf-signin__feature-item">
                <svg
                  className="gf-signin__feature-icon"
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
                <span>Structured mentor feedback and sprint alignment</span>
              </li>
            </ul>
          </div>

          <div className="gf-signin__context-footer">
            GrowFlow Soft Intelligence Foundation · All sessions protected with cryptographic identity
          </div>
        </aside>
      </div>
    </div>
  );
}
