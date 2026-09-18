import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import type { User, Session, AuthError } from '@supabase/supabase-js';
import { MentorRegister } from '@/pages/Auth/MentorRegister/MentorRegister';
import { AuthRoute } from '@/auth/AuthRoute';
import { AuthContext } from '@/auth/AuthContext';
import { DEFAULT_MENTOR_DESTINATION } from '@/auth/returnTo';
import type { AuthContextValue } from '@/auth/types';
import { supabase } from '@/lib/supabase';

vi.mock('@/lib/supabase', () => ({
  supabase: {
    auth: {
      signUp: vi.fn(),
    },
  },
}));

function renderMentorRegister(
  authOverrides: Partial<AuthContextValue> = {},
  initialEntry = '/auth/mentor/register',
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
              path="/auth/mentor/register"
              element={
                <AuthRoute defaultDestination={DEFAULT_MENTOR_DESTINATION}>
                  <MentorRegister />
                </AuthRoute>
              }
            />
            <Route path="/auth/mentor/sign-in" element={<div data-testid="sign-in-dest">Sign In Page</div>} />
            <Route
              path="/mentor/overview"
              element={<div data-testid="mentor-overview-dest">Mentor Overview Destination</div>}
            />
            <Route
              path="/mentor/projects/999"
              element={<div data-testid="deep-dest">Deep Link Destination</div>}
            />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    ),
    auth: defaultAuth,
  };
}

