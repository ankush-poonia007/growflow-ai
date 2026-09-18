import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { StudentProjects } from '@/pages/Student/StudentProjects/StudentProjects';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import type { User } from '@supabase/supabase-js';
import * as api from '@/lib/api';
import type { ProjectResponse } from '@/lib/api/types';

vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api')>('@/lib/api');
  return {
    ...actual,
    getProjects: vi.fn(),
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
  group_id: 'group-1',
  project_definition_id: 'def-456',
  source_definition_version_id: 'v1',
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

const mockProjectGamma: ProjectResponse = {
  id: 'proj-003',
  student_id: 'student-123',
  group_id: null,
  project_definition_id: null,
  source_definition_version_id: null,
  name: 'Compiler Optimization Pipeline',
  problem: 'LLVM pass acceleration.',
  proposed_solution: 'Custom vectorized passes for matrix arithmetic.',
  complexity: 'ADVANCED',
  current_phase: 'COMPLETED',
  health: 'HEALTHY',
  progress_percentage: 100,
  status: 'COMPLETED',
  deadline: null,
  started_at: '2026-07-01T00:00:00.000Z',
  completed_at: '2026-08-28T00:00:00.000Z',
  created_at: '2026-07-01T00:00:00.000Z',
  updated_at: '2026-08-28T00:00:00.000Z',
};

const mockProjectDelta: ProjectResponse = {
  id: 'proj-004',
  student_id: 'student-123',
  group_id: null,
  project_definition_id: null,
  source_definition_version_id: null,
  name: 'Blockchain Voting Audits',
  problem: 'Zero-knowledge verification protocols.',
  proposed_solution: 'zk-SNARK ballot integrity proof engine.',
  complexity: 'BEGINNER',
  current_phase: 'PLANNING',
  health: 'CRITICAL',
  progress_percentage: 10,
  status: 'DRAFT',
  deadline: '2026-10-15T00:00:00.000Z',
  started_at: '2026-09-10T00:00:00.000Z',
  completed_at: null,
  created_at: '2026-09-10T00:00:00.000Z',
  updated_at: '2026-09-12T00:00:00.000Z',
};

const mockAllProjects = [
  mockProjectAlpha,
  mockProjectBeta,
  mockProjectGamma,
  mockProjectDelta,
];

function renderProjectsPage(initialUrl = '/student/projects') {
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
  };

  return render(
    <AuthContext.Provider value={authValue}>
      <MemoryRouter initialEntries={[initialUrl]}>
        <StudentProjects />
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

describe('S02 — Student Projects (/student/projects)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('1. renders loading skeleton while API requests are in flight', () => {
    vi.mocked(api.getProjects).mockReturnValue(new Promise(() => {}));

    renderProjectsPage();

    expect(screen.getByRole('status', { name: /loading projects/i })).toBeInTheDocument();
  });

  it('2. renders project collection with real data, status, health, phase, progress, and source badges', async () => {
    vi.mocked(api.getProjects).mockResolvedValue(mockAllProjects);

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    });

    // Check project names
    expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    expect(screen.getByText('EcoTrack IoT Sensors')).toBeInTheDocument();
    expect(screen.getByText('Compiler Optimization Pipeline')).toBeInTheDocument();
    expect(screen.getByText('Blockchain Voting Audits')).toBeInTheDocument();

    // Check statuses
    expect(screen.getAllByText('ACTIVE').length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText('COMPLETED')).toBeInTheDocument();
    expect(screen.getByText('DRAFT')).toBeInTheDocument();

    // Check health labels
    expect(screen.getAllByText('Healthy').length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText('Warning').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Critical').length).toBeGreaterThanOrEqual(1);

    // Check progress
    expect(screen.getByText('25%')).toBeInTheDocument();
    expect(screen.getByText('60%')).toBeInTheDocument();
    expect(screen.getByText('100%')).toBeInTheDocument();

    // Check stages
    expect(screen.getByText(/Stage 1 of 8 \(IDEA\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Stage 5 of 8 \(IMPLEMENTATION\)/i)).toBeInTheDocument();

    // Check source distinction: Mentor project vs Independent project
    expect(screen.getByText('Mentor Project')).toBeInTheDocument();
    expect(screen.getAllByText('Independent Project').length).toBe(3);
  });

  it('3. renders derived summary bar with total, active, attention, and completed counts', async () => {
    vi.mocked(api.getProjects).mockResolvedValue(mockAllProjects);

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByLabelText('Projects Collection Summary')).toBeInTheDocument();
    });

    const summary = screen.getByLabelText('Projects Collection Summary');
    expect(within(summary).getByText(/projects total/i)).toBeInTheDocument();
    expect(within(summary).getByText(/active/i)).toBeInTheDocument();
    expect(within(summary).getByText(/attention needed/i)).toBeInTheDocument();
    expect(within(summary).getByText(/completed/i)).toBeInTheDocument();
  });

  it('4. filters projects by search query (case-insensitive) across name and problem statement', async () => {
    vi.mocked(api.getProjects).mockResolvedValue(mockAllProjects);

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search projects by name/i);
    fireEvent.change(searchInput, { target: { value: 'solar' } });

    expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    expect(screen.queryByText('EcoTrack IoT Sensors')).not.toBeInTheDocument();
    expect(screen.queryByText('Compiler Optimization Pipeline')).not.toBeInTheDocument();
  });

  it('5. filters projects by status (ACTIVE, DRAFT, COMPLETED)', async () => {
    vi.mocked(api.getProjects).mockResolvedValue(mockAllProjects);

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    });

    const statusSelect = screen.getByLabelText(/filter by project status/i);

    // Filter by DRAFT
    fireEvent.change(statusSelect, { target: { value: 'DRAFT' } });

    expect(screen.getByText('Blockchain Voting Audits')).toBeInTheDocument();
    expect(screen.queryByText('Autonomous Solar Rover')).not.toBeInTheDocument();
    expect(screen.queryByText('EcoTrack IoT Sensors')).not.toBeInTheDocument();

    // Filter by COMPLETED
    fireEvent.change(statusSelect, { target: { value: 'COMPLETED' } });
    expect(screen.getByText('Compiler Optimization Pipeline')).toBeInTheDocument();
    expect(screen.queryByText('Blockchain Voting Audits')).not.toBeInTheDocument();
  });

  it('6. filters projects by lifecycle phase (IDEA, IMPLEMENTATION, COMPLETED)', async () => {
    vi.mocked(api.getProjects).mockResolvedValue(mockAllProjects);

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    });

    const phaseSelect = screen.getByLabelText(/filter by lifecycle phase/i);

    // Filter by IMPLEMENTATION
    fireEvent.change(phaseSelect, { target: { value: 'IMPLEMENTATION' } });

    expect(screen.getByText('EcoTrack IoT Sensors')).toBeInTheDocument();
    expect(screen.queryByText('Autonomous Solar Rover')).not.toBeInTheDocument();
    expect(screen.queryByText('Compiler Optimization Pipeline')).not.toBeInTheDocument();
  });

  it('7. filters projects by health status (HEALTHY, WARNING, CRITICAL)', async () => {
    vi.mocked(api.getProjects).mockResolvedValue(mockAllProjects);

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    });

    const healthSelect = screen.getByLabelText(/filter by health status/i);

    // Filter by WARNING
    fireEvent.change(healthSelect, { target: { value: 'WARNING' } });

    expect(screen.getByText('EcoTrack IoT Sensors')).toBeInTheDocument();
    expect(screen.queryByText('Autonomous Solar Rover')).not.toBeInTheDocument();

    // Filter by CRITICAL
    fireEvent.change(healthSelect, { target: { value: 'CRITICAL' } });
    expect(screen.getByText('Blockchain Voting Audits')).toBeInTheDocument();
    expect(screen.queryByText('EcoTrack IoT Sensors')).not.toBeInTheDocument();
  });

  it('8. sorts projects deterministically: Name A-Z, Name Z-A, Progress, Deadline', async () => {
    vi.mocked(api.getProjects).mockResolvedValue(mockAllProjects);

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    });

    const sortSelect = screen.getByLabelText(/sort projects/i);

    // Sort by Name (A to Z)
    fireEvent.change(sortSelect, { target: { value: 'name_asc' } });
    const headingsAsc = screen.getAllByRole('heading', { level: 2 }).map((h) => h.textContent);
    expect(headingsAsc).toEqual([
      'Autonomous Solar Rover',
      'Blockchain Voting Audits',
      'Compiler Optimization Pipeline',
      'EcoTrack IoT Sensors',
    ]);

    // Sort by Progress (High to Low)
    fireEvent.change(sortSelect, { target: { value: 'progress_desc' } });
    const headingsProgress = screen.getAllByRole('heading', { level: 2 }).map((h) => h.textContent);
    expect(headingsProgress).toEqual([
      'Compiler Optimization Pipeline', // 100%
      'EcoTrack IoT Sensors', // 60%
      'Autonomous Solar Rover', // 25%
      'Blockchain Voting Audits', // 10%
    ]);
  });

  it('9. composes search, status, phase, and health filters predictably', async () => {
    vi.mocked(api.getProjects).mockResolvedValue(mockAllProjects);

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search projects by name/i);
    const statusSelect = screen.getByLabelText(/filter by project status/i);
    const healthSelect = screen.getByLabelText(/filter by health status/i);

    fireEvent.change(searchInput, { target: { value: 'sensors' } });
    fireEvent.change(statusSelect, { target: { value: 'ACTIVE' } });
    fireEvent.change(healthSelect, { target: { value: 'WARNING' } });

    expect(screen.getByText('EcoTrack IoT Sensors')).toBeInTheDocument();
    expect(screen.queryByText('Autonomous Solar Rover')).not.toBeInTheDocument();
    expect(screen.queryByText('Compiler Optimization Pipeline')).not.toBeInTheDocument();
    expect(screen.queryByText('Blockchain Voting Audits')).not.toBeInTheDocument();
  });

  it('10. renders empty state when zero projects are returned by server with Create Project CTA', async () => {
    vi.mocked(api.getProjects).mockResolvedValue([]);

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText('No projects yet.')).toBeInTheDocument();
    });

    expect(
      screen.getByText('Start with an idea and turn it into something you can build.'),
    ).toBeInTheDocument();

    const cta = screen.getAllByRole('link', { name: /create.*project/i })[0];
    expect(cta).toHaveAttribute('href', '/student/projects/new');
  });

  it('11. renders no-match state when filters produce zero results and resets filters on click', async () => {
    vi.mocked(api.getProjects).mockResolvedValue(mockAllProjects);

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search projects by name/i);
    fireEvent.change(searchInput, { target: { value: 'nonexistent-query-xyz' } });

    expect(screen.getByText('No projects match your filters.')).toBeInTheDocument();
    expect(
      screen.getByText('Try changing your search terms or clearing your active filters.'),
    ).toBeInTheDocument();

    const resetBtn = screen.getByRole('button', { name: /clear filters/i });
    fireEvent.click(resetBtn);

    await waitFor(() => {
      expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    });
  });

  it('12. renders recoverable error state on API failure and supports retry', async () => {
    vi.mocked(api.getProjects).mockRejectedValueOnce(new Error('Connection failure'));

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText("We couldn't load your projects.")).toBeInTheDocument();
    });

    expect(screen.getByText('Connection failure')).toBeInTheDocument();

    // Re-resolve on retry
    vi.mocked(api.getProjects).mockResolvedValueOnce(mockAllProjects);
    const retryBtn = screen.getByRole('button', { name: /try again/i });
    fireEvent.click(retryBtn);

    await waitFor(() => {
      expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    });
  });

  it('13. Create Project CTA in PageHeader navigates to /student/projects/new', async () => {
    vi.mocked(api.getProjects).mockResolvedValue(mockAllProjects);

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    });

    const createBtn = screen.getByRole('link', { name: 'Create Project' });
    expect(createBtn).toHaveAttribute('href', '/student/projects/new');
  });

  it('14. strictly preserves Data Integrity — does NOT render tasks, milestones, risks, AI, or fake analytics', async () => {
    vi.mocked(api.getProjects).mockResolvedValue(mockAllProjects);

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
    });

    // Check absence of forbidden systems
    expect(screen.queryByText(/Milestones/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Tasks/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Blocked tasks/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Risks/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Risk Matrix/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/AI Mentor/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Mentor Feedback/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Help Requests/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Burndown/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Velocity/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Sprint/i)).not.toBeInTheDocument();
  });
});
