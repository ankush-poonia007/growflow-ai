import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import type { User } from '@supabase/supabase-js';

import { ProjectsDirectory } from '@/pages/Mentor/ProjectsDirectory/ProjectsDirectory';
import { DefinitionDetail } from '@/pages/Mentor/DefinitionDetail/DefinitionDetail';
import { DefinitionCreate } from '@/pages/Mentor/DefinitionCreate/DefinitionCreate';
import { DefinitionEdit } from '@/pages/Mentor/DefinitionEdit/DefinitionEdit';
import { DefinitionAssign } from '@/pages/Mentor/DefinitionAssign/DefinitionAssign';
import { NotFound } from '@/pages/NotFound/NotFound';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import * as apiClient from '@/lib/api/client';
import type { ProjectDefinition, ProjectDefinitionVersion, GroupResponse, GroupStudentResponse, ProjectResponse } from '@/lib/api/types';

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

describe('Phase 7 Batch 2: Mentor Project Definitions & Versioned Assignment', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  const mockVersion1: ProjectDefinitionVersion = {
    id: 'ver-1',
    project_definition_id: 'def-1',
    version_number: 1,
    name: 'Precision Agriculture Drone',
    problem: 'Crop telemetry latency in rural farmland',
    proposed_solution: 'Autonomous fixed-wing UAV with multispectral camera',
    complexity: 'ADVANCED',
    description: 'Design and simulate an automated crop survey drone.',
    duration: '12 weeks',
    constraints: 'Budget limit $800',
    assumptions: 'GPS available',
    technology_snapshot: [{ name: 'PX4' }, { name: 'ROS2' }],
    created_by: 'mentor-1',
    created_at: '2026-09-01T10:00:00Z',
  };

  const mockVersion2: ProjectDefinitionVersion = {
    id: 'ver-2',
    project_definition_id: 'def-1',
    version_number: 2,
    name: 'Precision Agriculture Drone Gen-2',
    problem: 'Crop telemetry latency in rural farmland with adverse weather',
    proposed_solution: 'Autonomous hybrid UAV with satellite uplink',
    complexity: 'ADVANCED',
    description: 'Updated industrial-grade rover template.',
    duration: '16 weeks',
    constraints: 'Budget limit $1200',
    assumptions: 'Satellite link permitted',
    technology_snapshot: [{ name: 'PX4' }, { name: 'Iridium' }],
    created_by: 'mentor-1',
    created_at: '2026-09-13T12:00:00Z',
  };

  const mockDefinition: ProjectDefinition = {
    id: 'def-1',
    owner_mentor_id: 'user-1',
    name: 'Precision Agriculture Drone',
    status: 'ACTIVE',
    current_version_id: 'ver-1',
    current_version: mockVersion1,
    created_at: '2026-09-01T10:00:00Z',
    updated_at: '2026-09-10T14:30:00Z',
  };

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe('M17: ProjectsDirectory (/mentor/projects)', () => {
    it('renders definition cards with version, complexity, and status badges', async () => {
      vi.spyOn(apiClient, 'getMentorDefinitions').mockResolvedValueOnce([mockDefinition]);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter>
            <ProjectsDirectory />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      // Loading state
      expect(screen.getByRole('main')).toHaveAttribute('aria-busy', 'true');

      // Loaded state
      await waitFor(() => {
        expect(screen.getByText('Precision Agriculture Drone')).toBeInTheDocument();
      });

      expect(screen.getByText('v1')).toBeInTheDocument();
      expect(screen.getByText('ADVANCED')).toBeInTheDocument();
      expect(screen.getByText('ACTIVE')).toBeInTheDocument();
      expect(screen.getByText('Crop telemetry latency in rural farmland')).toBeInTheDocument();
      expect(screen.getByText('View Detail')).toBeInTheDocument();
      expect(screen.getByText('Assign')).toBeInTheDocument();
    });

    it('filters definitions by search query and complexity', async () => {
      const def2: ProjectDefinition = {
        id: 'def-2',
        owner_mentor_id: 'user-1',
        name: 'Basic Weather Station',
        status: 'ACTIVE',
        current_version_id: 'ver-2',
        current_version: {
          ...mockVersion1,
          id: 'ver-2',
          name: 'Basic Weather Station',
          complexity: 'BEGINNER',
          problem: 'Localized weather tracking',
        },
      };

      vi.spyOn(apiClient, 'getMentorDefinitions').mockResolvedValueOnce([mockDefinition, def2]);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter>
            <ProjectsDirectory />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Precision Agriculture Drone')).toBeInTheDocument();
        expect(screen.getByText('Basic Weather Station')).toBeInTheDocument();
      });

      // Filter by search
      const searchInput = screen.getByLabelText('Filter project definitions');
      fireEvent.change(searchInput, { target: { value: 'Weather' } });

      expect(screen.queryByText('Precision Agriculture Drone')).not.toBeInTheDocument();
      expect(screen.getByText('Basic Weather Station')).toBeInTheDocument();

      // Reset search and filter by complexity
      fireEvent.change(searchInput, { target: { value: '' } });
      const complexitySelect = screen.getByLabelText('Filter by complexity');
      fireEvent.change(complexitySelect, { target: { value: 'ADVANCED' } });

      expect(screen.getByText('Precision Agriculture Drone')).toBeInTheDocument();
      expect(screen.queryByText('Basic Weather Station')).not.toBeInTheDocument();
    });

    it('renders truthful empty state when no definitions exist', async () => {
      vi.spyOn(apiClient, 'getMentorDefinitions').mockResolvedValueOnce([]);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter>
            <ProjectsDirectory />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('No project definitions yet')).toBeInTheDocument();
        expect(screen.getByText('Create First Definition')).toBeInTheDocument();
      });
    });

    it('renders error state with retry on failure', async () => {
      vi.spyOn(apiClient, 'getMentorDefinitions').mockRejectedValueOnce(new Error('Network error'));

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter>
            <ProjectsDirectory />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument();
        expect(screen.getByText(/Network error/)).toBeInTheDocument();
      });

      // Retry
      vi.spyOn(apiClient, 'getMentorDefinitions').mockResolvedValueOnce([mockDefinition]);
      fireEvent.click(screen.getByText('Retry'));

      await waitFor(() => {
        expect(screen.getByText('Precision Agriculture Drone')).toBeInTheDocument();
      });
    });
  });

  describe('M18: DefinitionDetail (/mentor/projects/:definitionId)', () => {
    it('renders specification details and version history distinguishing Current vs Historical', async () => {
      vi.spyOn(apiClient, 'getMentorDefinition').mockResolvedValueOnce({
        ...mockDefinition,
        current_version_id: 'ver-2',
        current_version: mockVersion2,
      });
      vi.spyOn(apiClient, 'getDefinitionVersions').mockResolvedValueOnce([mockVersion2, mockVersion1]);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/projects/def-1']}>
            <Routes>
              <Route path="/mentor/projects/:definitionId" element={<DefinitionDetail />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Specification Snapshot')).toBeInTheDocument();
      });

      expect(screen.getAllByText('Crop telemetry latency in rural farmland with adverse weather').length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('Autonomous hybrid UAV with satellite uplink')).toBeInTheDocument();
      expect(screen.getByText('Version History')).toBeInTheDocument();
      expect(screen.getByText('2 Versions Total')).toBeInTheDocument();

      // Badges for current and historical
      expect(screen.getByText('Current')).toBeInTheDocument();
      expect(screen.getByText('Historical')).toBeInTheDocument();

      // Action buttons
      expect(screen.getByText('Edit Definition')).toBeInTheDocument();
      expect(screen.getByText('Assign to Student')).toBeInTheDocument();
    });

    it('toggles expanding historical version snapshot details', async () => {
      vi.spyOn(apiClient, 'getMentorDefinition').mockResolvedValueOnce(mockDefinition);
      vi.spyOn(apiClient, 'getDefinitionVersions').mockResolvedValueOnce([mockVersion1]);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/projects/def-1']}>
            <Routes>
              <Route path="/mentor/projects/:definitionId" element={<DefinitionDetail />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('View Snapshot')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('View Snapshot'));
      expect(screen.getByText('Hide Details')).toBeInTheDocument();
      expect(screen.getAllByText(/Design and simulate an automated crop survey drone/).length).toBeGreaterThanOrEqual(1);
    });
  });

  describe('M19: DefinitionCreate (/mentor/projects/new)', () => {
    it('validates required fields on submit', async () => {
      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter>
            <DefinitionCreate />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      fireEvent.click(screen.getByText('Create Definition'));

      await waitFor(() => {
        expect(screen.getByText('Project definition name is required.')).toBeInTheDocument();
        expect(screen.getByText('Problem statement is required.')).toBeInTheDocument();
        expect(screen.getByText('Proposed solution is required.')).toBeInTheDocument();
      });
    });

    it('submits valid definition payload and initiates version 1 snapshot', async () => {
      const createSpy = vi.spyOn(apiClient, 'createMentorDefinition').mockResolvedValueOnce({
        ...mockDefinition,
        id: 'new-def-99',
      });

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter>
            <DefinitionCreate />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      fireEvent.change(screen.getByLabelText(/Definition Name/), {
        target: { value: 'IoT Smart Greenhouse' },
      });
      fireEvent.change(screen.getByLabelText(/Problem Statement/), {
        target: { value: 'Excessive thermal fluctuation inside greenhouses' },
      });
      fireEvent.change(screen.getByLabelText(/Proposed Solution/), {
        target: { value: 'Automated shading & ventilation microcontroller network' },
      });

      fireEvent.click(screen.getByText('Create Definition'));

      await waitFor(() => {
        expect(createSpy).toHaveBeenCalledWith(
          expect.objectContaining({
            name: 'IoT Smart Greenhouse',
            problem: 'Excessive thermal fluctuation inside greenhouses',
            proposed_solution: 'Automated shading & ventilation microcontroller network',
            complexity: 'INTERMEDIATE',
          })
        );
      });
    });
  });

  describe('M20: DefinitionEdit (/mentor/projects/:definitionId/edit)', () => {
    it('renders pre-populated values and prominent versioning notice', async () => {
      vi.spyOn(apiClient, 'getMentorDefinition').mockResolvedValueOnce(mockDefinition);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/projects/def-1/edit']}>
            <Routes>
              <Route path="/mentor/projects/:definitionId/edit" element={<DefinitionEdit />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText(/Versioning Immutability Guarantee/)).toBeInTheDocument();
      });

      expect(screen.getByText(/Existing Student Project Instances created under/)).toBeInTheDocument();
      expect(screen.getByDisplayValue('Precision Agriculture Drone')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Crop telemetry latency in rural farmland')).toBeInTheDocument();
      expect(screen.getByText('Save & Publish Version 2')).toBeInTheDocument();
    });

    it('submits update payload creating new version snapshot', async () => {
      vi.spyOn(apiClient, 'getMentorDefinition').mockResolvedValueOnce(mockDefinition);
      const updateSpy = vi.spyOn(apiClient, 'updateMentorDefinition').mockResolvedValueOnce({
        ...mockDefinition,
        current_version_id: 'ver-2',
      });

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/projects/def-1/edit']}>
            <Routes>
              <Route path="/mentor/projects/:definitionId/edit" element={<DefinitionEdit />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByDisplayValue('Precision Agriculture Drone')).toBeInTheDocument();
      });

      fireEvent.change(screen.getByLabelText(/Definition Name/), {
        target: { value: 'Precision Agriculture Drone Pro' },
      });

      fireEvent.click(screen.getByText('Save & Publish Version 2'));

      await waitFor(() => {
        expect(updateSpy).toHaveBeenCalledWith(
          'def-1',
          expect.objectContaining({
            name: 'Precision Agriculture Drone Pro',
          })
        );
      });
    });
  });

  describe('M21: DefinitionAssign (/mentor/projects/:definitionId/assign)', () => {
    const mockGroups: GroupResponse[] = [
      {
        id: 'grp-1',
        mentor_id: 'user-1',
        name: 'Distributed Systems 2026',
        join_code: 'DS-2026',
        status: 'ACTIVE',
      },
    ];

    const mockStudents: GroupStudentResponse[] = [
      {
        student_id: 'stu-1',
        email: 'student1@growflow.test',
        full_name: 'Alice Student',
        status: 'ACTIVE',
        joined_at: '2026-09-02T10:00:00Z',
      },
    ];

    it('loads groups and students and enforces safety confirmation before assignment', async () => {
      vi.spyOn(apiClient, 'getMentorDefinition').mockResolvedValueOnce(mockDefinition);
      vi.spyOn(apiClient, 'getMentorGroups').mockResolvedValueOnce(mockGroups);
      vi.spyOn(apiClient, 'getGroupStudents').mockResolvedValueOnce(mockStudents);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/projects/def-1/assign']}>
            <Routes>
              <Route path="/mentor/projects/:definitionId/assign" element={<DefinitionAssign />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Selected Template Snapshot')).toBeInTheDocument();
        expect(screen.getByText('Alice Student (student1@growflow.test)')).toBeInTheDocument();
      });

      const submitBtn = screen.getByText('Confirm & Assign Project');
      expect(submitBtn).toBeDisabled();

      // Check confirmation checkbox
      const checkbox = screen.getByLabelText(/I understand that this action creates a new student project instance/);
      fireEvent.click(checkbox);

      expect(submitBtn).not.toBeDisabled();
    });

    it('submits assignment and renders success card with created instance details', async () => {
      vi.spyOn(apiClient, 'getMentorDefinition').mockResolvedValueOnce(mockDefinition);
      vi.spyOn(apiClient, 'getMentorGroups').mockResolvedValueOnce(mockGroups);
      vi.spyOn(apiClient, 'getGroupStudents').mockResolvedValueOnce(mockStudents);

      const createdInstance: ProjectResponse = {
        id: 'proj-instance-1',
        student_id: 'stu-1',
        group_id: 'grp-1',
        project_definition_id: 'def-1',
        source_definition_version_id: 'ver-1',
        name: 'Precision Agriculture Drone',
        problem: 'Crop telemetry latency in rural farmland',
        proposed_solution: 'Autonomous fixed-wing UAV with multispectral camera',
        complexity: 'ADVANCED',
        current_phase: 'IDEA',
        health: 'HEALTHY',
        progress_percentage: 0,
        status: 'ACTIVE',
        deadline: null,
        started_at: '2026-09-13T12:00:00Z',
        completed_at: null,
        created_at: '2026-09-13T12:00:00Z',
        updated_at: '2026-09-13T12:00:00Z',
      };

      const assignSpy = vi.spyOn(apiClient, 'assignMentorDefinition').mockResolvedValueOnce(createdInstance);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/projects/def-1/assign']}>
            <Routes>
              <Route path="/mentor/projects/:definitionId/assign" element={<DefinitionAssign />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Alice Student (student1@growflow.test)')).toBeInTheDocument();
        expect(screen.getByLabelText(/I understand that this action/)).toBeInTheDocument();
      });

      fireEvent.click(screen.getByLabelText(/I understand that this action/));
      fireEvent.click(screen.getByText('Confirm & Assign Project'));

      await waitFor(() => {
        expect(assignSpy).toHaveBeenCalledWith('def-1', {
          student_id: 'stu-1',
          group_id: 'grp-1',
          deadline: null,
        });
        expect(screen.getByText('Project Successfully Assigned')).toBeInTheDocument();
        expect(screen.getByText('View in Group Workspace')).toBeInTheDocument();
      });
    });

    it('surfaces canonical duplicate assignment error message', async () => {
      vi.spyOn(apiClient, 'getMentorDefinition').mockResolvedValueOnce(mockDefinition);
      vi.spyOn(apiClient, 'getMentorGroups').mockResolvedValueOnce(mockGroups);
      vi.spyOn(apiClient, 'getGroupStudents').mockResolvedValueOnce(mockStudents);

      vi.spyOn(apiClient, 'assignMentorDefinition').mockRejectedValueOnce(
        new Error('Student already has an active instance of this project definition.')
      );

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/projects/def-1/assign']}>
            <Routes>
              <Route path="/mentor/projects/:definitionId/assign" element={<DefinitionAssign />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Alice Student (student1@growflow.test)')).toBeInTheDocument();
        expect(screen.getByLabelText(/I understand that this action/)).toBeInTheDocument();
      });

      fireEvent.click(screen.getByLabelText(/I understand that this action/));
      fireEvent.click(screen.getByText('Confirm & Assign Project'));

      await waitFor(() => {
        expect(screen.getByText(/Student already has an active instance of this project definition/)).toBeInTheDocument();
      });
    });
  });

  describe('SYS03: 404 Visual Spacing and Role Navigation', () => {
    it('renders 404 page with role-aware return button and proper vertical structure', () => {
      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter>
            <NotFound />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByText('404 — Not Found')).toBeInTheDocument();
      expect(screen.getByText('Page Not Found')).toBeInTheDocument();
      expect(screen.getByText('Return to Overview')).toBeInTheDocument();
      expect(screen.getByText('Go Back')).toBeInTheDocument();
    });
  });

  describe('SYS04: ErrorBoundary Production Protection', () => {
    it('does not expose stack trace or diagnostic button in production', () => {
      // Temporarily mock import.meta.env.DEV = false
      const originalDev = import.meta.env.DEV;
      try {
        (import.meta.env as unknown as { DEV: boolean }).DEV = false;

        const spy = vi.spyOn(console, 'error').mockImplementation(() => {});

        function CrashingComponent(): React.ReactNode {
          throw new Error('Secret internal failure');
        }

        render(
          <ErrorBoundary>
            <CrashingComponent />
          </ErrorBoundary>
        );

        expect(screen.getByText('Something went wrong')).toBeInTheDocument();
        expect(screen.getByText('Try Again')).toBeInTheDocument();
        expect(screen.getByText('Return to Home')).toBeInTheDocument();

        // Must NOT render diagnostics button or stack trace
        expect(screen.queryByText('View Diagnostics')).not.toBeInTheDocument();
        expect(screen.queryByText('Hide Diagnostics')).not.toBeInTheDocument();
        expect(screen.queryByText(/Stack Trace/)).not.toBeInTheDocument();

        spy.mockRestore();
      } finally {
        (import.meta.env as unknown as { DEV: boolean }).DEV = originalDev;
      }
    });
  });
});
