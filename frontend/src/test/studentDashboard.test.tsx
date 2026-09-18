import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { StudentDashboard } from '@/pages/Student/StudentDashboard/StudentDashboard';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import type { User } from '@supabase/supabase-js';
import * as api from '@/lib/api';
import type { ProjectResponse, ProjectOverviewResponse } from '@/lib/api/types';
import {
  CANONICAL_LIFECYCLE_STAGES,
  getDeterministicNextAction,
  getStageNumber,
} from '@/pages/Student/StudentDashboard/utils';

// Spy on API client methods
vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api')>('@/lib/api');
  return {
    ...actual,
    getProjects: vi.fn(),
    getProjectOverview: vi.fn(),
  };
});

const mockProjectAlpha: ProjectResponse = {
  id: 'proj-001',
  student_id: 'student-123',
  group_id: null,
  project_definition_id: null,
  source_definition_version_id: null,
  name: 'Autonomous Solar Rover',
  problem: 'Inefficient ground monitoring in remote arid terrain.',
  proposed_solution: 'Solar-powered autonomous rover with edge computer vision.',
  complexity: 'INTERMEDIATE',
  current_phase: 'IDEA',
  health: 'HEALTHY',
  progress_percentage: 25,
  status: 'ACTIVE',
  deadline: '2026-11-30T00:00:00.000Z',
  started_at: '2026-09-01T00:00:00.000Z',
  completed_at: null,
  created_at: '2026-09-01T00:00:00.000Z',
  updated_at: '2026-09-10T00:00:00.000Z',
};

const mockProjectBeta: ProjectResponse = {
  id: 'proj-002',
  student_id: 'student-123',
  group_id: null,
  project_definition_id: null,
  source_definition_version_id: null,
  name: 'EcoTrack IoT Sensors',
  problem: 'Urban stormwater runoff monitoring.',
  proposed_solution: 'LoRaWAN IoT water quality sensing network.',
  complexity: 'ADVANCED',
  current_phase: 'IMPLEMENTATION',
  health: 'WARNING',
  progress_percentage: 60,
  status: 'ACTIVE',
  deadline: '2026-12-15T00:00:00.000Z',
  started_at: '2026-08-01T00:00:00.000Z',
  completed_at: null,
  created_at: '2026-08-01T00:00:00.000Z',
  updated_at: '2026-09-11T00:00:00.000Z',
};

const mockOverviewAlpha: ProjectOverviewResponse = {
  id: 'proj-001',
  student_id: 'student-123',
  group_id: null,
  project_definition_id: null,
  name: 'Autonomous Solar Rover',
  problem: 'Inefficient ground monitoring in remote arid terrain.',
  proposed_solution: 'Solar-powered autonomous rover with edge computer vision.',
  complexity: 'INTERMEDIATE',
  current_phase: 'IDEA',
  health: 'HEALTHY',
  progress_percentage: 25,
  status: 'ACTIVE',
  deadline: '2026-11-30T00:00:00.000Z',
  days_remaining: 78,
  profile: {
    objective: 'Build and validate an autonomous solar-powered rover prototype.',
    scope: 'Mechanical chassis, solar power distribution, and computer vision navigation.',
  },
  technologies: [
    { id: 'tech-1', technology_id: 'Python', category: 'Language' },
    { id: 'tech-2', technology_id: 'ROS2', category: 'Robotics' },
    { id: 'tech-3', technology_id: 'OpenCV', category: 'Vision' },
  ],
  recent_activity: {
    latest_phase_transition: {
      previous_phase: 'DRAFT',
      new_phase: 'IDEA',
      changed_at: '2026-09-02T14:30:00.000Z',
      reason: 'Initial proposal approved by mentor.',
    },
    latest_health_transition: {
      previous_health: 'WARNING',
      new_health: 'HEALTHY',
      changed_at: '2026-09-05T09:15:00.000Z',
      reason: 'Hardware bill of materials verified.',
    },
  },
};

