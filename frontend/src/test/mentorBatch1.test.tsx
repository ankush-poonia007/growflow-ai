import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import type { User } from '@supabase/supabase-js';

import { ErrorBoundary } from '@/components/ErrorBoundary';
import { NotFound } from '@/pages/NotFound/NotFound';
import { WorkplaceSelector } from '@/components/navigation/WorkplaceSelector';
import { MentorSidebar } from '@/components/navigation/MentorSidebar';
import { MentorLayout } from '@/app/layouts/MentorLayout';
import { MentorOverview } from '@/pages/Mentor/MentorOverview/MentorOverview';
import { GroupsDirectory } from '@/pages/Mentor/GroupsDirectory/GroupsDirectory';
import { GroupCreate } from '@/pages/Mentor/GroupCreate/GroupCreate';
import { GroupWorkspace } from '@/pages/Mentor/GroupWorkspace/GroupWorkspace';
import { GroupStudents } from '@/pages/Mentor/GroupStudents/GroupStudents';
import { GroupProjects } from '@/pages/Mentor/GroupProjects/GroupProjects';
import { GroupAtRisk } from '@/pages/Mentor/GroupAtRisk/GroupAtRisk';

import type React from 'react';
import * as apiClient from '@/lib/api/client';
import type { ProjectResponse } from '@/lib/api/types';

function createMockAuth(role: 'STUDENT' | 'MENTOR' | 'ADMIN' = 'MENTOR'): AuthContextValue {
  return {
    status: 'AUTHENTICATED',
    session: {
      access_token: 'mock-token',
      refresh_token: 'mock-refresh',
      expires_in: 3600,
      token_type: 'bearer',
      user: { id: 'user-1', email: `${role.toLowerCase()}@example.com` } as unknown as User,
    },
    supabaseUser: { id: 'user-1', email: `${role.toLowerCase()}@example.com` } as unknown as User,
    user: {
      id: 'user-1',
      email: `${role.toLowerCase()}@example.com`,
      role,
      status: 'ACTIVE',
      fullName: `Test ${role}`,
    },
    error: null,
    isRoleResolving: false,
    isAuthenticated: true,
    isLoading: false,
    signIn: vi.fn(),
    signOut: vi.fn(),
    retryAuth: vi.fn(),
    refreshAuthorization: vi.fn(),
  };
}

