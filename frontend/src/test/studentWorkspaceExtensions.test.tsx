import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { StudentGitHub } from '@/pages/Student/StudentGitHub/StudentGitHub';
import { StudentActivity } from '@/pages/Student/StudentActivity/StudentActivity';
import { StudentAIMentor } from '@/pages/Student/StudentAIMentor/StudentAIMentor';
import { StudentHelpRequests } from '@/pages/Student/StudentHelpRequests/StudentHelpRequests';
import { StudentMentorFeedback } from '@/pages/Student/StudentMentorFeedback/StudentMentorFeedback';
import { StudentProjectChanges } from '@/pages/Student/StudentProjectChanges/StudentProjectChanges';
import { StudentProjectChangeDetail } from '@/pages/Student/StudentProjectChangeDetail/StudentProjectChangeDetail';
import type {
  ProjectResponse,
  GitHubIntegrationResponse,
  ActivityItemResponse,
  AIMentorConversationResponse,
  AIMentorSendResponse,
  HelpRequestResponse,
  MentorNoteResponse,
  ProjectChangeResponse,
  BlueprintVersionResponse,
} from '@/lib/api/types';
import * as api from '@/lib/api';

vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api')>('@/lib/api');
  return {
    ...actual,
    getProject: vi.fn(),
    getGitHubIntegration: vi.fn(),
    connectGitHub: vi.fn(),
    syncGitHub: vi.fn(),
    disconnectGitHub: vi.fn(),
    getProjectActivity: vi.fn(),
    getAIMentorHistory: vi.fn(),
    sendAIMentorMessage: vi.fn(),
    executeAIOperation: vi.fn(),
    getHelpRequests: vi.fn(),
    createHelpRequest: vi.fn(),
    getHelpRequest: vi.fn(),
    getMentorNotes: vi.fn(),
    acknowledgeMentorNote: vi.fn(),
    getProjectChanges: vi.fn(),
    getProjectChange: vi.fn(),
    analyzeProjectChange: vi.fn(),
    confirmProjectChange: vi.fn(),
    getBlueprintVersions: vi.fn(),
    getBlueprintVersion: vi.fn(),
  };
});

const mockProject: ProjectResponse = {
  id: 'proj-ext-100',
  student_id: 'student-001',
  group_id: null,
  project_definition_id: null,
  source_definition_version_id: null,
  name: 'Drone Telemetry Extensions Project',
  problem: 'Real-time telemetry streaming telemetry gaps',
  proposed_solution: 'Microservices edge ingestion telemetry',
  complexity: 'INTERMEDIATE',
  current_phase: 'IMPLEMENTATION',
  health: 'ON_TRACK',
  progress_percentage: 45,
  status: 'ACTIVE',
  deadline: '2026-12-01T00:00:00Z',
  started_at: '2026-09-01T00:00:00Z',
  completed_at: null,
  created_at: '2026-09-01T00:00:00Z',
  updated_at: '2026-09-02T00:00:00Z',
};

