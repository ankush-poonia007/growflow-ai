import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { StudentBlueprint } from '@/pages/Student/StudentBlueprint/StudentBlueprint';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import * as api from '@/lib/api';
import type {
  ProjectResponse,
  BlueprintStatusResponse,
  BlueprintContentResponse,
} from '@/lib/api/types';

vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api')>('@/lib/api');
  return {
    ...actual,
    getProject: vi.fn(),
    getBlueprintStatus: vi.fn(),
    startBlueprintGeneration: vi.fn(),
    retryBlueprintGeneration: vi.fn(),
    getBlueprintContent: vi.fn(),
    approveBlueprint: vi.fn(),
    subscribeBlueprintEvents: vi.fn(),
  };
});

const mockStudentAuthValue: AuthContextValue = {
  status: 'AUTHENTICATED',
  session: null,
  supabaseUser: null,
  user: {
    id: 'student-999',
    email: 'student@example.com',
    role: 'STUDENT',
    status: 'ACTIVE',
    fullName: 'Alex Vance',
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

const mockProjectReady: ProjectResponse = {
  id: 'proj-123',
  student_id: 'student-999',
  group_id: null,
  project_definition_id: null,
  source_definition_version_id: null,
  name: 'Distributed Climate Sensor Mesh',
  problem: 'Sparse terrestrial sensor telemetry in extreme climates.',
  proposed_solution: 'Solar-powered LoRa mesh network for field microclimate monitoring.',
  status: 'ACTIVE',
  current_phase: 'BLUEPRINT',
  health: 'HEALTHY',
  complexity: 'INTERMEDIATE',
  progress_percentage: 20,
  deadline: null,
  started_at: null,
  completed_at: null,
  created_at: '2026-09-10T08:00:00.000Z',
  updated_at: '2026-09-12T10:00:00.000Z',
};

const mockStatusGenerating: BlueprintStatusResponse = {
  blueprint_id: 'bp-123',
  project_id: 'proj-123',
  status: 'GENERATING',
  current_stage: 3,
  qa_status: 'PENDING',
  generation_progress: {
    completed_sections: ['project_profile', 'tech_stack', 'features'],
    total_sections: 10,
    in_progress_section: 'specifications',
  },
};

const mockStatusTerminalReady: BlueprintStatusResponse = {
  blueprint_id: 'bp-123',
  project_id: 'proj-123',
  status: 'READY_FOR_APPROVAL',
  current_stage: 10,
  qa_status: 'PASSED',
  qa_feedback: {
    score: 95,
    status: 'PASSED',
    evaluated_criteria: { architecture: 95 },
    strengths: ['Robust distributed architecture'],
    gaps: [],
    recommendations: [],
  },
  generation_progress: {
    completed_sections: [
      'project_profile',
      'tech_stack',
      'features',
      'specifications',
      'mvp',
      'duration',
      'risks',
      'tasks',
      'milestones',
      'readme',
    ],
    total_sections: 10,
  },
};

const mockContent: BlueprintContentResponse = {
  blueprint_id: 'bp-123',
  project_id: 'proj-123',
  status: 'READY_FOR_APPROVAL',
  qa_feedback: mockStatusTerminalReady.qa_feedback,
  content: {
    project_profile: {
      key: 'project_profile',
      title: 'Project Profile',
      summary: 'Summary',
      content: 'Profile details',
      is_generated: true,
      requires_attention: false,
    },
  },
};

function renderBlueprint() {
  return render(
    <AuthContext.Provider value={mockStudentAuthValue}>
      <MemoryRouter initialEntries={['/student/projects/proj-123/blueprint']}>
        <Routes>
          <Route
            path="/student/projects/:projectId/blueprint"
            element={<StudentBlueprint />}
          />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>
  );
}

describe('Phase 8 / Batch 4 — Frontend Background Jobs & SSE Reliability', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders Batch 2 loading state initially', async () => {
    vi.mocked(api.getProject).mockReturnValue(new Promise(() => {}));
    vi.mocked(api.getBlueprintStatus).mockReturnValue(new Promise(() => {}));

    renderBlueprint();

    expect(screen.getByTestId('blueprint-loading-state')).toBeInTheDocument();
    expect(screen.getByText('Loading Blueprint Workspace...')).toBeInTheDocument();
  });

  it('renders Batch 2 critical error state with retry button on initial load failure', async () => {
    vi.mocked(api.getProject).mockRejectedValue(new Error('Network error: server unreachable'));
    vi.mocked(api.getBlueprintStatus).mockRejectedValue(new Error('Network error: server unreachable'));

    renderBlueprint();

    await waitFor(() => {
      expect(screen.getByTestId('blueprint-error-state')).toBeInTheDocument();
    });

    expect(screen.getByText('Unable to Load Blueprint Workspace')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry loading/i })).toBeInTheDocument();
  });

  it('consumes SSE progress updates and displays actual section progress', async () => {
    vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
    vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusGenerating);

    let sseCallback: ((data: BlueprintStatusResponse) => void) | null = null;
    vi.mocked(api.subscribeBlueprintEvents).mockImplementation(
      async (_pid, onUpdate, _onError) => {
        sseCallback = onUpdate;
        return () => {};
      }
    );

    renderBlueprint();

    await waitFor(() => {
      expect(screen.getByText('Generating Architectural Blueprint')).toBeInTheDocument();
    });

    expect(screen.getByText('30%')).toBeInTheDocument();
    expect(screen.getByText('3 of 10')).toBeInTheDocument();

    // Emit live SSE update with advanced progress (50%)
    act(() => {
      if (sseCallback) {
        sseCallback({
          ...mockStatusGenerating,
          generation_progress: {
            completed_sections: [
              'project_profile',
              'tech_stack',
              'features',
              'specifications',
              'mvp',
            ],
            total_sections: 10,
            in_progress_section: 'duration',
          },
        });
      }
    });

    await waitFor(() => {
      expect(screen.getByText('50%')).toBeInTheDocument();
      expect(screen.getByText('5 of 10')).toBeInTheDocument();
    });
  });

  it('terminal SSE event closes stream and fetches full content', async () => {
    vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
    vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusGenerating);
    vi.mocked(api.getBlueprintContent).mockResolvedValue(mockContent);

    let sseCallback: ((data: BlueprintStatusResponse) => void) | null = null;
    const closeMock = vi.fn();
    vi.mocked(api.subscribeBlueprintEvents).mockImplementation(
      async (_pid, onUpdate, _onError) => {
        sseCallback = onUpdate;
        return closeMock;
      }
    );

    renderBlueprint();

    await waitFor(() => {
      expect(screen.getByText('Generating Architectural Blueprint')).toBeInTheDocument();
    });

    // Emit terminal SSE event
    act(() => {
      if (sseCallback) {
        sseCallback(mockStatusTerminalReady);
      }
    });

    await waitFor(() => {
      expect(api.getBlueprintContent).toHaveBeenCalledWith('proj-123');
      expect(closeMock).toHaveBeenCalled();
      expect(screen.getByText('Autonomous Judge & QA Scorecard')).toBeInTheDocument();
    });
  });

  it('duplicate identical SSE observations are idempotent and do not trigger extra side-effects', async () => {
    vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
    vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusGenerating);

    let sseCallback: ((data: BlueprintStatusResponse) => void) | null = null;
    vi.mocked(api.subscribeBlueprintEvents).mockImplementation(
      async (_pid, onUpdate) => {
        sseCallback = onUpdate;
        return () => {};
      }
    );

    renderBlueprint();

    await waitFor(() => {
      expect(screen.getByText('Generating Architectural Blueprint')).toBeInTheDocument();
    });

    vi.mocked(api.getBlueprintContent).mockClear();

    // Emit 3 identical progress events
    act(() => {
      if (sseCallback) {
        sseCallback(mockStatusGenerating);
        sseCallback(mockStatusGenerating);
        sseCallback(mockStatusGenerating);
      }
    });

    // Idempotent: No content refetch, remains safely in generating state
    expect(api.getBlueprintContent).not.toHaveBeenCalled();
    expect(screen.getByText('Generating Architectural Blueprint')).toBeInTheDocument();
  });

  it('SSE failure transparently falls back to polling', async () => {
    vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
    vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusGenerating);

    let sseErrorCallback: ((err: any) => void) | null = null;
    vi.mocked(api.subscribeBlueprintEvents).mockImplementation(
      async (_pid, _onUpdate, onError) => {
        sseErrorCallback = onError || null;
        return () => {};
      }
    );

    renderBlueprint();

    await waitFor(() => {
      expect(screen.getByText('Generating Architectural Blueprint')).toBeInTheDocument();
    });

    // Clear initial call
    vi.mocked(api.getBlueprintStatus).mockClear();

    // Trigger SSE error callback
    act(() => {
      if (sseErrorCallback) {
        sseErrorCallback(new Error('SSE connection terminated by proxy'));
      }
    });

    // Expect transparent fallback to polling
    await waitFor(() => {
      expect(api.getBlueprintStatus).toHaveBeenCalledWith('proj-123');
    });
  });

  it('displays actionable 3-minute stale generation safeguard with retry option', async () => {
    vi.useFakeTimers();

    vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
    vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusGenerating);
    vi.mocked(api.retryBlueprintGeneration).mockResolvedValue(mockStatusGenerating);
    vi.mocked(api.subscribeBlueprintEvents).mockResolvedValue(() => {});

    renderBlueprint();

    // Fast-forward initial promises
    await act(async () => {
      await vi.advanceTimersByTimeAsync(100);
    });

    expect(screen.queryByTestId('stale-generation-safeguard')).not.toBeInTheDocument();

    // Advance 3 minutes (180,000 ms) + interval tick
    await act(async () => {
      await vi.advanceTimersByTimeAsync(182000);
    });

    // Safeguard must be visible
    expect(screen.getByTestId('stale-generation-safeguard')).toBeInTheDocument();
    expect(
      screen.getByText(/Blueprint synthesis is taking longer than usual \(over 3 minutes\)/)
    ).toBeInTheDocument();

    // Click retry inside safeguard
    const retryBtn = screen.getByRole('button', { name: /retry generation/i });
    await act(async () => {
      fireEvent.click(retryBtn);
    });

    expect(api.retryBlueprintGeneration).toHaveBeenCalledWith('proj-123', undefined);
  });
});
