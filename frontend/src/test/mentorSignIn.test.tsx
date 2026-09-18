import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { MentorSignIn } from '@/pages/Auth/MentorSignIn/MentorSignIn';
import { AuthContext } from '@/auth/AuthContext';
import { AuthRoute } from '@/auth/AuthRoute';
import { DEFAULT_MENTOR_DESTINATION } from '@/auth/returnTo';
import type { AuthContextValue } from '@/auth/types';

function renderMentorSignIn(
  authOverrides: Partial<AuthContextValue> = {},
  initialEntry = '/auth/mentor/sign-in',
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
    signIn: vi.fn().mockResolvedValue({
      success: true,
      user: {
        id: 'mentor-uuid-1',
        email: 'mentor@university.edu',
        role: 'MENTOR',
        status: 'ACTIVE',
      },
    }),
    signOut: vi.fn(),
    retryAuth: vi.fn(),
    refreshAuthorization: vi.fn(),
    ...authOverrides,
  };

  return {
    ...render(
      <AuthContext.Provider value={defaultAuth}>
        <MemoryRouter initialEntries={[initialEntry]}>
          <Routes>
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
              element={<div data-testid="deep-dest">Deep Link Destination</div>}
            />
            <Route
              path="/auth/mentor/recover"
              element={<div data-testid="recover-dest">Mentor Password Recovery</div>}
            />
            <Route
              path="/auth/mentor/register"
              element={<div data-testid="register-dest">Mentor Registration</div>}
            />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    ),
    auth: defaultAuth,
  };
}

