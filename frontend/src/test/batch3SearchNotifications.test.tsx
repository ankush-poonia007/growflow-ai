import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { AuthHeader } from '@/components/navigation/AuthHeader';
import { GlobalSearchModal } from '@/components/navigation/GlobalSearchModal';
import { NotificationsPopover } from '@/components/navigation/NotificationsPopover';
import * as apiClient from '@/lib/api/client';
import type { NotificationItem } from '@/lib/api/types';

// Mock useAuth
vi.mock('@/auth/useAuth', () => ({
  useAuth: () => ({
    user: { id: 'usr-1', email: 'student@example.com', fullName: 'Student User', role: 'STUDENT' },
    isRoleResolving: false,
    signOut: vi.fn(),
  }),
}));

const mockNotifications: NotificationItem[] = [
  {
    id: 'notif-1',
    user_id: 'usr-1',
    title: 'Mentor Note Created',
    message: 'Please update your system architecture diagram.',
    notification_type: 'MentorNoteCreated',
    category: 'FEEDBACK',
    link: '/student/notes/1',
    is_read: false,
    read_at: null,
    created_at: new Date(Date.now() - 60000).toISOString(),
  },
  {
    id: 'notif-2',
    user_id: 'usr-1',
    title: 'Blueprint Approved',
    message: 'Your project blueprint has been approved by your mentor.',
    notification_type: 'BlueprintApproved',
    category: 'BLUEPRINT',
    link: '/student/projects/proj-1/blueprint',
    is_read: true,
    read_at: new Date(Date.now() - 3600000).toISOString(),
    created_at: new Date(Date.now() - 7200000).toISOString(),
  },
];

let searchSpy: any;

