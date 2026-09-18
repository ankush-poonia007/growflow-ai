import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import type { AuthError } from '@supabase/supabase-js';
import { MentorPasswordRecovery, RESERVED_MENTOR_RESET_CALLBACK_PATH } from '@/pages/Auth/MentorPasswordRecovery/MentorPasswordRecovery';
import { MentorSignIn } from '@/pages/Auth/MentorSignIn/MentorSignIn';
import { AuthRoute } from '@/auth/AuthRoute';
import { AuthContext } from '@/auth/AuthContext';
import { DEFAULT_MENTOR_DESTINATION } from '@/auth/returnTo';
import type { AuthContextValue } from '@/auth/types';
import { supabase } from '@/lib/supabase';

vi.mock('@/lib/supabase', () => ({
  supabase: {
    auth: {
      resetPasswordForEmail: vi.fn(),
    },
  },
}));

function renderMentorRecovery(
  authOverrides: Partial<AuthContextValue> = {},
  initialEntry = '/auth/mentor/recover',
) {
  const defaultAuth: AuthContextValue = {
    status: 'UNAUTHENTICATED',
    session: null,
    supabaseUser: null,
    user: null,
    error: null,
    isRoleResolving: false,
    isAuthenticated: false,
    isLoading: false,
    signIn: vi.fn(),
    signOut: vi.fn(),
    retryAuth: vi.fn(),
    refreshAuthorization: vi.fn().mockResolvedValue(undefined),
    ...authOverrides,
  };

  return {
    ...render(
      <AuthContext.Provider value={defaultAuth}>
        <MemoryRouter initialEntries={[initialEntry]}>
          <Routes>
            <Route
              path="/auth/mentor/recover"
              element={
                <AuthRoute defaultDestination={DEFAULT_MENTOR_DESTINATION}>
                  <MentorPasswordRecovery />
                </AuthRoute>
              }
            />
            <Route
              path="/auth/mentor/sign-in"
              element={
                <AuthRoute defaultDestination={DEFAULT_MENTOR_DESTINATION}>
                  <MentorSignIn />
                </AuthRoute>
              }
            />
            <Route
              path="/mentor/overview"
              element={<div data-testid="mentor-overview-dest">Mentor Overview Destination</div>}
            />
            <Route
              path="/mentor/projects/789"
              element={<div data-testid="deep-dest">Mentor Deep Destination</div>}
            />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    ),
    auth: defaultAuth,
  };
}

