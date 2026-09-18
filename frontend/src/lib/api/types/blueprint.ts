/**
 * Blueprint API Types (Stage 3 - Student Blueprint Workflow)
 */

export type BlueprintStatus =
  | 'NOT_STARTED'
  | 'GENERATING'
  | 'GENERATED'
  | 'VALIDATING'
  | 'QA_REJECTED'
  | 'READY_FOR_APPROVAL'
  | 'COMPLETED'
  | 'FAILED'
  | 'APPROVED';

export type BlueprintQAStatus =
  | 'PENDING'
  | 'IN_REVIEW'
  | 'PASSED'
  | 'FAILED';

export type BlueprintJobType =
  | 'FULL_GENERATION'
  | 'SECTION_RETRY';

export type BlueprintJobStatus =
  | 'PENDING'
  | 'RUNNING'
  | 'COMPLETED'
  | 'FAILED';

export type BlueprintSectionKey =
  | 'project_profile'
  | 'tech_stack'
  | 'features'
  | 'specifications'
  | 'mvp'
  | 'duration'
  | 'risks'
  | 'tasks'
  | 'milestones'
  | 'readme';

export const CANONICAL_BLUEPRINT_SECTION_LABELS: Record<BlueprintSectionKey, string> = {
  project_profile: 'Project Profile & Domain Context',
  tech_stack: 'Technical Stack & Architecture',
  features: 'Core Features & System Modules',
  specifications: 'Technical Specifications & Data Models',
  mvp: 'MVP Scope & Validation Criteria',
  duration: 'Timeline & Sprint Duration',
  risks: 'Technical Risks & Mitigations',
  tasks: 'Granular Work Breakdown (Tasks)',
  milestones: 'Stage Milestones & Gate Deliverables',
  readme: 'Production README & Setup Guide',
};

export const CANONICAL_BLUEPRINT_SECTION_ORDER: BlueprintSectionKey[] = [
  'project_profile',
  'tech_stack',
  'features',
  'specifications',
  'mvp',
  'duration',
  'risks',
  'tasks',
  'milestones',
  'readme',
];

export interface BlueprintQAFeedback {
  score: number;
  status: BlueprintQAStatus;
  evaluated_criteria?: Record<string, number>;
  summary?: string;
  issues?: Array<{
    section: string;
    severity: string;
    description: string;
    recommendation: string;
  }>;
  strengths?: string[];
  gaps?: string[];
  recommendations?: string[];
  evaluated_at?: string;
}

export interface BlueprintGenerationProgress {
  completed_sections: BlueprintSectionKey[];
  total_sections: number;
  in_progress_section?: BlueprintSectionKey | null;
  failed_sections?: BlueprintSectionKey[];
}

export interface BlueprintJobSummary {
  id: string;
  job_type: BlueprintJobType;
  status: BlueprintJobStatus;
  error_message?: string | null;
  failed_sections: BlueprintSectionKey[];
  created_at: string;
}

export interface BlueprintStatusResponse {
  blueprint_id: string;
  project_id: string;
  status: BlueprintStatus;
  current_stage: number;
  qa_status: BlueprintQAStatus;
  qa_feedback?: BlueprintQAFeedback | null;
  generation_progress: BlueprintGenerationProgress;
  active_job?: BlueprintJobSummary | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface BlueprintContentResponse {
  project_instance_id?: string;
  blueprint_id?: string;
  project_id?: string;
  status: BlueprintStatus;
  qa_status?: BlueprintQAStatus;
  qa_score?: number | null;
  content: Record<string, unknown>;
  qa_feedback?: BlueprintQAFeedback | null;
}

export interface BlueprintApprovalResponse {
  success?: boolean;
  status: BlueprintStatus | string;
  approved_at: string;
  blueprint_id?: string;
  project_id?: string;
  message?: string;
}

export interface BlueprintRetryRequest {
  target_output_key?: string | null;
}