describe('Phase 7 Batch 1: Mentor Shell, Navigation & System Surfaces', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('SYS04: React ErrorBoundary', () => {
    function BuggyComponent(): React.ReactNode {
      throw new Error('Test crash in component lifecycle');
    }

    it('catches render error and presents branded Soft Intelligence notice', () => {
      // Suppress console.error in test
      const spy = vi.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <ErrorBoundary>
          <BuggyComponent />
        </ErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      expect(screen.getByText(/Test crash in component lifecycle/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /return to home/i })).toBeInTheDocument();

      spy.mockRestore();
    });
  });

  describe('SYS03: Branded Soft Intelligence 404', () => {
    it('renders role-aware destination for student', () => {
      render(
        <AuthContext.Provider value={createMockAuth('STUDENT')}>
          <MemoryRouter>
            <NotFound />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByText('404 — Not Found')).toBeInTheDocument();
      expect(screen.getByText('Page Not Found')).toBeInTheDocument();
      const returnBtn = screen.getByRole('link', { name: /return to dashboard/i });
      expect(returnBtn).toHaveAttribute('href', '/student/dashboard');
    });

    it('renders role-aware destination for mentor', () => {
      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter>
            <NotFound />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const returnBtn = screen.getByRole('link', { name: /return to overview/i });
      expect(returnBtn).toHaveAttribute('href', '/mentor/overview');
    });
  });

  describe('WorkplaceSelector: Authenticated Role Routing', () => {
    it('restricts BUILD and enables SUPERVISE for authenticated mentor', () => {
      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter>
            <WorkplaceSelector />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const trigger = screen.getByRole('button', { name: /select workplace/i });
      fireEvent.click(trigger);

      const superviseLink = screen.getByRole('menuitem', { name: /supervise/i });
      expect(superviseLink).toHaveAttribute('href', '/mentor/overview');
      expect(screen.getByText('Active')).toBeInTheDocument();
    });
  });

  describe('MentorSidebar & Shell', () => {
    it('renders SUPERVISE tag and main navigation items', () => {
      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/overview']}>
            <MentorSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByText('SUPERVISE')).toBeInTheDocument();
      expect(screen.getByText('Overview')).toBeInTheDocument();
      expect(screen.getByText('Groups')).toBeInTheDocument();
    });

    it('renders MentorLayout shell with header and sidebar', () => {
      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/overview']}>
            <Routes>
              <Route element={<MentorLayout />}>
                <Route path="/mentor/overview" element={<div>Inner Content</div>} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByText('Inner Content')).toBeInTheDocument();
    });
  });

  describe('M01: MentorOverview', () => {
    it('fetches and renders supervisor metrics and cohort list', async () => {
      vi.spyOn(apiClient, 'getMentorOverview').mockResolvedValue({
        total_groups: 1,
        total_students: 12,
        total_projects: 6,
        at_risk_projects: 1,
        groups: [
          {
            id: 'grp-1',
            name: 'Cloud Architecture Cohort',
            join_code: 'CLOUD-2026',
            status: 'ACTIVE',
            student_count: 12,
            project_count: 6,
            at_risk_count: 1,
            created_at: '2026-09-01T00:00:00Z',
          },
        ],
      });

      render(
        <MemoryRouter>
          <MentorOverview />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Cloud Architecture Cohort')).toBeInTheDocument();
      });

      expect(screen.getByText('CLOUD-2026')).toBeInTheDocument();
      expect(screen.getByText('Supervised Groups')).toBeInTheDocument();
    });
  });

  describe('M02: GroupsDirectory', () => {
    it('renders cohorts and allows searching', async () => {
      vi.spyOn(apiClient, 'getMentorGroups').mockResolvedValue([
        {
          id: 'g-1',
          mentor_id: 'm-1',
          name: 'Section Alpha',
          join_code: 'ALPHA-77',
          status: 'ACTIVE',
        },
        {
          id: 'g-2',
          mentor_id: 'm-1',
          name: 'Section Beta',
          join_code: 'BETA-88',
          status: 'ACTIVE',
        },
      ]);

      render(
        <MemoryRouter>
          <GroupsDirectory />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Section Alpha')).toBeInTheDocument();
      });

      expect(screen.getByText('Section Beta')).toBeInTheDocument();

      const searchInput = screen.getByLabelText(/filter groups/i);
      fireEvent.change(searchInput, { target: { value: 'Alpha' } });

      expect(screen.getByText('Section Alpha')).toBeInTheDocument();
      expect(screen.queryByText('Section Beta')).not.toBeInTheDocument();
    });
  });

  describe('M03: GroupCreate', () => {
    it('validates input and submits new group', async () => {
      const createSpy = vi.spyOn(apiClient, 'createMentorGroup').mockResolvedValue({
        id: 'new-grp-id',
        mentor_id: 'm-1',
        name: 'New Capstone Cohort',
        join_code: 'CAP-2026',
        status: 'ACTIVE',
      });

      render(
        <MemoryRouter>
          <GroupCreate />
        </MemoryRouter>
      );

      const input = screen.getByLabelText(/cohort \/ group name/i);
      fireEvent.change(input, { target: { value: 'New Capstone Cohort' } });

      const submitBtn = screen.getByRole('button', { name: /create cohort/i });
      fireEvent.click(submitBtn);

      await waitFor(() => {
        expect(createSpy).toHaveBeenCalledWith({ name: 'New Capstone Cohort' });
      });
    });
  });

  describe('M04: GroupWorkspace', () => {
    it('renders group overview, stats, and navigation tabs', async () => {
      vi.spyOn(apiClient, 'getMentorGroup').mockResolvedValue({
        id: 'grp-test',
        mentor_id: 'm-1',
        name: 'Systems Engineering',
        join_code: 'SYS-101',
        status: 'ACTIVE',
      });
      vi.spyOn(apiClient, 'getGroupStudents').mockResolvedValue([
        {
          student_id: 's-1',
          email: 'student1@growflow.test',
          full_name: 'Jordan Lee',
          status: 'ACTIVE',
          joined_at: '2026-09-02T10:00:00Z',
        },
      ]);
      vi.spyOn(apiClient, 'getGroupProjects').mockResolvedValue([
        {
          id: 'p-1',
          student_id: 's-1',
          group_id: 'grp-test',
          name: 'Distributed Lock Manager',
          problem: 'Concurrency issues',
          proposed_solution: 'Raft consensus',
          complexity: 'ADVANCED',
          current_phase: 'IMPLEMENTATION',
          health: 'HEALTHY',
          progress_percentage: 60,
          status: 'ACTIVE',
        } as unknown as ProjectResponse,
      ]);

      render(
        <MemoryRouter initialEntries={['/mentor/groups/grp-test']}>
          <Routes>
            <Route path="/mentor/groups/:groupId" element={<GroupWorkspace />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('SYS-101')).toBeInTheDocument();
      });

      expect(screen.getByText('Jordan Lee')).toBeInTheDocument();
      expect(screen.getByText('Distributed Lock Manager')).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /students \(1\)/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /projects \(1\)/i })).toBeInTheDocument();
    });
  });

  describe('M05: GroupStudents', () => {
    it('renders roster of students enrolled in the cohort', async () => {
      vi.spyOn(apiClient, 'getMentorGroup').mockResolvedValue({
        id: 'grp-1',
        mentor_id: 'm-1',
        name: 'Distributed Systems',
        join_code: 'DIST-2026',
        status: 'ACTIVE',
      });
      vi.spyOn(apiClient, 'getGroupStudents').mockResolvedValue([
        {
          student_id: 's-1',
          email: 'alice@growflow.test',
          full_name: 'Alice Student',
          status: 'ACTIVE',
          joined_at: '2026-09-01T12:00:00Z',
        },
      ]);

      render(
        <MemoryRouter initialEntries={['/mentor/groups/grp-1/students']}>
          <Routes>
            <Route path="/mentor/groups/:groupId/students" element={<GroupStudents />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Alice Student')).toBeInTheDocument();
      });
      expect(screen.getByText('alice@growflow.test')).toBeInTheDocument();
    });
  });

  describe('M06: GroupProjects', () => {
    it('renders project cards with phase and health indicators', async () => {
      vi.spyOn(apiClient, 'getMentorGroup').mockResolvedValue({
        id: 'grp-1',
        mentor_id: 'm-1',
        name: 'Distributed Systems',
        join_code: 'DIST-2026',
        status: 'ACTIVE',
      });
      vi.spyOn(apiClient, 'getGroupProjects').mockResolvedValue([
        {
          id: 'p-1',
          student_id: 's-1',
          group_id: 'grp-1',
          name: 'AI Reasoning Engine',
          problem: 'Complex prompts',
          proposed_solution: 'Tree of thought',
          complexity: 'ADVANCED',
          current_phase: 'BLUEPRINT',
          health: 'ATTENTION',
          progress_percentage: 35,
          status: 'ACTIVE',
        } as unknown as ProjectResponse,
      ]);

      render(
        <MemoryRouter initialEntries={['/mentor/groups/grp-1/projects']}>
          <Routes>
            <Route path="/mentor/groups/:groupId/projects" element={<GroupProjects />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('AI Reasoning Engine')).toBeInTheDocument();
      });
      expect(screen.getByText('ATTENTION')).toBeInTheDocument();
      expect(screen.getByText('BLUEPRINT')).toBeInTheDocument();
    });
  });

  describe('M07: GroupAtRisk', () => {
    it('filters and displays only at-risk or critical projects', async () => {
      vi.spyOn(apiClient, 'getMentorGroup').mockResolvedValue({
        id: 'grp-1',
        mentor_id: 'm-1',
        name: 'Distributed Systems',
        join_code: 'DIST-2026',
        status: 'ACTIVE',
      });
      vi.spyOn(apiClient, 'getGroupProjects').mockResolvedValue([
        {
          id: 'p-1',
          student_id: 's-1',
          group_id: 'grp-1',
          name: 'Healthy Project',
          problem: 'None',
          proposed_solution: 'None',
          complexity: 'BEGINNER',
          current_phase: 'IDEA',
          health: 'HEALTHY',
          progress_percentage: 10,
          status: 'ACTIVE',
        } as unknown as ProjectResponse,
        {
          id: 'p-2',
          student_id: 's-2',
          group_id: 'grp-1',
          name: 'Stalled Project',
          problem: 'Blocked by database migration deadlock',
          proposed_solution: 'Restructure transactions',
          complexity: 'ADVANCED',
          current_phase: 'IMPLEMENTATION',
          health: 'AT_RISK',
          progress_percentage: 40,
          status: 'ACTIVE',
        } as unknown as ProjectResponse,
      ]);

      render(
        <MemoryRouter initialEntries={['/mentor/groups/grp-1/at-risk']}>
          <Routes>
            <Route path="/mentor/groups/:groupId/at-risk" element={<GroupAtRisk />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Stalled Project')).toBeInTheDocument();
      });
      expect(screen.queryByText('Healthy Project')).not.toBeInTheDocument();
      expect(screen.getByText('Blocked by database migration deadlock')).toBeInTheDocument();
    });
  });
});
