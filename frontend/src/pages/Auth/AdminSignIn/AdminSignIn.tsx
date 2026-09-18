import { useState, type FormEvent } from 'react';
import { useNavigate, useSearchParams } from 'react-router';
import { useAuth } from '@/auth/useAuth';
import { getSafeReturnTo, DEFAULT_ADMIN_DESTINATION } from '@/auth/returnTo';
import './AdminSignIn.css';

/**
 * AD-AUTH — Admin Governance Sign In
 *
 * Dedicated authentication entry point for Platform Administrators.
 * Restricted to pre-provisioned ADMIN accounts.
 */
export function AdminSignIn() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({});

  const validate = (): boolean => {
    const errors: { email?: string; password?: string } = {};
    let isValid = true;

    if (!email.trim()) {
      errors.email = 'Admin email address is required';
      isValid = false;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      errors.email = 'Please enter a valid email address';
      isValid = false;
    }

    if (!password) {
      errors.password = 'Password is required';
      isValid = false;
    }

    setFieldErrors(errors);
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
        if (result.user?.status === 'SUSPENDED') {
          setFormError('Your account has been suspended. Please contact platform governance.');
          return;
        }

        if (result.user?.status === 'INACTIVE') {
          setFormError('Your account is currently inactive. Please contact system support.');
          return;
        }

        if (result.user?.role && result.user.role !== 'ADMIN') {
          setFormError(
            `This account is registered as a ${result.user.role}. Administrative privileges are required for this workspace.`,
          );
          return;
        }

        const destination = getSafeReturnTo(searchParams, DEFAULT_ADMIN_DESTINATION);
        navigate(destination, { replace: true });
      } else {
        setFormError(
          result.error ||
            'Sign-in credentials could not be verified. Check your email and password.',
        );
      }
    } catch {
      setFormError('Unable to reach GrowFlow right now. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="gf-admin-signin">
      <div className="gf-admin-signin__container">
        {/* Left / Primary Sign-In Form Area */}
        <div className="gf-admin-signin__form-area">
          <span className="gf-admin-signin__eyebrow">
            <span className="gf-admin-signin__context-badge-dot" aria-hidden="true" />
            GOVERN — ADMIN WORKSPACE
          </span>
          <h1 className="gf-admin-signin__title">Platform Governance.</h1>
          <p className="gf-admin-signin__subtitle">
            Sign in to supervise platform health, manage cohorts, and review platform metrics.
          </p>

          {/* Form-level Error Alert */}
          {formError && (
            <div className="gf-admin-signin__alert" role="alert" aria-live="polite">
              <svg
                className="gf-admin-signin__alert-icon"
                viewBox="0 0 20 20"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <circle cx="10" cy="10" r="9" />
                <line x1="10" y1="8" x2="10" y2="12" />
                <line x1="10" y1="14" x2="10.01" y2="14" />
              </svg>
              <span>{formError}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate className="gf-admin-signin__form">
            {/* Email Field */}
            <div className="gf-admin-signin__field">
              <label htmlFor="admin-email" className="gf-admin-signin__label">
                Administrator Email
              </label>
              <div className="gf-admin-signin__input-wrapper">
                <input
                  id="admin-email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  autoFocus
                  required
                  placeholder="admin@growflow.internal"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (fieldErrors.email) {
                      setFieldErrors((prev) => ({ ...prev, email: undefined }));
                    }
                  }}
                  className={`gf-admin-signin__input ${
                    fieldErrors.email ? 'gf-admin-signin__input--error' : ''
                  }`}
                  aria-invalid={Boolean(fieldErrors.email)}
                  aria-describedby={fieldErrors.email ? 'admin-email-error' : undefined}
                  disabled={isSubmitting}
                />
              </div>
              {fieldErrors.email && (
                <span id="admin-email-error" className="gf-admin-signin__field-error" role="alert">
                  {fieldErrors.email}
                </span>
              )}
            </div>

            {/* Password Field */}
            <div className="gf-admin-signin__field">
              <div className="gf-admin-signin__label-row">
                <label htmlFor="admin-password" className="gf-admin-signin__label">
                  Password
                </label>
              </div>
              <div className="gf-admin-signin__input-wrapper">
                <input
                  id="admin-password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  placeholder="••••••••••••"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (fieldErrors.password) {
                      setFieldErrors((prev) => ({ ...prev, password: undefined }));
                    }
                  }}
                  className={`gf-admin-signin__input ${
                    fieldErrors.password ? 'gf-admin-signin__input--error' : ''
                  }`}
                  aria-invalid={Boolean(fieldErrors.password)}
                  aria-describedby={fieldErrors.password ? 'admin-password-error' : undefined}
                  disabled={isSubmitting}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="gf-admin-signin__password-toggle"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                      <line x1="1" y1="1" x2="23" y2="23" />
                    </svg>
                  ) : (
                    <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  )}
                </button>
              </div>
              {fieldErrors.password && (
                <span id="admin-password-error" className="gf-admin-signin__field-error" role="alert">
                  {fieldErrors.password}
                </span>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="gf-admin-signin__submit-btn"
            >
              {isSubmitting ? (
                <span className="gf-admin-signin__loading-content">
                  <span className="gf-admin-signin__spinner" aria-hidden="true" />
                  Authenticating...
                </span>
              ) : (
                'Sign In to GOVERN'
              )}
            </button>
          </form>

          {/* Access Policy Notice */}
          <div className="gf-admin-signin__policy-notice">
            <svg
              className="gf-admin-signin__policy-icon"
              viewBox="0 0 20 20"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <rect x="3" y="11" width="14" height="8" rx="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
            <p>
              Administrative access is restricted to pre-authorized personnel. All governance
              activities are logged and monitored.
            </p>
          </div>
        </div>

        {/* Right / Platform Governance Branding Panel */}
        <div className="gf-admin-signin__brand-panel">
          <div className="gf-admin-signin__brand-content">
            <div className="gf-admin-signin__badge">Platform Governance</div>
            <h2 className="gf-admin-signin__brand-headline">
              Authoritative Platform Oversight &amp; Health.
            </h2>
            <p className="gf-admin-signin__brand-description">
              Access real-time platform statistics, supervise mentor assignments, monitor student
              milestones, and enforce system security standards.
            </p>

            <div className="gf-admin-signin__features">
              <div className="gf-admin-signin__feature-item">
                <span className="gf-admin-signin__feature-check">✓</span>
                <div>
                  <strong>Canonical Platform Data</strong>
                  <p>True metrics calculated directly from verified database state.</p>
                </div>
              </div>
              <div className="gf-admin-signin__feature-item">
                <span className="gf-admin-signin__feature-check">✓</span>
                <div>
                  <strong>People Governance</strong>
                  <p>Comprehensive directories for mentors, students, and cohort assignments.</p>
                </div>
              </div>
              <div className="gf-admin-signin__feature-item">
                <span className="gf-admin-signin__feature-check">✓</span>
                <div>
                  <strong>Health Monitoring</strong>
                  <p>Early identification of at-risk projects and inactive cohorts.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
