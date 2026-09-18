/**
 * GrowFlow Project Domain API Types
 *
 * Reflects backend schemas:
 * backend/app/api/schemas/project.py
 * backend/app/domain/project/models.py
 */

export type ProjectPhase =
  | 'IDEA'
  | 'ASSESSMENT'
  | 'BLUEPRINT'
  | 'PLANNING'
  | 'IMPLEMENTATION'
  | 'TESTING'
  | 'DEPLOYMENT'
  | 'COMPLETED';

export type ProjectHealth = 'HEALTHY' | 'WARNING' | 'CRITICAL';

export type ProjectComplexity = 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';

export type ProjectStatus = 'DRAFT' | 'ACTIVE' | 'ON_HOLD' | 'COMPLETED' | 'ARCHIVED';

export interface ProjectResponse {
  id: string;
  student_id: string;
  group_id: string | null;
  project_definition_id: string | null;
  source_definition_version_id: string | null;
  name: string;
  problem: string;
  proposed_solution: string;
  complexity: ProjectComplexity | string | null;
  current_phase: ProjectPhase | string;
  health: ProjectHealth | string;
  progress_percentage: number;
  status: ProjectStatus | string;
  deadline: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface ProjectProfileData {
  objective?: string;
  target_users?: string;
  project_type?: string;
  student_skill_context?: string;
  goals?: string;
  scope?: string;
  expected_outcome?: string;
  constraints?: string;
  assumptions?: string;
  version?: number;
}

export interface ProjectTechnologyItem {
  id: string;
  technology_id: string;
  category?: string;
  purpose?: string;
  why_selected?: string;
}

export interface PhaseTransitionRecord {
  previous_phase: string;
  new_phase: string;
  changed_at: string;
  reason?: string;
}

export interface HealthTransitionRecord {
  previous_health: string;
  new_health: string;
  changed_at: string;
  reason?: string;
}

export interface ProjectRecentActivity {
  latest_phase_transition?: PhaseTransitionRecord | null;
  latest_health_transition?: HealthTransitionRecord | null;
}

export interface AssessmentOverviewSummary {
  status: string;
  overall_score: number | null;
  readiness_tier: string | null;
  dimension_scores: Record<string, number> | null;
  technical_gaps_count: number;
  recommendations_count: number;
  completed_at: string | null;
}

export interface BlueprintOverviewSummary {
  id: string | null;
  status: string;
  qa_status: string | null;
  qa_score: number | null;
  approved_at: string | null;
  total_sections: number;
}

export interface ProjectOverviewResponse {
  id: string;
  student_id: string;
  group_id: string | null;
  project_definition_id: string | null;
  source_definition_version_id?: string | null;
  is_mentor_project?: boolean;
  name: string;
  problem: string;
  proposed_solution: string;
  complexity: ProjectComplexity | string;
  current_phase: ProjectPhase | string;
  health: ProjectHealth | string;
  progress_percentage: number;
  status: ProjectStatus | string;
  deadline: string | null;
  days_remaining: number | null;
  profile: ProjectProfileData | null;
  technologies: ProjectTechnologyItem[];
  recent_activity: ProjectRecentActivity;
  assessment_summary?: AssessmentOverviewSummary | null;
  blueprint_summary?: BlueprintOverviewSummary | null;
}

export interface ProjectCreatePayload {
  name: string;
  problem?: string;
  proposed_solution?: string;
  complexity?: ProjectComplexity | string;
  technologies?: string[];
  deadline?: string | null;
  group_id?: string | null;
}

export interface ProjectUpdatePayload {
  name?: string;
  problem?: string;
  proposed_solution?: string;
  complexity?: ProjectComplexity | string;
  deadline?: string | null;
}

export interface ProjectPhaseTransitionPayload {
  target_phase: ProjectPhase | string;
  reason?: string;
}

export interface ProjectHealthUpdatePayload {
  health: ProjectHealth | string;
  reason?: string;
}

export interface ProjectDefinitionCatalogItem {
  id: string;
  name: string;
  status: string;
  version_number: number | null;
  problem: string;
  proposed_solution: string;
  complexity: ProjectComplexity | string;
  description: string;
  duration: string;
  constraints: string;
  assumptions: string;
  technology_snapshot: Array<Record<string, unknown> | string>;
  created_at: string | null;
  updated_at: string | null;
}
