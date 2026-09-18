/**
 * GrowFlow Admin Governance Frontend Types
 *
 * Types representing response structures for AD01–AD05:
 * - AdminOverviewResponse (AD01)
 * - AdminMentorSummary (AD02)
 * - AdminMentorDetail (AD03)
 * - AdminStudentSummary (AD04)
 * - AdminStudentDetail (AD05)
 */

export interface AdminOverviewResponse {
  total_mentors: number;
  active_mentors: number;
  total_students: number;
  active_students: number;
  total_groups: number;
  active_groups: number;
  total_projects: number;
  active_projects: number;
  completed_projects: number;
  at_risk_projects: number;
}

export interface AdminMentorSummary {
  id: string;
  email: string;
  full_name: string;
  role: string;
  status: string;
  avatar_url?: string | null;
  mentor_id?: string | null;
  designation?: string | null;
  organization?: string | null;
  specialization?: string | null;
  group_count: number;
  student_count: number;
  project_count: number;
  last_login_at?: string | null;
  created_at: string;
}

export interface AdminCohortSummary {
  id: string;
  name: string;
  join_code: string;
  status: string;
  student_count: number;
  project_count: number;
  created_at: string;
}

export interface AdminSupervisedStudent {
  id: string;
  full_name: string;
  email: string;
  group_name: string;
  active_projects_count: number;
}

export interface AdminMentorDetail {
  id: string;
  email: string;
  full_name: string;
  role: string;
  status: string;
  avatar_url?: string | null;
  mentor_id?: string | null;
  designation?: string | null;
  organization?: string | null;
  bio?: string | null;
  specialization?: string | null;
  skills: string[];
  max_students?: number | null;
  is_accepting_students: boolean;
  last_login_at?: string | null;
  created_at: string;
  groups: AdminCohortSummary[];
  supervised_students: AdminSupervisedStudent[];
}

export interface AdminStudentSummary {
  id: string;
  email: string;
  full_name: string;
  role: string;
  status: string;
  avatar_url?: string | null;
  student_id?: string | null;
  college?: string | null;
  branch?: string | null;
  year_of_study?: number | null;
  primary_track?: string | null;
  group_count: number;
  project_count: number;
  active_project_count: number;
  at_risk_project_count: number;
  last_login_at?: string | null;
  created_at: string;
}

export interface AdminStudentProject {
  id: string;
  name: string;
  track: string;
  current_phase: string;
  health: string;
  progress_percentage: number;
  status: string;
  group_name?: string | null;
  created_at: string;
}

export interface AdminStudentTechnology {
  technology_id: string;
  technology_name: string;
  proficiency_level: string;
}

export interface AdminStudentMembership {
  group_id: string;
  group_name: string;
  mentor_name: string;
  status: string;
  joined_at: string;
}

export interface AdminStudentDetail {
  id: string;
  email: string;
  full_name: string;
  role: string;
  status: string;
  avatar_url?: string | null;
  student_id?: string | null;
  enrollment_number?: string | null;
  college?: string | null;
  branch?: string | null;
  year_of_study?: number | null;
  cgpa?: number | null;
  primary_track?: string | null;
  headline?: string | null;
  bio?: string | null;
  target_role?: string | null;
  last_login_at?: string | null;
  created_at: string;
  technologies: AdminStudentTechnology[];
  groups: AdminStudentMembership[];
  projects: AdminStudentProject[];
}

// ============================================================
// AD06 — Groups Directory Types
// ============================================================

export interface AdminGroupSummary {
  id: string;
  name: string;
  join_code: string;
  status: string;
  mentor_id: string;
  mentor_name: string;
  mentor_email: string;
  student_count: number;
  project_count: number;
  created_at: string;
  updated_at: string;
}

// ============================================================
// AD07 — Group Detail Types
// ============================================================

export interface AdminGroupMember {
  id: string;
  student_id: string;
  full_name: string;
  email: string;
  avatar_url?: string | null;
  status: string;
  joined_at: string;
}

export interface AdminGroupProject {
  id: string;
  name: string;
  student_id: string;
  student_name: string;
  current_phase: string;
  health: string;
  progress_percentage: number;
  status: string;
  created_at: string;
}

export interface AdminGroupDetail {
  id: string;
  name: string;
  join_code: string;
  status: string;
  created_at: string;
  updated_at: string;
  mentor_id: string;
  mentor_name: string;
  mentor_email: string;
  mentor_avatar_url?: string | null;
  mentor_specialization?: string | null;
  student_count: number;
  project_count: number;
  active_project_count: number;
  members: AdminGroupMember[];
  projects: AdminGroupProject[];
}

