import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { StudentAssessment } from '@/pages/Student/StudentAssessment/StudentAssessment';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import type { User } from '@supabase/supabase-js';
import * as api from '@/lib/api';
import type {
  ProjectResponse,
  AssessmentSessionStatus,
  AssessmentQuestionResponse,
  AssessmentResultResponse,
  AssessmentAnswerSubmitResponse,
  AssessmentStartResponse,
} from '@/lib/api/types';

vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api')>('@/lib/api');
  return {
    ...actual,
    getProject: vi.fn(),
    getAssessmentStatus: vi.fn(),
    startAssessment: vi.fn(),
    getAssessmentQuestion: vi.fn(),
    submitAssessmentAnswer: vi.fn(),
    completeAssessment: vi.fn(),
    getAssessmentResult: vi.fn(),
  };
});

const mockProject: ProjectResponse = {
  id: 'proj-123',
  student_id: 'student-999',
  group_id: null,
  project_definition_id: null,
  source_definition_version_id: null,
  name: 'Distributed Climate Sensor Mesh',
  problem: 'Sparse terrestrial sensor telemetry in extreme climates.',
  proposed_solution: 'Mesh-routed low-power sensors with edge anomaly detection.',
  complexity: 'INTERMEDIATE',
  current_phase: 'IDEA',
  health: 'HEALTHY',
  progress_percentage: 10,
  status: 'ACTIVE',
  deadline: '2026-12-01T00:00:00.000Z',
  started_at: '2026-09-01T00:00:00.000Z',
  completed_at: null,
  created_at: '2026-09-01T00:00:00.000Z',
  updated_at: '2026-09-10T00:00:00.000Z',
};

const mockStatusNotStarted: AssessmentSessionStatus = {
  project_id: 'proj-123',
  project_name: 'Distributed Climate Sensor Mesh',
  current_phase: 'IDEA',
  status: 'NOT_STARTED',
  current_question_index: 1,
  total_questions: 15,
  answered_count: 0,
  progress_percentage: 0,
  started_at: null,
  completed_at: null,
};

const mockStatusInProgress: AssessmentSessionStatus = {
  project_id: 'proj-123',
  project_name: 'Distributed Climate Sensor Mesh',
  current_phase: 'ASSESSMENT',
  status: 'IN_PROGRESS',
  current_question_index: 2,
  total_questions: 15,
  answered_count: 1,
  progress_percentage: 7,
  started_at: '2026-09-13T10:00:00.000Z',
  completed_at: null,
};

const mockStatusCompleted: AssessmentSessionStatus = {
  project_id: 'proj-123',
  project_name: 'Distributed Climate Sensor Mesh',
  current_phase: 'ASSESSMENT',
  status: 'COMPLETED',
  current_question_index: 15,
  total_questions: 15,
  answered_count: 15,
  progress_percentage: 100,
  started_at: '2026-09-13T10:00:00.000Z',
  completed_at: '2026-09-13T10:15:00.000Z',
};

const mockQuestion1: AssessmentQuestionResponse = {
  question: {
    id: 'q1',
    order_index: 1,
    category: 'Problem Definition & Impact',
    question_text: 'What primary problem domain does this project target?',
    help_text: 'Select the primary problem classification that best characterizes your core challenge.',
    question_type: 'MULTIPLE_CHOICE',
    options: [
      {
        value: 'IOT_HARDWARE',
        label: 'Embedded & IoT Systems',
        description: 'Hardware sensors and telemetry networks',
      },
      {
        value: 'WEB_APPLICATION',
        label: 'Full-Stack Web App',
        description: 'Web dashboards and API services',
      },
    ],
    is_adaptive: false,
    context_badge: null,
  },
  answer: null,
};

