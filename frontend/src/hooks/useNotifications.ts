import { useState, useEffect, useCallback } from 'react';
import * as apiClient from '@/lib/api/client';
import type { NotificationItem } from '@/lib/api/types';

export interface UseNotificationsResult {
  notifications: NotificationItem[];
  unreadCount: number;
  isLoading: boolean;
  error: string | null;
  fetchNotifications: () => Promise<void>;
  fetchUnreadCount: () => Promise<void>;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
}

export function useNotifications(initialLimit = 20): UseNotificationsResult {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUnreadCount = useCallback(async () => {
    try {
      const res = await apiClient.getUnreadNotificationCount();
      setUnreadCount(res.unread_count || 0);
    } catch {
      // Background count fetch failures should degrade quietly
    }
  }, []);

  const fetchNotifications = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient.getNotifications({ limit: initialLimit });
      setNotifications(data || []);
      // Also sync count
      await fetchUnreadCount();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load notifications.';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [initialLimit, fetchUnreadCount]);

  useEffect(() => {
    fetchUnreadCount();
  }, [fetchUnreadCount]);

  const markAsRead = useCallback(
    async (id: string) => {
      // Optimistic update
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true, read_at: new Date().toISOString() } : n)),
      );
      setUnreadCount((c) => Math.max(0, c - 1));

      try {
        await apiClient.markNotificationRead(id);
      } catch (err) {
        // Revert by re-fetching on error
        fetchNotifications();
        throw err;
      }
    },
    [fetchNotifications],
  );

  const markAllAsRead = useCallback(async () => {
    // Optimistic update
    const now = new Date().toISOString();
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true, read_at: now })));
    setUnreadCount(0);

    try {
      await apiClient.markAllNotificationsRead();
    } catch (err) {
      fetchNotifications();
      throw err;
    }
  }, [fetchNotifications]);

  return {
    notifications,
    unreadCount,
    isLoading,
    error,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
  };
}
