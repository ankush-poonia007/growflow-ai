import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import type { AuthError } from '@supabase/supabase-js';
import { StudentPasswordRecovery } from '@/pages/Auth/StudentPasswordRecovery/StudentPasswordRecovery';
import { StudentSignIn } from '@/pages/Auth/StudentSignIn/StudentSignIn';
import { AuthRoute } from '@/auth/AuthRoute';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import { supabase } from '@/lib/supabase';

vi.mock('@/lib/supabase', () => ({
  supabase: {
    auth: {
      resetPasswordForEmail: vi.fn(),
    },
  },
}));

function renderRecovery(
  authOverrides: Partial<AuthContextValue> = {},
  initialEntry = '/auth/student/recover',
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
              path="/auth/student/recover"
              element={
                <AuthRoute>
                  <StudentPasswordRecovery />
                </AuthRoute>
              }
            />
            <Route path="/auth/student/sign-in" element={<StudentSignIn />} />
            <Route
              path="/student/dashboard"
              element={<div data-testid="dashboard-dest">Student Dashboard Destination</div>}
            />
            <Route
              path="/student/projects/123"
              element={<div data-testid="deep-dest">Deep Link Destination</div>}
            />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    ),
    auth: defaultAuth,
  };
}

describe('A03 — Student Password Recovery Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // 1. Initial page render
  it('1. renders all initial form elements, headings, labels, and contextual sidebar', () => {
    renderRecovery();

    expect(screen.getByText('BUILD — STUDENT WORKSPACE')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Forgot your password?' })).toBeInTheDocument();
    expect(
      screen.getByText(/Enter your email and we'll help you get back into your GrowFlow workspace/i),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Send recovery instructions' })).toBeInTheDocument();
    expect(screen.getByText('Remember your password?')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Sign in' })).toHaveAttribute(
      'href',
      '/auth/student/sign-in',
    );

    // Contextual sidebar
    expect(screen.getByText('Controlled recovery workflow.')).toBeInTheDocument();
    expect(screen.getByText('Secure email-based identity verification')).toBeInTheDocument();
    expect(screen.getByText('Instant restoration of student workspace access')).toBeInTheDocument();
    expect(
      screen.getByText('Uninterrupted progress on active milestone submissions'),
    ).toBeInTheDocument();
  });

  // 2. Email field rendering
  it('2. renders email field with correct type, autocomplete, inputmode, and accessible attributes', () => {
    renderRecovery();

    const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
    expect(emailInput).toBeInTheDocument();
    expect(emailInput.type).toBe('email');
    expect(emailInput.getAttribute('autocomplete')).toBe('email');
    expect(emailInput.getAttribute('inputmode')).toBe('email');
    expect(emailInput).toHaveAttribute('required');
    expect(emailInput.placeholder).toBe('student@university.edu');
  });

  // 3. Required email validation
  it('3. validates required email when submitted empty', async () => {
    renderRecovery();

    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(screen.getByText('Email is required.')).toBeInTheDocument();
    });

    expect(supabase.auth.resetPasswordForEmail).not.toHaveBeenCalled();
  });

  // 4. Invalid email format validation
  it('4. validates malformed email addresses with clear feedback', async () => {
    renderRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'not-an-email' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address.')).toBeInTheDocument();
    });

    expect(supabase.auth.resetPasswordForEmail).not.toHaveBeenCalled();
  });

  // 5. Valid email submission
  it('5. trims surrounding whitespace and normalizes email before submission', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
      data: {},
      error: null,
    });

    renderRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: '  Student@University.EDU  ' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(supabase.auth.resetPasswordForEmail).toHaveBeenCalledWith(
        'student@university.edu',
        expect.objectContaining({
          redirectTo: expect.stringContaining('/auth/student/reset'),
        }),
      );
    });
  });

  // 6. Submission loading state
  it('6. exhibits restrained loading state during submission with disabled controls', async () => {
    let resolvePromise: (val: unknown) => void;
    const pendingPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });

    vi.mocked(supabase.auth.resetPasswordForEmail).mockReturnValue(
      pendingPromise as ReturnType<typeof supabase.auth.resetPasswordForEmail>,
    );

    renderRecovery();

    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.change(emailInput, { target: { value: 'student@university.edu' } });

    const submitBtn = screen.getByRole('button', { name: 'Send recovery instructions' });
    fireEvent.click(submitBtn);

    // Verify loading state
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Sending instructions...' })).toBeDisabled();
      expect(emailInput).toBeDisabled();
    });

    // Cleanup promise
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

    renderRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'student@university.edu' },
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

  // 8. Supabase recovery request success
  it('8. calls supabase.auth.resetPasswordForEmail with safe origin redirect URL', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
      data: {},
      error: null,
    });

    renderRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'student@university.edu' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(supabase.auth.resetPasswordForEmail).toHaveBeenCalledWith(
        'student@university.edu',
        {
          redirectTo: `${window.location.origin}/auth/student/reset`,
        },
      );
    });
  });

  // 9. Generic success state
  it('9. renders calm, generic success confirmation screen upon completion', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
      data: {},
      error: null,
    });

    renderRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'student@university.edu' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(screen.getByText('PASSWORD RECOVERY')).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: 'Check your email.' })).toBeInTheDocument();
      expect(
        screen.getByText(/If an account exists for that email address, we'll send instructions/i),
      ).toBeInTheDocument();
      expect(screen.getByText('student@university.edu')).toBeInTheDocument();
      expect(screen.getByRole('link', { name: 'Back to sign in' })).toBeInTheDocument();
    });
  });

  // 10. Success state does not reveal account existence (Anti-enumeration)
  it('10. does not reveal whether account exists when provider indicates missing user', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
      data: null,
      error: { message: 'User not found', status: 400 } as unknown as AuthError,
    });

    renderRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'nonexistent@university.edu' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      // Must display the exact same generic success message
      expect(screen.getByRole('heading', { name: 'Check your email.' })).toBeInTheDocument();
      expect(
        screen.getByText(/If an account exists for that email address, we'll send instructions/i),
      ).toBeInTheDocument();
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
      expect(screen.queryByText(/user not found/i)).not.toBeInTheDocument();
    });
  });

  // 11. Provider error normalization
  it('11. normalizes rate limit and general provider errors into safe messages', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
      data: null,
      error: { message: 'rate limit exceeded', status: 429 } as unknown as AuthError,
    });

    renderRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'student@university.edu' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Too many requests. Please wait a moment and try again.',
      );
    });
  });

  // 12. Network error handling
  it('12. handles unexpected network failures gracefully', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockRejectedValue(
      new TypeError('Failed to fetch'),
    );

    renderRecovery();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'student@university.edu' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Unable to reach GrowFlow right now. Check your connection and try again.',
      );
    });
  });

  // 13. Email value preserved after error
  it('13. preserves entered email address in input field when error occurs', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
      data: null,
      error: { message: 'Internal Server Error', status: 500 } as unknown as AuthError,
    });

    renderRecovery();

    const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
    fireEvent.change(emailInput, { target: { value: 'student@university.edu' } });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    expect(emailInput.value).toBe('student@university.edu');
  });

  // 14. A01 Forgot password link
  it('14. verifies A01 Forgot password link targets /auth/student/recover', () => {
    renderRecovery({}, '/auth/student/sign-in');

    const forgotLink = screen.getByRole('link', { name: 'Forgot password?' });
    expect(forgotLink).toHaveAttribute('href', '/auth/student/recover');
  });

  // 15. A03 Back to sign in link
  it('15. verifies A03 Back to sign in link targets /auth/student/sign-in', () => {
    renderRecovery();

    const signInLink = screen.getByRole('link', { name: 'Sign in' });
    expect(signInLink).toHaveAttribute('href', '/auth/student/sign-in');
  });

  // 16. Safe returnTo behavior
  it('16. preserves safe returnTo query param when navigating between sign in and recovery', () => {
    renderRecovery({}, '/auth/student/sign-in?returnTo=%2Fstudent%2Fprojects%2F123');

    const forgotLink = screen.getByRole('link', { name: 'Forgot password?' });
    expect(forgotLink).toHaveAttribute(
      'href',
      '/auth/student/recover?returnTo=%2Fstudent%2Fprojects%2F123',
    );
  });

  // 17. Malicious returnTo rejection
  it('17. rejects malicious returnTo open redirects and strips them from recovery link', () => {
    renderRecovery({}, '/auth/student/sign-in?returnTo=https%3A%2F%2Fevil.example');

    const forgotLink = screen.getByRole('link', { name: 'Forgot password?' });
    expect(forgotLink).toHaveAttribute('href', '/auth/student/recover');
  });

  // 18. Authenticated-user AuthRoute behavior
  it('18. redirects authenticated students away from recovery page to dashboard', async () => {
    renderRecovery({
      isAuthenticated: true,
      status: 'AUTHENTICATED',
    });

    await waitFor(() => {
      expect(screen.getByTestId('dashboard-dest')).toBeInTheDocument();
      expect(screen.queryByRole('heading', { name: 'Forgot your password?' })).not.toBeInTheDocument();
    });
  });

  // 19. Keyboard submission
  it('19. allows form submission via Enter keypress in the email field', async () => {
    vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
      data: {},
      error: null,
    });

    renderRecovery();

    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.change(emailInput, { target: { value: 'student@university.edu' } });
    fireEvent.submit(emailInput.closest('form')!);

    await waitFor(() => {
      expect(supabase.auth.resetPasswordForEmail).toHaveBeenCalledWith(
        'student@university.edu',
        expect.anything(),
      );
    });
  });

  // 20. Accessibility attributes
  it('20. has accessible form attributes including aria-invalid and role="alert"', async () => {
    renderRecovery();

    const emailInput = screen.getByLabelText(/email/i);
    expect(emailInput).toHaveAttribute('aria-invalid', 'false');

    // Trigger validation error
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(emailInput).toHaveAttribute('aria-invalid', 'true');
      const alert = screen.getByRole('alert');
      expect(alert).toHaveTextContent('Email is required.');
      expect(emailInput).toHaveAttribute('aria-describedby', expect.stringContaining('error'));
    });
  });
});