// ============================================================
// AD08 & AD10 — Project Summary & Monitoring Types
// ============================================================

export interface AdminProjectSummary {
  id: string;
  name: string;
  student_id: string;
  student_name: string;
  student_email: string;
  mentor_id?: string | null;
  mentor_name?: string | null;
  group_id?: string | null;
  group_name?: string | null;
  current_phase: string;
  health: string;
  progress_percentage: number;
  status: string;
  complexity: string;
  source_definition_name?: string | null;
  created_at: string;
  updated_at: string;
}

// ============================================================
// AD09 — Project Definition Monitoring Types
// ============================================================

export interface AdminProjectDefinitionSummary {
  id: string;
  name: string;
  owner_mentor_id: string;
  owner_mentor_name: string;
  owner_mentor_email: string;
  status: string;
  current_version_id?: string | null;
  current_version_number?: number | null;
  complexity?: string | null;
  instance_count: number;
  version_count: number;
  created_at: string;
  updated_at: string;
}

export interface AdminProjectDefinitionVersion {
  id: string;
  version_number: number;
  name: string;
  problem: string;
  proposed_solution: string;
  complexity: string;
  description: string;
  duration: string;
  constraints: string;
  assumptions: string;
  technology_snapshot: any[];
  created_by: string;
  created_at: string;
}

export interface AdminProjectInstanceRef {
  id: string;
  name: string;
  student_name: string;
  current_phase: string;
  health: string;
  status: string;
}

export interface AdminProjectDefinitionDetail {
  id: string;
  name: string;
  owner_mentor_id: string;
  owner_mentor_name: string;
  owner_mentor_email: string;
  status: string;
  current_version_id?: string | null;
  current_version_number?: number | null;
  complexity?: string | null;
  instance_count: number;
  version_count: number;
  created_at: string;
  updated_at: string;
  versions: AdminProjectDefinitionVersion[];
  assigned_instances: AdminProjectInstanceRef[];
}

// ============================================================
// AD10 — Project Instance Monitoring & Canonical Detail Types
// ============================================================

export interface AdminInstanceSummary {
  total_instances: number;
  healthy_count: number;
  warning_count: number;
  critical_count: number;
  completed_count: number;
}

export interface AdminInstanceMonitoringResponse {
  summary: AdminInstanceSummary;
  instances: AdminProjectSummary[];
}

export interface AdminPhaseTransition {
  id: string;
  previous_phase: string;
  new_phase: string;
  reason: string;
  changed_at: string;
}

export interface AdminHealthTransition {
  id: string;
  previous_health: string;
  new_health: string;
  reason: string;
  changed_at: string;
}

export interface AdminProjectInstanceDetail {
  id: string;
  name: string;
  problem: string;
  proposed_solution: string;
  complexity: string;
  current_phase: string;
  health: string;
  progress_percentage: number;
  status: string;
  deadline?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
  student_id: string;
  student_name: string;
  student_email: string;
  student_avatar_url?: string | null;
  mentor_id?: string | null;
  mentor_name?: string | null;
  mentor_email?: string | null;
  group_id?: string | null;
  group_name?: string | null;
  definition_id?: string | null;
  definition_name?: string | null;
  version_number?: number | null;
  profile_objective?: string | null;
  profile_target_users?: string | null;
  profile_project_type?: string | null;
  profile_student_skill_context?: string | null;
  profile_goals?: string | null;
  profile_scope?: string | null;
  profile_expected_outcome?: string | null;
  profile_constraints?: string | null;
  profile_assumptions?: string | null;
  phase_history: AdminPhaseTransition[];
  health_history: AdminHealthTransition[];
}

// ============================================================
// AD19 & AD20 — System Health & Component Detail Types
// ============================================================

export interface AdminSubsystemSummary {
  id: string;
  name: string;
  status: 'OPERATIONAL' | 'CONFIGURED' | 'DEGRADED' | 'CRITICAL' | 'UNAVAILABLE' | string;
  type: string;
  details: string;
}

export interface AdminSystemHealthMetrics {
  outbox_pending: number;
  outbox_failed: number;
  outbox_published: number;
  active_ai_keys: number;
  db_pool_size: number;
  db_connected: boolean;
}

