/**
 * GrowFlow — Notification API Types (Phase 8 Batch 3)
 */

export interface NotificationItem {
  id: string;
  user_id: string;
  actor_id?: string | null;
  actor_role?: string | null;
  title: string;
  message: string;
  notification_type: string;
  category: string;
  resource_type?: string | null;
  resource_id?: string | null;
  link: string;
  is_read: boolean;
  read_at?: string | null;
  created_at: string;
}

export interface UnreadCountResponse {
  unread_count: number;
}

export interface MarkAllReadResponse {
  marked_count: number;
}
