import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { AuthHeader } from '@/components/navigation/AuthHeader';
import { MentorSidebar } from '@/components/navigation/MentorSidebar';
import { Sidebar as StudentSidebar } from '@/components/navigation/Sidebar';
import { ProtectedRoute } from '@/auth/ProtectedRoute';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue, GrowFlowUser } from '@/auth/types';
import type { User } from '@supabase/supabase-js';

function createMockAuthContext(user: GrowFlowUser | null, isRoleResolving = false): AuthContextValue {
  return {
    status: user ? 'AUTHENTICATED' : 'UNAUTHENTICATED',
    session: user
      ? ({
          access_token: 'valid-token',
          refresh_token: 'valid-refresh',
          expires_in: 3600,
          token_type: 'bearer',
          user: {
            id: user.id,
            email: user.email,
            user_metadata: {
              full_name: user.fullName,
            },
          } as unknown as User,
        } as unknown as AuthContextValue['session'])
      : null,
    supabaseUser: user
      ? ({
          id: user.id,
          email: user.email,
          user_metadata: {
            full_name: user.fullName,
          },
        } as unknown as User)
      : null,
    user,
    error: null,
    isRoleResolving,
    isAuthenticated: !!user,
    isLoading: false,
    signIn: vi.fn(),
    signOut: vi.fn(),
    retryAuth: vi.fn(),
    refreshAuthorization: vi.fn(),
  };
}

