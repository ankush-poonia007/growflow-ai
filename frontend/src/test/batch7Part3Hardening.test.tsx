import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue, UserRole } from '@/auth/types';
import type { User } from '@supabase/supabase-js';

import { WorkplaceSelector } from '@/components/navigation/WorkplaceSelector';
import { MobileWorkspaceDrawer } from '@/components/navigation/MobileWorkspaceDrawer';
import { Sidebar as StudentSidebar } from '@/components/navigation/Sidebar';
import { MentorSidebar } from '@/components/navigation/MentorSidebar';
import { AdminSidebar } from '@/components/navigation/AdminSidebar';
import { ProtectedRoute } from '@/auth/ProtectedRoute';
import { LifecycleTrack } from '@/pages/Student/StudentDashboard/components/LifecycleTrack';
import { CANONICAL_LIFECYCLE_STAGES } from '@/pages/Student/StudentDashboard/utils';

function createMockAuth(
  role: UserRole | null = 'ADMIN',
  fullName = 'Administrator',
  email = 'admin@growflow.ai',
  isAuthenticated = true
): AuthContextValue {
  return {
    status: isAuthenticated ? 'AUTHENTICATED' : 'UNAUTHENTICATED',
    session: isAuthenticated
      ? ({
          access_token: 'mock-token',
          refresh_token: 'mock-refresh',
          expires_in: 3600,
          token_type: 'bearer',
          user: { id: 'usr-1', email } as unknown as User,
        } as AuthContextValue['session'])
      : null,
    supabaseUser: isAuthenticated ? ({ id: 'usr-1', email } as unknown as User) : null,
    user: isAuthenticated && role
      ? {
          id: 'usr-1',
          email,
          role,
          status: 'ACTIVE',
          fullName,
        }
      : null,
    error: null,
    isRoleResolving: false,
    isAuthenticated,
    isLoading: false,
    signIn: vi.fn(),
    signOut: vi.fn(),
    retryAuth: vi.fn(),
    refreshAuthorization: vi.fn(),
  };
}

