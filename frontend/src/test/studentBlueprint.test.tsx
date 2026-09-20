import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { StudentBlueprint } from '@/pages/Student/StudentBlueprint/StudentBlueprint';
import { AuthHeader } from '@/components/navigation/AuthHeader';
import { Sidebar } from '@/components/navigation/Sidebar';
import { MobileWorkspaceDrawer } from '@/components/navigation/MobileWorkspaceDrawer';
import { AssessmentResultView } from '@/pages/Student/StudentAssessment/components/AssessmentResultView';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import * as api from '@/lib/api';
import * as apiClient from '@/lib/api/client';
import type {
  ProjectResponse,
  BlueprintStatusResponse,
  BlueprintContentResponse,
  AssessmentResultResponse,
} from '@/lib/api/types';

vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api')>('@/lib/api');
  return {
    ...actual,
    getProject: vi.fn(),
    getBlueprintStatus: vi.fn(),
    startBlueprintGeneration: vi.fn(),
    cancelBlueprintGeneration: vi.fn(),
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
  proposed_solution: 'Mesh-routed low-power sensors with edge anomaly detection.',
  complexity: 'INTERMEDIATE',
  current_phase: 'ASSESSMENT',
  health: 'HEALTHY',
  progress_percentage: 25,
  status: 'ACTIVE',
  deadline: '2026-12-01T00:00:00.000Z',
  started_at: '2026-09-01T00:00:00.000Z',
  completed_at: null,
  created_at: '2026-09-01T00:00:00.000Z',
  updated_at: '2026-09-10T00:00:00.000Z',
};

const mockStatusNotStarted: BlueprintStatusResponse = {
  blueprint_id: 'bp-123',
  project_id: 'proj-123',
  status: 'NOT_STARTED',
  current_stage: 3,
  qa_status: 'PENDING',
  qa_feedback: null,
  generation_progress: {
    completed_sections: [],
    total_sections: 10,
    in_progress_section: null,
    failed_sections: [],
  },
  active_job: null,
  created_at: null,
  updated_at: null,
};

const mockStatusGenerating: BlueprintStatusResponse = {
  blueprint_id: 'bp-123',
  project_id: 'proj-123',
  status: 'GENERATING',
  current_stage: 3,
  qa_status: 'PENDING',
  qa_feedback: null,
  generation_progress: {
    completed_sections: ['project_profile', 'tech_stack', 'features'],
    total_sections: 10,
    in_progress_section: 'specifications',
    failed_sections: [],
  },
  active_job: {
    id: 'job-1',
    job_type: 'FULL_GENERATION',
    status: 'RUNNING',
    failed_sections: [],
    created_at: '2026-09-13T10:00:00.000Z',
  },
};

const mockStatusFailed: BlueprintStatusResponse = {
  blueprint_id: 'bp-123',
  project_id: 'proj-123',
  status: 'FAILED',
  current_stage: 3,
  qa_status: 'FAILED',
  qa_feedback: null,
  generation_progress: {
    completed_sections: ['project_profile', 'tech_stack', 'features'],
    total_sections: 10,
    in_progress_section: null,
    failed_sections: ['specifications'],
  },
  active_job: {
    id: 'job-1',
    job_type: 'FULL_GENERATION',
    status: 'FAILED',
    error_message: 'OpenRouter timeout while formulating specifications section.',
    failed_sections: ['specifications'],
    created_at: '2026-09-13T10:00:00.000Z',
  },
};

const mockStatusCompleted: BlueprintStatusResponse = {
  blueprint_id: 'bp-123',
  project_id: 'proj-123',
  status: 'COMPLETED',
  current_stage: 3,
  qa_status: 'PASSED',
  qa_feedback: {
    score: 92,
    status: 'PASSED',
    evaluated_criteria: {
      completeness: 95,
      technical_feasibility: 90,
      architectural_soundness: 92,
      risk_coverage: 88,
      task_granularity: 94,
    },
    strengths: [
      'Comprehensive architecture covering all distributed ingestion requirements.',
      'Explicit boundary between edge hardware and cloud aggregation.',
    ],
    gaps: [],
    recommendations: [
      'Use TLS mutual authentication for remote sensor endpoints.',
    ],
    evaluated_at: '2026-09-13T10:05:00.000Z',
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
    in_progress_section: null,
    failed_sections: [],
  },
};

