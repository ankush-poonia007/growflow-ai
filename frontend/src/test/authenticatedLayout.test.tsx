import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, within } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { AuthenticatedLayout } from '@/app/layouts/AuthenticatedLayout';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import type { User } from '@supabase/supabase-js';

function renderInAuthLayout(
  initialRoute = '/student/dashboard',
  authOverrides: Partial<AuthContextValue> = {},
) {
  const authValue: AuthContextValue = {
    status: 'AUTHENTICATED',
    session: {
      access_token: 'mock-token',
      refresh_token: 'mock-refresh',
      expires_in: 3600,
      token_type: 'bearer',
      user: { id: 'mock-user-id', email: 'student@example.com' } as unknown as User,
    },
    supabaseUser: { id: 'mock-user-id', email: 'student@example.com' } as unknown as User,
    user: {
      id: 'mock-user-id',
      email: 'student@example.com',
      role: 'STUDENT',
      status: 'ACTIVE',
      fullName: 'Alex Student',
    },
    error: null,
    isRoleResolving: false,
    isAuthenticated: true,
    isLoading: false,
    signIn: vi.fn(),
    signOut: vi.fn(),
    retryAuth: vi.fn(),
    refreshAuthorization: vi.fn(),
    ...authOverrides,
  };

  return render(
    <AuthContext.Provider value={authValue}>
      <MemoryRouter initialEntries={[initialRoute]}>
        <Routes>
          <Route element={<AuthenticatedLayout />}>
            <Route path="/student/dashboard" element={<div>Dashboard Content</div>} />
            <Route path="/student/projects" element={<div>Projects Content</div>} />
            <Route path="/student/projects/new" element={<div>New Project Content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

describe('AuthenticatedLayout & Shell Foundation', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders the authenticated shell frame, header, sidebar, and child content', () => {
    renderInAuthLayout('/student/dashboard');

    // Header checks
    const banner = screen.getByRole('banner');
    expect(banner).toBeInTheDocument();
    expect(within(banner).getByText('Alex Student')).toBeInTheDocument();

    // Sidebar checks
    const aside = screen.getByLabelText('Student Workspace Navigation');
    expect(aside).toBeInTheDocument();

    // Child content checks
    expect(screen.getByText('Dashboard Content')).toBeInTheDocument();
  });

  it('highlights the active route in the sidebar', () => {
    renderInAuthLayout('/student/projects');

    const projectsLink = screen.getAllByRole('link', { name: /projects/i })[0];
    expect(projectsLink).toHaveAttribute('aria-current', 'page');
  });

  it('toggles desktop sidebar collapse and persists preference to localStorage', () => {
    renderInAuthLayout('/student/dashboard');

    const collapseBtn = screen.getByRole('button', { name: /collapse sidebar/i });
    expect(collapseBtn).toBeInTheDocument();

    // Toggle collapse
    fireEvent.click(collapseBtn);
    expect(localStorage.getItem('growflow_sidebar_collapsed')).toBe('true');

    // Button label should now indicate expand
    expect(screen.getByRole('button', { name: /expand sidebar/i })).toBeInTheDocument();

    // Toggle expand
    fireEvent.click(screen.getByRole('button', { name: /expand sidebar/i }));
    expect(localStorage.getItem('growflow_sidebar_collapsed')).toBe('false');
  });

  it('toggles mobile drawer navigation and supports closing via Escape key', () => {
    renderInAuthLayout('/student/dashboard');

    const hamburger = screen.getByRole('button', { name: /open workspace menu/i });
    expect(hamburger).toBeInTheDocument();

    // Open mobile drawer
    fireEvent.click(hamburger);
    const drawerDialog = screen.getByRole('dialog', { name: /student workspace menu/i });
    expect(drawerDialog).toHaveClass('gf-mobile-drawer--open');

    // Press Escape to close
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(drawerDialog).not.toHaveClass('gf-mobile-drawer--open');
  });
});
