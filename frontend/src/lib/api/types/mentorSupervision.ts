/**
 * Mentor Supervision API Types (Batch 3)
 *
 * Reflects backend schemas:
 * backend/app/api/schemas/mentor_supervision.py
 */

import { ProjectPhase, ProjectHealth, ProjectComplexity, ProjectStatus } from './project';

export interface MentorStudentGroupSummary {
  id: string;
  name: string;
  joined_at: string;
}

export interface MentorStudentSummary {
  id: string;
  full_name: string;
  email: string;
  avatar_url: string | null;
  group_count: number;
  groups: MentorStudentGroupSummary[];
  project_count: number;
  at_risk_project_count: number;
  created_at: string;
}

export interface MentorProjectInstanceSummary {
  id: string;
  name: string;
  student_id: string;
  student_name: string;
  student_email: string;
  group_id: string | null;
  group_name: string | null;
  current_phase: ProjectPhase;
  health: ProjectHealth;
  progress_percentage: number;
  status: ProjectStatus;
  deadline: string | null;
  source_definition_id: string | null;
  source_definition_name: string | null;
  source_definition_version_number: number | null;
  created_at: string;
  updated_at: string;
}

export interface MentorStudentDetail {
  id: string;
  student_id?: string;
  full_name: string;
  email: string;
  avatar_url: string | null;
  bio: string | null;
  skills: string[];
  group_count: number;
  groups: MentorStudentGroupSummary[];
  project_count: number;
  at_risk_project_count: number;
  created_at: string;
  projects: MentorProjectInstanceSummary[];
}

export interface MentorProjectInstanceDetail extends MentorProjectInstanceSummary {
  problem: string;
  proposed_solution: string;
  complexity: ProjectComplexity;
  source_definition_version_id: string | null;
  source_definition_version_summary: string | null;
  student_bio: string | null;
  student_skills: string[];
}

export interface MentorBlueprintInspectionResponse {
  project: MentorProjectInstanceDetail;
  blueprint: {
    id: string;
    project_instance_id: string;
    student_id: string;
    status: string;
    current_step?: string | null;
    progress_percent: number;
    error_message?: string | null;
    failed_output_key?: string | null;
    qa_status: string;
    qa_score?: number | null;
    qa_feedback?: {
      status: string;
      score: number;
      summary: string;
      evaluated_criteria?: Record<string, number>;
      issues?: Array<{
        section: string;
        severity: string;
        description: string;
        recommendation: string;
      }>;
      recommendations?: string[];
    } | null;
    approved_at?: string | null;
    created_at?: string | null;
    updated_at?: string | null;
  };
  content: Record<string, any>;
}