describe('A06 — Mentor Password Recovery Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // 1. Initial page render
  it('1. renders all initial form elements, headings, labels, and contextual sidebar', () => {
    renderMentorRecovery();

    expect(screen.getByText('SUPERVISE — MENTOR WORKSPACE')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Forgot your password?' })).toBeInTheDocument();
    expect(
      screen.getByText(/Enter your email and we'll help you get back into your Mentor workspace/i),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Send recovery instructions' })).toBeInTheDocument();
    expect(screen.getByText('Remember your password?')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Sign in' })).toHaveAttribute(
      'href',
      '/auth/mentor/sign-in',
    );

    // Contextual sidebar
    expect(screen.getByText('Controlled recovery workflow.')).toBeInTheDocument();
    expect(screen.getByText('Secure email-based identity verification')).toBeInTheDocument();
    expect(screen.getByText('Instant restoration of mentor workspace access')).toBeInTheDocument();
    expect(
      screen.getByText('Uninterrupted guidance on active student milestones'),
    ).toBeInTheDocument();
  });

  // 2. Email field attributes
  it('2. renders email field with correct type, autocomplete, inputmode, and accessible attributes', () => {
    renderMentorRecovery();

    const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
    expect(emailInput).toBeInTheDocument();
    expect(emailInput.type).toBe('email');
    expect(emailInput.getAttribute('autocomplete')).toBe('email');
    expect(emailInput.getAttribute('inputmode')).toBe('email');
    expect(emailInput).toHaveAttribute('required');
    expect(emailInput.placeholder).toBe('mentor@university.edu');
  });

  // 3. Required email validation
  it('3. validates required email when submitted empty', async () => {
    renderMentorRecovery();

    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(screen.getByText('Email is required.')).toBeInTheDocument();
    });

    expect(supabase.auth.resetPasswordForEmail).not.toHaveBeenCalled();
  });

  // 4. Invalid email format validation
  it('4. validates malformed email addresses with clear feedback', async () => {
    renderMentorRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'invalid-email-string' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address.')).toBeInTheDocument();
    });

    expect(supabase.auth.resetPasswordForEmail).not.toHaveBeenCalled();
  });

  // 5. Valid email submission with trimming & normalization
  it('5. trims surrounding whitespace and normalizes email before submission', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
      data: {},
      error: null,
    });

    renderMentorRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: '  Mentor@University.EDU  ' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(supabase.auth.resetPasswordForEmail).toHaveBeenCalledWith(
        'mentor@university.edu',
        expect.objectContaining({
          redirectTo: expect.stringContaining(RESERVED_MENTOR_RESET_CALLBACK_PATH),
        }),
      );
    });
  });

  // 6. Restrained loading state during submission
  it('6. exhibits restrained loading state during submission with disabled controls', async () => {
    let resolvePromise: (val: unknown) => void;
    const pendingPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });

    vi.mocked(supabase.auth.resetPasswordForEmail).mockReturnValue(
      pendingPromise as ReturnType<typeof supabase.auth.resetPasswordForEmail>,
    );

    renderMentorRecovery();

    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.change(emailInput, { target: { value: 'mentor@university.edu' } });

    const submitBtn = screen.getByRole('button', { name: 'Send recovery instructions' });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Sending instructions...' })).toBeDisabled();
      expect(emailInput).toBeDisabled();
    });

    await act(async () => {
      resolvePromise!({ data: {}, error: null });
    });
  });

  // 7. Duplicate submit prevention
  it('7. prevents duplicate submissions while request is already pending', async () => {
    let resolvePromise: (val: unknown) => void;
    const pendingPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });

    vi.mocked(supabase.auth.resetPasswordForEmail).mockReturnValue(
      pendingPromise as ReturnType<typeof supabase.auth.resetPasswordForEmail>,
    );

    renderMentorRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'mentor@university.edu' },
    });

    const submitBtn = screen.getByRole('button', { name: 'Send recovery instructions' });
    fireEvent.click(submitBtn);
    fireEvent.click(submitBtn);
    fireEvent.click(submitBtn);

    expect(supabase.auth.resetPasswordForEmail).toHaveBeenCalledTimes(1);

    await act(async () => {
      resolvePromise!({ data: {}, error: null });
    });
  });

  // 8. Reserved callback contract verification
  it('8. passes reserved mentor callback path /auth/mentor/reset to supabase redirect', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
      data: {},
      error: null,
    });

    renderMentorRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'mentor@university.edu' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(supabase.auth.resetPasswordForEmail).toHaveBeenCalledWith(
        'mentor@university.edu',
        {
          redirectTo: `${window.location.origin}/auth/mentor/reset`,
        },
      );
    });
  });

  // 9. Generic success state confirmation
  it('9. renders calm, generic success confirmation screen upon completion', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
      data: {},
      error: null,
    });

    renderMentorRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'mentor@university.edu' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(screen.getByText('PASSWORD RECOVERY')).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: 'Check your email.' })).toBeInTheDocument();
      expect(
        screen.getByText(/If an account exists for that email address, we'll send instructions/i),
      ).toBeInTheDocument();
      expect(screen.getByText('mentor@university.edu')).toBeInTheDocument();
      expect(screen.getByRole('link', { name: 'Back to sign in' })).toBeInTheDocument();
    });
  });

  // 10. Anti-enumeration: user not found
  it('10. does not reveal whether account exists when provider indicates missing user', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
      data: null,
      error: { message: 'User not found', status: 400 } as unknown as AuthError,
    });

    renderMentorRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'nonexistent-mentor@university.edu' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Check your email.' })).toBeInTheDocument();
      expect(
        screen.getByText(/If an account exists for that email address, we'll send instructions/i),
      ).toBeInTheDocument();
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
      expect(screen.queryByText(/user not found/i)).not.toBeInTheDocument();
    });
  });

  // 11. Anti-enumeration: unconfirmed / not registered
  it('11. does not reveal account existence when provider indicates unconfirmed or not registered', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
      data: null,
      error: { message: 'Email address not registered', status: 400 } as unknown as AuthError,
    });

    renderMentorRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'unregistered@university.edu' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Check your email.' })).toBeInTheDocument();
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
      expect(screen.queryByText(/not registered/i)).not.toBeInTheDocument();
    });
  });

  // 12. Rate limit normalization
  it('12. normalizes rate limit provider errors into safe, user-friendly message', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
      data: null,
      error: { message: 'rate limit exceeded', status: 429 } as unknown as AuthError,
    });

    renderMentorRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'mentor@university.edu' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Too many requests. Please wait a moment and try again.',
      );
    });
  });

  // 13. Network error handling
  it('13. handles unexpected network failures gracefully', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockRejectedValue(
      new TypeError('Failed to fetch'),
    );

    renderMentorRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'mentor@university.edu' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Unable to reach GrowFlow right now. Check your connection and try again.',
      );
    });
  });

  // 14. Email value preserved after error
  it('14. preserves entered email address in input field when error occurs', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
      data: null,
      error: { message: 'Internal Server Error', status: 500 } as unknown as AuthError,
    });

    renderMentorRecovery();

    const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
    fireEvent.change(emailInput, { target: { value: 'mentor@university.edu' } });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    expect(emailInput.value).toBe('mentor@university.edu');
  });

  // 15. Link back to Mentor Sign In
  it('15. verifies Sign in link targets /auth/mentor/sign-in', () => {
    renderMentorRecovery();

    const signInLink = screen.getByRole('link', { name: 'Sign in' });
    expect(signInLink).toHaveAttribute('href', '/auth/mentor/sign-in');
  });

  // 16. Link from Mentor Sign In to Recovery preserves returnTo
  it('16. verifies Mentor Sign In forgot password link targets /auth/mentor/recover and preserves safe returnTo', () => {
    renderMentorRecovery({}, '/auth/mentor/sign-in?returnTo=%2Fmentor%2Fprojects%2F789');

    const forgotLink = screen.getByRole('link', { name: 'Forgot password?' });
    expect(forgotLink).toHaveAttribute(
      'href',
      '/auth/mentor/recover?returnTo=%2Fmentor%2Fprojects%2F789',
    );
  });

  // 17. Safe returnTo preserved on recovery page navigation
  it('17. preserves safe returnTo param in Sign in link and Success state link', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
      data: {},
      error: null,
    });

    renderMentorRecovery({}, '/auth/mentor/recover?returnTo=%2Fmentor%2Fprojects%2F789');

    // On form page
    const signInLink = screen.getByRole('link', { name: 'Sign in' });
    expect(signInLink).toHaveAttribute(
      'href',
      '/auth/mentor/sign-in?returnTo=%2Fmentor%2Fprojects%2F789',
    );

    // Submit and check success view link
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'mentor@university.edu' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      const backToSignIn = screen.getByRole('link', { name: 'Back to sign in' });
      expect(backToSignIn).toHaveAttribute(
        'href',
        '/auth/mentor/sign-in?returnTo=%2Fmentor%2Fprojects%2F789',
      );
    });
  });

  // 18. Malicious returnTo rejected
  it('18. strips malicious returnTo query params from links', () => {
    renderMentorRecovery({}, '/auth/mentor/recover?returnTo=https%3A%2F%2Fmalicious.evil');

    const signInLink = screen.getByRole('link', { name: 'Sign in' });
    expect(signInLink).toHaveAttribute('href', '/auth/mentor/sign-in');
  });

  // 19. Authenticated-user AuthRoute redirection
  it('19. redirects authenticated mentors away from recovery page to /mentor/overview', async () => {
    renderMentorRecovery({
      isAuthenticated: true,
      status: 'AUTHENTICATED',
      user: {
        id: 'mentor-1',
        email: 'mentor@university.edu',
        role: 'MENTOR',
        status: 'ACTIVE',
      },
    });

    await waitFor(() => {
      expect(screen.getByTestId('mentor-overview-dest')).toBeInTheDocument();
      expect(screen.queryByRole('heading', { name: 'Forgot your password?' })).not.toBeInTheDocument();
    });
  });

  // 20. Accessible attributes
  it('20. exhibits accessible attributes including role="alert" and aria-invalid', async () => {
    renderMentorRecovery();

    const emailInput = screen.getByLabelText(/email/i);
    expect(emailInput).toHaveAttribute('aria-invalid', 'false');

    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(emailInput).toHaveAttribute('aria-invalid', 'true');
      const alert = screen.getByRole('alert');
      expect(alert).toHaveTextContent('Email is required.');
      expect(emailInput).toHaveAttribute('aria-describedby', expect.stringContaining('error'));
    });
  });
});