const mockBlueprintContent: BlueprintContentResponse = {
  blueprint_id: 'bp-123',
  project_id: 'proj-123',
  status: 'COMPLETED',
  content: {
    project_profile: {
      project_name: 'Distributed Climate Sensor Mesh',
      summary: 'Autonomous telemetry network for real-time microclimate modeling.',
    },
    tech_stack: {
      primary_languages: ['Rust', 'TypeScript', 'Python'],
      frameworks: ['FastAPI', 'React', 'Tokio'],
      storage: ['TimescaleDB', 'PostgreSQL'],
    },
    features: {
      core_modules: ['Edge Telemetry Node', 'Mesh Routing Gateway', 'Cloud Aggregator'],
    },
    specifications: {
      protocols: ['MQTT over TLS', 'CoAP'],
    },
    mvp: {
      scope: 'Deploy 5 node simulation with central ingest.',
    },
    duration: {
      total_weeks: 8,
    },
    risks: {
      high_priority_risks: ['Sensor power budget exhaustion under adverse solar conditions.'],
    },
    tasks: {
      initial_tasks: ['Firmware skeleton setup', 'MQTT broker integration'],
    },
    milestones: {
      key_milestones: ['Milestone 1: Simulation Passed', 'Milestone 2: Hardware Ingest'],
    },
    readme: '# Distributed Climate Sensor Mesh\n\nComprehensive setup guide.',
  },
  qa_feedback: mockStatusCompleted.qa_feedback,
};

function renderWithProviders(ui: React.ReactNode, initialEntries = ['/student/projects/proj-123/blueprint']) {
  return render(
    <AuthContext.Provider value={mockStudentAuthValue}>
      <MemoryRouter initialEntries={initialEntries}>
        <Routes>
          <Route path="/student/projects/:projectId/blueprint" element={ui} />
          <Route path="/student/projects/:projectId/profile" element={<div>Project Profile Page</div>} />
          <Route path="/student/projects/:projectId/assessment" element={<div>Assessment Page</div>} />
          <Route path="/profile" element={<div>Student Profile Placeholder</div>} />
          <Route path="/settings" element={<div>Workspace Settings Placeholder</div>} />
          <Route path="/" element={<div>Public Landing Page</div>} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>
  );
}