describe('A04 — Mentor Sign In Page', () => {
  it('renders all form elements, labels, headings, and contextual sidebar', () => {
    renderMentorSignIn();

    expect(screen.getByText('SUPERVISE — MENTOR WORKSPACE')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Guide projects with clarity.' })).toBeInTheDocument();
    expect(
      screen.getByText('Sign in to review student progress, provide feedback, and keep projects moving.'),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Password/i, { selector: 'input' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign in' })).toBeInTheDocument();
    expect(screen.getByText('Forgot password?')).toBeInTheDocument();
    expect(screen.getByText('Don\'t have a Mentor account?')).toBeInTheDocument();
    expect(screen.getByText('Create one.')).toBeInTheDocument();

    // Contextual sidebar
    expect(screen.getByText('SUPERVISE WORKPLACE')).toBeInTheDocument();
    expect(screen.getByText('Structured project oversight.')).toBeInTheDocument();
    expect(
      screen.getByText('Real-time student progress tracking & milestone verification'),
    ).toBeInTheDocument();
    expect(
      screen.getByText('Project health monitoring & early risk indicator alerts'),
    ).toBeInTheDocument();
    expect(
      screen.getByText('Direct feedback loops and technical architecture reviews'),
    ).toBeInTheDocument();
  });

  it('validates empty inputs on submit', async () => {
    renderMentorSignIn();

    const submitBtn = screen.getByRole('button', { name: 'Sign in' });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText('Email is required.')).toBeInTheDocument();
      expect(screen.getByText('Password is required.')).toBeInTheDocument();
    });
  });

  it('validates malformed email addresses', async () => {
    renderMentorSignIn();

    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.change(emailInput, { target: { value: 'not-an-email' } });

    const submitBtn = screen.getByRole('button', { name: 'Sign in' });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address.')).toBeInTheDocument();
    });
  });

  it('toggles password visibility with accessible button', () => {
    renderMentorSignIn();

    const pwdInput = screen.getByLabelText(/^Password/i, {
      selector: 'input',
    }) as HTMLInputElement;
    expect(pwdInput.type).toBe('password');

    const toggleBtn = screen.getByLabelText('Show password');
    fireEvent.click(toggleBtn);

    expect(pwdInput.type).toBe('text');
    expect(screen.getByLabelText('Hide password')).toBeInTheDocument();

    fireEvent.click(screen.getByLabelText('Hide password'));
    expect(pwdInput.type).toBe('password');
  });

  it('displays authentication error alert on failure without clearing email', async () => {
    const signInMock = vi.fn().mockResolvedValue({
      success: false,
      error: 'Sign-in details could not be verified. Check your email and password and try again.',
    });

    renderMentorSignIn({ signIn: signInMock });

    const emailInput = screen.getByLabelText(/email/i);
    const pwdInput = screen.getByLabelText(/^Password/i, { selector: 'input' });

    fireEvent.change(emailInput, { target: { value: 'mentor@university.edu' } });
    fireEvent.change(pwdInput, { target: { value: 'wrong-password' } });

    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Sign-in details could not be verified. Check your email and password and try again.',
      );
    });

    expect((emailInput as HTMLInputElement).value).toBe('mentor@university.edu');
  });

  it('handles network error gracefully', async () => {
    const signInMock = vi.fn().mockRejectedValue(new Error('Network unreachable'));

    renderMentorSignIn({ signIn: signInMock });

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'mentor@university.edu' },
    });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'ValidPass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Unable to reach GrowFlow right now. Please try again.',
      );
    });
  });

  it('enforces wrong-role boundary if student logs in at mentor sign-in', async () => {
    const signInMock = vi.fn().mockResolvedValue({
      success: true,
      user: {
        id: 'student-uuid-1',
        email: 'student@university.edu',
        role: 'STUDENT',
        status: 'ACTIVE',
      },
    });

    renderMentorSignIn({ signIn: signInMock });

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'student@university.edu' },
    });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'ValidPass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'This account is registered as a Student. Please sign in through the Student workspace.',
      );
    });

    // Did NOT navigate to mentor overview
    expect(screen.queryByTestId('mentor-overview-dest')).not.toBeInTheDocument();
  });

  it('enforces inactive account boundary', async () => {
    const signInMock = vi.fn().mockResolvedValue({
      success: true,
      user: {
        id: 'mentor-uuid-2',
        email: 'inactive@university.edu',
        role: 'MENTOR',
        status: 'INACTIVE',
      },
    });

    renderMentorSignIn({ signIn: signInMock });

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'inactive@university.edu' },
    });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'ValidPass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Your account is currently inactive. Please check your email or contact support.',
      );
    });

    expect(screen.queryByTestId('mentor-overview-dest')).not.toBeInTheDocument();
  });

  it('enforces suspended account boundary', async () => {
    const signInMock = vi.fn().mockResolvedValue({
      success: true,
      user: {
        id: 'mentor-uuid-3',
        email: 'suspended@university.edu',
        role: 'MENTOR',
        status: 'SUSPENDED',
      },
    });

    renderMentorSignIn({ signIn: signInMock });

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'suspended@university.edu' },
    });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'ValidPass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Your account has been suspended. Please contact platform support.',
      );
    });

    expect(screen.queryByTestId('mentor-overview-dest')).not.toBeInTheDocument();
  });

  it('redirects to default /mentor/overview on successful mentor sign in', async () => {
    renderMentorSignIn();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'mentor@university.edu' },
    });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'ValidPass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));

    await waitFor(() => {
      expect(screen.getByTestId('mentor-overview-dest')).toBeInTheDocument();
    });
  });

  it('redirects to safe returnTo destination on successful sign in', async () => {
    renderMentorSignIn(
      {},
      '/auth/mentor/sign-in?returnTo=%2Fmentor%2Fprojects%2F789',
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'mentor@university.edu' },
    });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'ValidPass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));

    await waitFor(() => {
      expect(screen.getByTestId('deep-dest')).toBeInTheDocument();
    });
  });

  it('rejects malicious returnTo destination and falls back to /mentor/overview', async () => {
    renderMentorSignIn(
      {},
      '/auth/mentor/sign-in?returnTo=https%3A%2F%2Fevil.example.com',
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'mentor@university.edu' },
    });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'ValidPass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));

    await waitFor(() => {
      expect(screen.getByTestId('mentor-overview-dest')).toBeInTheDocument();
    });
  });

  it('preserves safe returnTo query param on Forgot Password link', () => {
    renderMentorSignIn(
      {},
      '/auth/mentor/sign-in?returnTo=%2Fmentor%2Fprojects%2F789',
    );

    const forgotLink = screen.getByText('Forgot password?');
    expect(forgotLink).toHaveAttribute(
      'href',
      '/auth/mentor/recover?returnTo=%2Fmentor%2Fprojects%2F789',
    );
  });

  it('AuthRoute redirects already authenticated mentor to /mentor/overview', () => {
    renderMentorSignIn({
      status: 'AUTHENTICATED',
      isAuthenticated: true,
      user: {
        id: 'mentor-1',
        email: 'mentor@growflow.ai',
        role: 'MENTOR',
        status: 'ACTIVE',
      },
    });

    expect(screen.queryByRole('heading', { name: 'Guide projects with clarity.' })).not.toBeInTheDocument();
    expect(screen.getByTestId('mentor-overview-dest')).toBeInTheDocument();
  });
});
