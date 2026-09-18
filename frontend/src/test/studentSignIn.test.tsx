import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { StudentSignIn } from '@/pages/Auth/StudentSignIn/StudentSignIn';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';

function renderSignIn(
  authOverrides: Partial<AuthContextValue> = {},
  initialEntry = '/auth/student/sign-in',
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
    signIn: vi.fn().mockResolvedValue({ success: true }),
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

describe('A01 — Student Sign In Page', () => {
  it('renders all form elements, labels, and contextual sidebar', () => {
    renderSignIn();

    expect(screen.getByText('BUILD — STUDENT WORKSPACE')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Welcome back.' })).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(
      screen.getByLabelText(/^Password/i, { selector: 'input' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
    expect(screen.getByText('Forgot password?')).toBeInTheDocument();
    expect(screen.getByText('Create one.')).toBeInTheDocument();

    // Contextual sidebar
    expect(screen.getByText('Structured engineering execution.')).toBeInTheDocument();
  });

  it('validates empty inputs on submit', async () => {
    renderSignIn();

    const submitBtn = screen.getByRole('button', { name: 'Sign In' });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText('Email is required.')).toBeInTheDocument();
      expect(screen.getByText('Password is required.')).toBeInTheDocument();
    });
  });

  it('validates malformed email addresses', async () => {
    renderSignIn();

    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.change(emailInput, { target: { value: 'not-an-email' } });

    const submitBtn = screen.getByRole('button', { name: 'Sign In' });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address.')).toBeInTheDocument();
    });
  });

  it('toggles password visibility with accessible button', () => {
    renderSignIn();

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

    renderSignIn({ signIn: signInMock });

    const emailInput = screen.getByLabelText(/email/i);
    const pwdInput = screen.getByLabelText(/^Password/i, { selector: 'input' });

    fireEvent.change(emailInput, { target: { value: 'student@university.edu' } });
    fireEvent.change(pwdInput, { target: { value: 'wrong-password' } });

    fireEvent.click(screen.getByRole('button', { name: 'Sign In' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Sign-in details could not be verified. Check your email and password and try again.',
      );
    });

    // Email is preserved on failure
    expect((emailInput as HTMLInputElement).value).toBe('student@university.edu');
  });

  it('redirects to default dashboard on successful sign in', async () => {
    const signInMock = vi.fn().mockResolvedValue({ success: true });
    renderSignIn({ signIn: signInMock });

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'valid@university.edu' },
    });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'ValidPassword123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Sign In' }));

    await waitFor(() => {
      expect(screen.getByTestId('dashboard-dest')).toBeInTheDocument();
    });
  });

  it('redirects to safe returnTo destination on successful sign in', async () => {
    const signInMock = vi.fn().mockResolvedValue({ success: true });
    renderSignIn(
      { signIn: signInMock },
      '/auth/student/sign-in?returnTo=%2Fstudent%2Fprojects%2F123',
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'valid@university.edu' },
    });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'ValidPassword123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Sign In' }));

    await waitFor(() => {
      expect(screen.getByTestId('deep-dest')).toBeInTheDocument();
    });
  });
});