function renderDashboard(authOverrides: Partial<AuthContextValue> = {}) {
  const authValue: AuthContextValue = {
    status: 'AUTHENTICATED',
    session: {
      access_token: 'mock-token',
      refresh_token: 'mock-refresh',
      expires_in: 3600,
      token_type: 'bearer',
      user: { id: 'student-123', email: 'alex@example.com' } as unknown as User,
    },
    supabaseUser: { id: 'student-123', email: 'alex@example.com' } as unknown as User,
    user: {
      id: 'student-123',
      email: 'alex@example.com',
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
      <MemoryRouter initialEntries={['/student/dashboard']}>
        <StudentDashboard />
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

describe('S01 — Student Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('1. renders loading skeleton while API requests are in flight', () => {
    // Return pending promises
    vi.mocked(api.getProjects).mockReturnValue(new Promise(() => {}));

    renderDashboard();

    expect(screen.getByRole('status', { name: /loading workspace/i })).toBeInTheDocument();
  });

  it('2. renders real project data, identity, lifecycle, health, progress, and deadline', async () => {
    vi.mocked(api.getProjects).mockResolvedValue([mockProjectAlpha]);
    vi.mocked(api.getProjectOverview).mockResolvedValue(mockOverviewAlpha);

    renderDashboard();

    // Student identity greeting
    await waitFor(() => {
      expect(screen.getByText(/Alex/i)).toBeInTheDocument();
    });

    // Primary project title & stage
    expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    expect(screen.getAllByText(/Stage 1 of 8/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('INTERMEDIATE')).toBeInTheDocument();
    expect(screen.getByText('ACTIVE')).toBeInTheDocument();

    // Health indicator
    expect(screen.getAllByText('Healthy')[0]).toBeInTheDocument();

    // Progress bar
    const progressbar = screen.getByRole('progressbar', { name: /project progress/i });
    expect(progressbar).toBeInTheDocument();
    expect(progressbar).toHaveAttribute('aria-valuenow', '25');
    expect(screen.getByText('25%')).toBeInTheDocument();

    // Days remaining from overview
    expect(screen.getByText(/78 days remaining/i)).toBeInTheDocument();

    // Real Profile Objective & Technologies
    expect(
      screen.getByText(/Build and validate an autonomous solar-powered rover prototype/i),
    ).toBeInTheDocument();
    expect(screen.getByText('Python')).toBeInTheDocument();
    expect(screen.getByText('ROS2')).toBeInTheDocument();
    expect(screen.getByText('OpenCV')).toBeInTheDocument();

    // Navigation CTA
    expect(
      screen.getByRole('link', { name: /open in project workspace/i }),
    ).toHaveAttribute('href', '/student/projects');
  });

  it('3. renders intentional empty state when user has zero projects', async () => {
    vi.mocked(api.getProjects).mockResolvedValue([]);

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('You have no projects yet.')).toBeInTheDocument();
    });

    expect(
      screen.getByText('Start with an idea and turn it into something you can build.'),
    ).toBeInTheDocument();

    const ctaButton = screen.getByRole('link', { name: /create your first project/i });
    expect(ctaButton).toBeInTheDocument();
    expect(ctaButton).toHaveAttribute('href', '/student/projects/new');
  });

  it('4. renders calm recoverable error state on API failure and supports retry', async () => {
    vi.mocked(api.getProjects).mockRejectedValueOnce(new Error('Network connection timeout'));

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText("We couldn't load your workspace")).toBeInTheDocument();
    });

    expect(screen.getByText('Network connection timeout')).toBeInTheDocument();

    // Retry should trigger re-fetch
    vi.mocked(api.getProjects).mockResolvedValueOnce([mockProjectAlpha]);
    vi.mocked(api.getProjectOverview).mockResolvedValueOnce(mockOverviewAlpha);

    const retryBtn = screen.getByRole('button', { name: /try again/i });
    fireEvent.click(retryBtn);

    await waitFor(() => {
      expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    });
  });

  it('5. maps canonical lifecycle phases deterministically to What To Do Next', () => {
    const phases = [
      'IDEA',
      'ASSESSMENT',
      'BLUEPRINT',
      'PLANNING',
      'IMPLEMENTATION',
      'TESTING',
      'DEPLOYMENT',
      'COMPLETED',
    ];

    const expectedActions = [
      'Refine your project definition and profile.',
      'Continue through the assessment.',
      'Review the project blueprint.',
      'Prepare the execution plan.',
      'Continue project implementation.',
      'Continue validating the project.',
      'Prepare or continue deployment.',
      'Review your completed project.',
    ];

    phases.forEach((phase, idx) => {
      const result = getDeterministicNextAction(phase);
      expect(result.action).toBe(expectedActions[idx]);
    });
  });

  it('6. correctly renders all 8 canonical lifecycle stages with aria-current on active stage', async () => {
    vi.mocked(api.getProjects).mockResolvedValue([mockProjectAlpha]);
    vi.mocked(api.getProjectOverview).mockResolvedValue(mockOverviewAlpha);

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    });

    const lifecycleTrack = screen.getByRole('list', { name: /project lifecycle progression/i });
    expect(lifecycleTrack).toBeInTheDocument();

    // All 8 stages present
    CANONICAL_LIFECYCLE_STAGES.forEach((s) => {
      expect(screen.getByText(s.label)).toBeInTheDocument();
    });

    // Stage 1 (IDEA) has aria-current="step"
    const currentStep = screen.getByRole('listitem', { current: 'step' });
    expect(currentStep).toHaveTextContent('Idea');
  });

  it('7. renders real transition records from overview recent_activity', async () => {
    vi.mocked(api.getProjects).mockResolvedValue([mockProjectAlpha]);
    vi.mocked(api.getProjectOverview).mockResolvedValue(mockOverviewAlpha);

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('Recent Project Transitions')).toBeInTheDocument();
    });

    // Phase transition record
    expect(screen.getByText('Phase Transition')).toBeInTheDocument();
    expect(screen.getByText('Reason: Initial proposal approved by mentor.')).toBeInTheDocument();

    // Health transition record
    expect(screen.getByText('Health Transition')).toBeInTheDocument();
    expect(screen.getByText('Reason: Hardware bill of materials verified.')).toBeInTheDocument();
  });

  it('8. renders calm empty state when no recent transitions exist', async () => {
    const overviewWithoutTransitions: ProjectOverviewResponse = {
      ...mockOverviewAlpha,
      recent_activity: {
        latest_phase_transition: null,
        latest_health_transition: null,
      },
    };

    vi.mocked(api.getProjects).mockResolvedValue([mockProjectAlpha]);
    vi.mocked(api.getProjectOverview).mockResolvedValue(overviewWithoutTransitions);

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('No recent project changes')).toBeInTheDocument();
    });
  });

  it('9. strictly preserves Data Integrity — does NOT fabricate unavailable capabilities', async () => {
    vi.mocked(api.getProjects).mockResolvedValue([mockProjectAlpha]);
    vi.mocked(api.getProjectOverview).mockResolvedValue(mockOverviewAlpha);

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    });

    // Verify unavailable capabilities are NOT rendered
    expect(screen.queryByText(/Milestones/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Blocked tasks/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Tasks/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Risks/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Risk Matrix/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/AI Mentor/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Mentor Feedback/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Help Requests/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Burndown/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Velocity/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Sprint/i)).not.toBeInTheDocument();
  });

  it('10. renders secondary projects portfolio when multiple projects exist and allows focusing', async () => {
    vi.mocked(api.getProjects).mockResolvedValue([mockProjectAlpha, mockProjectBeta]);
    vi.mocked(api.getProjectOverview).mockResolvedValue(mockOverviewAlpha);

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('All Student Projects (2)')).toBeInTheDocument();
    });

    expect(screen.getByText('EcoTrack IoT Sensors')).toBeInTheDocument();

    // Focus secondary project
    const focusBtn = screen.getByRole('button', {
      name: /view ecotrack iot sensors overview in dashboard/i,
    });
    expect(focusBtn).toBeInTheDocument();

    const mockOverviewBeta: ProjectOverviewResponse = {
      ...mockOverviewAlpha,
      id: 'proj-002',
      name: 'EcoTrack IoT Sensors',
      current_phase: 'IMPLEMENTATION',
      progress_percentage: 60,
    };

    vi.mocked(api.getProjectOverview).mockResolvedValueOnce(mockOverviewBeta);
    fireEvent.click(focusBtn);

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 2, name: 'EcoTrack IoT Sensors' })).toBeInTheDocument();
      expect(screen.getAllByText(/Stage 5 of 8/i).length).toBeGreaterThanOrEqual(1);
    });
  });

  it('11. verifies getStageNumber helper returns correct stage indexes', () => {
    expect(getStageNumber('IDEA')).toBe(1);
    expect(getStageNumber('ASSESSMENT')).toBe(2);
    expect(getStageNumber('BLUEPRINT')).toBe(3);
    expect(getStageNumber('PLANNING')).toBe(4);
    expect(getStageNumber('IMPLEMENTATION')).toBe(5);
    expect(getStageNumber('TESTING')).toBe(6);
    expect(getStageNumber('DEPLOYMENT')).toBe(7);
    expect(getStageNumber('COMPLETED')).toBe(8);
    expect(getStageNumber('NON_EXISTENT')).toBe(1); // fallback
  });

  it('12. [B4-02] prevents race condition: stale project overview response cannot overwrite newer selection', async () => {
    vi.mocked(api.getProjects).mockResolvedValue([mockProjectAlpha, mockProjectBeta]);
    vi.mocked(api.getProjectOverview).mockResolvedValue(mockOverviewAlpha);

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 2, name: 'Autonomous Solar Rover' })).toBeInTheDocument();
    });

    const mockOverviewBeta: ProjectOverviewResponse = {
      ...mockOverviewAlpha,
      id: 'proj-002',
      name: 'EcoTrack IoT Sensors',
      current_phase: 'IMPLEMENTATION',
      progress_percentage: 60,
    };

    let resolveBeta!: (val: ProjectOverviewResponse) => void;
    const betaPromise = new Promise<ProjectOverviewResponse>((resolve) => {
      resolveBeta = resolve;
    });

    // When EcoTrack (beta) is selected, its response is delayed
    vi.mocked(api.getProjectOverview).mockImplementation((id: string) => {
      if (id === 'proj-002') return betaPromise;
      return Promise.resolve(mockOverviewAlpha);
    });

    // Click to focus EcoTrack (proj-002)
    const focusBetaBtn = screen.getByRole('button', {
      name: /view ecotrack iot sensors overview in dashboard/i,
    });
    fireEvent.click(focusBetaBtn);

    // Immediately switch back to Alpha (proj-001) before Beta resolves
    const focusAlphaBtn = await screen.findByRole('button', {
      name: /view autonomous solar rover overview in dashboard/i,
    });
    fireEvent.click(focusAlphaBtn);

    // Wait for Alpha to be firmly active
    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 2, name: 'Autonomous Solar Rover' })).toBeInTheDocument();
    });

    // Now resolve the stale delayed Beta response
    resolveBeta(mockOverviewBeta);

    // Ensure the overview remains Autonomous Solar Rover and is NOT overwritten by stale Beta
    await new Promise((r) => setTimeout(r, 50));
    expect(screen.getByRole('heading', { level: 2, name: 'Autonomous Solar Rover' })).toBeInTheDocument();
  });
});