describe('Phase 7 — Batch 3 Correction Pass: Role & Identity Authority Tests', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('1. Mentor authenticated + SUPERVISE workplace: header and sidebar show authentic Mentor identity', () => {
    const mentorUser: GrowFlowUser = {
      id: 'mentor-usr-1',
      email: 'sarah.chen@university.edu',
      role: 'MENTOR',
      status: 'ACTIVE',
      fullName: 'Dr. Sarah Chen',
    };

    const authValue = createMockAuthContext(mentorUser);

    const { container } = render(
      <AuthContext.Provider value={authValue}>
        <MemoryRouter initialEntries={['/mentor/students']}>
          <AuthHeader
            workplace="SUPERVISE"
            onToggleMobileNav={vi.fn()}
            isMobileNavOpen={false}
          />
          <MentorSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
        </MemoryRouter>
      </AuthContext.Provider>
    );

    const header = container.querySelector('.gf-auth-header') as HTMLElement;
    const sidebar = container.querySelector('.gf-mentor-sidebar') as HTMLElement;

    // Global Header verification
    expect(header.querySelector('.gf-auth-header__context-tag')).toHaveTextContent('SUPERVISE');
    expect(header.querySelector('.gf-auth-header__user-name')).toHaveTextContent('Dr. Sarah Chen');
    expect(header.querySelector('.gf-auth-header__user-role')).toHaveTextContent('MENTOR');

    // Mentor Sidebar verification
    expect(within(sidebar).getByText('SC')).toBeInTheDocument(); // Initials from Sarah Chen
    expect(within(sidebar).getByText('Dr. Sarah Chen')).toBeInTheDocument();
    expect(within(sidebar).getByText('Mentor Account')).toBeInTheDocument();
    expect(within(sidebar).queryByText('ME')).not.toBeInTheDocument();
  });

  it('2. Student authenticated + BUILD workplace: header and sidebar show authentic Student identity', () => {
    const studentUser: GrowFlowUser = {
      id: 'student-usr-1',
      email: 'alex.rivera@growflow.test',
      role: 'STUDENT',
      status: 'ACTIVE',
      fullName: 'Alex Rivera',
    };

    const authValue = createMockAuthContext(studentUser);

    const { container } = render(
      <AuthContext.Provider value={authValue}>
        <MemoryRouter initialEntries={['/student/dashboard']}>
          <AuthHeader
            workplace="BUILD"
            onToggleMobileNav={vi.fn()}
            isMobileNavOpen={false}
          />
          <StudentSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
        </MemoryRouter>
      </AuthContext.Provider>
    );

    const header = container.querySelector('.gf-auth-header') as HTMLElement;
    const sidebar = container.querySelector('.gf-sidebar') as HTMLElement;

    // Header verification
    expect(header.querySelector('.gf-auth-header__context-tag')).toHaveTextContent('BUILD');
    expect(header.querySelector('.gf-auth-header__user-name')).toHaveTextContent('Alex Rivera');
    expect(header.querySelector('.gf-auth-header__user-role')).toHaveTextContent('STUDENT');

    // Student Sidebar verification
    expect(within(sidebar).getByText('AR')).toBeInTheDocument();
    expect(within(sidebar).getByText('Student Account')).toBeInTheDocument();
  });

  it('3. Admin authenticated + GOVERN workplace: header shows authentic Admin context', () => {
    const adminUser: GrowFlowUser = {
      id: 'admin-usr-1',
      email: 'admin.governance@growflow.ai',
      role: 'ADMIN',
      status: 'ACTIVE',
      fullName: 'Chief Administrator',
    };

    const authValue = createMockAuthContext(adminUser);

    const { container } = render(
      <AuthContext.Provider value={authValue}>
        <MemoryRouter initialEntries={['/admin/overview']}>
          <AuthHeader
            workplace="GOVERN"
            onToggleMobileNav={vi.fn()}
            isMobileNavOpen={false}
          />
        </MemoryRouter>
      </AuthContext.Provider>
    );

    const header = container.querySelector('.gf-auth-header') as HTMLElement;

    expect(header.querySelector('.gf-auth-header__context-tag')).toHaveTextContent('GOVERN');
    expect(header.querySelector('.gf-auth-header__user-name')).toHaveTextContent('Chief Administrator');
    expect(header.querySelector('.gf-auth-header__user-role')).toHaveTextContent('ADMIN');
  });

  it('4. Student session attempting to render Mentor route: protected boundary denies entry and does not manufacture Mentor identity', () => {
    const studentUser: GrowFlowUser = {
      id: 'student-usr-2',
      email: 'attacker@student.edu',
      role: 'STUDENT',
      status: 'ACTIVE',
      fullName: 'Unauthorized Student',
    };

    const authValue = createMockAuthContext(studentUser);

    render(
      <AuthContext.Provider value={authValue}>
        <MemoryRouter initialEntries={['/mentor/students']}>
          <Routes>
            <Route
              element={
                <ProtectedRoute requiredRole="MENTOR" loginPath="/auth/mentor/sign-in">
                  <div>Protected Mentor Supervision Zone</div>
                </ProtectedRoute>
              }
            >
              <Route path="/mentor/students" element={<div>Mentor Content</div>} />
            </Route>
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    );

    // Must be blocked by role mismatch boundary
    expect(screen.queryByText('Protected Mentor Supervision Zone')).not.toBeInTheDocument();
    expect(screen.getByText(/designated for MENTOR accounts/i)).toBeInTheDocument();
    expect(screen.getByText(/authorized as STUDENT/i)).toBeInTheDocument();
  });

  it('5. Valid authenticated session while authorization endpoint is unavailable: role is NOT fabricated from workplace', () => {
    // Session identity exists, but backend authorization hasn't resolved role (role is null)
    const unverifiedUser: GrowFlowUser = {
      id: 'usr-unverified',
      email: 'pending.mentor@university.edu',
      role: null,
      status: null,
      fullName: 'Pending Professor',
    };

    const authValue = createMockAuthContext(unverifiedUser, false);

    const { container } = render(
      <AuthContext.Provider value={authValue}>
        <MemoryRouter initialEntries={['/mentor/students']}>
          <AuthHeader
            workplace="SUPERVISE"
            onToggleMobileNav={vi.fn()}
            isMobileNavOpen={false}
          />
          <MentorSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
        </MemoryRouter>
      </AuthContext.Provider>
    );

    const header = container.querySelector('.gf-auth-header') as HTMLElement;
    const sidebar = container.querySelector('.gf-mentor-sidebar') as HTMLElement;

    // Workplace contextual tag reflects UI surface
    expect(header.querySelector('.gf-auth-header__context-tag')).toHaveTextContent('SUPERVISE');

    // User display name reflects authenticated session
    expect(header.querySelector('.gf-auth-header__user-name')).toHaveTextContent('Pending Professor');

    // Crucially: Header role MUST NOT fabricate "MENTOR" or default to "STUDENT"
    expect(header.querySelector('.gf-auth-header__user-role')).toBeNull();

    // Sidebar role label defaults safely to generic "Account" instead of claiming "Mentor Account"
    expect(within(sidebar).getByText('Account')).toBeInTheDocument();
    expect(within(sidebar).queryByText('Mentor Account')).not.toBeInTheDocument();
  });
});
