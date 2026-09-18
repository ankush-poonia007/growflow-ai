import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import type { User } from '@supabase/supabase-js';

import { GroupActivity } from '@/pages/Mentor/GroupActivity/GroupActivity';
import { GroupAIMentor } from '@/pages/Mentor/GroupAIMentor/GroupAIMentor';
import { MentorStudentActivity } from '@/pages/Mentor/MentorStudentActivity/MentorStudentActivity';
import { MentorActivity } from '@/pages/Mentor/MentorActivity/MentorActivity';
import { MentorAI } from '@/pages/Mentor/MentorAI/MentorAI';
import * as apiClient from '@/lib/api/client';
import type {
  ActivityItemResponse,
  GroupResponse,
  MentorStudentDetail,
  MentorAIStatusResponse,
  MentorAIChatResponse,
} from '@/lib/api/types';

function createMockAuth(role: 'STUDENT' | 'MENTOR' = 'MENTOR'): AuthContextValue {
  return {
    status: 'AUTHENTICATED',
    session: {
      access_token: 'mock-token',
      refresh_token: 'mock-refresh',
      expires_in: 3600,
      token_type: 'bearer',
      user: { id: 'mentor-1', email: 'mentor.elena@growflow.ai' } as unknown as User,
    },
    supabaseUser: { id: 'mentor-1', email: 'mentor.elena@growflow.ai' } as unknown as User,
    user: {
      id: 'mentor-1',
      email: 'mentor.elena@growflow.ai',
      role,
      status: 'ACTIVE',
      fullName: 'Dr. Elena Rostova',
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

const mockGroup: GroupResponse = {
  id: 'grp-1',
  mentor_id: 'mentor-1',
  mentor_name: 'Dr. Elena Rostova',
  name: "Elena's AI Research Cohort",
  join_code: 'ELENA2026',
  status: 'ACTIVE',
  created_at: '2026-09-01T00:00:00Z',
  updated_at: '2026-09-01T00:00:00Z',
};

const mockStudent: MentorStudentDetail = {
  id: 'student-1',
  full_name: 'Aarav Sharma',
  email: 'student.aarav@growflow.ai',
  avatar_url: null,
  bio: null,
  skills: [],
  group_count: 1,
  groups: [{ id: 'grp-1', name: "Elena's AI Research Cohort", joined_at: '2026-09-01T00:00:00Z' }],
  project_count: 1,
  at_risk_project_count: 0,
  created_at: '2026-09-01T00:00:00Z',
  projects: [],
};

describe('Phase 7 Batch 6: Mentor Scoped Activity & AI Supervision', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  /* ==========================================================================
     AREA A — M08: GROUP ACTIVITY
     ========================================================================== */
  describe('M08: GroupActivity', () => {
    it('renders list of group activity items with actor names and event badges', async () => {
      const mockActivity: ActivityItemResponse[] = [
        {
          id: 'act-1',
          event_type: 'TASK_COMPLETED',
          title: 'Completed Task: Architecture Diagram',
          description: 'Aarav Sharma completed the baseline architecture diagram.',
          actor_id: 'student-1',
          actor_role: 'STUDENT',
          resource_type: 'PROJECT',
          resource_id: 'p-1',
          project_instance_id: 'p-1',
          group_id: 'grp-1',
          occurred_at: '2026-09-15T10:00:00Z',
          metadata: { task_id: 't-1' },
        },
      ];

      vi.spyOn(apiClient, 'getMentorGroup').mockResolvedValue(mockGroup);
      vi.spyOn(apiClient, 'getGroupActivity').mockResolvedValue(mockActivity);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/groups/grp-1/activity']}>
            <Routes>
              <Route path="/mentor/groups/:groupId/activity" element={<GroupActivity />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Completed Task: Architecture Diagram')).toBeInTheDocument();
      });
      expect(screen.getByText(/Aarav Sharma completed the baseline architecture diagram/i)).toBeInTheDocument();
      expect(screen.getByText('Student')).toBeInTheDocument();
      expect(screen.getAllByText(/Elena's AI Research Cohort/i).length).toBeGreaterThan(0);
    });

    it('renders empty state "No activity yet." when group has no events', async () => {
      vi.spyOn(apiClient, 'getMentorGroup').mockResolvedValue(mockGroup);
      vi.spyOn(apiClient, 'getGroupActivity').mockResolvedValue([]);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/groups/grp-1/activity']}>
            <Routes>
              <Route path="/mentor/groups/:groupId/activity" element={<GroupActivity />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('No activity yet.')).toBeInTheDocument();
      });
    });

    it('renders error state when activity fails to load', async () => {
      vi.spyOn(apiClient, 'getMentorGroup').mockRejectedValue(new Error('Network error: Forbidden'));
      vi.spyOn(apiClient, 'getGroupActivity').mockRejectedValue(new Error('Network error: Forbidden'));

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/groups/grp-1/activity']}>
            <Routes>
              <Route path="/mentor/groups/:groupId/activity" element={<GroupActivity />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Network error: Forbidden')).toBeInTheDocument();
      });
    });
  });

  /* ==========================================================================
     AREA A — M13: STUDENT ACTIVITY
     ========================================================================== */
  describe('M13: MentorStudentActivity', () => {
    it('renders student-scoped activity items', async () => {
      const mockActivity: ActivityItemResponse[] = [
        {
          id: 'act-2',
          event_type: 'HELP_REQUEST_CREATED',
          title: 'Submitted Help Request',
          description: 'Aarav asked for help on database migrations.',
          actor_id: 'student-1',
          actor_role: 'STUDENT',
          resource_type: 'PROJECT',
          resource_id: 'p-1',
          occurred_at: '2026-09-15T11:00:00Z',
          metadata: {},
        },
      ];

      vi.spyOn(apiClient, 'getMentorStudent').mockResolvedValue(mockStudent);
      vi.spyOn(apiClient, 'getMentorStudentActivity').mockResolvedValue(mockActivity);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/students/student-1/activity']}>
            <Routes>
              <Route path="/mentor/students/:studentId/activity" element={<MentorStudentActivity />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Submitted Help Request')).toBeInTheDocument();
      });
      expect(screen.getByRole('heading', { level: 1, name: /Aarav Sharma/i })).toBeInTheDocument();
      expect(screen.getByText('Student')).toBeInTheDocument();
    });

    it('renders empty state "No activity yet." for student with no activity', async () => {
      vi.spyOn(apiClient, 'getMentorStudent').mockResolvedValue(mockStudent);
      vi.spyOn(apiClient, 'getMentorStudentActivity').mockResolvedValue([]);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/students/student-1/activity']}>
            <Routes>
              <Route path="/mentor/students/:studentId/activity" element={<MentorStudentActivity />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('No activity yet.')).toBeInTheDocument();
      });
    });
  });

  /* ==========================================================================
     AREA A — M35: MENTOR ACTIVITY
     ========================================================================== */
  describe('M35: MentorActivity', () => {
    it('renders portfolio-wide activity stream for the mentor', async () => {
      const mockActivity: ActivityItemResponse[] = [
        {
          id: 'act-3',
          event_type: 'BLUEPRINT_APPROVED',
          title: 'Blueprint Approved',
          description: 'Dr. Elena approved blueprint v1 for Aarav Sharma.',
          actor_id: 'mentor-1',
          actor_role: 'MENTOR',
          resource_type: 'PROJECT',
          resource_id: 'p-1',
          occurred_at: '2026-09-15T12:00:00Z',
          metadata: {},
        },
      ];

      vi.spyOn(apiClient, 'getMentorPortfolioActivity').mockResolvedValue(mockActivity);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/activity']}>
            <Routes>
              <Route path="/mentor/activity" element={<MentorActivity />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Blueprint Approved')).toBeInTheDocument();
      });
      expect(screen.getByText('Portfolio Activity Stream')).toBeInTheDocument();
      expect(screen.getByText('Mentor')).toBeInTheDocument();
    });

    it('renders empty state "No activity yet." when portfolio has no events', async () => {
      vi.spyOn(apiClient, 'getMentorPortfolioActivity').mockResolvedValue([]);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/activity']}>
            <Routes>
              <Route path="/mentor/activity" element={<MentorActivity />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('No activity yet.')).toBeInTheDocument();
      });
    });
  });

  /* ==========================================================================
     AREA B — M09: GROUP AI MENTOR
     ========================================================================== */
  describe('M09: GroupAIMentor', () => {
    it('renders group scope and displays truthful offline message when AI provider is unavailable', async () => {
      const mockStatus: MentorAIStatusResponse = {
        scope: 'GROUP',
        group_id: 'grp-1',
        group_name: "Elena's AI Research Cohort",
        ai_available: false,
      };

      vi.spyOn(apiClient, 'getMentorGroup').mockResolvedValue(mockGroup);
      vi.spyOn(apiClient, 'getGroupAIStatus').mockResolvedValue(mockStatus);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/groups/grp-1/ai']}>
            <Routes>
              <Route path="/mentor/groups/:groupId/ai" element={<GroupAIMentor />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText(/AI Provider Offline/i)).toBeInTheDocument();
      });
      expect(screen.getByText(/OpenRouter provider keys are missing from server configuration/i)).toBeInTheDocument();
      expect(screen.getByText('BOUNDED TO THIS COHORT ONLY')).toBeInTheDocument();
    });

    it('submits a group supervisory question and displays assistant response', async () => {
      const mockStatus: MentorAIStatusResponse = {
        scope: 'GROUP',
        group_id: 'grp-1',
        group_name: "Elena's AI Research Cohort",
        ai_available: true,
      };

      const mockChatResponse: MentorAIChatResponse = {
        user_message: {
          id: 'u-1',
          role: 'user',
          content: 'How is the cohort progressing?',
          created_at: '2026-09-15T10:00:00Z',
        },
        assistant_message: {
          id: 'a-1',
          role: 'assistant',
          content: 'Cohort analysis: 3 students on track, 1 blocked on backend setup.',
          sources: [{ title: 'Group Blueprint', section: 'Milestones' }],
          created_at: '2026-09-15T10:00:01Z',
        },
        ai_available: true,
        scope: 'GROUP',
        group_id: 'grp-1',
      };

      vi.spyOn(apiClient, 'getMentorGroup').mockResolvedValue(mockGroup);
      vi.spyOn(apiClient, 'getGroupAIStatus').mockResolvedValue(mockStatus);
      const chatSpy = vi.spyOn(apiClient, 'sendGroupAIMessage').mockResolvedValue(mockChatResponse);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/groups/grp-1/ai']}>
            <Routes>
              <Route path="/mentor/groups/:groupId/ai" element={<GroupAIMentor />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Cohort Supervisory Consultation')).toBeInTheDocument();
      });

      const input = screen.getByRole('textbox', { name: /message group ai mentor/i });
      fireEvent.change(input, { target: { value: 'How is the cohort progressing?' } });

      const sendBtn = screen.getByRole('button', { name: /send/i });
      expect(sendBtn).not.toBeDisabled();
      fireEvent.click(sendBtn);

      await waitFor(() => {
        expect(screen.getByText('Cohort analysis: 3 students on track, 1 blocked on backend setup.')).toBeInTheDocument();
      });

      expect(screen.getByText(/Grounded in:/i)).toBeInTheDocument();
      expect(screen.getByText(/Group Blueprint/i)).toBeInTheDocument();

      expect(chatSpy).toHaveBeenCalledWith('grp-1', {
        message: 'How is the cohort progressing?',
        history: [],
      });
    });
  });

  /* ==========================================================================
     AREA B — M36: MENTOR AI
     ========================================================================== */
  describe('M36: MentorAI', () => {
    it('renders portfolio scope and displays truthful offline banner when unavailable', async () => {
      const mockStatus: MentorAIStatusResponse = {
        scope: 'PORTFOLIO',
        ai_available: false,
      };

      vi.spyOn(apiClient, 'getMentorAIStatus').mockResolvedValue(mockStatus);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/ai']}>
            <Routes>
              <Route path="/mentor/ai" element={<MentorAI />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Portfolio Scope: All Cohorts')).toBeInTheDocument();
      });
      expect(screen.getByText(/OpenRouter provider keys are missing from server configuration/i)).toBeInTheDocument();
      expect(screen.getByText('PORTFOLIO-WIDE SUPERVISION')).toBeInTheDocument();
    });

    it('submits a portfolio-level query and displays assistant response', async () => {
      const mockStatus: MentorAIStatusResponse = {
        scope: 'PORTFOLIO',
        ai_available: true,
      };

      const mockChatResponse: MentorAIChatResponse = {
        user_message: {
          id: 'u-2',
          role: 'user',
          content: 'Summarize portfolio risk status.',
          created_at: '2026-09-15T10:00:00Z',
        },
        assistant_message: {
          id: 'a-2',
          role: 'assistant',
          content: 'Portfolio summary: Across all cohorts, 2 projects are flagged at risk.',
          sources: [],
          created_at: '2026-09-15T10:00:01Z',
        },
        ai_available: true,
        scope: 'PORTFOLIO',
      };

      vi.spyOn(apiClient, 'getMentorAIStatus').mockResolvedValue(mockStatus);
      const chatSpy = vi.spyOn(apiClient, 'sendMentorAIMessage').mockResolvedValue(mockChatResponse);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/ai']}>
            <Routes>
              <Route path="/mentor/ai" element={<MentorAI />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Portfolio Scope: All Cohorts')).toBeInTheDocument();
      });

      const input = screen.getByRole('textbox', { name: /message mentor portfolio ai/i });
      fireEvent.change(input, { target: { value: 'Summarize portfolio risk status.' } });

      const sendBtn = screen.getByRole('button', { name: /send/i });
      expect(sendBtn).not.toBeDisabled();
      fireEvent.click(sendBtn);

      await waitFor(() => {
        expect(screen.getByText('Portfolio summary: Across all cohorts, 2 projects are flagged at risk.')).toBeInTheDocument();
      });

      expect(chatSpy).toHaveBeenCalledWith({
        message: 'Summarize portfolio risk status.',
        history: [],
      });
    });
  });
});
