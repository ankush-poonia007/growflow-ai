import { useState, type FormEvent } from 'react';
import { Link, useSearchParams } from 'react-router';
import { supabase } from '@/lib/supabase';
import { sanitizeReturnTo } from '@/auth/returnTo';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import './MentorPasswordRecovery.css';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Reserved callback path for the future mentor password reset callback/update experience.
 * Note: The actual password-update page is NOT part of Phase 6F and remains a future phase.
 */
export const RESERVED_MENTOR_RESET_CALLBACK_PATH = '/auth/mentor/reset';

export function MentorPasswordRecovery() {
  const [searchParams] = useSearchParams();

  // Controlled form inputs
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState<string | undefined>();
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [submittedEmail, setSubmittedEmail] = useState('');

  // Deep link preservation: preserve sanitized returnTo if present
  const rawReturnTo = searchParams.get('returnTo');
  const safeReturnTo = rawReturnTo ? sanitizeReturnTo(rawReturnTo, '') : '';
  const signInUrl = safeReturnTo
    ? `/auth/mentor/sign-in?returnTo=${encodeURIComponent(safeReturnTo)}`
    : '/auth/mentor/sign-in';

  const validate = (): boolean => {
    let isValid = true;
    setEmailError(undefined);
    setFormError(null);

    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      setEmailError('Email is required.');
      isValid = false;
    } else if (!EMAIL_REGEX.test(trimmedEmail)) {
      setEmailError('Please enter a valid email address.');
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

    // Use current origin for recovery redirect to prevent hardcoded URLs
    const redirectTo =
      typeof window !== 'undefined'
        ? `${window.location.origin}${RESERVED_MENTOR_RESET_CALLBACK_PATH}`
        : undefined;

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(trimmedEmail, {
        redirectTo,
      });

      if (error) {
        const msg = error.message ? error.message.toLowerCase() : '';
        const status = error.status;

        // Anti-enumeration: If provider returns user not found or unconfirmed,
        // mask it and treat as generic success so account existence is never leaked
        if (
          msg.includes('user not found') ||
          msg.includes('not registered') ||
          msg.includes('no user')
        ) {
          setSubmittedEmail(trimmedEmail);
          setIsSubmitted(true);
          return;
        }

        // Rate limiting normalization
        if (status === 429 || msg.includes('rate limit') || msg.includes('too many requests')) {
          setFormError('Too many requests. Please wait a moment and try again.');
          return;
        }

        // Network failure normalization
        if (msg.includes('network') || msg.includes('fetch') || msg.includes('connection')) {
          setFormError('Unable to reach GrowFlow right now. Check your connection and try again.');
          return;
        }

        // Generic safe provider error without exposing internals
        setFormError('Unable to process recovery request right now. Please try again.');
        return;
      }

      // Successful dispatch
      setSubmittedEmail(trimmedEmail);
      setIsSubmitted(true);
    } catch (err: unknown) {
      const isNetwork =
        err instanceof TypeError ||
        (err instanceof Error && err.message.toLowerCase().includes('fetch'));

      setFormError(
        isNetwork
          ? 'Unable to reach GrowFlow right now. Check your connection and try again.'
          : 'Unable to process recovery request right now. Please try again.',
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // Dedicated Success State: Anti-enumeration generic confirmation
  if (isSubmitted) {
    return (
      <div className="gf-mentor-recovery">
        <div className="gf-mentor-recovery__container">
          <div className="gf-mentor-recovery__form-area gf-mentor-recovery__success-view">
            <span className="gf-mentor-recovery__eyebrow">
              <span className="gf-mentor-recovery__context-badge-dot" aria-hidden="true" />
              PASSWORD RECOVERY
            </span>
            <h1 className="gf-mentor-recovery__title">Check your email.</h1>
            <p className="gf-mentor-recovery__subtitle">
              If an account exists for that email address, we&apos;ll send instructions to reset your password.
            </p>

            <div className="gf-mentor-recovery__email-chip-wrapper">
              <span className="gf-mentor-recovery__email-chip-label">Requested address</span>
              <strong className="gf-mentor-recovery__highlighted-email">{submittedEmail}</strong>
            </div>

            <div className="gf-mentor-recovery__instruction-card">
              <svg
                className="gf-mentor-recovery__instruction-icon"
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
              <div className="gf-mentor-recovery__instruction-text">
                <span className="gf-mentor-recovery__instruction-heading">Next step</span>
                <span className="gf-mentor-recovery__instruction-detail">
                  Open the link in your email to choose a new password. The link will direct you back to GrowFlow.
                </span>
              </div>
            </div>

            <div className="gf-mentor-recovery__actions">
              <Button as="link" to={signInUrl} variant="secondary" size="lg" fullWidth>
                Back to sign in
              </Button>
            </div>
          </div>

          <aside className="gf-mentor-recovery__context-area" aria-label="Mentor Workspace Context">
            <div className="gf-mentor-recovery__context-header">
              <div className="gf-mentor-recovery__context-badge">
                <span className="gf-mentor-recovery__context-badge-dot" aria-hidden="true" />
                SUPERVISE WORKPLACE
              </div>
              <h2 className="gf-mentor-recovery__context-heading">
                Controlled recovery workflow.
              </h2>
              <p className="gf-mentor-recovery__context-desc">
                Protect student evaluations, group progress logs, and mentoring feedback with cryptographic account recovery.
              </p>

              <ul className="gf-mentor-recovery__features">
                <li className="gf-mentor-recovery__feature-item">
                  <svg
                    className="gf-mentor-recovery__feature-icon"
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
                  <span>Secure email-based identity verification</span>
                </li>
                <li className="gf-mentor-recovery__feature-item">
                  <svg
                    className="gf-mentor-recovery__feature-icon"
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
                  <span>Instant restoration of mentor workspace access</span>
                </li>
                <li className="gf-mentor-recovery__feature-item">
                  <svg
                    className="gf-mentor-recovery__feature-icon"
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
                  <span>Uninterrupted guidance on active student milestones</span>
                </li>
              </ul>
            </div>

            <div className="gf-mentor-recovery__context-footer">
              GrowFlow Soft Intelligence Foundation · All sessions protected with cryptographic identity
            </div>
          </aside>
        </div>
      </div>
    );
  }

  // IDLE / SUBMITTING / ERROR Form State
  return (
    <div className="gf-mentor-recovery">
      <div className="gf-mentor-recovery__container">
        {/* Left / Primary Recovery Form Area */}
        <div className="gf-mentor-recovery__form-area">
          <span className="gf-mentor-recovery__eyebrow">
            <span className="gf-mentor-recovery__context-badge-dot" aria-hidden="true" />
            SUPERVISE — MENTOR WORKSPACE
          </span>
          <h1 className="gf-mentor-recovery__title">Forgot your password?</h1>
          <p className="gf-mentor-recovery__subtitle">
            Enter your email and we&apos;ll help you get back into your Mentor workspace.
          </p>

          {/* Form-level Error Alert */}
          {formError && (
            <div className="gf-mentor-recovery__alert" role="alert" aria-live="polite">
              <svg
                className="gf-mentor-recovery__alert-icon"
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

          <form className="gf-mentor-recovery__form" onSubmit={handleSubmit} noValidate>
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

            <div className="gf-mentor-recovery__actions">
              <Button
                as="button"
                type="submit"
                variant="primary"
                size="lg"
                fullWidth
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Sending instructions...' : 'Send recovery instructions'}
              </Button>
            </div>
          </form>

          <div className="gf-mentor-recovery__footer">
            Remember your password?
            <Link to={signInUrl} className="gf-mentor-recovery__signin-link">
              Sign in
            </Link>
          </div>
        </div>

        {/* Right / Secondary Contextual Information Area */}
        <aside className="gf-mentor-recovery__context-area" aria-label="Mentor Workspace Context">
          <div className="gf-mentor-recovery__context-header">
            <div className="gf-mentor-recovery__context-badge">
              <span className="gf-mentor-recovery__context-badge-dot" aria-hidden="true" />
              SUPERVISE WORKPLACE
            </div>
            <h2 className="gf-mentor-recovery__context-heading">
              Controlled recovery workflow.
            </h2>
            <p className="gf-mentor-recovery__context-desc">
              Protect student evaluations, group progress logs, and mentoring feedback with cryptographic account recovery.
            </p>

            <ul className="gf-mentor-recovery__features">
              <li className="gf-mentor-recovery__feature-item">
                <svg
                  className="gf-mentor-recovery__feature-icon"
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
                <span>Secure email-based identity verification</span>
              </li>
              <li className="gf-mentor-recovery__feature-item">
                <svg
                  className="gf-mentor-recovery__feature-icon"
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
                <span>Instant restoration of mentor workspace access</span>
              </li>
              <li className="gf-mentor-recovery__feature-item">
                <svg
                  className="gf-mentor-recovery__feature-icon"
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
                <span>Uninterrupted guidance on active student milestones</span>
              </li>
            </ul>
          </div>

          <div className="gf-mentor-recovery__context-footer">
            GrowFlow Soft Intelligence Foundation · All sessions protected with cryptographic identity
          </div>
        </aside>
      </div>
    </div>
  );
}
