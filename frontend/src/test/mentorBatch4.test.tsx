import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import type { User } from '@supabase/supabase-js';

import { MentorInstanceBlueprint } from '@/pages/Mentor/InstanceBlueprint/MentorInstanceBlueprint';
import { MentorInstanceTasks } from '@/pages/Mentor/InstanceTasks/MentorInstanceTasks';
import { MentorInstanceMilestones } from '@/pages/Mentor/InstanceMilestones/MentorInstanceMilestones';
import { MentorInstanceRisks } from '@/pages/Mentor/InstanceRisks/MentorInstanceRisks';
import { MentorInstanceDocuments } from '@/pages/Mentor/InstanceDocuments/MentorInstanceDocuments';
import { MentorInstanceGitHub } from '@/pages/Mentor/InstanceGitHub/MentorInstanceGitHub';
import { MentorInstanceActivity } from '@/pages/Mentor/InstanceActivity/MentorInstanceActivity';
import * as apiClient from '@/lib/api/client';
import type {
  MentorProjectInstanceDetail,
  MentorBlueprintInspectionResponse,
  TaskResponse,
  MilestoneResponse,
  RiskResponse,
  DocumentResponse,
  GitHubIntegrationResponse,
  ActivityItemResponse,
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
      fullName: 'Dr. Evelyn Vance',
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

describe('Phase 7 Batch 4: Mentor Project Instance Deep Inspection (M24–M30)', () => {
  const mockProject: MentorProjectInstanceDetail = {
    id: 'proj-101',
    name: 'Autonomous Precision Drone',
    student_id: 'student-202',
    student_name: 'Alex Rivera',
    student_email: 'alex@student.test',
    group_id: 'grp-303',
    group_name: 'Robotics Cohort Alpha',
    current_phase: 'DEVELOPMENT' as any,
    health: 'HEALTHY' as any,
    progress_percentage: 55,
    status: 'ACTIVE' as any,
    deadline: '2026-11-30T00:00:00Z',
    source_definition_id: 'defn-404',
    source_definition_name: 'UAV Survey Platform',
    source_definition_version_number: 2,
    source_definition_version_id: 'ver-505',
    source_definition_version_summary: 'Production stabilized UAV specification',
    problem: 'Manual inspection of vast crop fields is slow and cost-prohibitive.',
    proposed_solution: 'Automated UAV flights with multispectral sensors and edge telemetry.',
    complexity: 'ADVANCED' as any,
    student_bio: 'Final year aerospace engineering student.',
    student_skills: ['ROS', 'Python', 'Computer Vision'],
    created_at: '2026-09-01T10:00:00Z',
    updated_at: '2026-09-14T12:00:00Z',
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(apiClient, 'getMentorProjectInstance').mockResolvedValue(mockProject);
  });

  // ==========================================================================
  // M24: Instance Blueprint
  // ==========================================================================
  describe('M24 — Instance Blueprint', () => {
    const mockBlueprintRes: MentorBlueprintInspectionResponse = {
      project: mockProject,
      blueprint: {
        id: 'bp-1',
        project_instance_id: 'proj-101',
        student_id: 'student-202',
        status: 'APPROVED',
        progress_percent: 100,
        qa_status: 'PASS',
        qa_score: 95,
        qa_feedback: {
          status: 'PASS',
          score: 95,
          summary: 'Exemplary system architecture design.',
          recommendations: ['Consider battery thermal management.'],
        },
      },
      content: {
        project_profile: { title: 'UAV Platform', overview: 'Autonomous field surveyor.' },
        tech_stack: { primary_language: 'Python / C++' },
        readme: { markdown: '# Autonomous Precision Drone\nREADME content' },
      },
    };

    it('renders loading skeleton initially', () => {
      vi.spyOn(apiClient, 'getMentorInstanceBlueprint').mockImplementation(
        () => new Promise(() => {})
      );

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/blueprint']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/blueprint"
                element={<MentorInstanceBlueprint />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(document.getElementById('mentor-blueprint-loading')).toBeInTheDocument();
    });

    it('renders blueprint status, pinned definition version, and canonical sections', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceBlueprint').mockResolvedValue(mockBlueprintRes);

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/blueprint']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/blueprint"
                element={<MentorInstanceBlueprint />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Autonomous Precision Drone', level: 1 })).toBeInTheDocument();
        expect(screen.getByText(/Pinned v2/i)).toBeInTheDocument();
        expect(screen.getByText(/QA Score: 95\/100/i)).toBeInTheDocument();
        expect(screen.getByText('Exemplary system architecture design.')).toBeInTheDocument();
        expect(screen.getAllByText('1. Project Profile').length).toBeGreaterThan(0);
        expect(screen.getByRole('button', { name: /10\. README/i })).toBeInTheDocument();
      });
    });

    it('switches between canonical sections', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceBlueprint').mockResolvedValue(mockBlueprintRes);

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/blueprint']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/blueprint"
                element={<MentorInstanceBlueprint />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /1\. Project Profile/i })).toBeInTheDocument();
      });

      // Click README section
      fireEvent.click(screen.getByRole('button', { name: /10\. README/i }));
      expect(screen.getByText(/README content/i)).toBeInTheDocument();
    });

    it('displays error / forbidden state when authorization fails', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceBlueprint').mockRejectedValue(
        new Error('You do not supervise this project instance.')
      );

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/blueprint']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/blueprint"
                element={<MentorInstanceBlueprint />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Blueprint Supervision Restricted')).toBeInTheDocument();
        expect(screen.getByText(/You do not supervise this project instance/i)).toBeInTheDocument();
      });
    });

    it('contains ZERO mutation controls on Blueprint surface', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceBlueprint').mockResolvedValue(mockBlueprintRes);

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/blueprint']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/blueprint"
                element={<MentorInstanceBlueprint />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Autonomous Precision Drone', level: 1 })).toBeInTheDocument();
      });

      // Assert absence of mutation controls
      expect(screen.queryByRole('button', { name: /generate/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /regenerate/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /approve/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /reject/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument();
    });
  });

  // ==========================================================================
  // M25: Instance Tasks
  // ==========================================================================
  describe('M25 — Instance Tasks', () => {
    const mockTasks: TaskResponse[] = [
      {
        id: 't-1',
        project_instance_id: 'proj-101',
        milestone_id: 'm-1',
        task_code: 'T01',
        title: 'Calibrate Optical Flow Sensor',
        description: 'Ensure accurate position hold indoors without GPS.',
        status: 'IN_PROGRESS',
        priority: 'HIGH',
        category: 'EMBEDDED',
        phase: 'IMPLEMENTATION',
        due_date: '2026-10-15T00:00:00Z',
        dependencies: [],
        acceptance_criteria: ['Hold position drift < 5cm'],
        completed_at: null,
        created_at: '2026-09-02T10:00:00Z',
        updated_at: '2026-09-10T10:00:00Z',
      },
      {
        id: 't-2',
        project_instance_id: 'proj-101',
        milestone_id: 'm-1',
        task_code: 'T02',
        title: 'Payload Weight Budget Analysis',
        description: 'Verify all avionics and gimbal weight under 2.5kg.',
        status: 'COMPLETED',
        priority: 'MEDIUM',
        category: 'ANALYSIS',
        phase: 'PLANNING',
        due_date: '2026-09-10T00:00:00Z',
        dependencies: [],
        acceptance_criteria: ['Signed weight budget sheet'],
        completed_at: '2026-09-08T14:00:00Z',
        created_at: '2026-09-02T10:00:00Z',
        updated_at: '2026-09-08T14:00:00Z',
      },
    ];

    it('renders tasks with search and priority filtering', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceTasks').mockResolvedValue(mockTasks);

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/tasks']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/tasks"
                element={<MentorInstanceTasks />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Calibrate Optical Flow Sensor')).toBeInTheDocument();
        expect(screen.getByText('Payload Weight Budget Analysis')).toBeInTheDocument();
        expect(screen.getByText('T01')).toBeInTheDocument();
        expect(screen.getByText('T02')).toBeInTheDocument();
      });

      // Search filter
      const searchInput = screen.getByPlaceholderText(/search tasks/i);
      fireEvent.change(searchInput, { target: { value: 'Optical' } });
      expect(screen.getByText('Calibrate Optical Flow Sensor')).toBeInTheDocument();
      expect(screen.queryByText('Payload Weight Budget Analysis')).not.toBeInTheDocument();
    });

    it('contains ZERO mutation controls on Tasks surface', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceTasks').mockResolvedValue(mockTasks);

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/tasks']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/tasks"
                element={<MentorInstanceTasks />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Calibrate Optical Flow Sensor')).toBeInTheDocument();
      });

      expect(screen.queryByRole('button', { name: /create task/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /new task/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /delete/i })).not.toBeInTheDocument();
    });
  });

  // ==========================================================================
  // M26: Instance Milestones
  // ==========================================================================
  describe('M26 — Instance Milestones', () => {
    const mockMilestones: MilestoneResponse[] = [
      {
        id: 'm-1',
        project_instance_id: 'proj-101',
        title: 'Initial Flight Envelope Validation',
        description: 'Perform hover and low-speed flight stability tests.',
        gate_code: 'GATE-01',
        target_date: '2026-10-01T00:00:00Z',
        status: 'IN_PROGRESS',
        progress_percent: 75,
        deliverables: ['Telemetry log review', 'Flight video recording'],
        section_order: 1,
        task_count: 4,
        completed_task_count: 3,
        tasks: [],
        created_at: '2026-09-01T10:00:00Z',
        updated_at: '2026-09-12T10:00:00Z',
      },
    ];

    it('renders milestones with gate code and deliverables list', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceMilestones').mockResolvedValue(mockMilestones);

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/milestones']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/milestones"
                element={<MentorInstanceMilestones />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Initial Flight Envelope Validation')).toBeInTheDocument();
        expect(screen.getByText('GATE-01')).toBeInTheDocument();
        expect(screen.getByText('75%')).toBeInTheDocument();
        expect(screen.getByText('Telemetry log review')).toBeInTheDocument();
      });
    });

    it('contains ZERO mutation controls on Milestones surface', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceMilestones').mockResolvedValue(mockMilestones);

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/milestones']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/milestones"
                element={<MentorInstanceMilestones />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Initial Flight Envelope Validation')).toBeInTheDocument();
      });

      expect(screen.queryByRole('button', { name: /create milestone/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /complete/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /delete/i })).not.toBeInTheDocument();
    });
  });

  // ==========================================================================
  // M27: Instance Risks
  // ==========================================================================
  describe('M27 — Instance Risks', () => {
    const mockRisks: RiskResponse[] = [
      {
        id: 'r-1',
        project_instance_id: 'proj-101',
        risk_code: 'RSK-01',
        title: 'Motor ESC thermal cutoff in hot weather',
        description: 'Prolonged full-throttle climb causes motor ESC temperature cutoff.',
        severity: 'HIGH',
        probability: 'MEDIUM',
        impact: 'HIGH',
        status: 'MITIGATING',
        mitigation: 'Install aluminum finned heatsinks and intake ducting.',
        owner: 'Alex Rivera',
        review_date: '2026-10-05T00:00:00Z',
        created_at: '2026-09-03T10:00:00Z',
        updated_at: '2026-09-08T10:00:00Z',
      },
    ];

    it('renders risk cards with severity badges and mitigation strategies', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceRisks').mockResolvedValue(mockRisks);

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/risks']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/risks"
                element={<MentorInstanceRisks />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Motor ESC thermal cutoff in hot weather')).toBeInTheDocument();
        expect(screen.getByText('RSK-01')).toBeInTheDocument();
        expect(screen.getByText(/High Risk/i)).toBeInTheDocument();
        expect(screen.getByText(/Install aluminum finned heatsinks/i)).toBeInTheDocument();
      });
    });

    it('contains ZERO mutation controls on Risks surface', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceRisks').mockResolvedValue(mockRisks);

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/risks']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/risks"
                element={<MentorInstanceRisks />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Motor ESC thermal cutoff in hot weather')).toBeInTheDocument();
      });

      expect(screen.queryByRole('button', { name: /create risk/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /resolve/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /dismiss/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /delete/i })).not.toBeInTheDocument();
    });
  });

  // ==========================================================================
  // M28: Instance Documents
  // ==========================================================================
  describe('M28 — Instance Documents', () => {
    const mockDocs: DocumentResponse[] = [
      {
        id: 'doc-1',
        project_instance_id: 'proj-101',
        document_key: 'master_architecture_spec',
        title: 'Master Architecture Specification',
        doc_type: 'SPECIFICATION',
        format: 'markdown',
        content: '# Master Architecture\nHigh-level system topology with dual CAN bus.',
        version: '1.0',
        status: 'ACTIVE',
        source: 'BLUEPRINT_INIT',
        created_at: '2026-09-01T10:00:00Z',
        updated_at: '2026-09-05T10:00:00Z',
      },
    ];

    it('renders document list and opens read-only inspection modal', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceDocuments').mockResolvedValue(mockDocs);

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/documents']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/documents"
                element={<MentorInstanceDocuments />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Master Architecture Specification')).toBeInTheDocument();
        expect(screen.getByText('master_architecture_spec')).toBeInTheDocument();
      });

      // Open inspection modal
      fireEvent.click(screen.getByRole('button', { name: /inspect document/i }));
      expect(screen.getByText('READ-ONLY INSPECTION')).toBeInTheDocument();
      expect(screen.getByText(/High-level system topology with dual CAN bus/i)).toBeInTheDocument();

      // Close modal
      fireEvent.click(screen.getByRole('button', { name: /close preview/i }));
      expect(screen.queryByText('READ-ONLY INSPECTION')).not.toBeInTheDocument();
    });

    it('contains ZERO mutation controls on Documents surface', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceDocuments').mockResolvedValue(mockDocs);

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/documents']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/documents"
                element={<MentorInstanceDocuments />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Master Architecture Specification')).toBeInTheDocument();
      });

      expect(screen.queryByRole('button', { name: /upload/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /replace/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /delete/i })).not.toBeInTheDocument();
    });
  });

  // ==========================================================================
  // M29: Instance GitHub
  // ==========================================================================
  describe('M29 — Instance GitHub', () => {
    const mockGitHubConnected: GitHubIntegrationResponse = {
      id: 'gh-1',
      project_instance_id: 'proj-101',
      repository_name: 'alex-drone-firmware',
      repository_url: 'https://github.com/alexrivera/alex-drone-firmware',
      connection_status: 'CONNECTED',
      default_branch: 'main',
      commit_count: 28,
      last_sync_at: '2026-09-14T11:30:00Z',
      sync_error: null,
      cached_commits_preview: [
        {
          sha: 'd4e5f6a1',
          message: 'refactor: split PID controller into separate task',
          author: 'alexrivera',
          date: '2026-09-14T10:15:00Z',
        },
      ],
    };

    const mockGitHubDisconnected: GitHubIntegrationResponse = {
      id: null,
      project_instance_id: 'proj-101',
      repository_name: '',
      repository_url: '',
      connection_status: 'NOT_CONNECTED',
      default_branch: 'main',
      commit_count: 0,
      last_sync_at: null,
      sync_error: null,
      cached_commits_preview: [],
    };

    it('renders connected observational GitHub repository and commit telemetry', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceGitHub').mockResolvedValue(mockGitHubConnected);

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/github']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/github"
                element={<MentorInstanceGitHub />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('alex-drone-firmware')).toBeInTheDocument();
        expect(screen.getByText('Connected')).toBeInTheDocument();
        expect(screen.getByText(/28 commits/i)).toBeInTheDocument();
        expect(screen.getByText('refactor: split PID controller into separate task')).toBeInTheDocument();
      });
    });

    it('renders truthful disconnected empty state when unlinked', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceGitHub').mockResolvedValue(mockGitHubDisconnected);

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/github']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/github"
                element={<MentorInstanceGitHub />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('No Repository Connected')).toBeInTheDocument();
        expect(screen.getByText(/student has not connected an external GitHub repository/i)).toBeInTheDocument();
      });
    });

    it('contains ZERO mutation controls on GitHub surface', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceGitHub').mockResolvedValue(mockGitHubConnected);

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/github']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/github"
                element={<MentorInstanceGitHub />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('alex-drone-firmware')).toBeInTheDocument();
      });

      expect(screen.queryByRole('button', { name: /connect/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /disconnect/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /sync/i })).not.toBeInTheDocument();
    });
  });

  // ==========================================================================
  // M30: Instance Activity
  // ==========================================================================
  describe('M30 — Instance Activity', () => {
    const mockActivity: ActivityItemResponse[] = [
      {
        id: 'evt-1',
        event_type: 'TaskCompleted',
        title: 'Task Completed',
        description: "Task 'Calibrate Optical Flow Sensor' marked completed.",
        actor_role: 'STUDENT',
        actor_id: 'student-202',
        resource_type: 'project_task',
        resource_id: 't-1',
        occurred_at: '2026-09-14T11:00:00Z',
        metadata: { task_code: 'T01' },
      },
      {
        id: 'evt-2',
        event_type: 'BlueprintApproved',
        title: 'Blueprint Approved',
        description: 'Architecture blueprint reviewed and approved.',
        actor_role: 'STUDENT',
        actor_id: 'student-202',
        resource_type: 'blueprint',
        resource_id: 'bp-1',
        occurred_at: '2026-09-01T12:00:00Z',
        metadata: { qa_score: 95 },
      },
    ];

    it('renders project-scoped activity audit trail', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceActivity').mockResolvedValue(mockActivity);

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/activity']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/activity"
                element={<MentorInstanceActivity />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Project Event History')).toBeInTheDocument();
        expect(screen.getByText('Task Completed')).toBeInTheDocument();
        expect(screen.getByText("Task 'Calibrate Optical Flow Sensor' marked completed.")).toBeInTheDocument();
        expect(screen.getByText('Blueprint Approved')).toBeInTheDocument();
      });
    });

    it('renders truthful empty state when no domain events exist', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceActivity').mockResolvedValue([]);

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/activity']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/activity"
                element={<MentorInstanceActivity />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText(/No domain events have been recorded/i)).toBeInTheDocument();
      });
    });
  });

  // ==========================================================================
  // Contextual Header & Navigation Tabs
  // ==========================================================================
  describe('Contextual Navigation & Header', () => {
    it('renders all 8 inspection tabs and navigates between them', async () => {
      vi.spyOn(apiClient, 'getMentorInstanceBlueprint').mockResolvedValue({
        project: mockProject,
        blueprint: {
          id: 'bp-1',
          project_instance_id: 'proj-101',
          student_id: 'student-202',
          status: 'APPROVED',
          progress_percent: 100,
          qa_status: 'PASS',
        },
        content: {},
      });

      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-101/blueprint']}>
            <Routes>
              <Route
                path="/mentor/project-instances/:projectId/blueprint"
                element={<MentorInstanceBlueprint />}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByRole('link', { name: 'Overview' })).toHaveAttribute(
          'href',
          '/mentor/project-instances/proj-101'
        );
        expect(screen.getByRole('link', { name: 'Blueprint' })).toHaveAttribute(
          'href',
          '/mentor/project-instances/proj-101/blueprint'
        );
        expect(screen.getByRole('link', { name: 'Tasks' })).toHaveAttribute(
          'href',
          '/mentor/project-instances/proj-101/tasks'
        );
        expect(screen.getByRole('link', { name: 'Milestones' })).toHaveAttribute(
          'href',
          '/mentor/project-instances/proj-101/milestones'
        );
        expect(screen.getByRole('link', { name: 'Risks' })).toHaveAttribute(
          'href',
          '/mentor/project-instances/proj-101/risks'
        );
        expect(screen.getByRole('link', { name: 'Documents' })).toHaveAttribute(
          'href',
          '/mentor/project-instances/proj-101/documents'
        );
        expect(screen.getByRole('link', { name: 'GitHub' })).toHaveAttribute(
          'href',
          '/mentor/project-instances/proj-101/github'
        );
        expect(screen.getByRole('link', { name: 'Activity' })).toHaveAttribute(
          'href',
          '/mentor/project-instances/proj-101/activity'
        );
      });
    });
  });
});