export interface AdminSystemHealthResponse {
  overall_status: 'OPERATIONAL' | 'DEGRADED' | 'CRITICAL' | string;
  environment: string;
  version: string;
  timestamp: string;
  subsystems: AdminSubsystemSummary[];
  metrics: AdminSystemHealthMetrics;
}

export interface AdminSubsystemDetail {
  id: string;
  name: string;
  status: string;
  type: string;
  environment: string;
  checked_at: string;
  configuration: Record<string, any>;
  diagnostics: Record<string, any>;
  recent_failures: Array<{
    id: string;
    event_type: string;
    error: string;
    occurred_at?: string | null;
    attempt_count?: number;
  }>;
}

// ============================================================
// AD24 — Security & Audit Overview Types
// ============================================================

export interface AdminUserSecurityPosture {
  total_users: number;
  active_users: number;
  inactive_users: number;
  suspended_users: number;
  admin_count: number;
  mentor_count: number;
  student_count: number;
}

export interface AdminAuditSummaryMetrics {
  total_events: number;
  outbox_delivery_failures: number;
}

export interface AdminSecurityOverview {
  user_posture: AdminUserSecurityPosture;
  audit_summary: AdminAuditSummaryMetrics;
  recent_security_relevant_events: Array<{
    id: string;
    event_type: string;
    title: string;
    description: string;
    actor_id?: string | null;
    actor_role: string;
    resource_type: string;
    resource_id: string;
    occurred_at?: string | null;
    status: string;
  }>;
}

// ============================================================
// AD25 — Audit Log Types
// ============================================================

export interface AdminAuditEventItem {
  id: string;
  event_type: string;
  title: string;
  description: string;
  actor_id?: string | null;
  actor_role: string;
  resource_type: string;
  resource_id: string;
  project_instance_id?: string | null;
  group_id?: string | null;
  correlation_id: string;
  status: string;
  occurred_at: string;
  metadata: Record<string, any>;
}

export interface AdminAuditLogResponse {
  total: number;
  limit: number;
  offset: number;
  events: AdminAuditEventItem[];
}

// ============================================================
// AD26 & AD27 — Governed Investigation Types
// ============================================================

export interface AdminInspectableResource {
  resource_type: 'USER' | 'PROJECT' | 'OUTBOX_FAILURE' | string;
  resource_id: string;
  label: string;
  detail: string;
  flag_reason: string;
  flagged_at?: string | null;
  canonical_inspection_url: string;
}

export interface AdminInvestigationOverviewResponse {
  framework_status: string;
  disclaimer: string;
  total_flagged: number;
  flagged_resources: AdminInspectableResource[];
}

// ============================================================
// BATCH 9 — AD21: Platform Documents & Knowledge Types
// ============================================================

export interface AdminDocumentItem {
  id: string;
  project_instance_id: string;
  project_name: string;
  document_key: string;
  title: string;
  doc_type: string;
  format: string;
  version: string;
  status: string;
  source: string;
  size_bytes: number;
  created_at: string;
  updated_at: string;
}

export interface AdminDocumentsResponse {
  total: number;
  limit: number;
  offset: number;
  documents: AdminDocumentItem[];
  doc_type_counts: Record<string, number>;
}

// ============================================================
// BATCH 9 — AD22: RAG Subsystem Monitoring Types
// ============================================================

export interface AdminRAGDiagnostics {
  status: 'DEFERRED_INTEGRATION' | 'ACTIVE' | 'STANDBY' | 'ERROR' | string;
  posture_description: string;
  vector_store_type: string;
  embedding_model: string;
  target_chunk_size: number;
  target_chunk_overlap: number;
  target_top_k: number;
  index_generated_documents: boolean;
  eligible_documents_count: number;
  recent_events: Array<{
    id: string;
    event_type: string;
    title: string;
    description: string;
    occurred_at: string;
    status: string;
  }>;
}

// ============================================================
// BATCH 9 — AD23: Document Generation Jobs Types
// ============================================================

export interface AdminGenerationJobItem {
  id: string;
  blueprint_id: string;
  project_instance_id: string;
  project_name: string;
  job_type: string;
  target_output: string;
  status: string;
  current_step?: string | null;
  progress_percent: number;
  error?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
  duration_seconds?: number | null;
}

export interface AdminGenerationJobsSummary {
  total_jobs: number;
  completed_jobs: number;
  running_jobs: number;
  failed_jobs: number;
  pending_jobs: number;
  average_duration_seconds?: number | null;
}