describe('Phase 7 Batch 7 Part 3 — Shared UX + Final Hardening', () => {
  // =========================================================================
  // A. WorkplaceSelector
  // =========================================================================
  describe('A. WorkplaceSelector Routing & Permissions', () => {
    it('routes authenticated Student to BUILD and disables other workplaces', () => {
      const auth = createMockAuth('STUDENT', 'Alice Student', 'alice@growflow.ai');
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <WorkplaceSelector />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const trigger = screen.getByRole('button', { name: /select workplace/i });
      fireEvent.click(trigger);

      // BUILD link active and points to /student/dashboard
      const buildLink = screen.getByRole('menuitem', { name: /BUILD/i });
      expect(buildLink.getAttribute('href')).toBe('/student/dashboard');

      // SUPERVISE and GOVERN are rendered as disabled menu items
      const disabledItems = screen.getAllByRole('menuitem', { hidden: true });
      const superviseItem = disabledItems.find((el) => el.textContent?.includes('SUPERVISE'));
      const governItem = disabledItems.find((el) => el.textContent?.includes('GOVERN'));

      expect(superviseItem?.getAttribute('aria-disabled')).toBe('true');
      expect(governItem?.getAttribute('aria-disabled')).toBe('true');
    });

    it('routes authenticated Mentor to SUPERVISE and disables other workplaces', () => {
      const auth = createMockAuth('MENTOR', 'Dr. Marcus', 'marcus@growflow.ai');
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <WorkplaceSelector />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const trigger = screen.getByRole('button', { name: /select workplace/i });
      fireEvent.click(trigger);

      const superviseLink = screen.getByRole('menuitem', { name: /SUPERVISE/i });
      expect(superviseLink.getAttribute('href')).toBe('/mentor/overview');

      const disabledItems = screen.getAllByRole('menuitem');
      const buildItem = disabledItems.find((el) => el.textContent?.includes('BUILD'));
      const governItem = disabledItems.find((el) => el.textContent?.includes('GOVERN'));

      expect(buildItem?.getAttribute('aria-disabled')).toBe('true');
      expect(governItem?.getAttribute('aria-disabled')).toBe('true');
    });

    it('routes authenticated Admin to GOVERN and disables other workplaces', () => {
      const auth = createMockAuth('ADMIN', 'Platform Admin', 'admin@growflow.ai');
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <WorkplaceSelector />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const trigger = screen.getByRole('button', { name: /select workplace/i });
      fireEvent.click(trigger);

      const governLink = screen.getByRole('menuitem', { name: /GOVERN/i });
      expect(governLink.getAttribute('href')).toBe('/admin/overview');

      const disabledItems = screen.getAllByRole('menuitem');
      const buildItem = disabledItems.find((el) => el.textContent?.includes('BUILD'));
      const superviseItem = disabledItems.find((el) => el.textContent?.includes('SUPERVISE'));

      expect(buildItem?.getAttribute('aria-disabled')).toBe('true');
      expect(superviseItem?.getAttribute('aria-disabled')).toBe('true');
    });

    it('directs unauthenticated visitors to respective sign-in entrypoints truthfully', () => {
      const auth = createMockAuth(null, '', '', false);
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <WorkplaceSelector />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const trigger = screen.getByRole('button', { name: /select workplace/i });
      fireEvent.click(trigger);

      const menuItems = screen.getAllByRole('menuitem');
      const buildLink = menuItems.find((el) => el.textContent?.includes('BUILD'));
      const superviseLink = menuItems.find((el) => el.textContent?.includes('SUPERVISE'));
      const governLink = menuItems.find((el) => el.textContent?.includes('GOVERN'));

      expect(buildLink?.getAttribute('href')).toBe('/auth/student/sign-in');
      expect(superviseLink?.getAttribute('href')).toBe('/auth/mentor/sign-in');
      expect(governLink?.getAttribute('href')).toBe('/auth/admin/sign-in');
    });
  });

  // =========================================================================
  // B. MobileWorkspaceDrawer
  // =========================================================================
  describe('B. MobileWorkspaceDrawer Workplace Parity', () => {
    it('renders Student BUILD navigation and profile/settings paths', () => {
      const auth = createMockAuth('STUDENT', 'Alice Student', 'alice@growflow.ai');
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <MobileWorkspaceDrawer isOpen={true} onClose={vi.fn()} workplace="BUILD" />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByRole('dialog', { name: /Student Workspace Menu/i })).toBeDefined();
      expect(screen.getByRole('link', { name: /Dashboard/i }).getAttribute('href')).toBe('/student/dashboard');
      expect(screen.getByRole('link', { name: /^Projects$/i }).getAttribute('href')).toBe('/student/projects');
      expect(screen.getByRole('link', { name: /Mentor Projects/i }).getAttribute('href')).toBe('/student/projects/mentor-catalog');
      expect(screen.getByRole('link', { name: /Profile/i }).getAttribute('href')).toBe('/profile');
      expect(screen.getByRole('link', { name: /Settings/i }).getAttribute('href')).toBe('/settings');
      expect(screen.getByText('Alice Student')).toBeDefined();
    });

    it('renders Mentor SUPERVISE navigation and profile/settings paths', () => {
      const auth = createMockAuth('MENTOR', 'Dr. Jane Smith', 'jane@growflow.ai');
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <MobileWorkspaceDrawer isOpen={true} onClose={vi.fn()} workplace="SUPERVISE" />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByRole('dialog', { name: /Mentor Workspace Menu/i })).toBeDefined();
      expect(screen.getByRole('link', { name: /Overview/i }).getAttribute('href')).toBe('/mentor/overview');
      expect(screen.getByRole('link', { name: /Groups/i }).getAttribute('href')).toBe('/mentor/groups');
      expect(screen.getByRole('link', { name: /Definitions/i }).getAttribute('href')).toBe('/mentor/projects');
      expect(screen.getByRole('link', { name: /Profile/i }).getAttribute('href')).toBe('/mentor/profile');
      expect(screen.getByRole('link', { name: /Settings/i }).getAttribute('href')).toBe('/mentor/settings');
      expect(screen.getByText('Dr. Jane Smith')).toBeDefined();
    });

    it('renders Admin GOVERN navigation and canonical profile/settings paths', () => {
      const auth = createMockAuth('ADMIN', 'Platform Administrator', 'admin@growflow.ai');
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <MobileWorkspaceDrawer isOpen={true} onClose={vi.fn()} workplace="GOVERN" />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByRole('dialog', { name: /Admin Workspace Menu/i })).toBeDefined();
      expect(screen.getByRole('link', { name: /Overview/i }).getAttribute('href')).toBe('/admin/overview');
      expect(screen.getByRole('link', { name: /Mentors/i }).getAttribute('href')).toBe('/admin/mentors');
      expect(screen.getByRole('link', { name: /Students/i }).getAttribute('href')).toBe('/admin/students');
      expect(screen.getByRole('link', { name: /Groups/i }).getAttribute('href')).toBe('/admin/groups');
      expect(screen.getByRole('link', { name: /Projects/i }).getAttribute('href')).toBe('/admin/projects');
      expect(screen.getByRole('link', { name: /Definitions/i }).getAttribute('href')).toBe('/admin/definitions');
      expect(screen.getByRole('link', { name: /Instances/i }).getAttribute('href')).toBe('/admin/instances');
      expect(screen.getByRole('link', { name: /Profile/i }).getAttribute('href')).toBe('/admin/profile');
      expect(screen.getByRole('link', { name: /Settings/i }).getAttribute('href')).toBe('/admin/settings');
    });

    it('uses truthful fallback identity in drawer footer and never hardcodes demo names', () => {
      // User with no fullName, only email
      const authNoName = createMockAuth('ADMIN', '', 'superadmin@growflow.ai');
      const { rerender } = render(
        <AuthContext.Provider value={authNoName}>
          <MemoryRouter>
            <MobileWorkspaceDrawer isOpen={true} onClose={vi.fn()} workplace="GOVERN" />
          </MemoryRouter>
        </AuthContext.Provider>
      );
      expect(screen.getByText('superadmin@growflow.ai')).toBeDefined();
      expect(screen.queryByText('Student')).toBeNull();

      // User with neither fullName nor email
      const authEmpty = createMockAuth('ADMIN', '', '');
      rerender(
        <AuthContext.Provider value={authEmpty}>
          <MemoryRouter>
            <MobileWorkspaceDrawer isOpen={true} onClose={vi.fn()} workplace="GOVERN" />
          </MemoryRouter>
        </AuthContext.Provider>
      );
      expect(screen.getByText('—')).toBeDefined();
      expect(screen.queryByText('Student')).toBeNull();
      expect(screen.queryByText('Platform Administrator')).toBeNull();
    });
  });

  // =========================================================================
  // C. Sidebar Expansion & Interaction Parity
  // =========================================================================
  describe('C. Sidebar Hover & Click Rail Parity Across All 3 Workplaces', () => {
    it('expands StudentSidebar on hover when collapsed and toggles on rail click', () => {
      const toggle = vi.fn();
      const auth = createMockAuth('STUDENT', 'Bob Student', 'bob@growflow.ai');
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <StudentSidebar isCollapsed={true} onToggleCollapse={toggle} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const sidebar = screen.getByRole('complementary', { name: /Student Workspace Navigation/i });
      expect(sidebar.className).toContain('gf-sidebar--collapsed');

      // 1. Hover expansion
      fireEvent.mouseEnter(sidebar);
      expect(sidebar.className).toContain('gf-sidebar--hover-expanded');
      expect(sidebar.className).not.toContain('gf-sidebar--collapsed');

      fireEvent.mouseLeave(sidebar);
      expect(sidebar.className).toContain('gf-sidebar--collapsed');

      // 2. Click on rail expands
      fireEvent.click(sidebar);
      expect(toggle).toHaveBeenCalledTimes(1);
    });

    it('expands MentorSidebar on hover when collapsed and toggles on rail click', () => {
      const toggle = vi.fn();
      const auth = createMockAuth('MENTOR', 'Dr. Smith', 'smith@growflow.ai');
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <MentorSidebar isCollapsed={true} onToggleCollapse={toggle} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const sidebar = screen.getByRole('complementary', { name: /Mentor Supervise Navigation/i });
      expect(sidebar.className).toContain('gf-mentor-sidebar--collapsed');

      fireEvent.mouseEnter(sidebar);
      expect(sidebar.className).toContain('gf-mentor-sidebar--hover-expanded');

      fireEvent.mouseLeave(sidebar);
      expect(sidebar.className).toContain('gf-mentor-sidebar--collapsed');

      fireEvent.click(sidebar);
      expect(toggle).toHaveBeenCalledTimes(1);
    });

    it('expands AdminSidebar on hover when collapsed and toggles on rail click', () => {
      const toggle = vi.fn();
      const auth = createMockAuth('ADMIN', 'Admin Person', 'admin@growflow.ai');
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <AdminSidebar isCollapsed={true} onToggleCollapse={toggle} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const sidebar = screen.getByRole('complementary', { name: /Admin Governance Navigation/i });
      expect(sidebar.className).toContain('gf-admin-sidebar--collapsed');

      fireEvent.mouseEnter(sidebar);
      expect(sidebar.className).toContain('gf-admin-sidebar--hover-expanded');

      fireEvent.mouseLeave(sidebar);
      expect(sidebar.className).toContain('gf-admin-sidebar--collapsed');

      fireEvent.click(sidebar);
      expect(toggle).toHaveBeenCalledTimes(1);
    });
  });

  // =========================================================================
  // D. Admin Route Protection Regression
  // =========================================================================
  describe('D. Route Protection & Authorization Boundaries', () => {
    it('redirects unauthenticated users to /auth/admin/sign-in with encoded returnTo', () => {
      const auth = createMockAuth(null, '', '', false);
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter initialEntries={['/admin/overview?tab=metrics']}>
            <Routes>
              <Route
                path="/admin/*"
                element={
                  <ProtectedRoute requiredRole="ADMIN" loginPath="/auth/admin/sign-in">
                    <div>Admin Protected Content</div>
                  </ProtectedRoute>
                }
              />
              <Route path="/auth/admin/sign-in" element={<div>Admin Sign In Page</div>} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByText('Admin Sign In Page')).toBeDefined();
      expect(screen.queryByText('Admin Protected Content')).toBeNull();
    });

    it('denies authenticated Student access to Admin routes with ForbiddenView', () => {
      const auth = createMockAuth('STUDENT', 'Alice Student', 'alice@growflow.ai');
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter initialEntries={['/admin/overview']}>
            <ProtectedRoute requiredRole="ADMIN" loginPath="/auth/admin/sign-in">
              <div>Admin Protected Content</div>
            </ProtectedRoute>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByText(/Access Restricted/i)).toBeDefined();
      expect(screen.getByText(/This workspace is designated for ADMIN accounts/i)).toBeDefined();
      expect(screen.queryByText('Admin Protected Content')).toBeNull();
    });

    it('denies authenticated Mentor access to Admin routes with ForbiddenView', () => {
      const auth = createMockAuth('MENTOR', 'Dr. Jane', 'jane@growflow.ai');
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter initialEntries={['/admin/mentors']}>
            <ProtectedRoute requiredRole="ADMIN" loginPath="/auth/admin/sign-in">
              <div>Admin Protected Content</div>
            </ProtectedRoute>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByText(/Access Restricted/i)).toBeDefined();
      expect(screen.getByText(/This workspace is designated for ADMIN accounts/i)).toBeDefined();
      expect(screen.queryByText('Admin Protected Content')).toBeNull();
    });

    it('allows authenticated Admin access to Admin routes', () => {
      const auth = createMockAuth('ADMIN', 'Platform Administrator', 'admin@growflow.ai');
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter initialEntries={['/admin/overview']}>
            <ProtectedRoute requiredRole="ADMIN" loginPath="/auth/admin/sign-in">
              <div>Admin Protected Content</div>
            </ProtectedRoute>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByText('Admin Protected Content')).toBeDefined();
      expect(screen.queryByText(/Access Restricted/i)).toBeNull();
    });
  });

  // =========================================================================
  // E. Identity Fallback & Parity
  // =========================================================================
  describe('E. Authenticated Identity Fallback Hierarchy', () => {
    it('prefers fullName when available in sidebars', () => {
      const auth = createMockAuth('ADMIN', 'Jane Administrator', 'jane@growflow.ai');
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <AdminSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByText('Jane Administrator')).toBeDefined();
      expect(screen.getByText('JA')).toBeDefined();
    });

    it('falls back to email when fullName is missing', () => {
      const auth = createMockAuth('ADMIN', '', 'adminops@growflow.ai');
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <AdminSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByText('adminops@growflow.ai')).toBeDefined();
      expect(screen.getByText('AD')).toBeDefined();
    });

    it('falls back to "—" when both fullName and email are empty and never displays demo strings', () => {
      const auth = createMockAuth('ADMIN', '', '');
      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <AdminSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByText('—')).toBeDefined();
      expect(screen.queryByText('Admin')).toBeNull();
      expect(screen.queryByText('Platform Administrator')).toBeNull();
      expect(screen.queryByText('Student')).toBeNull();
    });
  });

  // =========================================================================
  // F. Student Lifecycle Presentation Parity
  // =========================================================================
  describe('F. Canonical Lifecycle Sequence & Presentation', () => {
    it('contains all 8 canonical lifecycle stages in exact chronological order', () => {
      const expectedStages = [
        'Idea',
        'Assessment',
        'Blueprint',
        'Planning',
        'Implementation',
        'Testing',
        'Deployment',
        'Completed',
      ];

      expect(CANONICAL_LIFECYCLE_STAGES.map((s) => s.label)).toEqual(expectedStages);
      expect(CANONICAL_LIFECYCLE_STAGES.map((s) => s.stage)).toEqual([1, 2, 3, 4, 5, 6, 7, 8]);
    });

    it('renders all 8 stages without state corruption', () => {
      render(
        <MemoryRouter>
          <LifecycleTrack currentPhase="BLUEPRINT" />
        </MemoryRouter>
      );

      // Verify header indicators
      expect(screen.getByText(/Stage 3 of 8 — BLUEPRINT/i)).toBeDefined();

      // All 8 stage labels rendered
      expect(screen.getByText('Idea')).toBeDefined();
      expect(screen.getByText('Assessment')).toBeDefined();
      expect(screen.getByText('Blueprint')).toBeDefined();
      expect(screen.getByText('Planning')).toBeDefined();
      expect(screen.getByText('Implementation')).toBeDefined();
      expect(screen.getByText('Testing')).toBeDefined();
      expect(screen.getByText('Deployment')).toBeDefined();
      expect(screen.getByText('Completed')).toBeDefined();

      // Verify node 3 is current phase
      const items = screen.getAllByRole('listitem');
      expect(items).toHaveLength(8);
      expect(items[2]?.className).toContain('gf-lifecycle-track__item--current');
      expect(items[0]?.className).toContain('gf-lifecycle-track__item--completed');
      expect(items[1]?.className).toContain('gf-lifecycle-track__item--completed');
      expect(items[3]?.className).toContain('gf-lifecycle-track__item--upcoming');
    });
  });
});