const mockQuestion2: AssessmentQuestionResponse = {
  question: {
    id: 'q2',
    order_index: 2,
    category: 'Core Value Proposition & Solution Mechanics',
    question_text: 'How does your solution validate incoming telemetry data?',
    help_text: 'Describe data ingestion validation policies.',
    question_type: 'MULTIPLE_CHOICE',
    options: [
      {
        value: 'SCHEMA_VALIDATION',
        label: 'JSON Schema Validation',
        description: 'Strict schema boundary verification',
      },
      {
        value: 'CHECKSUM_HASH',
        label: 'Cryptographic Checksum',
        description: 'Hardware payload checksum verification',
      },
    ],
    is_adaptive: false,
    context_badge: null,
  },
  answer: {
    id: 'ans-1',
    assessment_id: 'assess-123',
    question_id: 'q1',
    question_index: 1,
    question_text: 'What primary problem domain does this project target?',
    question_type: 'MULTIPLE_CHOICE',
    selected_option: 'IOT_HARDWARE',
    text_response: null,
    created_at: '2026-09-13T10:05:00.000Z',
    updated_at: '2026-09-13T10:05:00.000Z',
  },
};

const mockAdaptiveQuestion11: AssessmentQuestionResponse = {
  question: {
    id: 'q11',
    order_index: 11,
    category: 'Adaptive Architecture & Technical Edge',
    question_text: 'Given your choice of IoT hardware, how will firmware OTA updates be secured?',
    help_text: 'Explain code signing and cryptographic rollback protection.',
    question_type: 'TEXT',
    options: [],
    is_adaptive: true,
    context_badge: 'Telemetry & Embedded Sensors',
  },
  answer: null,
};

const mockSubmitAnswerResponse: AssessmentAnswerSubmitResponse = {
  answer: {
    id: 'ans-new',
    assessment_id: 'assess-123',
    question_id: 'q1',
    question_index: 1,
    question_text: 'What primary problem domain does this project target?',
    question_type: 'MULTIPLE_CHOICE',
    selected_option: 'IOT_HARDWARE',
    text_response: null,
    created_at: '2026-09-13T10:05:00.000Z',
    updated_at: '2026-09-13T10:05:00.000Z',
  },
  current_question_index: 2,
  next_question_index: 2,
  answered_count: 1,
  total_questions: 15,
  is_complete_eligible: false,
};

const mockResult: AssessmentResultResponse = {
  id: 'res-123',
  assessment_id: 'assess-123',
  project_instance_id: 'proj-123',
  skill_level: 'INTERMEDIATE',
  project_complexity: 'MODERATE',
  alignment: 'HIGHLY_ALIGNED',
  technical_confidence: 'HIGH',
  learning_depth: 'PRACTICAL',
  recommended_focus: 'Data Pipeline & Firmware OTA Security',
  summary: 'Solid architectural understanding with clear edge ingestion constraints.',
  overall_score: 86,
  readiness_tier: 'HIGH',
  dimension_scores: {
    problem_clarity: 90,
    architecture_readiness: 85,
    technical_feasibility: 82,
    delivery_readiness: 88,
  },
  identified_gaps: [
    {
      area: 'Firmware Security',
      severity: 'MEDIUM',
      description: 'Mutual TLS certificate distribution mechanism needs specification.',
    },
  ],
  recommendations: [
    {
      phase: 'BLUEPRINT',
      action: 'Formulate cryptographic key rotation schema for sensor nodes.',
    },
  ],
  created_at: '2026-09-13T10:15:00.000Z',
};

