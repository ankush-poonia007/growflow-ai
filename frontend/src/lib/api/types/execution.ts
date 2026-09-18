/**
 * GrowFlow Execution Management API Types (Batch 5: S18–S26).
 */

export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'BLOCKED' | 'COMPLETED';
export type TaskPhase = 'PLANNING' | 'IMPLEMENTATION' | 'TESTING' | 'DEPLOYMENT';

export interface TaskResponse {
  id: string;
  project_instance_id: string;
  milestone_id: string | null;
  task_code: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  category: string;
  phase: TaskPhase;
  due_date: string | null;
  dependencies: string[];
  acceptance_criteria: string[];
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreatePayload {
  title: string;
  description?: string;
  priority?: TaskPriority;
  category?: string;
  phase?: TaskPhase;
  milestone_id?: string | null;
  due_date?: string | null;
  dependencies?: string[];
  acceptance_criteria?: string[];
}

export interface TaskUpdatePayload {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  category?: string;
  phase?: TaskPhase;
  milestone_id?: string | null;
  due_date?: string | null;
  dependencies?: string[];
  acceptance_criteria?: string[];
}

export type MilestoneStatus = 'UPCOMING' | 'IN_PROGRESS' | 'COMPLETED' | 'AT_RISK';

export interface MilestoneResponse {
  id: string;
  project_instance_id: string;
  title: string;
  description: string;
  gate_code: string;
  target_date: string | null;
  status: MilestoneStatus;
  progress_percent: number;
  deliverables: string[];
  section_order: number;
  task_count: number;
  completed_task_count: number;
  tasks: TaskResponse[];
  created_at: string;
  updated_at: string;
}

export interface MilestoneCreatePayload {
  title: string;
  description?: string;
  gate_code?: string;
  target_date?: string | null;
  deliverables?: string[];
}

export interface MilestoneUpdatePayload {
  title?: string;
  description?: string;
  gate_code?: string;
  target_date?: string | null;
  status?: MilestoneStatus;
  deliverables?: string[];
}

export type RiskSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type RiskProbability = 'LOW' | 'MEDIUM' | 'HIGH';
export type RiskImpact = 'LOW' | 'MEDIUM' | 'HIGH';
export type RiskStatus = 'OPEN' | 'MITIGATING' | 'RESOLVED' | 'ACCEPTED';

export interface RiskResponse {
  id: string;
  project_instance_id: string;
  risk_code: string;
  title: string;
  description: string;
  severity: RiskSeverity;
  probability: RiskProbability;
  impact: RiskImpact;
  status: RiskStatus;
  mitigation: string;
  owner: string;
  review_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface RiskCreatePayload {
  title: string;
  description?: string;
  severity?: RiskSeverity;
  probability?: RiskProbability;
  impact?: RiskImpact;
  mitigation?: string;
  owner?: string;
  review_date?: string | null;
}

export interface RiskUpdatePayload {
  title?: string;
  description?: string;
  severity?: RiskSeverity;
  probability?: RiskProbability;
  impact?: RiskImpact;
  status?: RiskStatus;
  mitigation?: string;
  owner?: string;
  review_date?: string | null;
}

export interface RoadmapSummary {
  total_milestones: number;
  completed_milestones: number;
  total_tasks: number;
  completed_tasks: number;
  overdue_tasks_count: number;
  blocked_tasks_count: number;
  current_phase: string;
  overall_progress: number;
}

export interface RoadmapMilestoneItem {
  id: string;
  gate_code: string;
  title: string;
  description: string;
  status: MilestoneStatus;
  progress_percent: number;
  target_date: string | null;
  deliverables: string[];
  tasks: TaskResponse[];
}

export interface RoadmapGroupedTasks {
  overdue: TaskResponse[];
  blocked: TaskResponse[];
  in_progress: TaskResponse[];
  upcoming: TaskResponse[];
  completed: TaskResponse[];
}

export interface RoadmapResponse {
  project_id: string;
  project_name: string;
  current_phase: string;
  summary: RoadmapSummary;
  milestones: RoadmapMilestoneItem[];
  grouped_tasks: RoadmapGroupedTasks;
}

export type DocumentType = 'BLUEPRINT' | 'ARCHITECTURE' | 'SPECIFICATION' | 'README' | 'REPORT' | 'GENERAL';
export type DocumentStatus = 'ACTIVE' | 'ARCHIVED' | 'DRAFT';

export interface DocumentResponse {
  id: string;
  project_instance_id: string;
  document_key: string;
  title: string;
  doc_type: DocumentType;
  format: string;
  content: string;
  version: string;
  status: DocumentStatus;
  source: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentCreatePayload {
  title: string;
  doc_type?: DocumentType;
  format?: string;
  content?: string;
}

export interface DocumentUpdatePayload {
  title?: string;
  content?: string;
  status?: DocumentStatus;
}