export interface AdminGenerationJobsResponse {
  total: number;
  limit: number;
  offset: number;
  summary: AdminGenerationJobsSummary;
  jobs: AdminGenerationJobItem[];
}

// ============================================================
// BATCH 9 — AD28: Platform Analytics Types
// ============================================================

export interface AdminAnalyticsOverviewMetrics {
  total_users: number;
  total_students: number;
  total_mentors: number;
  total_groups: number;
  total_projects: number;
  active_projects: number;
  completed_projects: number;
  at_risk_projects: number;
  total_documents: number;
  total_generation_jobs: number;
  total_domain_events: number;
}

export interface AdminPlatformAnalyticsResponse {
  overview: AdminAnalyticsOverviewMetrics;
  project_phase_distribution: Record<string, number>;
  project_health_distribution: Record<string, number>;
  task_status_distribution: Record<string, number>;
  user_status_distribution: Record<string, number>;
  generation_job_distribution: Record<string, number>;
  document_type_distribution: Record<string, number>;
  event_type_distribution: Record<string, number>;
  help_request_distribution: Record<string, number>;
}

// ============================================================
// BATCH 9 — AD29: Analytics Dimension Detail Types
// ============================================================

export type AdminAnalyticsDimension = 'projects' | 'users' | 'documents' | 'activity';

export interface AdminAnalyticsDimensionDetail {
  dimension: AdminAnalyticsDimension | string;
  title: string;
  description: string;
  total_records: number;
  data: Record<string, any>;
  generated_at: string;
}

// ============================================================
// BATCH 10 — AD11: AI Observatory Types
// ============================================================

export interface AdminAIGatewayPosture {
  provider: string;
  configured_active_keys: number;
  total_key_slots: number;
  default_model: string;
  configured_models: string[];
  gateway_base_url: string;
  rotation_strategy: string;
  reachability_state: string;
  credential_note: string;
}

export interface AdminAIObservatoryKPI {
  total_ai_transactions: number;
  blueprint_jobs_total: number;
  blueprint_jobs_completed: number;
  blueprint_jobs_failed: number;
  success_rate_percent?: number | null;
  currently_running_jobs: number;
  average_duration_seconds?: number | null;
  mentor_messages_total: number;
  change_requests_total: number;
}

export interface AdminAIActiveJob {
  id: string;
  blueprint_id: string;
  project_instance_id: string;
  project_name: string;
  job_type: string;
  status: string;
  current_step?: string | null;
  progress_percent: number;
  started_at?: string | null;
  created_at: string;
}

export interface AdminAIRecentActivity {
  id: string;
  activity_type: string;
  title: string;
  detail: string;
  status: string;
  project_name?: string | null;
  correlation_id?: string | null;
  timestamp: string;
}

export interface AdminAIObservatoryResponse {
  gateway: AdminAIGatewayPosture;
  kpis: AdminAIObservatoryKPI;
  active_jobs: AdminAIActiveJob[];
  recent_activity: AdminAIRecentActivity[];
  notices: {
    token_metering: string;
    dollar_cost: string;
    wire_telemetry: string;
    key_rotation: string;
    [key: string]: string;
  };
}

// ============================================================
// BATCH 10 — AD12: AI Usage Types
// ============================================================

export interface AdminAIUsageOverallVolume {
  blueprint_synthesis_jobs: number;
  ai_mentor_messages: number;
  project_change_analyses: number;
  total_recorded_transactions: number;
}

export interface AdminAITimeBucket {
  date: string;
  blueprint_jobs_count: number;
  mentor_messages_count: number;
  total_count: number;
}

export interface AdminAICapabilityUsage {
  capability_key: string;
  label: string;
  count: number;
  percentage: number;
}

export interface AdminAIProjectUsage {
  project_id: string;
  project_name: string;
  synthesis_jobs_count: number;
  mentor_messages_count: number;
  total_transactions: number;
}

export interface AdminAIUsageResponse {
  overall_volume: AdminAIUsageOverallVolume;
  time_trend: AdminAITimeBucket[];
  capability_breakdown: AdminAICapabilityUsage[];
  project_distribution: AdminAIProjectUsage[];
  outcome_distribution: Record<string, number>;
  token_metering: string;
  rate_limit_telemetry: string;
}

// ============================================================
// BATCH 10 — AD13: Agent Executions Types
// ============================================================