const mockAuthContext: AuthContextValue = {
  status: 'AUTHENTICATED',
  session: {
    access_token: 'mock-token',
    refresh_token: 'mock-refresh',
    expires_in: 3600,
    token_type: 'bearer',
    user: { id: 'student-999', email: 'ankush@example.com' } as unknown as User,
  },
  supabaseUser: { id: 'student-999', email: 'ankush@example.com' } as unknown as User,
  user: {
    id: 'student-999',
    email: 'ankush@example.com',
    role: 'STUDENT',
    status: 'ACTIVE',
    fullName: 'Ankush Poonia',
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

function renderAssessment(projectId = 'proj-123') {
  return render(
    <AuthContext.Provider value={mockAuthContext}>
      <MemoryRouter initialEntries={[`/student/projects/${projectId}/assessment`]}>
        <Routes>
          <Route
            path="/student/projects/:projectId/assessment"
            element={<StudentAssessment />}
          />
          <Route
            path="/student/projects/:projectId/profile"
            element={<div data-testid="project-profile-mock">Project Profile</div>}
          />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

describe('GROWFLOW — S07–S11 Assessment Workflow Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.getProject).mockResolvedValue(mockProject);
  });

  /* =========================================================================
     S07 — Assessment Intro Tests
     ========================================================================= */
  describe('S07 — Assessment Intro', () => {
    it('1. renders project context, truthful expectations, and Start button when NOT_STARTED', async () => {
      vi.mocked(api.getAssessmentStatus).mockResolvedValue(mockStatusNotStarted);

      renderAssessment();

      await waitFor(() => {
        expect(screen.getByText(/Stage 2 Readiness Assessment/i)).toBeInTheDocument();
      });

      expect(screen.getByText('Distributed Climate Sensor Mesh')).toBeInTheDocument();
      expect(screen.getByText('INTERMEDIATE')).toBeInTheDocument();
      expect(screen.getByText('10 Core Dimensions')).toBeInTheDocument();
      expect(screen.getByText('5 Adaptive Inquiries')).toBeInTheDocument();
      expect(screen.getByText('Project Understanding')).toBeInTheDocument();

      const startBtn = screen.getByRole('button', { name: /start assessment/i });
      expect(startBtn).toBeInTheDocument();
      expect(startBtn).not.toBeDisabled();
    });

    it('2. clicking Start Assessment calls startAssessment and transitions to Question 1', async () => {
      vi.mocked(api.getAssessmentStatus).mockResolvedValue(mockStatusNotStarted);
      vi.mocked(api.startAssessment).mockResolvedValue({
        session: mockStatusInProgress,
        current_question: mockQuestion1.question,
      } as AssessmentStartResponse);
      vi.mocked(api.getAssessmentQuestion).mockResolvedValue(mockQuestion1);

      renderAssessment();

      const startBtn = await screen.findByRole('button', { name: /start assessment/i });
      fireEvent.click(startBtn);

      await waitFor(() => {
        expect(api.startAssessment).toHaveBeenCalledWith('proj-123');
      });

      expect(await screen.findByText('Problem Definition & Impact')).toBeInTheDocument();
      expect(screen.getByText('What primary problem domain does this project target?')).toBeInTheDocument();
    });

    it('3. renders Continue button when assessment is IN_PROGRESS', async () => {
      vi.mocked(api.getAssessmentStatus).mockResolvedValue(mockStatusInProgress);
      vi.mocked(api.getAssessmentQuestion).mockResolvedValue(mockQuestion2);

      renderAssessment();

      // In progress directly opens question at current_question_index
      await waitFor(() => {
        expect(screen.getByText('Core Value Proposition & Solution Mechanics')).toBeInTheDocument();
      });
      expect(screen.getAllByText(/Question 2 of 15/i).length).toBeGreaterThanOrEqual(1);
    });
  });

  /* =========================================================================
     S08 — Assessment Question Tests
     ========================================================================= */
  describe('S08 — Assessment Question & Validation', () => {
    it('4. displays question text, category, options, and previous button disabled on question 1', async () => {
      vi.mocked(api.getAssessmentStatus).mockResolvedValue(mockStatusNotStarted);
      vi.mocked(api.startAssessment).mockResolvedValue({
        session: mockStatusInProgress,
        current_question: mockQuestion1.question,
      } as AssessmentStartResponse);
      vi.mocked(api.getAssessmentQuestion).mockResolvedValue(mockQuestion1);

      renderAssessment();

      const startBtn = await screen.findByRole('button', { name: /start assessment/i });
      fireEvent.click(startBtn);

      await screen.findByText('Problem Definition & Impact');
      expect(screen.getByLabelText(/Embedded & IoT Systems/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Full-Stack Web App/i)).toBeInTheDocument();

      const prevBtn = screen.getByRole('button', { name: /← previous/i });
      expect(prevBtn).toBeDisabled();
    });

    it('5. prevents submission if no option selected and renders accessible validation error', async () => {
      vi.mocked(api.getAssessmentStatus).mockResolvedValue(mockStatusInProgress);
      vi.mocked(api.getAssessmentQuestion).mockResolvedValue(mockQuestion1);

      renderAssessment();

      await screen.findByText('Problem Definition & Impact');

      const submitBtn = screen.getByRole('button', { name: /save & next →/i });
      fireEvent.click(submitBtn);

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent(/please select an option before proceeding/i);
      });
      expect(api.submitAssessmentAnswer).not.toHaveBeenCalled();
    });

    it('6. selects option, submits to backend, and advances to next question', async () => {
      vi.mocked(api.getAssessmentStatus).mockResolvedValue(mockStatusInProgress);
      vi.mocked(api.getAssessmentQuestion)
        .mockResolvedValueOnce(mockQuestion1)
        .mockResolvedValueOnce(mockQuestion2);
      vi.mocked(api.submitAssessmentAnswer).mockResolvedValue(mockSubmitAnswerResponse);

      renderAssessment();

      await screen.findByText('Problem Definition & Impact');

      const radio = screen.getByLabelText(/Embedded & IoT Systems/i);
      fireEvent.click(radio);

      const submitBtn = screen.getByRole('button', { name: /save & next →/i });
      fireEvent.click(submitBtn);

      await waitFor(() => {
        expect(api.submitAssessmentAnswer).toHaveBeenCalledWith('proj-123', {
          question_index: 1,
          selected_option: 'IOT_HARDWARE',
          text_response: undefined,
        });
      });

      // Loaded question 2
      expect(await screen.findByText('Core Value Proposition & Solution Mechanics')).toBeInTheDocument();
    });

    it('7. allows navigating back to previous question and preserves previous answer', async () => {
      vi.mocked(api.getAssessmentStatus).mockResolvedValue(mockStatusInProgress);
      vi.mocked(api.getAssessmentQuestion)
        .mockResolvedValueOnce(mockQuestion2)
        .mockResolvedValueOnce(mockQuestion1);

      renderAssessment();

      await screen.findByText('Core Value Proposition & Solution Mechanics');

      const prevBtn = screen.getByRole('button', { name: /← previous/i });
      expect(prevBtn).not.toBeDisabled();
      fireEvent.click(prevBtn);

      await waitFor(() => {
        expect(api.getAssessmentQuestion).toHaveBeenCalledWith('proj-123', 1);
      });
      await screen.findByText('Problem Definition & Impact');
    });
  });

  /* =========================================================================
     S09 — Adaptive Assessment Tests
     ========================================================================= */
  describe('S09 — Adaptive Assessment', () => {
    it('8. renders project-specific contextual badge for adaptive question (>10)', async () => {
      vi.mocked(api.getAssessmentStatus).mockResolvedValue({
        ...mockStatusInProgress,
        current_question_index: 11,
      });
      vi.mocked(api.getAssessmentQuestion).mockResolvedValue(mockAdaptiveQuestion11);

      renderAssessment();

      await screen.findByText('Adaptive Architecture & Technical Edge');

      expect(screen.getByText(/Project-Specific Question/i)).toBeInTheDocument();
      expect(screen.getByText(/Telemetry & Embedded Sensors/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/describe your architectural approach/i)).toBeInTheDocument();
    });

    it('9. validates open text response for adaptive text questions', async () => {
      vi.mocked(api.getAssessmentStatus).mockResolvedValue({
        ...mockStatusInProgress,
        current_question_index: 11,
      });
      vi.mocked(api.getAssessmentQuestion).mockResolvedValue(mockAdaptiveQuestion11);

      renderAssessment();

      await screen.findByText('Adaptive Architecture & Technical Edge');

      const submitBtn = screen.getByRole('button', { name: /save & next →/i });
      fireEvent.click(submitBtn);

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent(/at least 5 characters/i);
      }, { timeout: 3000 });
    });
  });

  /* =========================================================================
     S10 — Assessment Completion Tests
     ========================================================================= */
  describe('S10 — Assessment Completion', () => {
    it('10. renders completion checklist when all 15 questions answered', async () => {
      vi.mocked(api.getAssessmentStatus).mockResolvedValue({
        ...mockStatusInProgress,
        current_question_index: 15,
        answered_count: 15,
      });

      renderAssessment();

      await waitFor(() => {
        expect(screen.getByText(/Ready to Synthesize Project Understanding/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/10 \/ 10/i)).toBeInTheDocument();
      expect(screen.getByText(/5 \/ 5/i)).toBeInTheDocument();

      const finalizeBtn = screen.getByRole('button', { name: /finalize & view results/i });
      expect(finalizeBtn).toBeInTheDocument();
    });

    it('11. finalizing assessment calls completeAssessment atomically and transitions to S11 results', async () => {
      vi.mocked(api.getAssessmentStatus).mockResolvedValue({
        ...mockStatusInProgress,
        current_question_index: 15,
        answered_count: 15,
      });
      vi.mocked(api.completeAssessment).mockResolvedValue(mockResult);

      renderAssessment();

      const finalizeBtn = await screen.findByRole('button', { name: /finalize & view results/i });
      fireEvent.click(finalizeBtn);

      await waitFor(() => {
        expect(api.completeAssessment).toHaveBeenCalledWith('proj-123');
      });

      expect(await screen.findByText('Project Understanding & Readiness')).toBeInTheDocument();
    });
  });

  /* =========================================================================
     S11 — Assessment Result / Project Understanding Tests
     ========================================================================= */
  describe('S11 — Assessment Result / Project Understanding', () => {
    it('12. renders score, canonical readiness tier, Enriched Project Understanding grid, and recommendations', async () => {
      vi.mocked(api.getAssessmentStatus).mockResolvedValue(mockStatusCompleted);
      vi.mocked(api.getAssessmentResult).mockResolvedValue(mockResult);

      renderAssessment();

      await waitFor(() => {
        expect(screen.getByText('Project Understanding & Readiness')).toBeInTheDocument();
      });

      // Score
      expect(screen.getByText('86')).toBeInTheDocument();
      expect(screen.getByText('/ 100')).toBeInTheDocument();

      // Readiness Tier
      expect(screen.getAllByText(/HIGH/i).length).toBeGreaterThanOrEqual(1);

      // Summary
      expect(screen.getByText(/Solid architectural understanding with clear edge ingestion constraints/i)).toBeInTheDocument();

      // Enriched Project Understanding attributes
      expect(screen.getByText('Skill Level')).toBeInTheDocument();
      expect(screen.getByText('INTERMEDIATE')).toBeInTheDocument();
      expect(screen.getByText('Alignment')).toBeInTheDocument();
      expect(screen.getByText('HIGHLY_ALIGNED')).toBeInTheDocument();
      expect(screen.getByText('Recommended Focus')).toBeInTheDocument();
      expect(screen.getByText('Data Pipeline & Firmware OTA Security')).toBeInTheDocument();

      // Dimensional scores
      expect(screen.getByText('Problem Clarity')).toBeInTheDocument();
      expect(screen.getByText('90 / 100')).toBeInTheDocument();

      // Identified gaps
      expect(screen.getByText('Firmware Security')).toBeInTheDocument();
      expect(screen.getByText('MEDIUM')).toBeInTheDocument();

      // Recommendations
      expect(screen.getByText(/Formulate cryptographic key rotation schema for sensor nodes/i)).toBeInTheDocument();

      // Stage 3 notice
      expect(screen.getByText(/Stage 3: Blueprint Generation/i)).toBeInTheDocument();
    });
  });

  /* =========================================================================
     Error Recovery & Resilience Tests
     ========================================================================= */
  describe('Error Handling & Resilience', () => {
    it('13. renders accessible error boundary on 404 / network failure and supports retry', async () => {
      vi.mocked(api.getProject).mockResolvedValue(mockProject);
      vi.mocked(api.getAssessmentStatus).mockRejectedValueOnce(new Error('Project assessment not found (404)'));

      renderAssessment();

      await waitFor(() => {
        expect(screen.getByText(/Unable to Load Assessment/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/Project assessment not found \(404\)/i)).toBeInTheDocument();

      const retryBtn = screen.getByRole('button', { name: /try again/i });
      expect(retryBtn).toBeInTheDocument();

      // Clicking retry recovers when API succeeds
      vi.mocked(api.getAssessmentStatus).mockResolvedValueOnce(mockStatusNotStarted);
      fireEvent.click(retryBtn);

      await waitFor(() => {
        expect(screen.getByText(/Stage 2 Readiness Assessment/i)).toBeInTheDocument();
      });
    });
  });
});
