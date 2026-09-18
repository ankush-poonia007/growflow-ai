import type { ProjectResponse } from './project';

export interface MentorGroupSummary {
  id: string;
  name: string;
  join_code: string;
  status: string;
  student_count: number;
  project_count: number;
  at_risk_count: number;
  created_at?: string | null;
}

export interface MentorOverviewResponse {
  total_groups: number;
  total_students: number;
  total_projects: number;
  at_risk_projects: number;
  groups: MentorGroupSummary[];
}

export interface GroupResponse {
  id: string;
  mentor_id: string;
  name: string;
  join_code: string;
  status: string;
  mentor_name?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface GroupMembershipResponse {
  id: string;
  group_id: string;
  student_id: string;
  status: string;
  joined_at?: string;
  left_at?: string | null;
  group_name?: string;
  mentor_name?: string;
  join_code?: string;
}

export interface GroupCreatePayload {
  name: string;
}

export interface GroupStudentResponse {
  student_id: string;
  email: string;
  full_name?: string | null;
  status: string;
  joined_at: string;
}

export type GroupProjectResponse = ProjectResponse;

export interface MentorHelpRequestSummary {
  id: string;
  project_instance_id: string;
  project_name: string;
  student_id: string;
  student_name: string;
  student_email: string;
  group_id?: string | null;
  group_name?: string | null;
  subject: string;
  description: string;
  category: string;
  priority: string;
  status: string;
  mentor_response?: string | null;
  resolved_at?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface HelpRequestRespondPayload {
  mentor_response: string;
  status?: string;
}

export interface MentorNoteCreatePayload {
  project_instance_id: string;
  title: string;
  message: string;
  note_type?: string;
  related_resource_type?: string | null;
  related_resource_id?: string | null;
}

export interface MentorNoteItem {
  id: string;
  project_instance_id: string;
  mentor_id?: string | null;
  mentor_name?: string | null;
  title: string;
  message: string;
  note_type: string;
  status: string;
  related_resource_type?: string | null;
  related_resource_id?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface MentorProfileResponse {
  user_id: string;
  mentor_id: string;
  bio: string | null;
  specialization: string | null;
}

export interface MentorProfileUpdatePayload {
  bio?: string | null;
  specialization?: string | null;
}

export interface UserPreferencesResponse {
  user_id: string;
  email_notifications: boolean;
  timezone: string;
  preferences: Record<string, unknown>;
}

export interface UserPreferencesUpdatePayload {
  email_notifications?: boolean | null;
  timezone?: string | null;
  preferences?: Record<string, unknown> | null;
}
