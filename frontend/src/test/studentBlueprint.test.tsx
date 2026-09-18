import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
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
    retryBlueprintGeneration: vi.fn(),
    getBlueprintContent: vi.fn(),
    approveBlueprint: vi.fn(),
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
});
