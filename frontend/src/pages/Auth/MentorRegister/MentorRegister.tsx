import { useState, type FormEvent } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router';
import { supabase } from '@/lib/supabase';
import { useAuth } from '@/auth/useAuth';
import { getSafeReturnTo, DEFAULT_MENTOR_DESTINATION } from '@/auth/returnTo';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import './MentorRegister.css';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function MentorRegister() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { refreshAuthorization } = useAuth();

  // Form input states
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Password visibility states
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Field validation errors
  const [firstNameError, setFirstNameError] = useState<string | undefined>();
  const [lastNameError, setLastNameError] = useState<string | undefined>();
  const [emailError, setEmailError] = useState<string | undefined>();
  const [passwordError, setPasswordError] = useState<string | undefined>();
  const [confirmPasswordError, setConfirmPasswordError] = useState<string | undefined>();

  // Global submission & workflow states
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isVerificationRequired, setIsVerificationRequired] = useState(false);
  const [registeredEmail, setRegisteredEmail] = useState('');

  const validate = (): boolean => {
    let isValid = true;
    setFirstNameError(undefined);
    setLastNameError(undefined);
    setEmailError(undefined);
    setPasswordError(undefined);
    setConfirmPasswordError(undefined);
    setFormError(null);

    const trimmedFirst = firstName.trim();
    if (!trimmedFirst) {
      setFirstNameError('First name is required.');
      isValid = false;
    } else if (trimmedFirst.length > 50) {
      setFirstNameError('First name cannot exceed 50 characters.');
      isValid = false;
    }

    const trimmedLast = lastName.trim();
    if (!trimmedLast) {
      setLastNameError('Last name is required.');
      isValid = false;
    } else if (trimmedLast.length > 50) {
      setLastNameError('Last name cannot exceed 50 characters.');
      isValid = false;
    }

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

    if (!confirmPassword) {
      setConfirmPasswordError('Confirm password is required.');
      isValid = false;
    } else if (password && password !== confirmPassword) {
      setConfirmPasswordError('Passwords do not match.');
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

    const trimmedEmail = email.trim().toLowerCase();
    const trimmedFirst = firstName.trim();
    const trimmedLast = lastName.trim();
    const fullName = `${trimmedFirst} ${trimmedLast}`.trim();

    try {
      const { data, error } = await supabase.auth.signUp({
        email: trimmedEmail,
        password,
        options: {
          data: {
            first_name: trimmedFirst,
            last_name: trimmedLast,
            full_name: fullName,
          },
        },
      });

      if (error) {
        // Safe provider error normalization without exposing provider internals
        const msg = error.message ? error.message.toLowerCase() : '';
        const status = error.status;

        if (msg.includes('already registered') || msg.includes('user already exists')) {
          setFormError('An account with this email already exists. Please sign in instead.');
        } else if (status === 429) {
          setFormError('Too many registration attempts. Please wait a few moments and try again.');
        } else if (msg.includes('network') || msg.includes('fetch') || msg.includes('connection')) {
          setFormError('Unable to reach GrowFlow right now. Check your connection and try again.');
        } else if (msg.includes('password') && (msg.includes('least') || msg.includes('short') || msg.includes('weak'))) {
          setFormError(error.message);
        } else {
          setFormError('Unable to create your account right now. Please try again.');
        }
        return;
      }

      // Check registration outcome
      // Case A: Email verification required (no active session returned)
      if (data.user && !data.session) {
        setRegisteredEmail(trimmedEmail);
        setIsVerificationRequired(true);
        return;
      }

      // Case B: Immediate active session returned
      if (data.session) {
        // Refresh canonical backend identity/role
        await refreshAuthorization();

        // Destination resolution
        const destination = getSafeReturnTo(searchParams, DEFAULT_MENTOR_DESTINATION);
        navigate(destination, { replace: true });
        return;
      }

      // Fallback if neither session nor error is clearly provided
      setRegisteredEmail(trimmedEmail);
      setIsVerificationRequired(true);
    } catch (err: unknown) {
      const isNetwork =
        err instanceof TypeError ||
        (err instanceof Error && err.message.toLowerCase().includes('fetch'));

      setFormError(
        isNetwork
          ? 'Unable to reach GrowFlow right now. Check your connection and try again.'
          : 'Unable to create your account right now. Please try again.',
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // Dedicated Verification Required View
  if (isVerificationRequired) {
    return (
      <div className="gf-mentor-register">
        <div className="gf-mentor-register__container">
          <div className="gf-mentor-register__form-area gf-mentor-register__verification-view">
            <span className="gf-mentor-register__eyebrow">
              <span className="gf-mentor-register__context-badge-dot" aria-hidden="true" />
              VERIFICATION REQUIRED
            </span>
            <h1 className="gf-mentor-register__title">Check your email.</h1>
            <p className="gf-mentor-register__subtitle">
              We sent a verification link to{' '}
              <strong className="gf-mentor-register__highlighted-email">{registeredEmail}</strong>.
              Verify your account before continuing to your Mentor workspace.
            </p>

            <div className="gf-mentor-register__verification-info">
              <div className="gf-mentor-register__verification-card">
                <svg
                  className="gf-mentor-register__verification-icon"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                  <polyline points="22,6 12,13 2,6" />
                </svg>
                <div className="gf-mentor-register__verification-text">
                  <span className="gf-mentor-register__verification-heading">Next step</span>
                  <span className="gf-mentor-register__verification-detail">
                    Open the link in your email to confirm your address, then sign in with your credentials.
                  </span>
                </div>
              </div>
            </div>

            <div className="gf-mentor-register__actions">
              <Button as="link" to="/auth/mentor/sign-in" variant="secondary" size="lg" fullWidth>
                Back to sign in
              </Button>
            </div>
          </div>

          <aside className="gf-mentor-register__context-area" aria-label="Mentor Workspace Context">
            <div className="gf-mentor-register__context-header">
              <div className="gf-mentor-register__context-badge">
                <span className="gf-mentor-register__context-badge-dot" aria-hidden="true" />
                SUPERVISE WORKPLACE
              </div>
              <h2 className="gf-mentor-register__context-heading">
                Structured project oversight.
              </h2>
              <p className="gf-mentor-register__context-desc">
                Designed specifically for mentors and faculty advisors supervising
                capstone engineering teams and student project milestones.
              </p>
            </div>
            <div className="gf-mentor-register__context-footer">
              GrowFlow Soft Intelligence Foundation · All sessions protected with cryptographic identity
            </div>
          </aside>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-mentor-register">
      <div className="gf-mentor-register__container">
        {/* Left / Primary Registration Form Area */}
        <div className="gf-mentor-register__form-area">
          <span className="gf-mentor-register__eyebrow">
            <span className="gf-mentor-register__context-badge-dot" aria-hidden="true" />
            SUPERVISE — MENTOR WORKSPACE
          </span>
          <h1 className="gf-mentor-register__title">Start guiding better projects.</h1>
          <p className="gf-mentor-register__subtitle">
            Create your Mentor account to support students and help projects move from plans to meaningful progress.
          </p>

          {/* Form-level Error Alert */}
          {formError && (
            <div className="gf-mentor-register__alert" role="alert" aria-live="polite">
              <svg
                className="gf-mentor-register__alert-icon"
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

          <form className="gf-mentor-register__form" onSubmit={handleSubmit} noValidate>
            {/* Name Fields Row */}
            <div className="gf-mentor-register__names-row">
              <Input
                id="mentor-first-name"
                label="First Name"
                type="text"
                autoComplete="given-name"
                required
                placeholder="Ada"
                value={firstName}
                error={firstNameError}
                disabled={isSubmitting}
                onChange={(e) => {
                  setFirstName(e.target.value);
                  if (firstNameError) setFirstNameError(undefined);
                }}
              />

              <Input
                id="mentor-last-name"
                label="Last Name"
                type="text"
                autoComplete="family-name"
                required
                placeholder="Lovelace"
                value={lastName}
                error={lastNameError}
                disabled={isSubmitting}
                onChange={(e) => {
                  setLastName(e.target.value);
                  if (lastNameError) setLastNameError(undefined);
                }}
              />
            </div>

            {/* Email Field */}
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

            {/* Password Field */}
            <Input
              id="mentor-password"
              label="Password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="new-password"
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
                  className="gf-mentor-register__pwd-toggle"
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

            {/* Confirm Password Field */}
            <Input
              id="mentor-confirm-password"
              label="Confirm Password"
              type={showConfirmPassword ? 'text' : 'password'}
              autoComplete="new-password"
              required
              value={confirmPassword}
              error={confirmPasswordError}
              disabled={isSubmitting}
              onChange={(e) => {
                setConfirmPassword(e.target.value);
                if (confirmPasswordError) setConfirmPasswordError(undefined);
              }}
              rightAddon={
                <button
                  type="button"
                  className="gf-mentor-register__pwd-toggle"
                  onClick={() => setShowConfirmPassword((v) => !v)}
                  aria-label={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
                  disabled={isSubmitting}
                  tabIndex={0}
                >
                  {showConfirmPassword ? (
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

            <div className="gf-mentor-register__actions">
              <Button
                as="button"
                type="submit"
                variant="primary"
                size="lg"
                fullWidth
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Creating account...' : 'Create Mentor Account'}
              </Button>
            </div>
          </form>

          <div className="gf-mentor-register__footer">
            Already have an account?
            <Link to="/auth/mentor/sign-in" className="gf-mentor-register__signin-link">
              Sign in
            </Link>
          </div>
        </div>

        {/* Right / Secondary Contextual Information Area */}
        <aside className="gf-mentor-register__context-area" aria-label="Mentor Workspace Context">
          <div className="gf-mentor-register__context-header">
            <div className="gf-mentor-register__context-badge">
              <span className="gf-mentor-register__context-badge-dot" aria-hidden="true" />
              SUPERVISE WORKPLACE
            </div>
            <h2 className="gf-mentor-register__context-heading">
              Structured project oversight.
            </h2>
            <p className="gf-mentor-register__context-desc">
              Designed specifically for mentors and faculty advisors supervising
              capstone engineering teams and student project milestones.
            </p>

            <ul className="gf-mentor-register__features">
              <li className="gf-mentor-register__feature-item">
                <svg
                  className="gf-mentor-register__feature-icon"
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
              <li className="gf-mentor-register__feature-item">
                <svg
                  className="gf-mentor-register__feature-icon"
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
              <li className="gf-mentor-register__feature-item">
                <svg
                  className="gf-mentor-register__feature-icon"
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

          <div className="gf-mentor-register__context-footer">
            GrowFlow Soft Intelligence Foundation · All sessions protected with cryptographic identity
          </div>
        </aside>
      </div>
    </div>
  );
}