describe('Student Workspace Extensions (Batch 06: S27–S33)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.getProject).mockResolvedValue(mockProject);
  });

  describe('S27: StudentGitHub', () => {
    it('renders connected GitHub integration and allows syncing', async () => {
      const mockIntegration: GitHubIntegrationResponse = {
        id: 'gh-1',
        project_instance_id: 'proj-ext-100',
        repository_name: 'test-org/drone-telemetry',
        repository_url: 'https://github.com/test-org/drone-telemetry',
        connection_status: 'CONNECTED',
        default_branch: 'main',
        commit_count: 14,
        last_sync_at: '2026-09-13T12:00:00Z',
        sync_error: null,
        cached_commits_preview: [
          {
            sha: 'abcdef1234567890',
            message: 'feat: add drone sensor interface',
            author: 'Ankush Poonia',
            date: '2026-09-13T10:00:00Z',
          },
        ],
      };

      vi.mocked(api.getGitHubIntegration).mockResolvedValue(mockIntegration);
      vi.mocked(api.syncGitHub).mockResolvedValue({
        ...mockIntegration,
        commit_count: 15,
        last_sync_at: '2026-09-13T12:05:00Z',
      });

      render(
        <MemoryRouter initialEntries={['/student/projects/proj-ext-100/github']}>
          <Routes>
            <Route path="/student/projects/:projectId/github" element={<StudentGitHub />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('GitHub Repository Integration')).toBeInTheDocument();
        expect(screen.getByText('test-org/drone-telemetry ↗')).toBeInTheDocument();
        expect(screen.getByText('feat: add drone sensor interface')).toBeInTheDocument();
      });

      const syncBtn = screen.getByRole('button', { name: /sync now/i });
      fireEvent.click(syncBtn);

      await waitFor(() => {
        expect(api.syncGitHub).toHaveBeenCalledWith('proj-ext-100');
        expect(screen.getByText('Repository synced successfully.')).toBeInTheDocument();
      });
    });
  });

  describe('S28: StudentActivity', () => {
    it('renders domain event chronological activity and filters categories', async () => {
      const mockActivities: ActivityItemResponse[] = [
        {
          id: 'evt-1',
          event_type: 'task.created',
          title: 'Task Created: Setup Telemetry Server',
          description: 'New task created by student',
          actor_role: 'STUDENT',
          actor_id: 'student-001',
          resource_type: 'task',
          resource_id: 'task-1',
          occurred_at: '2026-09-13T11:00:00Z',
          metadata: { priority: 'HIGH' },
        },
        {
          id: 'evt-2',
          event_type: 'blueprint.regenerated',
          title: 'Blueprint Regenerated (v2)',
          description: 'System re-evaluated blueprint scorecard',
          actor_role: 'SYSTEM',
          actor_id: null,
          resource_type: 'blueprint',
          resource_id: 'bp-1',
          occurred_at: '2026-09-13T11:30:00Z',
          metadata: { qa_score: 88 },
        },
      ];

      vi.mocked(api.getProjectActivity).mockResolvedValue(mockActivities);

      render(
        <MemoryRouter initialEntries={['/student/projects/proj-ext-100/activity']}>
          <Routes>
            <Route path="/student/projects/:projectId/activity" element={<StudentActivity />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Audit Trail & Activity Stream')).toBeInTheDocument();
        expect(screen.getByText('Task Created: Setup Telemetry Server')).toBeInTheDocument();
        expect(screen.getByText('Blueprint Regenerated (v2)')).toBeInTheDocument();
      });

      // Filter by tasks
      const tasksFilterBtn = screen.getByRole('button', { name: /^tasks$/i });
      fireEvent.click(tasksFilterBtn);

      expect(screen.getByText('Task Created: Setup Telemetry Server')).toBeInTheDocument();
      expect(screen.queryByText('Blueprint Regenerated (v2)')).not.toBeInTheDocument();
    });
  });

  describe('S29: StudentAIMentor', () => {
    it('renders AI Mentor chat with truthful availability indicator and handles sending messages', async () => {
      const mockConversation: AIMentorConversationResponse = {
        conversation_id: 'conv-1',
        project_instance_id: 'proj-ext-100',
        title: 'Project Guidance',
        ai_available: true,
        messages: [
          {
            id: 'm-1',
            role: 'assistant',
            content: 'Hello! I am your AI project mentor.',
            sources: [{ title: 'System Architecture' }],
            suggested_action: null,
            created_at: '2026-09-13T10:00:00Z',
          },
        ],
      };

      const mockSendResp: AIMentorSendResponse = {
        ai_available: true,
        user_message: {
          id: 'm-2',
          role: 'user',
          content: 'How should I test the telemetry pipeline?',
          sources: [],
          suggested_action: null,
          created_at: '2026-09-13T10:01:00Z',
        },
        assistant_message: {
          id: 'm-3',
          role: 'assistant',
          content: 'You should write unit tests for the ingestion worker.',
          sources: [{ title: 'Testing Strategy' }],
          suggested_action: null,
          created_at: '2026-09-13T10:01:02Z',
        },
      };

      vi.mocked(api.getAIMentorHistory).mockResolvedValue(mockConversation);
      vi.mocked(api.sendAIMentorMessage).mockResolvedValue(mockSendResp);

      render(
        <MemoryRouter initialEntries={['/student/projects/proj-ext-100/ai-mentor']}>
          <Routes>
            <Route path="/student/projects/:projectId/ai-mentor" element={<StudentAIMentor />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('AI Project Mentor')).toBeInTheDocument();
        expect(screen.getByText('Hello! I am your AI project mentor.')).toBeInTheDocument();
        expect(screen.getByText('AI Mentor Connected')).toBeInTheDocument();
      });

      const input = screen.getByPlaceholderText(/ask a question/i);
      fireEvent.change(input, { target: { value: 'How should I test the telemetry pipeline?' } });

      const sendBtn = screen.getByRole('button', { name: /send/i });
      fireEvent.click(sendBtn);

      await waitFor(() => {
        expect(api.sendAIMentorMessage).toHaveBeenCalledWith(
          'proj-ext-100',
          'How should I test the telemetry pipeline?'
        );
        expect(screen.getByText('You should write unit tests for the ingestion worker.')).toBeInTheDocument();
      });
    });

    it('[B4-03] rolls back optimistic message and restores prompt input upon send failure', async () => {
      const mockConversation: AIMentorConversationResponse = {
        conversation_id: 'conv-1',
        project_instance_id: 'proj-ext-100',
        title: 'Project Guidance',
        ai_available: true,
        messages: [
          {
            id: 'm-1',
            role: 'assistant',
            content: 'Hello! I am your AI project mentor.',
            sources: [],
            suggested_action: null,
            created_at: '2026-09-13T10:00:00Z',
          },
        ],
      };

      vi.mocked(api.getAIMentorHistory).mockResolvedValue(mockConversation);
      vi.mocked(api.sendAIMentorMessage).mockRejectedValue(new Error('Network error sending prompt'));

      render(
        <MemoryRouter initialEntries={['/student/projects/proj-ext-100/ai-mentor']}>
          <Routes>
            <Route path="/student/projects/:projectId/ai-mentor" element={<StudentAIMentor />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Hello! I am your AI project mentor.')).toBeInTheDocument();
      });

      const input = screen.getByPlaceholderText(/ask a question/i) as HTMLInputElement;
      fireEvent.change(input, { target: { value: 'Why is my build failing?' } });

      const sendBtn = screen.getByRole('button', { name: /send/i });
      fireEvent.click(sendBtn);

      // On failure, error message appears
      await waitFor(() => {
        expect(screen.getByText(/Network error sending prompt/i)).toBeInTheDocument();
      });

      // Optimistic message should be removed from messages list
      expect(screen.queryByText('Why is my build failing?')).not.toBeInTheDocument();

      // Input text should be restored so student can retry
      expect(input.value).toBe('Why is my build failing?');
    });
  });

  describe('S30: StudentHelpRequests', () => {
    it('renders help requests list and creates a new request', async () => {
      const mockRequests: HelpRequestResponse[] = [
        {
          id: 'hr-1',
          project_instance_id: 'proj-ext-100',
          student_id: 'student-001',
          subject: 'Database schema migration blocker',
          description: 'Encountered lock issue on Postgres table',
          category: 'TECHNICAL',
          priority: 'URGENT',
          status: 'OPEN',
          mentor_response: null,
          resolved_at: null,
          created_at: '2026-09-13T09:00:00Z',
          updated_at: '2026-09-13T09:00:00Z',
        },
      ];

      const newCreated: HelpRequestResponse = {
        id: 'hr-2',
        project_instance_id: 'proj-ext-100',
        student_id: 'student-001',
        subject: 'Architecture review for websocket gateway',
        description: 'Need advice on connection heartbeat intervals',
        category: 'ARCHITECTURE',
        priority: 'HIGH',
        status: 'OPEN',
        mentor_response: null,
        resolved_at: null,
        created_at: '2026-09-13T10:00:00Z',
        updated_at: '2026-09-13T10:00:00Z',
      };

      vi.mocked(api.getHelpRequests).mockResolvedValue(mockRequests);
      vi.mocked(api.createHelpRequest).mockResolvedValue(newCreated);

      render(
        <MemoryRouter initialEntries={['/student/projects/proj-ext-100/help-requests']}>
          <Routes>
            <Route path="/student/projects/:projectId/help-requests" element={<StudentHelpRequests />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Mentor Help Requests')).toBeInTheDocument();
        expect(screen.getByText('Database schema migration blocker')).toBeInTheDocument();
      });

      // Open modal
      const newBtn = screen.getByRole('button', { name: /\+ request help/i });
      fireEvent.click(newBtn);

      expect(screen.getByText('Submit Help Request')).toBeInTheDocument();

      fireEvent.change(screen.getByLabelText(/subject/i), {
        target: { value: 'Architecture review for websocket gateway' },
      });
      fireEvent.change(screen.getByLabelText(/detailed description/i), {
        target: { value: 'Need advice on connection heartbeat intervals' },
      });

      const submitBtn = screen.getByRole('button', { name: /submit request/i });
      fireEvent.click(submitBtn);

      await waitFor(() => {
        expect(api.createHelpRequest).toHaveBeenCalledWith('proj-ext-100', {
          subject: 'Architecture review for websocket gateway',
          description: 'Need advice on connection heartbeat intervals',
          category: 'TECHNICAL',
          priority: 'MEDIUM',
        });
        expect(screen.getAllByText('Architecture review for websocket gateway').length).toBeGreaterThanOrEqual(1);
      });
    });
  });

  describe('S31: StudentMentorFeedback', () => {
    it('renders feedback notes and acknowledges an unread note', async () => {
      const mockNotes: MentorNoteResponse[] = [
        {
          id: 'note-1',
          project_instance_id: 'proj-ext-100',
          mentor_id: 'mentor-007',
          title: 'Review of milestone 2 deliverables',
          message: 'Telemetry parser looks clean. Ensure edge case timeouts are tested.',
          note_type: 'ACTIONABLE',
          status: 'UNREAD',
          related_resource_type: 'MILESTONE',
          related_resource_id: 'm-2',
          created_at: '2026-09-13T08:00:00Z',
          updated_at: '2026-09-13T08:00:00Z',
        },
      ];

      vi.mocked(api.getMentorNotes).mockResolvedValue(mockNotes);
      const noteToAck = mockNotes[0]!;
      vi.mocked(api.acknowledgeMentorNote).mockResolvedValue({
        ...noteToAck,
        status: 'ACKNOWLEDGED',
      });

      render(
        <MemoryRouter initialEntries={['/student/projects/proj-ext-100/mentor-feedback']}>
          <Routes>
            <Route path="/student/projects/:projectId/mentor-feedback" element={<StudentMentorFeedback />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Mentor Feedback & Guidance Notes')).toBeInTheDocument();
        expect(screen.getByText('Review of milestone 2 deliverables')).toBeInTheDocument();
        expect(screen.getByText('1 Unread Note')).toBeInTheDocument();
      });

      const ackBtn = screen.getByRole('button', { name: /acknowledge note/i });
      fireEvent.click(ackBtn);

      await waitFor(() => {
        expect(api.acknowledgeMentorNote).toHaveBeenCalledWith('proj-ext-100', 'note-1');
        expect(screen.getByText('All Notes Acknowledged')).toBeInTheDocument();
      });
    });
  });

  describe('S32 & S33: StudentProjectChanges & Detail', () => {
    it('renders changes list and navigates to change detail for regeneration', async () => {
      const mockChange: ProjectChangeResponse = {
        id: 'chg-101',
        project_instance_id: 'proj-ext-100',
        student_id: 'student-001',
        change_title: 'Migrate to TimescaleDB for telemetry series',
        change_description: 'Need hypertables for high frequency sensor logs',
        change_type: 'TECH_STACK',
        status: 'ANALYZED',
        idempotency_key: null,
        impact_analysis: {
          affected_sections: ['Database Schema', 'Architecture'],
          affected_tasks_count: 3,
          estimated_risk: 'MEDIUM',
          analysis_narrative: 'Non-breaking data store evolution.',
          recommended_action: 'Apply schema migration script and regenerate blueprint.',
        },
        source_blueprint_version_number: 1,
        resulting_blueprint_version_number: null,
        qa_score: null,
        qa_feedback: null,
        created_at: '2026-09-13T09:00:00Z',
        updated_at: '2026-09-13T09:00:00Z',
      };

      const mockVersions: BlueprintVersionResponse[] = [
        {
          id: 'bp-v1',
          blueprint_id: 'bp-1',
          project_instance_id: 'proj-ext-100',
          version_number: 1,
          status: 'APPROVED',
          qa_score: 85,
          change_summary: 'Initial approved blueprint version',
          created_at: '2026-09-01T00:00:00Z',
        },
      ];

      vi.mocked(api.getProjectChanges).mockResolvedValue([mockChange]);
      vi.mocked(api.getBlueprintVersions).mockResolvedValue(mockVersions);
      vi.mocked(api.getProjectChange).mockResolvedValue(mockChange);

      // Render S32 list
      render(
        <MemoryRouter initialEntries={['/student/projects/proj-ext-100/changes']}>
          <Routes>
            <Route path="/student/projects/:projectId/changes" element={<StudentProjectChanges />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Project Change & Blueprint Evolution')).toBeInTheDocument();
        expect(screen.getByText('Migrate to TimescaleDB for telemetry series')).toBeInTheDocument();
        expect(screen.getByText('Archived Blueprint Versions (1)')).toBeInTheDocument();
      });
    });

    it('renders S33 impact detail and confirms regeneration', async () => {
      const mockChange: ProjectChangeResponse = {
        id: 'chg-101',
        project_instance_id: 'proj-ext-100',
        student_id: 'student-001',
        change_title: 'Migrate to TimescaleDB for telemetry series',
        change_description: 'Need hypertables for high frequency sensor logs',
        change_type: 'TECH_STACK',
        status: 'ANALYZED',
        idempotency_key: null,
        impact_analysis: {
          affected_sections: ['Database Schema', 'Architecture'],
          affected_tasks_count: 3,
          estimated_risk: 'MEDIUM',
          analysis_narrative: 'Non-breaking data store evolution.',
          recommended_action: 'Apply schema migration script and regenerate blueprint.',
        },
        source_blueprint_version_number: 1,
        resulting_blueprint_version_number: null,
        qa_score: null,
        qa_feedback: null,
        created_at: '2026-09-13T09:00:00Z',
        updated_at: '2026-09-13T09:00:00Z',
      };

      const confirmedChange: ProjectChangeResponse = {
        ...mockChange,
        status: 'CONFIRMED',
        resulting_blueprint_version_number: 2,
        qa_score: 89,
        qa_feedback: { checks_passed: true },
      };

      vi.mocked(api.getProjectChange).mockResolvedValue(mockChange);
      vi.mocked(api.confirmProjectChange).mockResolvedValue(confirmedChange);
      vi.spyOn(window, 'confirm').mockReturnValue(true);

      render(
        <MemoryRouter initialEntries={['/student/projects/proj-ext-100/changes/chg-101']}>
          <Routes>
            <Route
              path="/student/projects/:projectId/changes/:changeId"
              element={<StudentProjectChangeDetail />}
            />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Impact Analysis Report')).toBeInTheDocument();
        expect(screen.getByText('Zero Silent Deletion Guarantee:')).toBeInTheDocument();
        expect(screen.getByText('Database Schema')).toBeInTheDocument();
      });

      const confirmBtn = screen.getByRole('button', { name: /confirm & regenerate blueprint/i });
      fireEvent.click(confirmBtn);

      await waitFor(() => {
        expect(api.confirmProjectChange).toHaveBeenCalledWith(
          'proj-ext-100',
          'chg-101',
          expect.objectContaining({ idempotency_key: expect.any(String) })
        );
        expect(screen.getByText(/blueprint successfully regenerated/i)).toBeInTheDocument();
        expect(screen.getByText(/Regenerated QA Scorecard/i)).toBeInTheDocument();
      });
    });
  });
});
