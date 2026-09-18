import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue, UserRole } from '@/auth/types';
import type { User } from '@supabase/supabase-js';

import { ProtectedRoute } from '@/auth/ProtectedRoute';
import { Sidebar as StudentSidebar } from '@/components/navigation/Sidebar';
import { MentorSidebar } from '@/components/navigation/MentorSidebar';
import { AdminSidebar } from '@/components/navigation/AdminSidebar';
import { AdminOverview } from '@/pages/Admin/AdminOverview/AdminOverview';
import { MentorDirectory } from '@/pages/Admin/MentorDirectory/MentorDirectory';
import { MentorDetail } from '@/pages/Admin/MentorDetail/MentorDetail';
import { StudentDirectory } from '@/pages/Admin/StudentDirectory/StudentDirectory';
import { StudentDetail } from '@/pages/Admin/StudentDetail/StudentDetail';
import { LifecycleTrack } from '@/pages/Student/StudentDashboard/components/LifecycleTrack';
import * as apiClient from '@/lib/api/client';
import type {
  AdminOverviewResponse,
  AdminMentorSummary,
  AdminMentorDetail,
  AdminStudentSummary,
  AdminStudentDetail,
} from '@/lib/api/types';

function createMockAuth(
  role: UserRole = 'ADMIN',
  fullName = 'Administrator',
  email = 'admin@growflow.ai'
): AuthContextValue {
  return {
    status: 'AUTHENTICATED',
    session: {
      access_token: 'mock-token',
      refresh_token: 'mock-refresh',
      expires_in: 3600,
      token_type: 'bearer',
      user: { id: 'usr-admin-1', email } as unknown as User,
    },
    supabaseUser: { id: 'usr-admin-1', email } as unknown as User,
    user: {
      id: 'usr-admin-1',
      email,
      role,
      status: 'ACTIVE',
      fullName,
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

const mockOverview: AdminOverviewResponse = {
  total_mentors: 14,
  active_mentors: 12,
  total_students: 180,
  active_students: 155,
  total_groups: 10,
  active_groups: 9,
  total_projects: 120,
  active_projects: 40,
  completed_projects: 75,
  at_risk_projects: 5,
};

const mockMentors: AdminMentorSummary[] = [
  {
    id: 'm-1',
    email: 'dr.smith@growflow.ai',
    full_name: 'Dr. Jane Smith',
    role: 'MENTOR',
    status: 'ACTIVE',
    designation: 'Principal Architect',
    organization: 'Tech Labs',
    specialization: 'Distributed Systems',
    group_count: 2,
    student_count: 24,
    project_count: 15,
    created_at: '2026-01-01T00:00:00Z',
  },
];

const mockMentorDetail: AdminMentorDetail = {
  id: 'm-1',
  email: 'dr.smith@growflow.ai',
  full_name: 'Dr. Jane Smith',
  role: 'MENTOR',
  status: 'ACTIVE',
  mentor_id: 'MNT-001',
  designation: 'Principal Architect',
  organization: 'Tech Labs',
  bio: 'Expert in cloud scale infrastructure',
  specialization: 'Distributed Systems',
  skills: ['Go', 'Kubernetes', 'PostgreSQL'],
  max_students: 30,
  is_accepting_students: true,
  created_at: '2026-01-01T00:00:00Z',
  groups: [
    {
      id: 'g-1',
      name: 'Distributed Cloud 2026',
      join_code: 'DIST26',
      status: 'ACTIVE',
      student_count: 14,
      project_count: 8,
      created_at: '2026-01-10T00:00:00Z',
    },
  ],
  supervised_students: [
    {
      id: 's-1',
      full_name: 'John Doe',
      email: 'john@example.com',
      group_name: 'Distributed Cloud 2026',
      active_projects_count: 1,
    },
  ],
};

const mockStudents: AdminStudentSummary[] = [
  {
    id: 's-1',
    email: 'john@example.com',
    full_name: 'John Doe',
    role: 'STUDENT',
    status: 'ACTIVE',
    student_id: 'STU-101',
    college: 'Engineering Institute',
    branch: 'Computer Science',
    year_of_study: 3,
    primary_track: 'Full-Stack Web Development',
    group_count: 1,
    project_count: 2,
    active_project_count: 1,
    at_risk_project_count: 0,
    created_at: '2026-01-05T00:00:00Z',
  },
];

const mockStudentDetail: AdminStudentDetail = {
  id: 's-1',
  email: 'john@example.com',
  full_name: 'John Doe',
  role: 'STUDENT',
  status: 'ACTIVE',
  student_id: 'STU-101',
  college: 'Engineering Institute',
  branch: 'Computer Science',
  year_of_study: 3,
  bio: 'Building full-stack web applications',
  primary_track: 'Full-Stack Web Development',
  technologies: [
    { technology_id: 't-1', technology_name: 'React', proficiency_level: 'ADVANCED' },
    { technology_id: 't-2', technology_name: 'Python', proficiency_level: 'EXPERT' },
  ],
  created_at: '2026-01-05T00:00:00Z',
  groups: [
    {
      group_id: 'g-1',
      group_name: 'Distributed Cloud 2026',
      mentor_name: 'Dr. Jane Smith',
      status: 'ACTIVE',
      joined_at: '2026-01-10T00:00:00Z',
    },
  ],
  projects: [
    {
      id: 'p-1',
      name: 'Cloud Telemetry Pipeline',
      track: 'Full-Stack Web Development',
      current_phase: 'IMPLEMENTATION',
      health: 'HEALTHY',
      progress_percentage: 60,
      status: 'ACTIVE',
      created_at: '2026-01-15T00:00:00Z',
    },
  ],
};

describe('GrowFlow Phase 7 Batch 7 Part 1 — Admin Foundation & People Governance', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  // -------------------------------------------------------------------------
  // 1. Authorization & Route Protection
  // -------------------------------------------------------------------------
  describe('Admin Route Protection (ProtectedRoute)', () => {
    it('blocks authenticated STUDENT from Admin workspace with 403 Forbidden', () => {
      const studentAuth = createMockAuth('STUDENT', 'Student Alice', 'alice@growflow.ai');

      render(
        <AuthContext.Provider value={studentAuth}>
          <MemoryRouter initialEntries={['/admin/overview']}>
            <Routes>
              <Route
                element={
                  <ProtectedRoute requiredRole="ADMIN" loginPath="/auth/admin/sign-in">
                    <div>Admin Protected View</div>
                  </ProtectedRoute>
                }
              >
                <Route path="/admin/overview" element={<div>Admin Protected View</div>} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.queryByText('Admin Protected View')).not.toBeInTheDocument();
      expect(screen.getByText('Access Restricted')).toBeInTheDocument();
      expect(screen.getByText(/This workspace is designated for ADMIN accounts/i)).toBeInTheDocument();
      expect(screen.getByText(/currently authorized as STUDENT/i)).toBeInTheDocument();
    });

    it('blocks authenticated MENTOR from Admin workspace with 403 Forbidden', () => {
      const mentorAuth = createMockAuth('MENTOR', 'Dr. Elena Vance', 'elena@growflow.ai');

      render(
        <AuthContext.Provider value={mentorAuth}>
          <MemoryRouter initialEntries={['/admin/overview']}>
            <Routes>
              <Route
                element={
                  <ProtectedRoute requiredRole="ADMIN" loginPath="/auth/admin/sign-in">
                    <div>Admin Protected View</div>
                  </ProtectedRoute>
                }
              >
                <Route path="/admin/overview" element={<div>Admin Protected View</div>} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.queryByText('Admin Protected View')).not.toBeInTheDocument();
      expect(screen.getByText('Access Restricted')).toBeInTheDocument();
      expect(screen.getByText(/This workspace is designated for ADMIN accounts/i)).toBeInTheDocument();
      expect(screen.getByText(/currently authorized as MENTOR/i)).toBeInTheDocument();
    });

    it('allows authenticated ADMIN through to Admin workspace', () => {
      const adminAuth = createMockAuth('ADMIN', 'Admin Root', 'root@growflow.ai');

      render(
        <AuthContext.Provider value={adminAuth}>
          <MemoryRouter initialEntries={['/admin/overview']}>
            <Routes>
              <Route
                element={
                  <ProtectedRoute requiredRole="ADMIN" loginPath="/auth/admin/sign-in">
                    <div>Admin Protected Content Available</div>
                  </ProtectedRoute>
                }
              >
                <Route path="/admin/overview" element={<div>Admin Protected Content Available</div>} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByText('Admin Protected Content Available')).toBeInTheDocument();
    });
  });

  // -------------------------------------------------------------------------
  // 2. Global Collapsed Sidebar Hover & Click Expansion
  // -------------------------------------------------------------------------
  describe('Global Collapsed Sidebar Hover & Click Expansion', () => {
    it('handles hover expansion and click expansion on Student Sidebar', () => {
      const onToggle = vi.fn();
      const auth = createMockAuth('STUDENT');

      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <StudentSidebar isCollapsed={true} onToggleCollapse={onToggle} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const sidebar = screen.getByLabelText('Student Workspace Navigation');
      expect(sidebar.className).toContain('gf-sidebar--collapsed');

      // Hover expansion
      fireEvent.mouseEnter(sidebar);
      expect(sidebar.className).toContain('gf-sidebar--hover-expanded');

      fireEvent.mouseLeave(sidebar);
      expect(sidebar.className).not.toContain('gf-sidebar--hover-expanded');

      // Click on collapsed rail background triggers expansion
      fireEvent.click(sidebar);
      expect(onToggle).toHaveBeenCalledTimes(1);
    });

    it('handles hover expansion and click expansion on Mentor Sidebar', () => {
      const onToggle = vi.fn();
      const auth = createMockAuth('MENTOR');

      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <MentorSidebar isCollapsed={true} onToggleCollapse={onToggle} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const sidebar = screen.getByLabelText('Mentor Supervise Navigation');
      expect(sidebar.className).toContain('gf-mentor-sidebar--collapsed');

      // Hover expansion
      fireEvent.mouseEnter(sidebar);
      expect(sidebar.className).toContain('gf-mentor-sidebar--hover-expanded');

      fireEvent.mouseLeave(sidebar);
      expect(sidebar.className).not.toContain('gf-mentor-sidebar--hover-expanded');

      // Click on rail background
      fireEvent.click(sidebar);
      expect(onToggle).toHaveBeenCalledTimes(1);
    });

    it('handles hover expansion and click expansion on Admin Sidebar', () => {
      const onToggle = vi.fn();
      const auth = createMockAuth('ADMIN');

      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <AdminSidebar isCollapsed={true} onToggleCollapse={onToggle} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const sidebar = screen.getByLabelText('Admin Governance Navigation');
      expect(sidebar.className).toContain('gf-admin-sidebar--collapsed');

      // Hover expansion
      fireEvent.mouseEnter(sidebar);
      expect(sidebar.className).toContain('gf-admin-sidebar--hover-expanded');

      fireEvent.mouseLeave(sidebar);
      expect(sidebar.className).not.toContain('gf-admin-sidebar--hover-expanded');

      // Click on rail background
      fireEvent.click(sidebar);
      expect(onToggle).toHaveBeenCalledTimes(1);
    });
  });

  // -------------------------------------------------------------------------
  // 3. AD01 — Admin Overview
  // -------------------------------------------------------------------------
  describe('AD01 — Admin Overview View', () => {
    it('loads and renders platform metrics', async () => {
      vi.spyOn(apiClient, 'getAdminOverview').mockResolvedValue(mockOverview);
      const auth = createMockAuth('ADMIN');

      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <AdminOverview />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Platform Overview')).toBeInTheDocument();
        expect(screen.getByText('14')).toBeInTheDocument(); // total mentors
        expect(screen.getByText('180')).toBeInTheDocument(); // total students
        expect(screen.getByText('12 active accounts')).toBeInTheDocument();
        expect(screen.getByText('5 At Risk')).toBeInTheDocument();
      });
    });
  });

  // -------------------------------------------------------------------------
  // 4. AD02 — Mentor Directory
  // -------------------------------------------------------------------------
  describe('AD02 — Mentor Directory View', () => {
    it('loads and renders mentor directory list with search', async () => {
      vi.spyOn(apiClient, 'getAdminMentors').mockResolvedValue(mockMentors);
      const auth = createMockAuth('ADMIN');

      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <MentorDirectory />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Mentor Directory')).toBeInTheDocument();
        expect(screen.getByText('Dr. Jane Smith')).toBeInTheDocument();
        expect(screen.getByText('Distributed Systems')).toBeInTheDocument();
        expect(screen.getByText('2 cohorts')).toBeInTheDocument();
        expect(screen.getByText('24 students')).toBeInTheDocument();
      });
    });
  });

  // -------------------------------------------------------------------------
  // 5. AD03 — Mentor Detail
  // -------------------------------------------------------------------------
  describe('AD03 — Mentor Detail View', () => {
    it('loads and renders mentor details, cohorts, and supervised students', async () => {
      vi.spyOn(apiClient, 'getAdminMentor').mockResolvedValue(mockMentorDetail);
      const auth = createMockAuth('ADMIN');

      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter initialEntries={['/admin/mentors/m-1']}>
            <Routes>
              <Route path="/admin/mentors/:mentorId" element={<MentorDetail />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Dr. Jane Smith' })).toBeInTheDocument();
        expect(screen.getByText('MNT-001')).toBeInTheDocument();
        expect(screen.getAllByText('Distributed Cloud 2026').length).toBeGreaterThanOrEqual(1);
        expect(screen.getByText('DIST26')).toBeInTheDocument();
        expect(screen.getByText('John Doe')).toBeInTheDocument();
      });
    });
  });

  // -------------------------------------------------------------------------
  // 6. AD04 — Student Directory
  // -------------------------------------------------------------------------
  describe('AD04 — Student Directory View', () => {
    it('loads and renders student directory list', async () => {
      vi.spyOn(apiClient, 'getAdminStudents').mockResolvedValue(mockStudents);
      const auth = createMockAuth('ADMIN');

      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter>
            <StudentDirectory />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Student Directory')).toBeInTheDocument();
        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.getByText('Engineering Institute')).toBeInTheDocument();
        expect(screen.getByText('1 cohorts')).toBeInTheDocument();
        expect(screen.getByText('1 active')).toBeInTheDocument();
      });
    });
  });

  // -------------------------------------------------------------------------
  // 7. AD05 — Student Detail
  // -------------------------------------------------------------------------
  describe('AD05 — Student Detail View', () => {
    it('loads and renders student details, academic info, and project instances', async () => {
      vi.spyOn(apiClient, 'getAdminStudent').mockResolvedValue(mockStudentDetail);
      const auth = createMockAuth('ADMIN');

      render(
        <AuthContext.Provider value={auth}>
          <MemoryRouter initialEntries={['/admin/students/s-1']}>
            <Routes>
              <Route path="/admin/students/:studentId" element={<StudentDetail />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.getByText('STU-101')).toBeInTheDocument();
        expect(screen.getByText('Cloud Telemetry Pipeline')).toBeInTheDocument();
        expect(screen.getByText('60%')).toBeInTheDocument();
      });
    });
  });

  // -------------------------------------------------------------------------
  // 8. Student Dashboard Lifecycle Spacing
  // -------------------------------------------------------------------------
  describe('Student Dashboard Lifecycle Spacing', () => {
    it('renders all 8 canonical lifecycle stages with clean labels', () => {
      render(
        <MemoryRouter>
          <LifecycleTrack currentPhase="IMPLEMENTATION" />
        </MemoryRouter>
      );

      expect(screen.getByText('LIFECYCLE POSITION')).toBeInTheDocument();
      expect(screen.getByText('Idea')).toBeInTheDocument();
      expect(screen.getByText('Assessment')).toBeInTheDocument();
      expect(screen.getByText('Blueprint')).toBeInTheDocument();
      expect(screen.getByText('Planning')).toBeInTheDocument();
      expect(screen.getByText('Implementation')).toBeInTheDocument();
      expect(screen.getByText('Testing')).toBeInTheDocument();
      expect(screen.getByText('Deployment')).toBeInTheDocument();
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });
  });
});
