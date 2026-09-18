/**
 * GrowFlow Mentor Project Definition Types
 *
 * Reflects backend schemas:
 * backend/app/api/schemas/project_definition.py
 * backend/app/domain/project/models.py
 */

export interface ProjectDefinitionVersion {
  id: string;
  project_definition_id: string;
  version_number: number;
  name: string;
  problem: string;
  proposed_solution: string;
  complexity: string;
  description?: string | null;
  duration?: string | null;
  constraints?: string | null;
  assumptions?: string | null;
  technology_snapshot: Array<Record<string, unknown>>;
  created_by: string;
  created_at?: string | null;
}

export interface ProjectDefinition {
  id: string;
  owner_mentor_id: string;
  name: string;
  status: string;
  current_version_id?: string | null;
  current_version?: ProjectDefinitionVersion | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface ProjectDefinitionCreatePayload {
  name: string;
  problem: string;
  proposed_solution: string;
  complexity?: string;
  description?: string;
  duration?: string;
  constraints?: string;
  assumptions?: string;
  technology_snapshot?: Array<Record<string, unknown>>;
}

export interface ProjectDefinitionUpdatePayload {
  name?: string;
  problem?: string;
  proposed_solution?: string;
  complexity?: string;
  description?: string;
  duration?: string;
  constraints?: string;
  assumptions?: string;
  technology_snapshot?: Array<Record<string, unknown>>;
}

export interface ProjectDefinitionAssignPayload {
  student_id: string;
  group_id?: string | null;
  deadline?: string | null;
}
