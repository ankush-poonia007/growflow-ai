import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import type { User } from '@supabase/supabase-js';

import { MentorSidebar } from '@/components/navigation/MentorSidebar';
import { Sidebar as StudentSidebar } from '@/components/navigation/Sidebar';
import { MentorProfile } from '@/pages/Mentor/MentorProfile/MentorProfile';
import { MentorSettings } from '@/pages/Mentor/MentorSettings/MentorSettings';
import { LifecycleTrack } from '@/pages/Student/StudentDashboard/components/LifecycleTrack';
import * as apiClient from '@/lib/api/client';
import type {
  MentorProfileResponse,
  UserPreferencesResponse,
} from '@/lib/api/types';

function createMockAuth(
  role: 'STUDENT' | 'MENTOR' = 'MENTOR',
  fullName = 'Dr. Elena Vance',
  email = 'mentor.elena@growflow.ai'
): AuthContextValue {
  return {
    status: 'AUTHENTICATED',
    session: {
      access_token: 'mock-token',
      refresh_token: 'mock-refresh',
      expires_in: 3600,
      token_type: 'bearer',
      user: { id: 'usr-mentor-1', email } as unknown as User,
    },
    supabaseUser: { id: 'usr-mentor-1', email } as unknown as User,
    user: {
      id: 'usr-mentor-1',
      email,
      role,
      status: 'ACTIVE',
      fullName,
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

const mockMentorProfileData: MentorProfileResponse = {
  user_id: 'usr-mentor-1',
  mentor_id: 'MTR-ELENA-01',
  bio: 'Senior Staff Systems Architect with 15+ years of experience in distributed consensus.',
  specialization: 'Distributed Systems & Cloud Architecture',
};

const mockPreferencesData: UserPreferencesResponse = {
  user_id: 'usr-mentor-1',
  email_notifications: true,
  timezone: 'America/New_York',
  preferences: {
    digest_frequency: 'DAILY',
    compact_view: false,
  },
};

describe('Phase 7 Batch 6 Final Closure Pass', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Area 1 & 4: Mentor Sidebar Parity & Dynamic Identity', () => {
    it('renders all 9 primary mentor navigation destinations with correct links', () => {
      const authVal = createMockAuth('MENTOR', 'Dr. Elena Vance');
      render(
        <AuthContext.Provider value={authVal}>
          <MemoryRouter initialEntries={['/mentor/overview']}>
            <MentorSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByRole('link', { name: /overview/i })).toHaveAttribute('href', '/mentor/overview');
      expect(screen.getByRole('link', { name: /groups/i })).toHaveAttribute('href', '/mentor/groups');
      expect(screen.getByRole('link', { name: /definitions/i })).toHaveAttribute('href', '/mentor/projects');
      expect(screen.getByRole('link', { name: /students/i })).toHaveAttribute('href', '/mentor/students');
      expect(screen.getByRole('link', { name: /project instances/i })).toHaveAttribute('href', '/mentor/project-instances');
      expect(screen.getByRole('link', { name: /at risk/i })).toHaveAttribute('href', '/mentor/at-risk');
      expect(screen.getByRole('link', { name: /help requests/i })).toHaveAttribute('href', '/mentor/help-requests');
      expect(screen.getByRole('link', { name: /activity/i })).toHaveAttribute('href', '/mentor/activity');
      expect(screen.getByRole('link', { name: /ai mentor/i })).toHaveAttribute('href', '/mentor/ai');
    });

    it('displays bottom profile link (/mentor/profile) and settings link (/mentor/settings)', () => {
      const authVal = createMockAuth('MENTOR', 'Dr. Elena Vance');
      render(
        <AuthContext.Provider value={authVal}>
          <MemoryRouter initialEntries={['/mentor/overview']}>
            <MentorSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const profileLink = screen.getByLabelText('Mentor Profile');
      expect(profileLink).toBeInTheDocument();
      expect(profileLink).toHaveAttribute('href', '/mentor/profile');
      expect(screen.getByText('Dr. Elena Vance')).toBeInTheDocument();
      expect(screen.getByText('Mentor Account')).toBeInTheDocument();

      const settingsLink = screen.getByLabelText('Workspace Settings');
      expect(settingsLink).toBeInTheDocument();
      expect(settingsLink).toHaveAttribute('href', '/mentor/settings');
    });

    it('dynamically computes initials EV for Elena Vance and SC for Sofia Chen', () => {
      // Test 1: Elena Vance -> "EV"
      const elenaAuth = createMockAuth('MENTOR', 'Dr. Elena Vance');
      const { unmount } = render(
        <AuthContext.Provider value={elenaAuth}>
          <MemoryRouter initialEntries={['/mentor/overview']}>
            <MentorSidebar isCollapsed={true} onToggleCollapse={vi.fn()} />
          </MemoryRouter>
        </AuthContext.Provider>
      );
      expect(screen.getByText('EV')).toBeInTheDocument();
      unmount();

      // Test 2: Sofia Chen -> "SC"
      const sofiaAuth = createMockAuth('MENTOR', 'Dr. Sofia Chen', 'mentor.sofia@growflow.ai');
      render(
        <AuthContext.Provider value={sofiaAuth}>
          <MemoryRouter initialEntries={['/mentor/overview']}>
            <MentorSidebar isCollapsed={true} onToggleCollapse={vi.fn()} />
          </MemoryRouter>
        </AuthContext.Provider>
      );
      expect(screen.getByText('SC')).toBeInTheDocument();
      expect(screen.queryByText('EV')).not.toBeInTheDocument();
    });
  });

  describe('Area 2 & 3: Collapsed Sidebar Hover & Click Expansion', () => {
    it('temporarily expands collapsed sidebar on hover and contracts on mouse leave', () => {
      const authVal = createMockAuth('MENTOR', 'Dr. Elena Vance');
      render(
        <AuthContext.Provider value={authVal}>
          <MemoryRouter initialEntries={['/mentor/overview']}>
            <MentorSidebar isCollapsed={true} onToggleCollapse={vi.fn()} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const aside = screen.getByLabelText('Mentor Supervise Navigation');
      expect(aside.className).toContain('gf-mentor-sidebar--collapsed');

      // Hover over sidebar
      fireEvent.mouseEnter(aside);
      expect(aside.className).toContain('gf-mentor-sidebar--hover-expanded');
      expect(aside.className).not.toContain('gf-mentor-sidebar--collapsed');

      // Leave sidebar
      fireEvent.mouseLeave(aside);
      expect(aside.className).toContain('gf-mentor-sidebar--collapsed');
      expect(aside.className).not.toContain('gf-mentor-sidebar--hover-expanded');
    });

    it('clicking non-navigation area inside collapsed sidebar expands it permanently via onToggleCollapse', () => {
      const onToggleCollapse = vi.fn();
      const authVal = createMockAuth('MENTOR', 'Dr. Elena Vance');
      render(
        <AuthContext.Provider value={authVal}>
          <MemoryRouter initialEntries={['/mentor/overview']}>
            <MentorSidebar isCollapsed={true} onToggleCollapse={onToggleCollapse} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const aside = screen.getByLabelText('Mentor Supervise Navigation');
      // Click on the empty aside container
      fireEvent.click(aside);
      expect(onToggleCollapse).toHaveBeenCalledTimes(1);
    });

    it('clicking an actual nav item navigates and does not trigger toggleCollapse', () => {
      const onToggleCollapse = vi.fn();
      const authVal = createMockAuth('MENTOR', 'Dr. Elena Vance');
      render(
        <AuthContext.Provider value={authVal}>
          <MemoryRouter initialEntries={['/mentor/overview']}>
            <MentorSidebar isCollapsed={true} onToggleCollapse={onToggleCollapse} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const groupsLink = screen.getByRole('link', { name: /groups/i });
      fireEvent.click(groupsLink);
      // Link click should NOT fire toggle collapse
      expect(onToggleCollapse).not.toHaveBeenCalled();
    });
  });

  describe('Area 5: Mentor Profile Surface', () => {
    it('loads and renders mentor profile with canonical identity, specialization, and bio', async () => {
      vi.spyOn(apiClient, 'getMentorProfile').mockResolvedValue(mockMentorProfileData);

      const authVal = createMockAuth('MENTOR', 'Dr. Elena Vance');
      render(
        <AuthContext.Provider value={authVal}>
          <MemoryRouter>
            <MentorProfile />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Mentor Profile')).toBeInTheDocument();
      });

      expect(screen.getByText('Dr. Elena Vance')).toBeInTheDocument();
      expect(screen.getByText('mentor.elena@growflow.ai')).toBeInTheDocument();
      expect(screen.getByText('MTR-ELENA-01')).toBeInTheDocument();
      expect(screen.getByText('Distributed Systems & Cloud Architecture')).toBeInTheDocument();
      expect(screen.getByText(/Senior Staff Systems Architect/i)).toBeInTheDocument();
    });

    it('allows entering edit mode and saving updated bio/specialization', async () => {
      vi.spyOn(apiClient, 'getMentorProfile').mockResolvedValue(mockMentorProfileData);
      const updateSpy = vi.spyOn(apiClient, 'updateMentorProfile').mockResolvedValue({
        ...mockMentorProfileData,
        bio: 'Updated bio description',
      });

      const authVal = createMockAuth('MENTOR', 'Dr. Elena Vance');
      render(
        <AuthContext.Provider value={authVal}>
          <MemoryRouter>
            <MentorProfile />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Edit Profile')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Edit Profile'));
      expect(screen.getByText('Edit Supervision Context')).toBeInTheDocument();

      const bioInput = screen.getByLabelText(/Professional Biography/i);
      fireEvent.change(bioInput, { target: { value: 'Updated bio description' } });

      fireEvent.click(screen.getByText('Save Profile'));

      await waitFor(() => {
        expect(updateSpy).toHaveBeenCalledWith({
          specialization: 'Distributed Systems & Cloud Architecture',
          bio: 'Updated bio description',
        });
        expect(screen.getByText('Profile updated successfully.')).toBeInTheDocument();
      });
    });
  });

  describe('Area 6: Mentor Settings Surface', () => {
    it('loads and renders preferences including email notifications, timezone, and digest frequency', async () => {
      vi.spyOn(apiClient, 'getUserPreferences').mockResolvedValue(mockPreferencesData);

      const authVal = createMockAuth('MENTOR', 'Dr. Elena Vance');
      render(
        <AuthContext.Provider value={authVal}>
          <MemoryRouter>
            <MentorSettings />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Workspace Settings')).toBeInTheDocument();
      });

      expect(screen.getByLabelText('Email Notifications')).toBeChecked();
      expect(screen.getByLabelText('System Timezone')).toHaveValue('America/New_York');
      expect(screen.getByLabelText(/Digest Frequency/i)).toHaveValue('DAILY');
      expect(screen.getByText('mentor.elena@growflow.ai')).toBeInTheDocument();
    });

    it('submits updated settings to backend preferences endpoint', async () => {
      vi.spyOn(apiClient, 'getUserPreferences').mockResolvedValue(mockPreferencesData);
      const updatePrefsSpy = vi.spyOn(apiClient, 'updateUserPreferences').mockResolvedValue({
        ...mockPreferencesData,
        email_notifications: false,
        timezone: 'Asia/Kolkata',
      });

      const authVal = createMockAuth('MENTOR', 'Dr. Elena Vance');
      render(
        <AuthContext.Provider value={authVal}>
          <MemoryRouter>
            <MentorSettings />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Save Settings')).toBeInTheDocument();
      });

      // Toggle email notifications
      fireEvent.click(screen.getByLabelText('Email Notifications'));
      // Change timezone
      fireEvent.change(screen.getByLabelText('System Timezone'), { target: { value: 'Asia/Kolkata' } });

      fireEvent.click(screen.getByText('Save Settings'));

      await waitFor(() => {
        expect(updatePrefsSpy).toHaveBeenCalledWith(
          expect.objectContaining({
            email_notifications: false,
            timezone: 'Asia/Kolkata',
          })
        );
        expect(screen.getByText('Settings saved successfully.')).toBeInTheDocument();
      });
    });
  });

  describe('Area 8: Student Sidebar Parity', () => {
    it('provides Profile link (/profile), Settings button (/settings), and hover/click expansion', () => {
      const onToggleCollapse = vi.fn();
      const authVal = createMockAuth('STUDENT', 'Aarav Sharma', 'student.aarav@growflow.ai');
      render(
        <AuthContext.Provider value={authVal}>
          <MemoryRouter initialEntries={['/student/dashboard']}>
            <StudentSidebar isCollapsed={true} onToggleCollapse={onToggleCollapse} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const profileLink = screen.getByLabelText('Student Profile');
      expect(profileLink).toHaveAttribute('href', '/profile');

      const settingsLink = screen.getByLabelText('Workspace Settings');
      expect(settingsLink).toHaveAttribute('href', '/settings');

      const aside = screen.getByLabelText('Student Workspace Navigation');
      // Hover expansion
      fireEvent.mouseEnter(aside);
      expect(aside.className).toContain('gf-sidebar--hover-expanded');
      fireEvent.mouseLeave(aside);
      expect(aside.className).toContain('gf-sidebar--collapsed');

      // Click to expand
      fireEvent.click(aside);
      expect(onToggleCollapse).toHaveBeenCalledTimes(1);
    });
  });

  describe('Area 9: Student Lifecycle Track Spacing & Rendering', () => {
    it('renders all 8 canonical lifecycle stages with correct stage progression', () => {
      render(
        <MemoryRouter>
          <LifecycleTrack currentPhase="IDEA" />
        </MemoryRouter>
      );

      expect(screen.getByText('Stage 1 of 8 — IDEA')).toBeInTheDocument();
      expect(screen.getByText('Idea')).toBeInTheDocument();
      expect(screen.getByText('Assessment')).toBeInTheDocument();
      expect(screen.getByText('Blueprint')).toBeInTheDocument();
      expect(screen.getByText('Planning')).toBeInTheDocument();
      expect(screen.getByText('Implementation')).toBeInTheDocument();
      expect(screen.getByText('Testing')).toBeInTheDocument();
      expect(screen.getByText('Deployment')).toBeInTheDocument();
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });
  });
});