describe('A05 — Mentor Registration Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all registration form elements, labels, headings, and contextual sidebar', () => {
    renderMentorRegister();

    expect(screen.getByText('SUPERVISE — MENTOR WORKSPACE')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Start guiding better projects.' })).toBeInTheDocument();
    expect(
      screen.getByText(
        'Create your Mentor account to support students and help projects move from plans to meaningful progress.',
      ),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Password/i, { selector: 'input' })).toBeInTheDocument();
    expect(screen.getByLabelText(/^Confirm Password/i, { selector: 'input' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create Mentor Account' })).toBeInTheDocument();
    expect(screen.getByText('Already have an account?')).toBeInTheDocument();
    expect(screen.getByText('Sign in')).toBeInTheDocument();

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
    renderMentorRegister();

    const submitBtn = screen.getByRole('button', { name: 'Create Mentor Account' });
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
    renderMentorRegister();

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Katherine' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Johnson' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'invalid-email' } });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'MentorPass123!' },
    });
    fireEvent.change(screen.getByLabelText(/^Confirm Password/i, { selector: 'input' }), {
      target: { value: 'MentorPass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create Mentor Account' }));

    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address.')).toBeInTheDocument();
    });

    expect(supabase.auth.signUp).not.toHaveBeenCalled();
  });

  it('validates password mismatch', async () => {
    renderMentorRegister();

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Katherine' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Johnson' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'katherine@university.edu' } });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'PasswordOne1!' },
    });
    fireEvent.change(screen.getByLabelText(/^Confirm Password/i, { selector: 'input' }), {
      target: { value: 'PasswordTwo2!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create Mentor Account' }));

    await waitFor(() => {
      expect(screen.getByText('Passwords do not match.')).toBeInTheDocument();
    });

    expect(supabase.auth.signUp).not.toHaveBeenCalled();
  });

  it('toggles password and confirm-password visibility with accessible buttons', () => {
    renderMentorRegister();

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
        user: { id: 'mentor-123', email: 'katherine@university.edu' } as unknown as User,
        session: null,
      },
      error: null,
    });

    renderMentorRegister();

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Katherine' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Johnson' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'katherine@university.edu' } });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'MentorPass123!' },
    });
    fireEvent.change(screen.getByLabelText(/^Confirm Password/i, { selector: 'input' }), {
      target: { value: 'MentorPass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create Mentor Account' }));

    await waitFor(() => {
      expect(screen.getByText('Check your email.')).toBeInTheDocument();
      expect(screen.getByText('katherine@university.edu')).toBeInTheDocument();
      expect(
        screen.getByText(/We sent a verification link to/i),
      ).toBeInTheDocument();
      expect(screen.getByText('Back to sign in')).toBeInTheDocument();
    });

    expect(supabase.auth.signUp).toHaveBeenCalledWith({
      email: 'katherine@university.edu',
      password: 'MentorPass123!',
      options: {
        data: {
          first_name: 'Katherine',
          last_name: 'Johnson',
          full_name: 'Katherine Johnson',
        },
      },
    });
  });

  it('redirects to /mentor/overview on immediate session signup', async () => {
    vi.mocked(supabase.auth.signUp).mockResolvedValue({
      data: {
        user: { id: 'mentor-123', email: 'katherine@university.edu' } as unknown as User,
        session: { access_token: 'fake-jwt', user: { id: 'mentor-123' } } as unknown as Session,
      },
      error: null,
    });

    renderMentorRegister();

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Katherine' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Johnson' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'katherine@university.edu' } });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'MentorPass123!' },
    });
    fireEvent.change(screen.getByLabelText(/^Confirm Password/i, { selector: 'input' }), {
      target: { value: 'MentorPass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create Mentor Account' }));

    await waitFor(() => {
      expect(screen.getByTestId('mentor-overview-dest')).toBeInTheDocument();
    });
  });

  it('redirects to safe returnTo destination on immediate session signup', async () => {
    vi.mocked(supabase.auth.signUp).mockResolvedValue({
      data: {
        user: { id: 'mentor-123', email: 'katherine@university.edu' } as unknown as User,
        session: { access_token: 'fake-jwt', user: { id: 'mentor-123' } } as unknown as Session,
      },
      error: null,
    });

    renderMentorRegister({}, '/auth/mentor/register?returnTo=%2Fmentor%2Fprojects%2F999');

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Katherine' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Johnson' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'katherine@university.edu' } });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'MentorPass123!' },
    });
    fireEvent.change(screen.getByLabelText(/^Confirm Password/i, { selector: 'input' }), {
      target: { value: 'MentorPass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create Mentor Account' }));

    await waitFor(() => {
      expect(screen.getByTestId('deep-dest')).toBeInTheDocument();
    });
  });

  it('safely normalizes duplicate account error', async () => {
    vi.mocked(supabase.auth.signUp).mockResolvedValue({
      data: { user: null, session: null },
      error: { message: 'User already registered', status: 400 } as unknown as AuthError,
    });

    renderMentorRegister();

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Katherine' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Johnson' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'existing@university.edu' } });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'MentorPass123!' },
    });
    fireEvent.change(screen.getByLabelText(/^Confirm Password/i, { selector: 'input' }), {
      target: { value: 'MentorPass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create Mentor Account' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'An account with this email already exists. Please sign in instead.',
      );
    });
  });

  it('handles network failure gracefully', async () => {
    vi.mocked(supabase.auth.signUp).mockRejectedValue(new TypeError('Failed to fetch'));

    renderMentorRegister();

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Katherine' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Johnson' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'katherine@university.edu' } });
    fireEvent.change(screen.getByLabelText(/^Password/i, { selector: 'input' }), {
      target: { value: 'MentorPass123!' },
    });
    fireEvent.change(screen.getByLabelText(/^Confirm Password/i, { selector: 'input' }), {
      target: { value: 'MentorPass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create Mentor Account' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Unable to reach GrowFlow right now. Check your connection and try again.',
      );
    });
  });

  it('AuthRoute redirects already-authenticated mentor to /mentor/overview', () => {
    renderMentorRegister({
      status: 'AUTHENTICATED',
      isAuthenticated: true,
      user: {
        id: 'mentor-1',
        email: 'mentor@university.edu',
        role: 'MENTOR',
        status: 'ACTIVE',
      },
    });

    expect(screen.queryByRole('heading', { name: 'Start guiding better projects.' })).not.toBeInTheDocument();
    expect(screen.getByTestId('mentor-overview-dest')).toBeInTheDocument();
  });
});
