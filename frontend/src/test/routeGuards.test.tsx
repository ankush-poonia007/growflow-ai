import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { ProtectedRoute } from '@/auth/ProtectedRoute';
import { AuthRoute } from '@/auth/AuthRoute';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';

function renderWithAuth(
  ui: React.ReactNode,
  authValues: Partial<AuthContextValue>,
  initialRoute = '/student/dashboard',
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
    refreshAuthorization: vi.fn(),
    ...authValues,
  };

  return render(
    <AuthContext.Provider value={defaultAuth}>
      <MemoryRouter initialEntries={[initialRoute]}>{ui}</MemoryRouter>
    </AuthContext.Provider>,
  );
}

describe('ProtectedRoute', () => {
  it('renders loading state while authentication is initializing', () => {
    renderWithAuth(
      <ProtectedRoute>
        <div>Protected Secret</div>
      </ProtectedRoute>,
      { status: 'INITIALIZING', isLoading: true },
    );

    expect(screen.queryByText('Protected Secret')).not.toBeInTheDocument();
    expect(screen.getByText('Verifying workspace credentials...')).toBeInTheDocument();
  });

  it('redirects unauthenticated users to sign-in with returnTo parameter', () => {
    renderWithAuth(
      <Routes>
        <Route
          path="/student/dashboard"
          element={
            <ProtectedRoute>
              <div>Protected Dashboard</div>
            </ProtectedRoute>
          }
        />
        <Route
          path="/auth/student/sign-in"
          element={<div data-testid="login-page">Sign In Page</div>}
        />
      </Routes>,
      { status: 'UNAUTHENTICATED', isAuthenticated: false },
      '/student/dashboard?filter=active',
    );

    expect(screen.queryByText('Protected Dashboard')).not.toBeInTheDocument();
    expect(screen.getByTestId('login-page')).toBeInTheDocument();
  });

  it('renders 403 ForbiddenView when user has unauthorized role', () => {
    renderWithAuth(
      <ProtectedRoute requiredRole="STUDENT">
        <div>Protected Student Content</div>
      </ProtectedRoute>,
      {
        status: 'AUTHENTICATED',
        isAuthenticated: true,
        user: {
          id: 'mentor-1',
          email: 'mentor@growflow.ai',
          role: 'MENTOR',
          status: 'ACTIVE',
        },
      },
    );

    expect(screen.queryByText('Protected Student Content')).not.toBeInTheDocument();
    expect(screen.getByText('Access Restricted')).toBeInTheDocument();
    expect(screen.getByText(/authorized as MENTOR/i)).toBeInTheDocument();
  });

  it('renders 403 ForbiddenView when account is suspended', () => {
    renderWithAuth(
      <ProtectedRoute requiredRole="STUDENT">
        <div>Protected Student Content</div>
      </ProtectedRoute>,
      {
        status: 'AUTHENTICATED',
        isAuthenticated: true,
        user: {
          id: 'student-1',
          email: 'suspended@growflow.ai',
          role: 'STUDENT',
          status: 'SUSPENDED',
        },
      },
    );

    expect(screen.queryByText('Protected Student Content')).not.toBeInTheDocument();
    expect(screen.getByText('Account Suspended')).toBeInTheDocument();
  });

  it('renders protected content when authenticated with authorized role and active status', () => {
    renderWithAuth(
      <ProtectedRoute requiredRole="STUDENT">
        <div>Protected Student Content</div>
      </ProtectedRoute>,
      {
        status: 'AUTHENTICATED',
        isAuthenticated: true,
        user: {
          id: 'student-1',
          email: 'active@growflow.ai',
          role: 'STUDENT',
          status: 'ACTIVE',
        },
      },
    );

    expect(screen.getByText('Protected Student Content')).toBeInTheDocument();
  });
});

describe('AuthRoute', () => {
  it('renders child auth page when user is unauthenticated', () => {
    renderWithAuth(
      <AuthRoute>
        <div>Student Login Form</div>
      </AuthRoute>,
      { status: 'UNAUTHENTICATED', isAuthenticated: false },
      '/auth/student/sign-in',
    );

    expect(screen.getByText('Student Login Form')).toBeInTheDocument();
  });

  it('redirects authenticated user to safe returnTo destination', () => {
    renderWithAuth(
      <Routes>
        <Route
          path="/auth/student/sign-in"
          element={
            <AuthRoute>
              <div>Student Login Form</div>
            </AuthRoute>
          }
        />
        <Route
          path="/student/projects/999"
          element={<div data-testid="target-destination">Target Projects Page</div>}
        />
      </Routes>,
      { status: 'AUTHENTICATED', isAuthenticated: true },
      '/auth/student/sign-in?returnTo=%2Fstudent%2Fprojects%2F999',
    );

    expect(screen.queryByText('Student Login Form')).not.toBeInTheDocument();
    expect(screen.getByTestId('target-destination')).toBeInTheDocument();
  });
});
