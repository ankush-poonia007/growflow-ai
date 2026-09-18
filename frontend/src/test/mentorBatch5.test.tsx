import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import type { User } from '@supabase/supabase-js';

import { StudentGroups } from '@/pages/Student/StudentGroups/StudentGroups';
import { MentorHelpRequests } from '@/pages/Mentor/HelpRequests/MentorHelpRequests';
import { MentorInstanceNotes } from '@/pages/Mentor/InstanceNotes/MentorInstanceNotes';
import * as apiClient from '@/lib/api/client';
import type {
  GroupResponse,
  GroupMembershipResponse,
  MentorHelpRequestSummary,
  MentorNoteItem,
  MentorProjectInstanceDetail,
} from '@/lib/api/types';

function createMockAuth(role: 'STUDENT' | 'MENTOR' = 'STUDENT'): AuthContextValue {
  return {
    status: 'AUTHENTICATED',
    session: {
      access_token: 'mock-token',
      refresh_token: 'mock-refresh',
      expires_in: 3600,
      token_type: 'bearer',
      user: { id: 'user-1', email: `${role.toLowerCase()}@growflow.ai` } as unknown as User,
    },
    supabaseUser: { id: 'user-1', email: `${role.toLowerCase()}@growflow.ai` } as unknown as User,
    user: {
      id: 'user-1',
      email: `${role.toLowerCase()}@growflow.ai`,
      role,
      status: 'ACTIVE',
      fullName: role === 'MENTOR' ? 'Dr. Elena Rostova' : 'Aarav Sharma',
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

describe('Phase 7 Batch 5: Communication, Help Requests, Notes & Groups', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe('StudentGroups Component', () => {
    it('renders list of student groups with mentor details', async () => {
      const mockGroups: GroupResponse[] = [
        {
          id: 'group-1',
          mentor_id: 'mentor-1',
          mentor_name: 'Dr. Elena Rostova',
          name: "Elena's AI Research Cohort",
          join_code: 'ELENA2026',
          status: 'ACTIVE',
          created_at: '2026-09-01T00:00:00Z',
          updated_at: '2026-09-01T00:00:00Z',
        },
      ];
      vi.spyOn(apiClient, 'getStudentGroups').mockResolvedValue(mockGroups);

      render(
        <AuthContext.Provider value={createMockAuth('STUDENT')}>
          <MemoryRouter>
            <StudentGroups />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText("Elena's AI Research Cohort")).toBeInTheDocument();
      });
      expect(screen.getByText('Dr. Elena Rostova')).toBeInTheDocument();
      expect(screen.getByText('ELENA2026')).toBeInTheDocument();
    });

    it('opens join modal, validates input, and successfully joins group', async () => {
      vi.spyOn(apiClient, 'getStudentGroups').mockResolvedValue([]);
      const mockJoined: GroupMembershipResponse = {
        id: 'member-1',
        group_id: 'group-2',
        student_id: 'user-1',
        status: 'ACTIVE',
        joined_at: '2026-09-15T00:00:00Z',
        group_name: "Sofia's Cloud Studio",
        join_code: 'SOFIA2026',
      };
      const joinSpy = vi.spyOn(apiClient, 'joinGroup').mockResolvedValue(mockJoined);

      render(
        <AuthContext.Provider value={createMockAuth('STUDENT')}>
          <MemoryRouter>
            <StudentGroups />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText("You haven't joined any groups yet.")).toBeInTheDocument();
      });

      // Open modal
      const joinBtn = screen.getByRole('button', { name: '+ Join a Group' });
      fireEvent.click(joinBtn);

      expect(screen.getByText('Join a Cohort Group')).toBeInTheDocument();

      const input = screen.getByPlaceholderText('e.g. ELENA001');
      fireEvent.change(input, { target: { value: 'SOFIA2026' } });

      const submitBtn = screen.getByRole('button', { name: 'Join Group' });
      fireEvent.click(submitBtn);

      await waitFor(() => {
        expect(joinSpy).toHaveBeenCalledWith('SOFIA2026');
      });

      await waitFor(() => {
        expect(screen.getByText(/Successfully Joined/i)).toBeInTheDocument();
      });
    });
  });

  describe('MentorHelpRequests Component (M33)', () => {
    it('renders list of help requests and filters by status', async () => {
      const mockRequests: MentorHelpRequestSummary[] = [
        {
          id: 'hr-1',
          project_instance_id: 'proj-1',
          project_name: 'Autonomous Rover Navigation',
          student_id: 'student-1',
          student_name: 'Aarav Sharma',
          student_email: 'student.aarav@growflow.ai',
          group_name: "Elena's AI Research Cohort",
          subject: 'Camera calibration drift',
          description: 'Intrinsic matrix fails on resolution change',
          category: 'TECHNICAL',
          priority: 'HIGH',
          status: 'OPEN',
          created_at: '2026-09-15T00:00:00Z',
        },
        {
          id: 'hr-2',
          project_instance_id: 'proj-2',
          project_name: 'Smart Retail Analytics',
          student_id: 'student-2',
          student_name: 'Riya Patel',
          student_email: 'student.riya@growflow.ai',
          group_name: "Elena's AI Research Cohort",
          subject: 'Database connection pool',
          description: 'Connection exhausted',
          category: 'TECHNICAL',
          priority: 'MEDIUM',
          status: 'RESOLVED',
          mentor_response: 'Increased pool size to 20.',
          resolved_at: '2026-09-15T01:00:00Z',
          created_at: '2026-09-15T00:00:00Z',
        },
      ];
      vi.spyOn(apiClient, 'getMentorHelpRequests').mockImplementation(async (params) => {
        if (params?.status && params.status !== 'ALL') {
          return mockRequests.filter((r) => r.status === params.status);
        }
        return mockRequests;
      });

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter>
            <MentorHelpRequests />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Camera calibration drift')).toBeInTheDocument();
      });
      expect(screen.getByText('Database connection pool')).toBeInTheDocument();

      // Filter by OPEN
      const openFilter = screen.getByRole('button', { name: /OPEN/i });
      fireEvent.click(openFilter);

      await waitFor(() => {
        expect(screen.queryByText('Database connection pool')).not.toBeInTheDocument();
      });
      expect(screen.getByText('Camera calibration drift')).toBeInTheDocument();
    });

    it('submits response and marks help request resolved', async () => {
      const mockRequests: MentorHelpRequestSummary[] = [
        {
          id: 'hr-1',
          project_instance_id: 'proj-1',
          project_name: 'Autonomous Rover Navigation',
          student_id: 'student-1',
          student_name: 'Aarav Sharma',
          student_email: 'student.aarav@growflow.ai',
          group_name: "Elena's AI Research Cohort",
          subject: 'Camera calibration drift',
          description: 'Intrinsic matrix fails on resolution change',
          category: 'TECHNICAL',
          priority: 'HIGH',
          status: 'OPEN',
          created_at: '2026-09-15T00:00:00Z',
        },
      ];
      vi.spyOn(apiClient, 'getMentorHelpRequests').mockResolvedValue(mockRequests);
      const respondSpy = vi.spyOn(apiClient, 'respondMentorHelpRequest').mockResolvedValue({
        ...mockRequests[0],
        status: 'RESOLVED',
        mentor_response: 'Calibrate with fisheye model.',
        resolved_at: '2026-09-15T02:00:00Z',
      } as MentorHelpRequestSummary);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter>
            <MentorHelpRequests />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Camera calibration drift')).toBeInTheDocument();
      });

      const respondBtn = screen.getByRole('button', { name: 'Respond to Request' });
      fireEvent.click(respondBtn);

      expect(screen.getByText(/Respond to Help Request/i)).toBeInTheDocument();

      const textarea = screen.getByPlaceholderText(/Provide technical guidance/i);
      fireEvent.change(textarea, { target: { value: 'Calibrate with fisheye model.' } });

      const sendBtn = screen.getByRole('button', { name: 'Save & Send Response' });
      fireEvent.click(sendBtn);

      await waitFor(() => {
        expect(respondSpy).toHaveBeenCalledWith('hr-1', {
          mentor_response: 'Calibrate with fisheye model.',
          status: 'RESOLVED',
        });
      });
    });

    it('[B4-04] defaults targetStatus to IN_PROGRESS when responding to an IN_PROGRESS request', async () => {
      const mockRequests: MentorHelpRequestSummary[] = [
        {
          id: 'hr-prog',
          project_instance_id: 'proj-1',
          project_name: 'Autonomous Rover Navigation',
          student_id: 'student-1',
          student_name: 'Aarav Sharma',
          student_email: 'student.aarav@growflow.ai',
          group_name: "Elena's AI Research Cohort",
          subject: 'Camera calibration drift',
          description: 'Intrinsic matrix fails on resolution change',
          category: 'TECHNICAL',
          priority: 'HIGH',
          status: 'IN_PROGRESS',
          mentor_response: 'Working on camera fix.',
          created_at: '2026-09-15T00:00:00Z',
        },
      ];
      vi.spyOn(apiClient, 'getMentorHelpRequests').mockResolvedValue(mockRequests);

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter>
            <MentorHelpRequests />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Camera calibration drift')).toBeInTheDocument();
      });

      const respondBtn = screen.getByRole('button', { name: 'Respond to Request' });
      fireEvent.click(respondBtn);

      const statusSelect = document.getElementById('target-status-select') as HTMLSelectElement;
      expect(statusSelect).toBeInTheDocument();
      expect(statusSelect.value).toBe('IN_PROGRESS');
    });
  });

  describe('MentorInstanceNotes Component (M34)', () => {
    it('renders project notes and allows creating a new internal note', async () => {
      const mockProject: MentorProjectInstanceDetail = {
        id: 'proj-1',
        name: 'Autonomous Rover Navigation',
        student_id: 'student-1',
        student_name: 'Aarav Sharma',
        student_email: 'student.aarav@growflow.ai',
        group_id: 'grp-1',
        group_name: "Elena's AI Research Cohort",
        health: 'HEALTHY',
        current_phase: 'BLUEPRINT',
        progress_percentage: 50,
        status: 'ACTIVE',
        deadline: null,
        source_definition_id: null,
        source_definition_name: null,
        source_definition_version_number: null,
        problem: 'Obstacle avoidance',
        proposed_solution: 'LIDAR SLAM',
        complexity: 'INTERMEDIATE',
        source_definition_version_id: null,
        source_definition_version_summary: null,
        student_bio: null,
        student_skills: [],
        created_at: '2026-09-01T00:00:00Z',
        updated_at: '2026-09-01T00:00:00Z',
      };
      const mockNotes: MentorNoteItem[] = [
        {
          id: 'note-1',
          project_instance_id: 'proj-1',
          mentor_id: 'mentor-1',
          mentor_name: 'Dr. Elena Rostova',
          title: 'Review System Specs',
          message: 'Ensure LiDAR driver is pinned.',
          note_type: 'ACTIONABLE',
          status: 'UNREAD',
          created_at: '2026-09-10T00:00:00Z',
        },
        {
          id: 'note-2',
          project_instance_id: 'proj-1',
          mentor_id: 'mentor-1',
          mentor_name: 'Dr. Elena Rostova',
          title: 'Internal Assessment',
          message: 'Student might struggle with calibration math.',
          note_type: 'INTERNAL',
          status: 'UNREAD',
          created_at: '2026-09-11T00:00:00Z',
        },
      ];

      vi.spyOn(apiClient, 'getMentorProjectInstance').mockResolvedValue(mockProject);
      vi.spyOn(apiClient, 'getMentorProjectNotes').mockResolvedValue(mockNotes);
      const createSpy = vi.spyOn(apiClient, 'createMentorNote').mockResolvedValue({
        id: 'note-3',
        project_instance_id: 'proj-1',
        mentor_id: 'mentor-1',
        mentor_name: 'Dr. Elena Rostova',
        title: 'New Internal Observation',
        message: 'Verified calibration logs.',
        note_type: 'INTERNAL',
        status: 'UNREAD',
        created_at: '2026-09-15T00:00:00Z',
      });

      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter initialEntries={['/mentor/project-instances/proj-1/notes']}>
            <Routes>
              <Route path="/mentor/project-instances/:projectId/notes" element={<MentorInstanceNotes />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Review System Specs')).toBeInTheDocument();
      });
      expect(screen.getByText('Internal Assessment')).toBeInTheDocument();
      expect(screen.getByText(/Internal \(Mentor Only\)/i)).toBeInTheDocument();

      // Open new note modal
      const addNoteBtn = screen.getByRole('button', { name: '+ Add Note / Feedback' });
      fireEvent.click(addNoteBtn);

      expect(screen.getByText('Create Mentor Note / Feedback')).toBeInTheDocument();

      const titleInput = screen.getByPlaceholderText(/Architecture Critique/i);
      fireEvent.change(titleInput, { target: { value: 'New Internal Observation' } });

      const msgInput = screen.getByPlaceholderText(/Enter detailed feedback/i);
      fireEvent.change(msgInput, { target: { value: 'Verified calibration logs.' } });

      // Change type select to INTERNAL
      const typeSelect = screen.getByDisplayValue('Student Feedback (Constructive review/critique)');
      fireEvent.change(typeSelect, { target: { value: 'INTERNAL' } });

      const submitBtn = screen.getByRole('button', { name: 'Create Note' });
      fireEvent.click(submitBtn);

      await waitFor(() => {
        expect(createSpy).toHaveBeenCalledWith({
          project_instance_id: 'proj-1',
          title: 'New Internal Observation',
          message: 'Verified calibration logs.',
          note_type: 'INTERNAL',
          related_resource_type: 'PROJECT',
          related_resource_id: undefined,
        });
      });
    });
  });
});
