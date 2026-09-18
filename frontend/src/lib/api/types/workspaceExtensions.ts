/**
 * GrowFlow Workspace Extensions API Types (Batch 06: S27–S33).
 */

export interface GitHubCommitPreview {
  sha: string;
  message: string;
  author: string;
  date: string;
}

export interface GitHubIntegrationResponse {
  id: string | null;
  project_instance_id: string;
  repository_name: string;
  repository_url: string;
  connection_status: 'NOT_CONNECTED' | 'CONNECTED' | 'SYNCING' | 'ERROR';
  default_branch: string;
  commit_count: number;
  last_sync_at: string | null;
  sync_error: string | null;
  cached_commits_preview: GitHubCommitPreview[];
}

export interface GitHubConnectPayload {
  repository_url: string;
  repository_name?: string;
  default_branch?: string;
}

export interface ActivityItemResponse {
  id: string;
  event_type: string;
  title: string;
  description: string;
  actor_role: string;
  actor_id: string | null;
  resource_type: string;
  resource_id: string;
  project_instance_id?: string | null;
  group_id?: string | null;
  occurred_at: string | null;
  metadata: Record<string, any>;
}


export interface AIMentorMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources: Array<{ title: string; section?: string }>;
  suggested_action: {
    action_type: string;
    label: string;
    payload: Record<string, any>;
  } | null;
  created_at: string | null;
}

export interface AIMentorConversationResponse {
  conversation_id: string;
  project_instance_id: string;
  title: string;
  ai_available: boolean;
  messages: AIMentorMessage[];
}

export interface AIMentorSendResponse {
  user_message: AIMentorMessage;
  assistant_message: AIMentorMessage;
  ai_available: boolean;
}

export interface HelpRequestResponse {
  id: string;
  project_instance_id: string;
  student_id: string;
  subject: string;
  description: string;
  category: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  status: 'OPEN' | 'IN_REVIEW' | 'RESOLVED';
  mentor_response: string | null;
  resolved_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface HelpRequestCreatePayload {
  subject: string;
  description: string;
  category?: string;
  priority?: string;
}

export interface MentorNoteResponse {
  id: string;
  project_instance_id: string;
  mentor_id: string | null;
  title: string;
  message: string;
  note_type: 'INFORMATIONAL' | 'ACTIONABLE' | 'FEEDBACK';
  status: 'UNREAD' | 'ACKNOWLEDGED';
  related_resource_type: string | null;
  related_resource_id: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface ImpactAnalysis {
  affected_sections: string[];
  affected_tasks_count: number;
  total_tasks_count?: number;
  total_milestones_count?: number;
  estimated_risk: 'LOW' | 'MEDIUM' | 'HIGH';
  analysis_narrative: string;
  duration_impact?: string;
  recommended_action?: string;
}

export interface ProjectChangeResponse {
  id: string;
  project_instance_id: string;
  student_id: string;
  change_title: string;
  change_description: string;
  change_type: 'SCOPE' | 'TECH_STACK' | 'ARCHITECTURE' | 'SCHEDULE';
  status: 'ANALYZED' | 'CONFIRMED' | 'COMPLETED' | 'REJECTED';
  idempotency_key: string | null;
  impact_analysis: ImpactAnalysis;
  source_blueprint_version_number: number;
  resulting_blueprint_version_number: number | null;
  qa_score: number | null;
  qa_feedback: Record<string, any> | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface ProjectChangeAnalyzePayload {
  change_title: string;
  change_description: string;
  change_type: string;
}

export interface ProjectChangeConfirmPayload {
  idempotency_key?: string;
}

export interface BlueprintVersionResponse {
  id: string;
  blueprint_id: string;
  project_instance_id: string;
  version_number: number;
  status: string;
  qa_score: number | null;
  qa_feedback?: Record<string, any> | null;
  change_summary: string | null;
  created_at: string | null;
  content?: Record<string, any> | null;
}

export interface MentorAIChatPayload {
  message: string;
  history?: Array<{ role: string; content: string }>;
}

export interface MentorAIChatResponse {
  user_message: {
    id: string;
    role: string;
    content: string;
    created_at: string;
  };
  assistant_message: {
    id: string;
    role: string;
    content: string;
    sources: Array<{ title: string; section?: string }>;
    created_at: string;
  };
  ai_available: boolean;
  scope: 'GROUP' | 'PORTFOLIO' | string;
  group_id?: string | null;
  group_name?: string | null;
  mentor_id?: string | null;
}

export interface MentorAIStatusResponse {
  ai_available: boolean;
  scope: 'GROUP' | 'PORTFOLIO' | string;
  group_id?: string | null;
  group_name?: string | null;
  mentor_id?: string | null;
}

