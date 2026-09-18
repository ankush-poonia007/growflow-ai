import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import type { User } from '@supabase/supabase-js';

import { StudentsDirectory } from '@/pages/Mentor/StudentsDirectory/StudentsDirectory';
import { StudentDetail } from '@/pages/Mentor/StudentDetail/StudentDetail';
import { StudentProjects } from '@/pages/Mentor/StudentProjects/StudentProjects';
import { MentorProjectsDirectory } from '@/pages/Mentor/InstancesDirectory/MentorProjectsDirectory';
import { ProjectInstances } from '@/pages/Mentor/ProjectInstances/ProjectInstances';
import { ProjectInstanceDetail } from '@/pages/Mentor/ProjectInstanceDetail/ProjectInstanceDetail';
import { AtRiskDirectory } from '@/pages/Mentor/AtRiskDirectory/AtRiskDirectory';
import { AtRiskDetail } from '@/pages/Mentor/AtRiskDetail/AtRiskDetail';
import * as apiClient from '@/lib/api/client';
import type {
  MentorStudentSummary,
  MentorStudentDetail,
  MentorProjectInstanceSummary,
  MentorProjectInstanceDetail,
  GroupResponse,
} from '@/lib/api/types';

function createMockAuth(role: 'STUDENT' | 'MENTOR' | 'ADMIN' = 'MENTOR'): AuthContextValue {
  return {
    status: 'AUTHENTICATED',
    session: {
      access_token: 'mock-token',
      refresh_token: 'mock-refresh',
      expires_in: 3600,
      token_type: 'bearer',
      user: { id: 'mentor-1', email: 'mentor@example.com' } as unknown as User,
    },
    supabaseUser: { id: 'mentor-1', email: 'mentor@example.com' } as unknown as User,
    user: {
      id: 'mentor-1',
      email: 'mentor@example.com',
      role,
      status: 'ACTIVE',
      fullName: 'Dr. Evelyn Mentor',
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

describe('Phase 7 Batch 3: Mentor Supervision Directories (M10, M11, M12, M16, M22, M23, M31, M32)', () => {
  const mockGroups: GroupResponse[] = [
    {
      id: 'grp-1',
      mentor_id: 'mentor-1',
      name: 'AgriTech Cohort 2026',
      join_code: 'AGRI-2026',
      status: 'ACTIVE',
      created_at: '2026-09-01T10:00:00Z',
    },
  ];

  const mockStudents: MentorStudentSummary[] = [
    {
      id: 'student-1',
      full_name: 'Alice Student',
      email: 'alice@student.test',
      avatar_url: null,
      group_count: 1,
      groups: [{ id: 'grp-1', name: 'AgriTech Cohort 2026', joined_at: '2026-09-02T10:00:00Z' }],
      project_count: 2,
      at_risk_project_count: 0,
      created_at: '2026-09-02T10:00:00Z',
    },
    {
      id: 'student-2',
      full_name: 'Bob AtRisk',
      email: 'bob@student.test',
      avatar_url: null,
      group_count: 1,
      groups: [{ id: 'grp-1', name: 'AgriTech Cohort 2026', joined_at: '2026-09-02T10:00:00Z' }],
      project_count: 1,
      at_risk_project_count: 1,
      created_at: '2026-09-02T10:00:00Z',
    },
  ];

  const mockProject1: MentorProjectInstanceSummary = {
    id: 'proj-1',
    name: 'Autonomous Crop Drone',
    student_id: 'student-1',
    student_name: 'Alice Student',
    student_email: 'alice@student.test',
    group_id: 'grp-1',
    group_name: 'AgriTech Cohort 2026',
    current_phase: 'IMPLEMENTATION',
    health: 'HEALTHY',
    progress_percentage: 65,
    status: 'ACTIVE',
    deadline: '2026-12-01T00:00:00Z',
    source_definition_id: 'def-1',
    source_definition_name: 'Drone Template',
    source_definition_version_number: 1,
    created_at: '2026-09-03T10:00:00Z',
    updated_at: '2026-09-10T10:00:00Z',
  };

  const mockProjectAtRisk: MentorProjectInstanceSummary = {
    id: 'proj-2',
    name: 'Failing Irrigation Controller',
    student_id: 'student-2',
    student_name: 'Bob AtRisk',
    student_email: 'bob@student.test',
    group_id: 'grp-1',
    group_name: 'AgriTech Cohort 2026',
    current_phase: 'ASSESSMENT',
    health: 'CRITICAL',
    progress_percentage: 15,
    status: 'ACTIVE',
    deadline: '2026-10-01T00:00:00Z',
    source_definition_id: null,
    source_definition_name: null,
    source_definition_version_number: null,
    created_at: '2026-09-03T10:00:00Z',
    updated_at: '2026-09-12T10:00:00Z',
  };

  const mockStudentDetail: MentorStudentDetail = {
    id: 'student-1',
    full_name: 'Alice Student',
    email: 'alice@student.test',
    avatar_url: null,
    bio: 'Robotics and telemetry researcher',
    skills: ['ROS2', 'Python', 'Computer Vision'],
    group_count: 1,
    groups: [{ id: 'grp-1', name: 'AgriTech Cohort 2026', joined_at: '2026-09-02T10:00:00Z' }],
    project_count: 1,
    at_risk_project_count: 0,
    created_at: '2026-09-02T10:00:00Z',
    projects: [mockProject1],
  };

  const mockProjectDetail: MentorProjectInstanceDetail = {
    ...mockProject1,
    problem: 'Crop pest tracking requires manual inspection',
    proposed_solution: 'Automated UAV multispectral scanning',
    complexity: 'ADVANCED',
    source_definition_version_id: 'ver-1',
    source_definition_version_summary: 'Initial specification with PX4 autopilot and 12-week schedule',
    student_bio: 'Robotics and telemetry researcher',
    student_skills: ['ROS2', 'Python', 'Computer Vision'],
  };

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  // --------------------------------------------------------------------------
  // Surface M10: StudentsDirectory (/mentor/students)
  // --------------------------------------------------------------------------
  describe('M10: Mentor Students Directory', () => {
    it('renders supervised students and metrics correctly', async () => {
      vi.spyOn(apiClient, 'getMentorStudents').mockResolvedValue(mockStudents);
      vi.spyOn(apiClient, 'getMentorGroups').mockResolvedValue(mockGroups);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/students']}>
            <Routes>
              <Route path="/mentor/students" element={<StudentsDirectory />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Alice Student')).toBeInTheDocument();
        expect(screen.getByText('Bob AtRisk')).toBeInTheDocument();
      });

      expect(document.getElementById('stat-total-students')?.textContent).toContain('2');
      expect(screen.getByText('1 At Risk')).toBeInTheDocument(); // Bob's risk badge
      expect(screen.getByText('All Healthy')).toBeInTheDocument(); // Alice's health badge

      // Guardrail 8: Read-Only verification - no mutation buttons
      expect(screen.queryByRole('button', { name: /delete/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /edit student/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /remove/i })).not.toBeInTheDocument();
    });

    it('filters students by search input', async () => {
      const getStudentsMock = vi
        .spyOn(apiClient, 'getMentorStudents')
        .mockResolvedValue([mockStudents[0]!]);
      vi.spyOn(apiClient, 'getMentorGroups').mockResolvedValue(mockGroups);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/students']}>
            <Routes>
              <Route path="/mentor/students" element={<StudentsDirectory />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const searchInput = screen.getByPlaceholderText(/search by student name/i);
      fireEvent.change(searchInput, { target: { value: 'Alice' } });

      await waitFor(() => {
        expect(getStudentsMock).toHaveBeenCalledWith(
          expect.objectContaining({ search: 'Alice' })
        );
      });
    });
  });

  // --------------------------------------------------------------------------
  // Surface M11: StudentDetail (/mentor/students/:studentId)
  // --------------------------------------------------------------------------
  describe('M11: Student Detail', () => {
    it('renders read-only student details with skills, cohort, and projects', async () => {
      vi.spyOn(apiClient, 'getMentorStudent').mockResolvedValue(mockStudentDetail);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/students/student-1']}>
            <Routes>
              <Route path="/mentor/students/:studentId" element={<StudentDetail />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getAllByText('Alice Student').length).toBeGreaterThan(0);
        expect(screen.getByText('alice@student.test')).toBeInTheDocument();
        expect(screen.getByText('Robotics and telemetry researcher')).toBeInTheDocument();
        expect(screen.getByText('ROS2')).toBeInTheDocument();
        expect(screen.getByText('Autonomous Crop Drone')).toBeInTheDocument();
      });

      // Guardrail 8: Read-Only verification
      expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /delete/i })).not.toBeInTheDocument();
    });

    it('renders 403 / 404 supervision restriction state gracefully', async () => {
      vi.spyOn(apiClient, 'getMentorStudent').mockRejectedValue(
        new Error('Access denied. Student is not enrolled in your cohorts.')
      );

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/students/student-foreign']}>
            <Routes>
              <Route path="/mentor/students/:studentId" element={<StudentDetail />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Supervision Access Restriction')).toBeInTheDocument();
      });
    });
  });

  // --------------------------------------------------------------------------
  // Surface M12: StudentProjects (/mentor/students/:studentId/projects)
  // --------------------------------------------------------------------------
  describe('M12: Student Projects', () => {
    it('renders dedicated view of supervised student projects', async () => {
      vi.spyOn(apiClient, 'getMentorStudentProjects').mockResolvedValue([mockProject1]);
      vi.spyOn(apiClient, 'getMentorStudent').mockResolvedValue(mockStudentDetail);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/students/student-1/projects']}>
            <Routes>
              <Route
                path="/mentor/students/:studentId/projects"
                element={<StudentProjects />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText("Alice Student's Projects")).toBeInTheDocument();
        expect(screen.getByText('Autonomous Crop Drone')).toBeInTheDocument();
        expect(screen.getByText('IMPLEMENTATION')).toBeInTheDocument();
        expect(screen.getByText('65%')).toBeInTheDocument();
      });

      // Guardrail 8: Read-Only verification
      expect(screen.queryByRole('button', { name: /transition/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /create project/i })).not.toBeInTheDocument();
    });
  });

  // --------------------------------------------------------------------------
  // Surface M16: MentorProjectsDirectory (/mentor/projects/instances)
  // --------------------------------------------------------------------------
  describe('M16: Mentor Projects Directory', () => {
    it('renders project instances table on distinct route /mentor/projects/instances', async () => {
      vi.spyOn(apiClient, 'getMentorProjects').mockResolvedValue([mockProject1, mockProjectAtRisk]);
      vi.spyOn(apiClient, 'getMentorGroups').mockResolvedValue(mockGroups);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/projects/instances']}>
            <Routes>
              <Route
                path="/mentor/projects/instances"
                element={<MentorProjectsDirectory />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Autonomous Crop Drone')).toBeInTheDocument();
        expect(screen.getByText('Failing Irrigation Controller')).toBeInTheDocument();
      });

      // Pinned version display verification
      expect(screen.getByText(/Drone Template/i)).toBeInTheDocument();
      expect(screen.getByText('v1')).toBeInTheDocument();

      // Guardrail 8: Read-only
      expect(screen.queryByRole('button', { name: /new project/i })).not.toBeInTheDocument();
    });
  });

  // --------------------------------------------------------------------------
  // Surface M22: ProjectInstances (/mentor/project-instances)
  // --------------------------------------------------------------------------
  describe('M22: Student Project Instances Monitoring', () => {
    it('renders operational monitoring dashboard with health metrics', async () => {
      vi.spyOn(apiClient, 'getMentorProjectInstances').mockResolvedValue([
        mockProject1,
        mockProjectAtRisk,
      ]);
      vi.spyOn(apiClient, 'getMentorGroups').mockResolvedValue(mockGroups);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/project-instances']}>
            <Routes>
              <Route path="/mentor/project-instances" element={<ProjectInstances />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Autonomous Crop Drone')).toBeInTheDocument();
      });

      expect(document.getElementById('metric-total-instances')?.textContent).toContain('2');
      expect(document.getElementById('metric-healthy-instances')?.textContent).toContain('1');
      expect(document.getElementById('metric-critical-instances')?.textContent).toContain('1');
      expect(screen.getByText('Autonomous Crop Drone')).toBeInTheDocument();
      expect(screen.getByText('Failing Irrigation Controller')).toBeInTheDocument();

      // Guardrail 8: Read-only
      expect(screen.queryByRole('button', { name: /delete/i })).not.toBeInTheDocument();
    });
  });

  // --------------------------------------------------------------------------
  // Surface M23: ProjectInstanceDetail (/mentor/project-instances/:projectId)
  // --------------------------------------------------------------------------
  describe('M23: Project Instance Detail', () => {
    it('renders in-depth project inspection with pinned version snapshot', async () => {
      vi.spyOn(apiClient, 'getMentorProjectInstance').mockResolvedValue(mockProjectDetail);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-1']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId"
                element={<ProjectInstanceDetail />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getAllByText('Autonomous Crop Drone').length).toBeGreaterThan(0);
      });

      // Problem and solution
      expect(screen.getByText('Crop pest tracking requires manual inspection')).toBeInTheDocument();
      expect(screen.getByText('Automated UAV multispectral scanning')).toBeInTheDocument();

      // Guardrail 16: Pinned ProjectDefinitionVersion verification
      expect(screen.getByText('Pinned Project Definition & Version')).toBeInTheDocument();
      expect(screen.getByText('Drone Template')).toBeInTheDocument();
      expect(screen.getAllByText('Pinned v1').length).toBeGreaterThanOrEqual(1);
      expect(
        screen.getByText('Initial specification with PX4 autopilot and 12-week schedule')
      ).toBeInTheDocument();

      // Student info
      expect(screen.getAllByText('Alice Student').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/alice@student\.test/i).length).toBeGreaterThanOrEqual(1);

      // Guardrail 8: Read-Only verification - no mutation controls
      expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /delete/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /approve/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /regenerate/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /sync github/i })).not.toBeInTheDocument();
    });
  });

  // --------------------------------------------------------------------------
  // Surface M31: AtRiskDirectory (/mentor/at-risk)
  // --------------------------------------------------------------------------
  describe('M31: Global At-Risk Directory', () => {
    it('renders WARNING and CRITICAL projects only', async () => {
      vi.spyOn(apiClient, 'getMentorAtRiskProjects').mockResolvedValue([mockProjectAtRisk]);
      vi.spyOn(apiClient, 'getMentorGroups').mockResolvedValue(mockGroups);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/at-risk']}>
            <Routes>
              <Route path="/mentor/at-risk" element={<AtRiskDirectory />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Failing Irrigation Controller')).toBeInTheDocument();
      });

      // Critical count
      expect(screen.getByText('Critical Standing')).toBeInTheDocument();
      expect(screen.getByText('CRITICAL')).toBeInTheDocument();

      // Guardrail 17: Healthy projects must never appear in at-risk directory
      expect(screen.queryByText('Autonomous Crop Drone')).not.toBeInTheDocument();

      // Guardrail 8: Read-only
      expect(screen.queryByRole('button', { name: /override/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /resolve/i })).not.toBeInTheDocument();
    });
  });

  // --------------------------------------------------------------------------
  // Surface M32: AtRiskDetail (/mentor/at-risk/:projectId)
  // --------------------------------------------------------------------------
  describe('M32: Global At-Risk Detail', () => {
    it('renders risk alert banner and supervision guidance', async () => {
      const atRiskDetail: MentorProjectInstanceDetail = {
        ...mockProjectDetail,
        id: 'proj-2',
        name: 'Failing Irrigation Controller',
        health: 'CRITICAL',
        progress_percentage: 15,
      };

      vi.spyOn(apiClient, 'getMentorAtRiskProject').mockResolvedValue(atRiskDetail);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/at-risk/proj-2']}>
            <Routes>
              <Route path="/mentor/at-risk/:projectId" element={<AtRiskDetail />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(
          screen.getByText('At-Risk Inspection: Failing Irrigation Controller')
        ).toBeInTheDocument();
      });

      // Risk banner
      expect(screen.getByText(/Standing: CRITICAL \(15% Progress\)/i)).toBeInTheDocument();
      expect(
        screen.getByText(/Critical project standing requires urgent mentor intervention/i)
      ).toBeInTheDocument();

      // Guardrail 8: Read-Only verification
      expect(screen.queryByRole('button', { name: /mark healthy/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /delete/i })).not.toBeInTheDocument();
    });
  });
});