describe('Phase 8 Batch 3: Search & Notifications UI', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(apiClient, 'getUnreadNotificationCount').mockResolvedValue({ unread_count: 1 });
    vi.spyOn(apiClient, 'getNotifications').mockResolvedValue(mockNotifications);
    vi.spyOn(apiClient, 'markNotificationRead').mockResolvedValue({
      ...mockNotifications[0]!,
      is_read: true,
      read_at: new Date().toISOString(),
    });
    vi.spyOn(apiClient, 'markAllNotificationsRead').mockResolvedValue({ marked_count: 1 });
    searchSpy = vi.spyOn(apiClient, 'searchWorkspace').mockResolvedValue({
      query: 'telemetry',
      workplace: 'BUILD',
      total: 1,
      results: [
        {
          title: 'Precision Drone Telemetry',
          subtitle: 'Phase: BLUEPRINT • Health: HEALTHY',
          resource_type: 'project',
          url: '/student/projects/proj-1',
          badge: 'PROJECT',
          metadata: { status: 'ACTIVE' },
        },
      ],
    });
  });

  // =========================================================================
  // 1. GLOBAL SEARCH SHORTCUT & MODAL BEHAVIOR
  // =========================================================================
  describe('Global Search Modal', () => {
    it('opens on Ctrl+K and closes on Escape', async () => {
      render(
        <MemoryRouter>
          <AuthHeader onToggleMobileNav={vi.fn()} isMobileNavOpen={false} workplace="BUILD" />
        </MemoryRouter>,
      );

      // Initially search modal not rendered
      expect(screen.queryByRole('dialog', { name: /global workspace search/i })).not.toBeInTheDocument();

      // Press Ctrl+K
      fireEvent.keyDown(window, { key: 'k', ctrlKey: true });
      expect(await screen.findByRole('dialog', { name: /global workspace search/i })).toBeInTheDocument();

      // Press Escape
      fireEvent.keyDown(window, { key: 'Escape' });
      await waitFor(() => {
        expect(screen.queryByRole('dialog', { name: /global workspace search/i })).not.toBeInTheDocument();
      });
    });

    it('opens when clicking search icon button', async () => {
      render(
        <MemoryRouter>
          <AuthHeader onToggleMobileNav={vi.fn()} isMobileNavOpen={false} workplace="BUILD" />
        </MemoryRouter>,
      );

      const searchBtn = screen.getByRole('button', { name: /search workspace/i });
      fireEvent.click(searchBtn);

      expect(await screen.findByRole('dialog', { name: /global workspace search/i })).toBeInTheDocument();
    });

    it('renders initial empty guidance state when no query has been typed', () => {
      render(
        <MemoryRouter>
          <GlobalSearchModal isOpen={true} onClose={vi.fn()} workplace="BUILD" />
        </MemoryRouter>,
      );

      expect(screen.getByText(/BUILD Workspace Search/i)).toBeInTheDocument();
      expect(screen.getByText(/Role-aware discovery across your authorized build resources/i)).toBeInTheDocument();
    });

    it('displays search results when query matches', async () => {
      render(
        <MemoryRouter>
          <GlobalSearchModal isOpen={true} onClose={vi.fn()} workplace="BUILD" />
        </MemoryRouter>,
      );

      const input = screen.getByPlaceholderText(/search build workspace\.\.\./i);
      fireEvent.change(input, { target: { value: 'telemetry' } });

      await waitFor(
        () => {
          expect(screen.getByText('Precision Drone Telemetry')).toBeInTheDocument();
          expect(screen.getByText('PROJECT')).toBeInTheDocument();
        },
        { timeout: 2000 },
      );
    });

    it('displays empty state when query returns 0 results', async () => {
      searchSpy.mockResolvedValueOnce({
        query: 'unknown-query',
        workplace: 'BUILD',
        total: 0,
        results: [],
      });

      render(
        <MemoryRouter>
          <GlobalSearchModal isOpen={true} onClose={vi.fn()} workplace="BUILD" />
        </MemoryRouter>,
      );

      const input = screen.getByPlaceholderText(/search build workspace\.\.\./i);
      fireEvent.change(input, { target: { value: 'unknown-query' } });

      await waitFor(
        () => {
          expect(screen.getByText(/no resources found/i)).toBeInTheDocument();
          expect(screen.getByText(/no matching authorized resources found for "unknown-query"/i)).toBeInTheDocument();
        },
        { timeout: 2000 },
      );
    });

    it('displays error state with retry when search fails', async () => {
      searchSpy.mockRejectedValue(new Error('Network error'));

      render(
        <MemoryRouter>
          <GlobalSearchModal isOpen={true} onClose={vi.fn()} workplace="BUILD" />
        </MemoryRouter>,
      );

      const input = screen.getByPlaceholderText(/search build workspace\.\.\./i);
      fireEvent.change(input, { target: { value: 'error-query' } });

      await waitFor(
        () => {
          expect(screen.getByRole('alert')).toBeInTheDocument();
          expect(screen.getByText(/Network error/i)).toBeInTheDocument();
        },
        { timeout: 2000 },
      );
    });

    it('renders role-aware workplace category chips', () => {
      const { rerender } = render(
        <MemoryRouter>
          <GlobalSearchModal isOpen={true} onClose={vi.fn()} workplace="BUILD" />
        </MemoryRouter>,
      );
      expect(screen.getByRole('button', { name: 'Projects' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Catalog' })).toBeInTheDocument();

      rerender(
        <MemoryRouter>
          <GlobalSearchModal isOpen={true} onClose={vi.fn()} workplace="SUPERVISE" />
        </MemoryRouter>,
      );
      expect(screen.getByRole('button', { name: 'Groups' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Students' })).toBeInTheDocument();

      rerender(
        <MemoryRouter>
          <GlobalSearchModal isOpen={true} onClose={vi.fn()} workplace="GOVERN" />
        </MemoryRouter>,
      );
      expect(screen.getByRole('button', { name: 'Audit' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Users' })).toBeInTheDocument();
    });
  });

  // =========================================================================
  // 2. NOTIFICATIONS POPOVER BEHAVIOR
  // =========================================================================
  describe('Notifications Popover', () => {
    it('displays unread count badge in header when unreadCount > 0', async () => {
      render(
        <MemoryRouter>
          <AuthHeader onToggleMobileNav={vi.fn()} isMobileNavOpen={false} workplace="BUILD" />
        </MemoryRouter>,
      );

      await waitFor(() => {
        expect(screen.getByText('1')).toBeInTheDocument();
      });
    });

    it('renders list with read/unread distinctions', () => {
      render(
        <MemoryRouter>
          <NotificationsPopover
            isOpen={true}
            onClose={vi.fn()}
            notifications={mockNotifications}
            unreadCount={1}
            isLoading={false}
            error={null}
            onMarkAsRead={vi.fn()}
            onMarkAllAsRead={vi.fn()}
          />
        </MemoryRouter>,
      );

      expect(screen.getByText('Mentor Note Created')).toBeInTheDocument();
      expect(screen.getByText('Blueprint Approved')).toBeInTheDocument();
      expect(screen.getByText('1 New')).toBeInTheDocument();
    });

    it('calls onMarkAsRead when clicking an unread notification', async () => {
      const markAsReadMock = vi.fn().mockResolvedValue(undefined);
      const closeMock = vi.fn();

      render(
        <MemoryRouter>
          <NotificationsPopover
            isOpen={true}
            onClose={closeMock}
            notifications={mockNotifications}
            unreadCount={1}
            isLoading={false}
            error={null}
            onMarkAsRead={markAsReadMock}
            onMarkAllAsRead={vi.fn()}
          />
        </MemoryRouter>,
      );

      const unreadItem = screen.getByRole('button', { name: /mentor note created/i });
      fireEvent.click(unreadItem);

      expect(markAsReadMock).toHaveBeenCalledWith('notif-1');
      await waitFor(() => {
        expect(closeMock).toHaveBeenCalled();
      });
    });

    it('calls onMarkAllAsRead when clicking mark all read button', async () => {
      const markAllMock = vi.fn().mockResolvedValue(undefined);

      render(
        <MemoryRouter>
          <NotificationsPopover
            isOpen={true}
            onClose={vi.fn()}
            notifications={mockNotifications}
            unreadCount={1}
            isLoading={false}
            error={null}
            onMarkAsRead={vi.fn()}
            onMarkAllAsRead={markAllMock}
          />
        </MemoryRouter>,
      );

      const markAllBtn = screen.getByRole('button', { name: /mark all notifications as read/i });
      fireEvent.click(markAllBtn);

      expect(markAllMock).toHaveBeenCalled();
    });

    it('renders truthful empty state when there are 0 notifications', () => {
      render(
        <MemoryRouter>
          <NotificationsPopover
            isOpen={true}
            onClose={vi.fn()}
            notifications={[]}
            unreadCount={0}
            isLoading={false}
            error={null}
            onMarkAsRead={vi.fn()}
            onMarkAllAsRead={vi.fn()}
          />
        </MemoryRouter>,
      );

      expect(screen.getByText(/you're all caught up/i)).toBeInTheDocument();
      expect(screen.getByText(/no notifications right now/i)).toBeInTheDocument();
    });

    it('renders loading spinner when isLoading is true', () => {
      render(
        <MemoryRouter>
          <NotificationsPopover
            isOpen={true}
            onClose={vi.fn()}
            notifications={[]}
            unreadCount={0}
            isLoading={true}
            error={null}
            onMarkAsRead={vi.fn()}
            onMarkAllAsRead={vi.fn()}
          />
        </MemoryRouter>,
      );

      expect(screen.getByRole('status')).toBeInTheDocument();
      expect(screen.getByText(/loading notifications\.\.\./i)).toBeInTheDocument();
    });

    it('renders error state with retry when error is provided', () => {
      const retryMock = vi.fn();
      render(
        <MemoryRouter>
          <NotificationsPopover
            isOpen={true}
            onClose={vi.fn()}
            notifications={[]}
            unreadCount={0}
            isLoading={false}
            error="Failed to load notifications."
            onMarkAsRead={vi.fn()}
            onMarkAllAsRead={vi.fn()}
            onRefresh={retryMock}
          />
        </MemoryRouter>,
      );

      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText('Failed to load notifications.')).toBeInTheDocument();
      const retryBtn = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(retryBtn);
      expect(retryMock).toHaveBeenCalled();
    });
  });
});