export interface AdminAIExecutionItem {
  id: string;
  source: string;
  project_instance_id: string;
  project_name: string;
  capability: string;
  job_type: string;
  target_output?: string | null;
  status: string;
  current_step?: string | null;
  progress_percent: number;
  duration_seconds?: number | null;
  error?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
}

export interface AdminAIExecutionsSummary {
  total: number;
  completed: number;
  failed: number;
  running: number;
  pending: number;
}

export interface AdminAIExecutionsResponse {
  total: number;
  limit: number;
  offset: number;
  summary: AdminAIExecutionsSummary;
  executions: AdminAIExecutionItem[];
}

// ============================================================
// BATCH 10 — AD14: AI Trace Detail Types
// ============================================================

export interface AdminAITracePipelineStage {
  stage_order: number;
  section_key: string;
  title: string;
  status: string;
  progress_milestone: number;
}

export interface AdminAITraceQAFeedback {
  qa_status: string;
  qa_score?: number | null;
  summary: string;
  evaluated_criteria: Record<string, any>;
  issues: Array<Record<string, any>>;
  recommendations: string[];
}

export interface AdminAITraceDomainEvent {
  id: string;
  event_type: string;
  status: string;
  correlation_id: string;
  occurred_at: string;
}

export interface AdminAITraceDetailResponse {
  id: string;
  blueprint_id: string;
  project_instance_id: string;
  project_name: string;
  student_id?: string | null;
  job_type: string;
  target_output?: string | null;
  status: string;
  current_step?: string | null;
  progress_percent: number;
  duration_seconds?: number | null;
  sanitized_error?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
  pipeline_stages: AdminAITracePipelineStage[];
  qa_result?: AdminAITraceQAFeedback | null;
  domain_events: AdminAITraceDomainEvent[];
  telemetry_notices: {
    http_wire_packets: string;
    dns_tls_timing: string;
    ttft: string;
    provider_wire_latency: string;
    langgraph_checkpoints: string;
    [key: string]: string;
  };
}

// ============================================================
// BATCH 10 — AD15: AI Quality Types
// ============================================================

export interface AdminAIQualityScoreDistribution {
  range_0_49: number;
  range_50_69: number;
  range_70_84: number;
  range_85_100: number;
}

export interface AdminAIQualityTopIssue {
  section: string;
  severity: string;
  count: number;
  sample_description: string;
  recommendation: string;
}

export interface AdminAIQualityResponse {
  total_evaluated: number;
  passed_count: number;
  failed_count: number;
  pending_count: number;
  pass_rate_percent?: number | null;
  average_qa_score?: number | null;
  min_qa_score?: number | null;
  max_qa_score?: number | null;
  score_distribution: AdminAIQualityScoreDistribution;
  criteria_averages: Record<string, number>;
  top_issues: AdminAIQualityTopIssue[];
  approval_conversion_rate?: number | null;
  deferred_capabilities: {
    rag_faithfulness_evaluation: string;
    automated_hallucination_benchmarking: string;
    student_csat_ratings: string;
    [key: string]: string;
  };
}

// ============================================================
// BATCH 10 — AD16: Cost & Usage Types
// ============================================================

export interface AdminAICostResponse {
  execution_volume_total: number;
  blueprint_jobs_count: number;
  ai_mentor_messages_count: number;
  change_analyses_count: number;
  active_models: string[];
  provider: string;
  billing_model: string;
  cost_telemetry_state: string;
  token_metering_state: string;
  disclaimer: string;
}

// ============================================================
// BATCH 10 — AD17: Cost Breakdown Types
// ============================================================

export interface AdminAICostDimensionItem {
  key: string;
  label: string;
  execution_count: number;
  percentage: number;
  detail?: string | null;
}

export interface AdminAICostDimensionResponse {
  dimension: string;
  title: string;
  metric_type: string;
  total_volume: number;
  items: AdminAICostDimensionItem[];
  cost_notice: string;
}

// ============================================================
// BATCH 10 — AD18: API Key Pool Monitoring Types
// ============================================================

export interface AdminAIKeySlot {
  slot_index: number;
  slot_label: string;
  env_var_name: string;
  status: string;
  provider: string;
  masked_identifier?: string | null;
  rotation_posture: string;
}

export interface AdminAIKeysResponse {
  provider: string;
  gateway_base_url: string;
  total_slots: number;
  configured_key_count: number;
  rotation_mechanism: string;
  rotation_runtime_state: string;
  slots: AdminAIKeySlot[];
  security_notice: string;
}