describe('Student Blueprint Workflow (S12–S14) & Global Navigation Corrections', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(apiClient, 'getUnreadNotificationCount').mockResolvedValue({ unread_count: 0 });
    vi.spyOn(apiClient, 'getNotifications').mockResolvedValue([]);
  });

  describe('Global Workspace Navigation Corrections', () => {
    it('GrowFlow brand in AuthHeader links to public Landing page ("/")', () => {
      render(
        <AuthContext.Provider value={mockStudentAuthValue}>
          <MemoryRouter initialEntries={['/student/dashboard']}>
            <AuthHeader onToggleMobileNav={vi.fn()} isMobileNavOpen={false} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const brandLink = screen.getByLabelText('GrowFlow Home');
      expect(brandLink).toBeInTheDocument();
      expect(brandLink.getAttribute('href')).toBe('/');
    });

    it('Global Search opens accessible modal, autofocuses input, and closes on Escape', () => {
      render(
        <AuthContext.Provider value={mockStudentAuthValue}>
          <MemoryRouter initialEntries={['/student/dashboard']}>
            <AuthHeader onToggleMobileNav={vi.fn()} isMobileNavOpen={false} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const searchBtn = screen.getByLabelText('Search workspace');
      fireEvent.click(searchBtn);

      const searchInput = screen.getByPlaceholderText('Search build workspace...');
      expect(searchInput).toBeInTheDocument();
      expect(screen.getByRole('dialog', { name: /global workspace search/i })).toBeInTheDocument();
      expect(screen.getByText(/BUILD Workspace Search/i)).toBeInTheDocument();

      // Type search query
      fireEvent.change(searchInput, { target: { value: 'Rust' } });
      const clearBtn = screen.getByLabelText('Clear query');
      expect(clearBtn).toBeInTheDocument();

      // Clear search
      fireEvent.click(clearBtn);
      expect(screen.getByText(/BUILD Workspace Search/i)).toBeInTheDocument();

      // Escape key closes modal
      fireEvent.keyDown(window, { key: 'Escape' });
      expect(screen.queryByPlaceholderText('Search build workspace...')).not.toBeInTheDocument();
    });

    it('Global Notifications popover opens with truthful empty state and closes on Escape', async () => {
      render(
        <AuthContext.Provider value={mockStudentAuthValue}>
          <MemoryRouter initialEntries={['/student/dashboard']}>
            <AuthHeader onToggleMobileNav={vi.fn()} isMobileNavOpen={false} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const notifBtn = screen.getByLabelText('Notifications');
      fireEvent.click(notifBtn);

      expect(await screen.findByText("You're all caught up")).toBeInTheDocument();
      expect(screen.getByText(/No notifications right now/)).toBeInTheDocument();

      // Close on Escape
      fireEvent.keyDown(window, { key: 'Escape' });
      expect(screen.queryByText("You're all caught up")).not.toBeInTheDocument();
    });

    it('Sidebar provides Profile link (/profile), Settings button (/settings), and collapse toggle', () => {
      const toggleCollapse = vi.fn();
      render(
        <AuthContext.Provider value={mockStudentAuthValue}>
          <MemoryRouter initialEntries={['/student/dashboard']}>
            <Sidebar isCollapsed={false} onToggleCollapse={toggleCollapse} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const profileLink = screen.getByLabelText('Student Profile');
      expect(profileLink).toBeInTheDocument();
      expect(profileLink.getAttribute('href')).toBe('/profile');
      expect(screen.getByText('AV')).toBeInTheDocument(); // Alex Vance initials

      const settingsLink = screen.getByLabelText('Workspace Settings');
      expect(settingsLink).toBeInTheDocument();
      expect(settingsLink.getAttribute('href')).toBe('/settings');

      const collapseBtn = screen.getByLabelText('Collapse sidebar');
      fireEvent.click(collapseBtn);
      expect(toggleCollapse).toHaveBeenCalledTimes(1);
    });

    it('MobileWorkspaceDrawer includes Profile and Settings navigation items', () => {
      const closeDrawer = vi.fn();
      render(
        <AuthContext.Provider value={mockStudentAuthValue}>
          <MemoryRouter initialEntries={['/student/dashboard']}>
            <MobileWorkspaceDrawer isOpen={true} onClose={closeDrawer} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const profileLink = screen.getByRole('link', { name: /profile/i });
      expect(profileLink).toBeInTheDocument();
      expect(profileLink.getAttribute('href')).toBe('/profile');

      const settingsLink = screen.getByRole('link', { name: /settings/i });
      expect(settingsLink).toBeInTheDocument();
      expect(settingsLink.getAttribute('href')).toBe('/settings');
    });
  });

  describe('S11 Assessment Result -> S12 Blueprint Transition', () => {
    it('renders "Generate Project Blueprint" CTA on completed S11 Assessment Result view', () => {
      const mockResult: AssessmentResultResponse = {
        id: 'res-1',
        assessment_id: 'assess-1',
        project_instance_id: 'proj-123',
        overall_score: 84,
        readiness_tier: 'HIGH',
        skill_level: 'INTERMEDIATE',
        project_complexity: 'MODERATE',
        alignment: 'STRONGLY_ALIGNED',
        technical_confidence: 'HIGH',
        learning_depth: 'DEEP',
        recommended_focus: 'System Architecture',
        dimension_scores: { architecture: 85, security: 80 },
        summary: 'Excellent foundation.',
        identified_gaps: [],
        recommendations: [],
        created_at: '2026-09-13T09:00:00.000Z',
      };

      render(
        <MemoryRouter>
          <AssessmentResultView projectId="proj-123" result={mockResult} />
        </MemoryRouter>
      );

      const blueprintBtn = screen.getByRole('link', { name: /generate project blueprint/i });
      expect(blueprintBtn).toBeInTheDocument();
      expect(blueprintBtn.getAttribute('href')).toBe('/student/projects/proj-123/blueprint');
    });
  });

  describe('Stage 3 Blueprint Workflow (S12–S14)', () => {
    it('shows prerequisite notice when project is still in IDEA phase without completed assessment', async () => {
      const mockIdeaProject: ProjectResponse = {
        ...mockProjectReady,
        current_phase: 'IDEA',
      };

      vi.mocked(api.getProject).mockResolvedValue(mockIdeaProject);
      vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusNotStarted);

      renderWithProviders(<StudentBlueprint />);

      await waitFor(() => {
        expect(screen.getByText('Complete Stage 2 Assessment First')).toBeInTheDocument();
      });

      expect(screen.getByRole('link', { name: /go to project assessment/i })).toBeInTheDocument();
    });

    it('renders S12 BlueprintNotStarted with 10 canonical sections and starts generation', async () => {
      vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
      vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusNotStarted);
      vi.mocked(api.startBlueprintGeneration).mockResolvedValue(mockStatusGenerating);

      renderWithProviders(<StudentBlueprint />);

      await waitFor(() => {
        expect(screen.getByText('Architectural Blueprint Synthesis')).toBeInTheDocument();
      });

      // Check for canonical sections preview
      expect(screen.getByText('Project Profile & Domain Context')).toBeInTheDocument();
      expect(screen.getByText('Production README & Setup Guide')).toBeInTheDocument();

      const startBtn = screen.getByRole('button', { name: /generate project blueprint/i });
      fireEvent.click(startBtn);

      await waitFor(() => {
        expect(api.startBlueprintGeneration).toHaveBeenCalledWith('proj-123');
      });
    });

    it('renders S12 BlueprintGeneratingProgress during active synthesis', async () => {
      vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
      vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusGenerating);

      renderWithProviders(<StudentBlueprint />);

      await waitFor(() => {
        expect(screen.getByText('Generating Architectural Blueprint')).toBeInTheDocument();
      });

      expect(screen.getByText('30%')).toBeInTheDocument();
      expect(screen.getByText('3 of 10')).toBeInTheDocument();
    });

    it('renders S13 BlueprintFailureView on synthesis failure and triggers targeted recovery', async () => {
      vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
      vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusFailed);
      vi.mocked(api.retryBlueprintGeneration).mockResolvedValue(mockStatusGenerating);

      renderWithProviders(<StudentBlueprint />);

      await waitFor(() => {
        expect(screen.getByText('Synthesis Interrupted')).toBeInTheDocument();
      });

      expect(
        screen.getByText(/OpenRouter timeout while formulating specifications section/)
      ).toBeInTheDocument();
      expect(screen.getByText(/State Preservation Active/)).toBeInTheDocument();

      const retryBtn = screen.getByRole('button', { name: /retry affected sections/i });
      fireEvent.click(retryBtn);

      await waitFor(() => {
        expect(api.retryBlueprintGeneration).toHaveBeenCalledWith('proj-123', {
          target_output_key: 'specifications',
        });
      });
    });

    it('renders S14 BlueprintReviewApproval with QA Scorecard, section tabs, and approves stage', async () => {
      vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
      vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusCompleted);
      vi.mocked(api.getBlueprintContent).mockResolvedValue(mockBlueprintContent);
      vi.mocked(api.approveBlueprint).mockResolvedValue({
        blueprint_id: 'bp-123',
        project_id: 'proj-123',
        status: 'APPROVED',
        approved_at: '2026-09-13T10:10:00.000Z',
        message: 'Blueprint approved successfully.',
      });

      renderWithProviders(<StudentBlueprint />);

      await waitFor(() => {
        expect(screen.getByText('Autonomous Judge & QA Scorecard')).toBeInTheDocument();
      });

      // Score and PASS badge
      expect(screen.getByText('92')).toBeInTheDocument();
      expect(screen.getByText('QA STATUS: PASS')).toBeInTheDocument();

      // Section tabs
      expect(screen.getByRole('tab', { name: /technical stack/i })).toBeInTheDocument();

      // Approve CTA
      const approveBtn = screen.getByRole('button', { name: /approve blueprint & advance stage/i });
      fireEvent.click(approveBtn);

      await waitFor(() => {
        expect(api.approveBlueprint).toHaveBeenCalledWith('proj-123');
      });
    });
  });

  describe('Gate 09 — Unit 6: Student Blueprint Generation & Monitoring Experience', () => {
    // Test 1 — Existing initial state
    it('Test 1: renders BlueprintNotStarted correctly with 10 canonical sections', async () => {
      vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
      vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusNotStarted);

      renderWithProviders(<StudentBlueprint />);

      await waitFor(() => {
        expect(screen.getByText('Architectural Blueprint Synthesis')).toBeInTheDocument();
      });

      expect(screen.getByText('Project Profile & Domain Context')).toBeInTheDocument();
      expect(screen.getByText('Technical Stack & Architecture')).toBeInTheDocument();
      expect(screen.getByText('Core Features & System Modules')).toBeInTheDocument();
      expect(screen.getByText('Technical Specifications & Data Models')).toBeInTheDocument();
      expect(screen.getByText('MVP Scope & Validation Criteria')).toBeInTheDocument();
      expect(screen.getByText('Timeline & Sprint Duration')).toBeInTheDocument();
      expect(screen.getByText('Technical Risks & Mitigations')).toBeInTheDocument();
      expect(screen.getByText('Granular Work Breakdown (Tasks)')).toBeInTheDocument();
      expect(screen.getByText('Stage Milestones & Gate Deliverables')).toBeInTheDocument();
      expect(screen.getByText('Production README & Setup Guide')).toBeInTheDocument();

      expect(screen.getByRole('button', { name: /generate project blueprint/i })).toBeInTheDocument();
    });

    // Test 2 — Start generation
    it('Test 2: start generation invokes API and begins SSE tracking', async () => {
      vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
      vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusNotStarted);
      vi.mocked(api.startBlueprintGeneration).mockResolvedValue(mockStatusGenerating);
      vi.mocked(api.subscribeBlueprintEvents).mockResolvedValue(() => {});

      renderWithProviders(<StudentBlueprint />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /generate project blueprint/i })).toBeInTheDocument();
      });

      fireEvent.click(screen.getByRole('button', { name: /generate project blueprint/i }));

      await waitFor(() => {
        expect(api.startBlueprintGeneration).toHaveBeenCalledWith('proj-123');
      });

      await waitFor(() => {
        expect(api.subscribeBlueprintEvents).toHaveBeenCalledWith(
          'proj-123',
          expect.any(Function),
          expect.any(Function)
        );
      });
    });

    // Test 3 — Live progress
    it('Test 3: reflects live SSE updates with progress percent and active step', async () => {
      vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
      vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusGenerating);

      let sseCallback: ((data: BlueprintStatusResponse) => void) | null = null;
      vi.mocked(api.subscribeBlueprintEvents).mockImplementation((_pid, onUpdate) => {
        sseCallback = onUpdate;
        return Promise.resolve(() => {});
      });

      renderWithProviders(<StudentBlueprint />);

      await waitFor(() => {
        expect(screen.getByText('Generating Architectural Blueprint')).toBeInTheDocument();
      });

      // Simulate live SSE event
      act(() => {
        if (sseCallback) {
          sseCallback({
            ...mockStatusGenerating,
            current_step: 'tasks',
            progress_percent: 65,
            generation_progress: {
              completed_sections: [
                'project_profile',
                'tech_stack',
                'features',
                'mvp',
                'specifications',
                'duration',
                'risks',
              ],
              total_sections: 10,
              in_progress_section: 'tasks',
            },
          });
        }
      });

      await waitFor(() => {
        expect(screen.getByText('65%')).toBeInTheDocument();
      });
      expect(screen.getByText('7 of 10')).toBeInTheDocument();
    });

    // Test 4 — Parallel group
    it('Test 4: renders Technology, Features, and MVP grouped in parallel synthesis', async () => {
      vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
      vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusGenerating);

      renderWithProviders(<StudentBlueprint />);

      await waitFor(() => {
        expect(screen.getByTestId('parallel-synthesis-group')).toBeInTheDocument();
      });

      const parallelGroup = screen.getByTestId('parallel-synthesis-group');
      expect(parallelGroup).toHaveTextContent('Core Architecture & Scope');
      expect(parallelGroup).toHaveTextContent('Parallel Synthesis');

      // Verify Technology, Features, MVP sub-items appear in the parallel group
      expect(parallelGroup).toHaveTextContent('Technology');
      expect(parallelGroup).toHaveTextContent('Tech Stack & Architecture');
      expect(parallelGroup).toHaveTextContent('Features');
      expect(parallelGroup).toHaveTextContent('Core Features & Modules');
      expect(parallelGroup).toHaveTextContent('MVP');
      expect(parallelGroup).toHaveTextContent('MVP Scope & Validation');
    });

    // Test 5 — QA/Judge
    it('Test 5: renders QA/Judge step with score and evaluation status', async () => {
      vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
      vi.mocked(api.getBlueprintStatus).mockResolvedValue({
        ...mockStatusGenerating,
        current_step: 'qa_judge',
        qa_score: 88,
        qa_status: 'IN_REVIEW',
        progress_percent: 95,
      });

      renderWithProviders(<StudentBlueprint />);

      await waitFor(() => {
        expect(screen.getByTestId('qa-judge-step')).toBeInTheDocument();
      });

      const qaStep = screen.getByTestId('qa-judge-step');
      expect(qaStep).toHaveTextContent('Architectural QA & Schema Validation');
      expect(qaStep).toHaveTextContent('(Score: 88/100)');
      expect(qaStep).toHaveTextContent('Evaluating...');
    });

    // Test 6 — Targeted regeneration
    it('Test 6: renders targeted refinement notice with attempt number and dynamic section target', async () => {
      vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
      vi.mocked(api.getBlueprintStatus).mockResolvedValue({
        ...mockStatusGenerating,
        regeneration_attempt: 1,
        regeneration_target: 'timeline',
      });

      renderWithProviders(<StudentBlueprint />);

      await waitFor(() => {
        expect(screen.getByTestId('targeted-refinement-notice')).toBeInTheDocument();
      });

      const notice = screen.getByTestId('targeted-refinement-notice');
      expect(notice).toHaveTextContent('Targeted Refinement in Progress');
      expect(notice).toHaveTextContent('(Attempt 1 of 2)');
      expect(notice).toHaveTextContent('Timeline & Sprint Duration');
      expect(notice).toHaveTextContent('Upstream sections remain preserved while this section is being refined.');
    });

    it('Test 6b: handles non-timeline regeneration target dynamically without hardcoding', async () => {
      vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
      vi.mocked(api.getBlueprintStatus).mockResolvedValue({
        ...mockStatusGenerating,
        regeneration_attempt: 2,
        regeneration_target: 'risks',
      });

      renderWithProviders(<StudentBlueprint />);

      await waitFor(() => {
        expect(screen.getByTestId('targeted-refinement-notice')).toBeInTheDocument();
      });

      const notice = screen.getByTestId('targeted-refinement-notice');
      expect(notice).toHaveTextContent('(Attempt 2 of 2)');
      expect(notice).toHaveTextContent('Technical Risks & Mitigations');
    });

    // Test 7 — Cancellation modal
    it('Test 7: opens cancellation modal, allows dismissing, and confirms cancellation', async () => {
      vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
      vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusGenerating);
      vi.mocked(api.cancelBlueprintGeneration).mockResolvedValue({
        ...mockStatusGenerating,
        status: 'CANCELLED',
      });

      renderWithProviders(<StudentBlueprint />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /cancel generation/i })).toBeInTheDocument();
      });

      // Click "Cancel Generation"
      fireEvent.click(screen.getByRole('button', { name: /cancel generation/i }));

      // Modal should open
      const modal = screen.getByRole('dialog');
      expect(modal).toBeInTheDocument();
      expect(screen.getByText('Cancel Blueprint Generation?')).toBeInTheDocument();
      expect(
        screen.getByText(
          'Are you sure you want to stop generation? Any uncommitted architectural sections from this run will be discarded.'
        )
      ).toBeInTheDocument();

      // Click "Keep Generating" -> modal closes without calling API
      fireEvent.click(screen.getByRole('button', { name: /keep generating/i }));
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      expect(api.cancelBlueprintGeneration).not.toHaveBeenCalled();

      // Re-open and confirm cancellation
      fireEvent.click(screen.getByRole('button', { name: /cancel generation/i }));
      fireEvent.click(screen.getByRole('button', { name: /yes, cancel generation/i }));

      await waitFor(() => {
        expect(api.cancelBlueprintGeneration).toHaveBeenCalledWith('proj-123');
      });
    });

    // Test 8 — Cancellation completion
    it('Test 8: renders BlueprintCancelledView when status is CANCELLED', async () => {
      const mockStatusCancelled: BlueprintStatusResponse = {
        blueprint_id: 'bp-123',
        project_id: 'proj-123',
        status: 'CANCELLED',
        current_stage: 3,
        qa_status: 'PENDING',
        generation_progress: {
          completed_sections: [],
          total_sections: 10,
        },
      };

      vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
      vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusCancelled);

      renderWithProviders(<StudentBlueprint />);

      await waitFor(() => {
        expect(screen.getByTestId('blueprint-cancelled-view')).toBeInTheDocument();
      });

      expect(screen.getByText('Blueprint Generation Cancelled')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /start new generation/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /return to project/i })).toBeInTheDocument();
    });

    // Test 9 — Cancellation race
    it('Test 9: honors terminal completion over late CANCELLED event during cancellation race', async () => {
      vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
      vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusGenerating);
      vi.mocked(api.getBlueprintContent).mockResolvedValue(mockBlueprintContent);

      let sseCallback: ((data: BlueprintStatusResponse) => void) | null = null;
      vi.mocked(api.subscribeBlueprintEvents).mockImplementation((_pid, onUpdate) => {
        sseCallback = onUpdate;
        return Promise.resolve(() => {});
      });

      // Cancellation request delayed
      vi.mocked(api.cancelBlueprintGeneration).mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(
              () =>
                resolve({
                  ...mockStatusGenerating,
                  status: 'CANCELLED',
                }),
              50
            );
          })
      );

      renderWithProviders(<StudentBlueprint />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /cancel generation/i })).toBeInTheDocument();
      });

      // User initiates cancellation
      fireEvent.click(screen.getByRole('button', { name: /cancel generation/i }));
      fireEvent.click(screen.getByRole('button', { name: /yes, cancel generation/i }));

      // Backend finishes synthesis first with READY_FOR_APPROVAL
      act(() => {
        if (sseCallback) {
          sseCallback({
            ...mockStatusCompleted,
            status: 'READY_FOR_APPROVAL',
          });
        }
      });

      // Even if CANCELLED arrives afterwards, READY_FOR_APPROVAL wins
      await waitFor(() => {
        expect(screen.getByText('Autonomous Judge & QA Scorecard')).toBeInTheDocument();
      });
      expect(screen.queryByTestId('blueprint-cancelled-view')).not.toBeInTheDocument();
    });

    // Test 10 — SSE fallback
    it('Test 10: transparently falls back to polling when SSE subscription fails', async () => {
      vi.mocked(api.getProject).mockResolvedValue(mockProjectReady);
      vi.mocked(api.getBlueprintStatus).mockResolvedValue(mockStatusGenerating);

      vi.mocked(api.subscribeBlueprintEvents).mockImplementation((_pid, _onUpdate, onError) => {
        if (onError) onError(new Error('SSE connection failed'));
        return Promise.reject(new Error('SSE connection failed'));
      });

      renderWithProviders(<StudentBlueprint />);

      await waitFor(() => {
        expect(screen.getByText('Generating Architectural Blueprint')).toBeInTheDocument();
      });

      // Polling fallback called getBlueprintStatus
      await waitFor(() => {
        expect(api.getBlueprintStatus).toHaveBeenCalledWith('proj-123');
      });
    });

    // Test 11 — Malformed event
    it('Test 11: malformed SSE event data does not crash client stream', async () => {
      // Test subscribeBlueprintEvents handling of malformed event data
      interface MockESListener {
        (event: { data: string }): void;
      }
      const mockEventSourceInstances: MockEventSource[] = [];
      const originalEventSource = window.EventSource;

      class MockEventSource {
        url: string;
        listeners: Record<string, MockESListener[]> = {};
        onerror: ((err: unknown) => void) | null = null;

        constructor(url: string) {
          this.url = url;
          mockEventSourceInstances.push(this);
        }

        addEventListener(type: string, listener: MockESListener) {
          if (!this.listeners[type]) this.listeners[type] = [];
          this.listeners[type].push(listener);
        }

        close() {}
      }

      window.EventSource = MockEventSource as unknown as typeof EventSource;

      try {
        const onUpdate = vi.fn();
        const onError = vi.fn();

        const unsubscribe = await apiClient.subscribeBlueprintEvents('proj-123', onUpdate, onError);
        const esInstance = mockEventSourceInstances[0];

        // Emit malformed JSON
        const updateListeners = esInstance.listeners['update'] || [];
        expect(updateListeners.length).toBeGreaterThan(0);

        // This should not throw or crash
        expect(() => {
          updateListeners[0]({ data: 'INVALID_JSON{{{' });
        }).not.toThrow();

        // onUpdate should NOT be called with invalid JSON
        expect(onUpdate).not.toHaveBeenCalled();

        // Stream should still be alive and accept valid JSON next
        updateListeners[0]({
          data: JSON.stringify(mockStatusGenerating),
        });
        expect(onUpdate).toHaveBeenCalledWith(mockStatusGenerating);

        unsubscribe();
      } finally {
        window.EventSource = originalEventSource;
      }
    });

    // Test 12 — TypeScript types
    it('Test 12: confirms BlueprintStatus and BlueprintStatusResponse accept all Unit 5 metadata', () => {
      const fullResponse: BlueprintStatusResponse = {
        blueprint_id: 'bp-test',
        project_id: 'proj-test',
        status: 'CANCELLED',
        current_stage: 3,
        qa_status: 'PASSED',
        generation_progress: {
          completed_sections: ['project_profile'],
          total_sections: 10,
          in_progress_section: 'tech_stack',
          failed_sections: [],
        },
        event_id: 'event-001',
        event_type: 'job.started',
        event_version: '1.0.0',
        job_id: 'job-123',
        generation_number: 1,
        current_step: 'technology',
        progress_percent: 25,
        regeneration_attempt: 1,
        regeneration_target: 'timeline',
        qa_score: 85,
        error_message: null,
        failed_output_key: null,
      };

      expect(fullResponse.status).toBe('CANCELLED');
      expect(fullResponse.progress_percent).toBe(25);
      expect(fullResponse.regeneration_target).toBe('timeline');
    });
  });
});
