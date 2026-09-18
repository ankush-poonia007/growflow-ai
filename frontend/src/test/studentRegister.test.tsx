import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import type { User, Session, AuthError } from '@supabase/supabase-js';
import { StudentRegister } from '@/pages/Auth/StudentRegister/StudentRegister';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import { supabase } from '@/lib/supabase';

vi.mock('@/lib/supabase', () => ({
  supabase: {
    auth: {
      signUp: vi.fn(),
    },
  },
}));

function renderRegister(
  authOverrides: Partial<AuthContextValue> = {},
  initialEntry = '/auth/student/register',
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
            <Route path="/auth/student/register" element={<StudentRegister />} />
            <Route path="/auth/student/sign-in" element={<div data-testid="sign-in-dest">Sign In Page</div>} />
            <Route
              path="/student/dashboard"
              element={<div data-testid="dashboard-dest">Student Dashboard Destination</div>}
            />
            <Route
              path="/student/projects/456"
              element={<div data-testid="deep-dest">Deep Link Destination</div>}
            />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    ),
    auth: defaultAuth,
  };
}

describe('A02 — Student Registration Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all registration form elements, labels, and contextual sidebar', () => {
    renderRegister();

    expect(screen.getByText('BUILD — STUDENT WORKSPACE')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Start building with GrowFlow.' })).toBeInTheDocument();
    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Password/i, { selector: 'input' })).toBeInTheDocument();
    expect(screen.getByLabelText(/^Confirm Password/i, { selector: 'input' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create Student Account' })).toBeInTheDocument();
    expect(screen.getByText('Already have an account?')).toBeInTheDocument();
    expect(screen.getByText('Sign in')).toBeInTheDocument();

    // Contextual sidebar
    expect(screen.getByText('Turn ambition into structured engineering.')).toBeInTheDocument();
  });

  it('validates empty inputs on submit', async () => {
    renderRegister();

    const submitBtn = screen.getByRole('button', { name: 'Create Student Account' });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText('First name is required.')).toBeInTheDocument();
      expect(screen.getByText('Last name is required.')).toBeInTheDocument();
      expect(screen.getByText('Email is required.')).toBeInTheDocument();
      expect(screen.getByText('Password is required.')).toBeInTheDocument();
      expect(screen.getByText('Confirm password is required.')).toBeInTheDocument();
    });

    expect(supabase.auth.signUp).not.toHaveBeenCalled();
  });

  it('validates malformed email address', async () => {
    renderRegister();

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Grace' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Hopper' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'invalid-email' } });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'SecurePass123!' },
    });
    fireEvent.change(screen.getByLabelText(/^Confirm Password/i, { selector: 'input' }), {
      target: { value: 'SecurePass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create Student Account' }));

    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address.')).toBeInTheDocument();
    });

    expect(supabase.auth.signUp).not.toHaveBeenCalled();
  });

  it('validates password mismatch', async () => {
    renderRegister();

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Grace' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Hopper' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'grace@university.edu' } });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'PasswordOne1!' },
    });
    fireEvent.change(screen.getByLabelText(/^Confirm Password/i, { selector: 'input' }), {
      target: { value: 'PasswordTwo2!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create Student Account' }));

    await waitFor(() => {
      expect(screen.getByText('Passwords do not match.')).toBeInTheDocument();
    });

    expect(supabase.auth.signUp).not.toHaveBeenCalled();
  });

  it('toggles password and confirm-password visibility with accessible buttons', () => {
    renderRegister();

    const pwdInput = screen.getByLabelText(/^Password/i, {
      selector: 'input',
    }) as HTMLInputElement;
    const confirmInput = screen.getByLabelText(/^Confirm Password/i, {
      selector: 'input',
    }) as HTMLInputElement;

    expect(pwdInput.type).toBe('password');
    expect(confirmInput.type).toBe('password');

    // Toggle password
    const showPwdBtn = screen.getByLabelText('Show password');
    fireEvent.click(showPwdBtn);
    expect(pwdInput.type).toBe('text');
    expect(screen.getByLabelText('Hide password')).toBeInTheDocument();

    fireEvent.click(screen.getByLabelText('Hide password'));
    expect(pwdInput.type).toBe('password');

    // Toggle confirm password
    const showConfirmBtn = screen.getByLabelText('Show confirm password');
    fireEvent.click(showConfirmBtn);
    expect(confirmInput.type).toBe('text');
    expect(screen.getByLabelText('Hide confirm password')).toBeInTheDocument();

    fireEvent.click(screen.getByLabelText('Hide confirm password'));
    expect(confirmInput.type).toBe('password');
  });

  it('renders dedicated verification-required screen when email confirmation is required', async () => {
    vi.mocked(supabase.auth.signUp).mockResolvedValue({
      data: {
        user: { id: 'user-123', email: 'grace@university.edu' } as unknown as User,
        session: null,
      },
      error: null,
    });

    renderRegister();

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Grace' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Hopper' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'grace@university.edu' } });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'SecurePass123!' },
    });
    fireEvent.change(screen.getByLabelText(/^Confirm Password/i, { selector: 'input' }), {
      target: { value: 'SecurePass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create Student Account' }));

    await waitFor(() => {
      expect(screen.getByText('Check your email.')).toBeInTheDocument();
      expect(screen.getByText('grace@university.edu')).toBeInTheDocument();
      expect(screen.getByText(/We sent a verification link/i)).toBeInTheDocument();
      expect(screen.getByText('Back to sign in')).toBeInTheDocument();
    });
  });

  it('redirects to default dashboard on immediate session signup', async () => {
    vi.mocked(supabase.auth.signUp).mockResolvedValue({
      data: {
        user: { id: 'user-123', email: 'grace@university.edu' } as unknown as User,
        session: { access_token: 'fake-token', user: { id: 'user-123' } } as unknown as Session,
      },
      error: null,
    });

    renderRegister();

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Grace' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Hopper' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'grace@university.edu' } });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'SecurePass123!' },
    });
    fireEvent.change(screen.getByLabelText(/^Confirm Password/i, { selector: 'input' }), {
      target: { value: 'SecurePass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create Student Account' }));

    await waitFor(() => {
      expect(screen.getByTestId('dashboard-dest')).toBeInTheDocument();
    });
  });

  it('redirects to safe returnTo destination on immediate session signup', async () => {
    vi.mocked(supabase.auth.signUp).mockResolvedValue({
      data: {
        user: { id: 'user-123', email: 'grace@university.edu' } as unknown as User,
        session: { access_token: 'fake-token', user: { id: 'user-123' } } as unknown as Session,
      },
      error: null,
    });

    renderRegister({}, '/auth/student/register?returnTo=%2Fstudent%2Fprojects%2F456');

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Grace' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Hopper' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'grace@university.edu' } });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'SecurePass123!' },
    });
    fireEvent.change(screen.getByLabelText(/^Confirm Password/i, { selector: 'input' }), {
      target: { value: 'SecurePass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create Student Account' }));

    await waitFor(() => {
      expect(screen.getByTestId('deep-dest')).toBeInTheDocument();
    });
  });

  it('safely normalizes duplicate account error', async () => {
    vi.mocked(supabase.auth.signUp).mockResolvedValue({
      data: { user: null, session: null },
      error: { message: 'User already registered', status: 400 } as unknown as AuthError,
    });

    renderRegister();

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Grace' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Hopper' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'existing@university.edu' } });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'SecurePass123!' },
    });
    fireEvent.change(screen.getByLabelText(/^Confirm Password/i, { selector: 'input' }), {
      target: { value: 'SecurePass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create Student Account' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'An account with this email already exists. Please sign in instead.',
      );
    });
  });

  it('handles network failure gracefully', async () => {
    vi.mocked(supabase.auth.signUp).mockRejectedValue(new TypeError('Failed to fetch'));

    renderRegister();

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Grace' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Hopper' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'grace@university.edu' } });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'SecurePass123!' },
    });
    fireEvent.change(screen.getByLabelText(/^Confirm Password/i, { selector: 'input' }), {
      target: { value: 'SecurePass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create Student Account' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Unable to reach GrowFlow right now. Check your connection and try again.',
      );
    });
  });
});
