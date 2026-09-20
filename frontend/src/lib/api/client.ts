/**
 * GrowFlow Centralized Frontend API Client
 *
 * Requirements:
 * - Automatic injection of Supabase Bearer JWT
 * - Canonical response envelope unwrapping ({ success: true, data: T })
 * - Normalized ApiClientError handling (401, 403, 404, 422, 5xx, network)
 * - Pure typed functions for Student workspace APIs
 * - Safe for testing and browser environments
 */

import { supabase } from '@/lib/supabase';
import { ApiClientError } from './errors';
import type {
  ApiResponse,
  CurrentUserIdentity,
  StudentProfile,
  StudentProfileUpdatePayload,
  ProjectResponse,
  ProjectOverviewResponse,
  ProjectCreatePayload,
  ProjectUpdatePayload,
  ProjectPhaseTransitionPayload,
  ProjectHealthUpdatePayload,
  ProjectDefinitionCatalogItem,
  AssessmentSessionStatus,
  AssessmentStartResponse,
  AssessmentQuestionResponse,
  AssessmentAnswerSubmitPayload,
  AssessmentAnswerSubmitResponse,
  AssessmentResultResponse,
  BlueprintStatusResponse,
  BlueprintContentResponse,
  BlueprintApprovalResponse,
  BlueprintRetryRequest,
  BlueprintSectionDetail,
  BlueprintDocumentDetail,
  TaskResponse,
  TaskCreatePayload,
  TaskUpdatePayload,
  MilestoneResponse,
  MilestoneCreatePayload,
  MilestoneUpdatePayload,
  RiskResponse,
  RiskCreatePayload,
  RiskUpdatePayload,
  RoadmapResponse,
  DocumentResponse,
  DocumentCreatePayload,
  DocumentUpdatePayload,
  MentorOverviewResponse,
  GroupResponse,
  GroupCreatePayload,
  GroupStudentResponse,
  GroupMembershipResponse,
  MentorHelpRequestSummary,
  HelpRequestRespondPayload,
  MentorNoteCreatePayload,
  MentorNoteItem,
  ProjectDefinition,
  ProjectDefinitionVersion,
  ProjectDefinitionCreatePayload,
  ProjectDefinitionUpdatePayload,
  ProjectDefinitionAssignPayload,
  MentorStudentSummary,
  MentorStudentDetail,
  MentorProjectInstanceSummary,
  MentorProjectInstanceDetail,
  MentorBlueprintInspectionResponse,
  MentorProfileResponse,
  MentorProfileUpdatePayload,
  UserPreferencesResponse,
  UserPreferencesUpdatePayload,
  AdminOverviewResponse,
  AdminMentorSummary,
  AdminMentorDetail,
  AdminStudentSummary,
  AdminStudentDetail,
  AdminGroupSummary,
  AdminGroupDetail,
  AdminProjectSummary,
  AdminProjectDefinitionSummary,
  AdminProjectDefinitionDetail,
  AdminInstanceMonitoringResponse,
  AdminProjectInstanceDetail,
  AdminSystemHealthResponse,
  AdminSubsystemDetail,
  AdminSecurityOverview,
  AdminAuditLogResponse,
  AdminInvestigationOverviewResponse,
  AdminDocumentsResponse,
  AdminRAGDiagnostics,
  AdminGenerationJobsResponse,
  AdminPlatformAnalyticsResponse,
  AdminAnalyticsDimensionDetail,
  AdminAIObservatoryResponse,
  AdminAIUsageResponse,
  AdminAIExecutionsResponse,
  AdminAITraceDetailResponse,
  AdminAIQualityResponse,
  AdminAICostResponse,
  AdminAICostDimensionResponse,
  AdminAIKeysResponse,
  SearchResponseData,
  NotificationItem,
  UnreadCountResponse,
  MarkAllReadResponse,
} from './types';

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '');

/**
 * Retrieve the current active Supabase session access token safely.
 */
async function getAuthToken(): Promise<string | null> {
  try {
    const { data, error } = await supabase.auth.getSession();
    if (error || !data?.session) {
      return null;
    }
    return data.session.access_token;
  } catch {
    return null;
  }
}

/**
 * Core authenticated HTTP request function.
 */
export async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = new Headers(options.headers || {});

  if (!headers.has('Content-Type') && options.body && typeof options.body === 'string') {
    headers.set('Content-Type', 'application/json');
  }

  // Inject Bearer token if available and not explicitly provided
  if (!headers.has('Authorization')) {
    const token = await getAuthToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Network request failed';
    throw new ApiClientError(0, 'NETWORK_ERROR', `Unable to reach GrowFlow API: ${message}`);
  }

  // Parse JSON body if present
  let payload: ApiResponse<T> | null = null;
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }
  }

  if (!response.ok) {
    const code = payload?.error?.code || `HTTP_${response.status}`;
    const message =
      payload?.error?.message ||
      payload?.message ||
      getDefaultErrorMessage(response.status);
    const details = payload?.error?.details;

    throw new ApiClientError(response.status, code, message, details);
  }

  // Canonical envelope: return data directly if wrapped in success envelope
  if (payload && typeof payload === 'object' && 'data' in payload && payload.data !== undefined) {
    return payload.data as T;
  }

  return (payload as T) ?? (undefined as T);
}

function getDefaultErrorMessage(status: number): string {
  switch (status) {
    case 400:
      return 'The request contained invalid parameters.';
    case 401:
      return 'Your session has expired. Please sign in again.';
    case 403:
      return 'You do not have permission to access this resource.';
    case 404:
      return 'The requested resource could not be found.';
    case 422:
      return 'Validation error. Please verify your input.';
    case 429:
      return 'Too many requests. Please slow down and try again.';
    default:
      if (status >= 500) {
        return 'An internal service error occurred. Please try again shortly.';
      }
      return 'An unexpected error occurred.';
  }
}

/* =========================================================================
   Typed API Methods
   ========================================================================= */

/**
 * Get current authenticated user identity and application role.
 * GET /api/v1/auth/me
 */
export async function getCurrentUser(): Promise<CurrentUserIdentity> {
  return apiFetch<CurrentUserIdentity>('/api/v1/auth/me');
}

/**
 * Get student profile and skills.
 * GET /api/v1/students/me
 */
export async function getStudentProfile(): Promise<StudentProfile> {
  return apiFetch<StudentProfile>('/api/v1/students/me');
}

/**
 * Update student profile and skills.
 * PATCH /api/v1/students/me
 */
export async function updateStudentProfile(
  payload: StudentProfileUpdatePayload,
): Promise<StudentProfile> {
  return apiFetch<StudentProfile>('/api/v1/students/me', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

/**
 * List all project instances owned by or accessible to the current user.
 * GET /api/v1/projects
 */
export async function getProjects(): Promise<ProjectResponse[]> {
  return apiFetch<ProjectResponse[]>('/api/v1/projects');
}

/**
 * Get a specific project instance by ID.
 * GET /api/v1/projects/:projectId
 */
export async function getProject(projectId: string): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(`/api/v1/projects/${projectId}`);
}

/**
 * Get aggregated project workspace overview (phase history, health, profile, technologies).
 * GET /api/v1/projects/:projectId/overview
 */
export async function getProjectOverview(projectId: string): Promise<ProjectOverviewResponse> {
  return apiFetch<ProjectOverviewResponse>(`/api/v1/projects/${projectId}/overview`);
}

/**
 * Create a new independent student project instance.
 * POST /api/v1/projects
 */
export async function createProject(payload: ProjectCreatePayload): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>('/api/v1/projects', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Update mutable properties of a student project instance.
 * PATCH /api/v1/projects/:projectId
 */
export async function updateProject(
  projectId: string,
  payload: ProjectUpdatePayload,
): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(`/api/v1/projects/${projectId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

/**
 * Transition project lifecycle phase according to canonical state machine.
 * POST /api/v1/projects/:projectId/phase
 */
export async function transitionProjectPhase(
  projectId: string,
  payload: ProjectPhaseTransitionPayload,
): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(`/api/v1/projects/${projectId}/phase`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Record a health indicator update with reason.
 * POST /api/v1/projects/:projectId/health
 */
export async function updateProjectHealth(
  projectId: string,
  payload: ProjectHealthUpdatePayload,
): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(`/api/v1/projects/${projectId}/health`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Retrieve the active mentor project definition catalog available for student discovery.
 * GET /api/v1/project-definitions/catalog
 */
export async function getMentorProjectCatalog(): Promise<ProjectDefinitionCatalogItem[]> {
  return apiFetch<ProjectDefinitionCatalogItem[]>('/api/v1/project-definitions/catalog');
}

/**
 * Retrieve active mentor project definition detail available for student discovery.
 * GET /api/v1/project-definitions/catalog/:definitionId
 */
export async function getMentorProjectDefinition(
  definitionId: string,
): Promise<ProjectDefinitionCatalogItem> {
  return apiFetch<ProjectDefinitionCatalogItem>(
    `/api/v1/project-definitions/catalog/${definitionId}`,
  );
}

/**
 * Student selects an active mentor project definition to instantiate a linked student project.
 * POST /api/v1/project-definitions/catalog/:definitionId/select
 */
export async function selectMentorProject(
  definitionId: string,
): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(
    `/api/v1/project-definitions/catalog/${definitionId}/select`,
    {
      method: 'POST',
    },
  );
}

/**
 * Retrieve active assessment status and progression summary for a project.
 * GET /api/v1/projects/:projectId/assessment/status
 */
export async function getAssessmentStatus(
  projectId: string,
): Promise<AssessmentSessionStatus> {
  return apiFetch<AssessmentSessionStatus>(
    `/api/v1/projects/${projectId}/assessment/status`,
  );
}

/**
 * Start or resume an assessment session for a project.
 * POST /api/v1/projects/:projectId/assessment/start
 */
export async function startAssessment(
  projectId: string,
): Promise<AssessmentStartResponse> {
  return apiFetch<AssessmentStartResponse>(
    `/api/v1/projects/${projectId}/assessment/start`,
    {
      method: 'POST',
    },
  );
}

/**
 * Retrieve a specific question (1..15) and existing answer for a project assessment.
 * GET /api/v1/projects/:projectId/assessment/questions/:questionIndex
 */
export async function getAssessmentQuestion(
  projectId: string,
  questionIndex: number,
): Promise<AssessmentQuestionResponse> {
  return apiFetch<AssessmentQuestionResponse>(
    `/api/v1/projects/${projectId}/assessment/questions/${questionIndex}`,
  );
}

/**
 * Submit or update an answer for an assessment question.
 * POST /api/v1/projects/:projectId/assessment/answers
 */
export async function submitAssessmentAnswer(
  projectId: string,
  payload: AssessmentAnswerSubmitPayload,
): Promise<AssessmentAnswerSubmitResponse> {
  return apiFetch<AssessmentAnswerSubmitResponse>(
    `/api/v1/projects/${projectId}/assessment/answers`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
  );
}

/**
 * Finalize and complete an assessment workflow.
 * POST /api/v1/projects/:projectId/assessment/complete
 */
export async function completeAssessment(
  projectId: string,
): Promise<AssessmentResultResponse> {
  return apiFetch<AssessmentResultResponse>(
    `/api/v1/projects/${projectId}/assessment/complete`,
    {
      method: 'POST',
    },
  );
}

/**
 * Retrieve synthesized Enriched Project Understanding result for a completed assessment.
 * GET /api/v1/projects/:projectId/assessment/result
 */
export async function getAssessmentResult(
  projectId: string,
): Promise<AssessmentResultResponse> {
  return apiFetch<AssessmentResultResponse>(
    `/api/v1/projects/${projectId}/assessment/result`,
  );
}

/**
 * Retrieve current blueprint session state, progress, and QA scorecard.
 * GET /api/v1/projects/:projectId/blueprint/status
 */
export async function getBlueprintStatus(
  projectId: string,
): Promise<BlueprintStatusResponse> {
  return apiFetch<BlueprintStatusResponse>(
    `/api/v1/projects/${projectId}/blueprint/status`,
  );
}

/**
 * Trigger sequential synthesis across all 10 canonical blueprint sections.
 * POST /api/v1/projects/:projectId/blueprint/generate
 */
export async function startBlueprintGeneration(
  projectId: string,
): Promise<BlueprintStatusResponse> {
  return apiFetch<BlueprintStatusResponse>(
    `/api/v1/projects/${projectId}/blueprint/generate`,
    {
      method: 'POST',
    },
  );
}

/**
 * Retry generation for specifically failed or targeted blueprint sections.
 * POST /api/v1/projects/:projectId/blueprint/retry
 */
export async function retryBlueprintGeneration(
  projectId: string,
  payload?: BlueprintRetryRequest,
): Promise<BlueprintStatusResponse> {
  return apiFetch<BlueprintStatusResponse>(
    `/api/v1/projects/${projectId}/blueprint/retry`,
    {
      method: 'POST',
      body: payload ? JSON.stringify(payload) : undefined,
    },
  );
}

/**
 * Cooperatively request cancellation of active blueprint generation.
 * POST /api/v1/projects/:projectId/blueprint/cancel
 */
export async function cancelBlueprintGeneration(
  projectId: string,
): Promise<BlueprintStatusResponse> {
  return apiFetch<BlueprintStatusResponse>(
    `/api/v1/projects/${projectId}/blueprint/cancel`,
    {
      method: 'POST',
    },
  );
}

/**
 * Fetch full synthesized blueprint sections and QA feedback.
 * GET /api/v1/projects/:projectId/blueprint/content
 */
export async function getBlueprintContent(
  projectId: string,
): Promise<BlueprintContentResponse> {
  return apiFetch<BlueprintContentResponse>(
    `/api/v1/projects/${projectId}/blueprint/content`,
  );
}

/**
 * Authoritatively approve the generated blueprint and lock Stage 3.
 * POST /api/v1/projects/:projectId/blueprint/approve
 */
export async function approveBlueprint(
  projectId: string,
): Promise<BlueprintApprovalResponse> {
  return apiFetch<BlueprintApprovalResponse>(
    `/api/v1/projects/${projectId}/blueprint/approve`,
    {
      method: 'POST',
    },
  );
}

/**
 * Retrieve structured content and compiled Markdown for a specific canonical section.
 * GET /api/v1/projects/:projectId/blueprint/sections/:sectionKey
 */
export async function getBlueprintSection(
  projectId: string,
  sectionKey: string,
): Promise<BlueprintSectionDetail> {
  return apiFetch<BlueprintSectionDetail>(
    `/api/v1/projects/${projectId}/blueprint/sections/${sectionKey}`,
  );
}

/**
 * Retrieve document-oriented representation of a blueprint output.
 * GET /api/v1/projects/:projectId/blueprint/documents/:documentKey
 */
export async function getBlueprintDocument(
  projectId: string,
  documentKey: string,
): Promise<BlueprintDocumentDetail> {
  return apiFetch<BlueprintDocumentDetail>(
    `/api/v1/projects/${projectId}/blueprint/documents/${documentKey}`,
  );
}

/**
 * Subscribe to blueprint SSE generation events.
 * Returns an unsubscribe cleanup function.
 */
export async function subscribeBlueprintEvents(
  projectId: string,
  onUpdate: (data: BlueprintStatusResponse) => void,
  onError?: (err: any) => void,
): Promise<() => void> {
  const token = await getAuthToken();
  const url = `${API_BASE_URL}/api/v1/projects/${projectId}/blueprint/events${token ? `?token=${encodeURIComponent(token)}` : ''}`;
  const es = new EventSource(url);

  es.addEventListener('update', (event) => {
    try {
      const data = JSON.parse(event.data) as BlueprintStatusResponse;
      onUpdate(data);
    } catch (e) {
      console.error('Failed to parse blueprint event data', e);
    }
  });

  es.onerror = (err) => {
    if (onError) onError(err);
  };

  return () => {
    es.close();
  };
}

/**
 * Helper to download raw markdown for a blueprint document in the browser.
 */
export async function downloadBlueprintDocument(
  projectId: string,
  documentKey: string,
  customFilename?: string,
): Promise<void> {
  const token = await getAuthToken();
  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}/api/v1/projects/${projectId}/blueprint/documents/${documentKey}/raw`;
  const response = await fetch(url, { headers });
  if (!response.ok) {
    throw new ApiClientError(response.status, 'DOWNLOAD_FAILED', 'Failed to download blueprint document.');
  }

  const contentDisposition = response.headers.get('content-disposition');
  let filename = customFilename;
  if (!filename && contentDisposition) {
    const match = contentDisposition.match(/filename="?([^";]+)"?/i);
    if (match && match[1]) {
      filename = match[1];
    }
  }
  if (!filename) {
    filename = `blueprint-${documentKey}.md`;
  }

  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(downloadUrl);
}

// ============================================================================
// Execution Management Client Methods (Batch 5: S18–S26)
// ============================================================================

export async function getTasks(
  projectId: string,
  filters?: { status?: string; priority?: string; milestone_id?: string; phase?: string; search?: string }
): Promise<TaskResponse[]> {
  const query = new URLSearchParams();
  if (filters?.status) query.set('status', filters.status);
  if (filters?.priority) query.set('priority', filters.priority);
  if (filters?.milestone_id) query.set('milestone_id', filters.milestone_id);
  if (filters?.phase) query.set('phase', filters.phase);
  if (filters?.search) query.set('search', filters.search);
  const qs = query.toString();
  return apiFetch<TaskResponse[]>(`/api/v1/projects/${projectId}/tasks${qs ? `?${qs}` : ''}`);
}

export async function getTask(projectId: string, taskId: string): Promise<TaskResponse> {
  return apiFetch<TaskResponse>(`/api/v1/projects/${projectId}/tasks/${taskId}`);
}

export async function createTask(projectId: string, payload: TaskCreatePayload): Promise<TaskResponse> {
  return apiFetch<TaskResponse>(`/api/v1/projects/${projectId}/tasks`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateTask(
  projectId: string,
  taskId: string,
  payload: TaskUpdatePayload
): Promise<TaskResponse> {
  return apiFetch<TaskResponse>(`/api/v1/projects/${projectId}/tasks/${taskId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function deleteTask(projectId: string, taskId: string): Promise<void> {
  await apiFetch<null>(`/api/v1/projects/${projectId}/tasks/${taskId}`, {
    method: 'DELETE',
  });
}

export async function getMilestones(projectId: string): Promise<MilestoneResponse[]> {
  return apiFetch<MilestoneResponse[]>(`/api/v1/projects/${projectId}/milestones`);
}

export async function getMilestone(projectId: string, milestoneId: string): Promise<MilestoneResponse> {
  return apiFetch<MilestoneResponse>(`/api/v1/projects/${projectId}/milestones/${milestoneId}`);
}

export async function createMilestone(
  projectId: string,
  payload: MilestoneCreatePayload
): Promise<MilestoneResponse> {
  return apiFetch<MilestoneResponse>(`/api/v1/projects/${projectId}/milestones`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateMilestone(
  projectId: string,
  milestoneId: string,
  payload: MilestoneUpdatePayload
): Promise<MilestoneResponse> {
  return apiFetch<MilestoneResponse>(`/api/v1/projects/${projectId}/milestones/${milestoneId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function getRisks(
  projectId: string,
  filters?: { status?: string; severity?: string; search?: string }
): Promise<RiskResponse[]> {
  const query = new URLSearchParams();
  if (filters?.status) query.set('status', filters.status);
  if (filters?.severity) query.set('severity', filters.severity);
  if (filters?.search) query.set('search', filters.search);
  const qs = query.toString();
  return apiFetch<RiskResponse[]>(`/api/v1/projects/${projectId}/risks${qs ? `?${qs}` : ''}`);
}

export async function getRisk(projectId: string, riskId: string): Promise<RiskResponse> {
  return apiFetch<RiskResponse>(`/api/v1/projects/${projectId}/risks/${riskId}`);
}

export async function createRisk(projectId: string, payload: RiskCreatePayload): Promise<RiskResponse> {
  return apiFetch<RiskResponse>(`/api/v1/projects/${projectId}/risks`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateRisk(
  projectId: string,
  riskId: string,
  payload: RiskUpdatePayload
): Promise<RiskResponse> {
  return apiFetch<RiskResponse>(`/api/v1/projects/${projectId}/risks/${riskId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function deleteRisk(projectId: string, riskId: string): Promise<void> {
  await apiFetch<null>(`/api/v1/projects/${projectId}/risks/${riskId}`, {
    method: 'DELETE',
  });
}

export async function getRoadmap(projectId: string): Promise<RoadmapResponse> {
  return apiFetch<RoadmapResponse>(`/api/v1/projects/${projectId}/roadmap`);
}

export async function getDocuments(
  projectId: string,
  filters?: { doc_type?: string; status?: string; search?: string }
): Promise<DocumentResponse[]> {
  const query = new URLSearchParams();
  if (filters?.doc_type) query.set('doc_type', filters.doc_type);
  if (filters?.status) query.set('status', filters.status);
  if (filters?.search) query.set('search', filters.search);
  const qs = query.toString();
  return apiFetch<DocumentResponse[]>(`/api/v1/projects/${projectId}/documents${qs ? `?${qs}` : ''}`);
}

export async function getDocument(projectId: string, documentId: string): Promise<DocumentResponse> {
  return apiFetch<DocumentResponse>(`/api/v1/projects/${projectId}/documents/${documentId}`);
}

export async function createDocument(
  projectId: string,
  payload: DocumentCreatePayload
): Promise<DocumentResponse> {
  return apiFetch<DocumentResponse>(`/api/v1/projects/${projectId}/documents`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateDocument(
  projectId: string,
  documentId: string,
  payload: DocumentUpdatePayload
): Promise<DocumentResponse> {
  return apiFetch<DocumentResponse>(`/api/v1/projects/${projectId}/documents/${documentId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function downloadDocument(
  projectId: string,
  documentId: string,
  customFilename?: string
): Promise<void> {
  const token = await getAuthToken();
  const headers = new Headers();
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(
    `${API_BASE_URL}/api/v1/projects/${projectId}/documents/${documentId}/download`,
    { headers }
  );

  if (!response.ok) {
    throw new ApiClientError(
      response.status,
      'DOWNLOAD_FAILED',
      'Failed to download document markdown.'
    );
  }

  let filename = customFilename;
  const contentDisposition = response.headers.get('content-disposition');
  if (!filename && contentDisposition) {
    const match = contentDisposition.match(/filename="?([^";]+)"?/i);
    if (match && match[1]) {
      filename = match[1];
    }
  }
  if (!filename) {
    filename = `document-${documentId}.md`;
  }

  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(downloadUrl);
}

/**
 * Centralized API Client bundle.
 */
export const apiClient = {
  getCurrentUser,
  getStudentProfile,
  updateStudentProfile,
  getProjects,
  getProject,
  getProjectOverview,
  createProject,
  updateProject,
  transitionProjectPhase,
  updateProjectHealth,
  getMentorProjectCatalog,
  getMentorProjectDefinition,
  getAssessmentStatus,
  startAssessment,
  getAssessmentQuestion,
  submitAssessmentAnswer,
  completeAssessment,
  getAssessmentResult,
  getBlueprintStatus,
  subscribeBlueprintEvents,
  startBlueprintGeneration,
  cancelBlueprintGeneration,
  retryBlueprintGeneration,
  getBlueprintContent,
  approveBlueprint,
  getBlueprintSection,
  getBlueprintDocument,
  downloadBlueprintDocument,
  // S18–S26 Execution APIs
  getTasks,
  getTask,
  createTask,
  updateTask,
  deleteTask,
  getMilestones,
  getMilestone,
  createMilestone,
  updateMilestone,
  getRisks,
  getRisk,
  createRisk,
  updateRisk,
  deleteRisk,
  getRoadmap,
  getDocuments,
  getDocument,
  createDocument,
  updateDocument,
  downloadDocument,
};

// ============================================================================
// Batch 06 Workspace Extensions APIs (S27–S33)
// ============================================================================

import type {
  GitHubIntegrationResponse,
  GitHubConnectPayload,
  ActivityItemResponse,
  AIMentorConversationResponse,
  AIMentorSendResponse,
  HelpRequestResponse,
  HelpRequestCreatePayload,
  MentorNoteResponse,
  ProjectChangeResponse,
  ProjectChangeAnalyzePayload,
  ProjectChangeConfirmPayload,
  BlueprintVersionResponse,
  MentorAIChatPayload,
  MentorAIChatResponse,
  MentorAIStatusResponse,
} from './types';

export async function getGitHubIntegration(projectId: string): Promise<GitHubIntegrationResponse> {
  return apiFetch<GitHubIntegrationResponse>(`/api/v1/projects/${projectId}/github`);
}

export async function connectGitHub(
  projectId: string,
  payload: GitHubConnectPayload
): Promise<GitHubIntegrationResponse> {
  return apiFetch<GitHubIntegrationResponse>(`/api/v1/projects/${projectId}/github/connect`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function syncGitHub(projectId: string): Promise<GitHubIntegrationResponse> {
  return apiFetch<GitHubIntegrationResponse>(`/api/v1/projects/${projectId}/github/sync`, {
    method: 'POST',
  });
}

export async function disconnectGitHub(projectId: string): Promise<GitHubIntegrationResponse> {
  return apiFetch<GitHubIntegrationResponse>(`/api/v1/projects/${projectId}/github/disconnect`, {
    method: 'POST',
  });
}

export async function getProjectActivity(
  projectId: string,
  params?: { limit?: number; offset?: number }
): Promise<ActivityItemResponse[]> {
  const query = new URLSearchParams();
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.offset) query.set('offset', String(params.offset));
  const qs = query.toString();
  return apiFetch<ActivityItemResponse[]>(`/api/v1/projects/${projectId}/activity${qs ? `?${qs}` : ''}`);
}

export async function getAIMentorHistory(projectId: string): Promise<AIMentorConversationResponse> {
  return apiFetch<AIMentorConversationResponse>(`/api/v1/projects/${projectId}/ai-mentor`);
}

export async function sendAIMentorMessage(
  projectId: string,
  content: string
): Promise<AIMentorSendResponse> {
  return apiFetch<AIMentorSendResponse>(`/api/v1/projects/${projectId}/ai-mentor/chat`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
}

export async function executeAIOperation(
  projectId: string,
  actionType: string,
  payload: Record<string, any> = {}
): Promise<{ status: string; action_type: string; resource_id?: string }> {
  return apiFetch<{ status: string; action_type: string; resource_id?: string }>(
    `/api/v1/projects/${projectId}/ai-mentor/execute-action`,
    {
      method: 'POST',
      body: JSON.stringify({ action_type: actionType, payload }),
    }
  );
}

export async function getHelpRequests(projectId: string): Promise<HelpRequestResponse[]> {
  return apiFetch<HelpRequestResponse[]>(`/api/v1/projects/${projectId}/help-requests`);
}

export async function createHelpRequest(
  projectId: string,
  payload: HelpRequestCreatePayload
): Promise<HelpRequestResponse> {
  return apiFetch<HelpRequestResponse>(`/api/v1/projects/${projectId}/help-requests`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getHelpRequest(projectId: string, requestId: string): Promise<HelpRequestResponse> {
  return apiFetch<HelpRequestResponse>(`/api/v1/projects/${projectId}/help-requests/${requestId}`);
}

export async function getMentorNotes(projectId: string): Promise<MentorNoteResponse[]> {
  return apiFetch<MentorNoteResponse[]>(`/api/v1/projects/${projectId}/mentor-notes`);
}

export async function acknowledgeMentorNote(
  projectId: string,
  noteId: string
): Promise<MentorNoteResponse> {
  return apiFetch<MentorNoteResponse>(`/api/v1/projects/${projectId}/mentor-notes/${noteId}/acknowledge`, {
    method: 'POST',
  });
}

export async function getProjectChanges(projectId: string): Promise<ProjectChangeResponse[]> {
  return apiFetch<ProjectChangeResponse[]>(`/api/v1/projects/${projectId}/changes`);
}

export async function getProjectChange(projectId: string, changeId: string): Promise<ProjectChangeResponse> {
  return apiFetch<ProjectChangeResponse>(`/api/v1/projects/${projectId}/changes/${changeId}`);
}

export async function analyzeProjectChange(
  projectId: string,
  payload: ProjectChangeAnalyzePayload
): Promise<ProjectChangeResponse> {
  return apiFetch<ProjectChangeResponse>(`/api/v1/projects/${projectId}/changes/analyze`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function confirmProjectChange(
  projectId: string,
  changeId: string,
  payload?: ProjectChangeConfirmPayload
): Promise<ProjectChangeResponse> {
  return apiFetch<ProjectChangeResponse>(`/api/v1/projects/${projectId}/changes/${changeId}/confirm`, {
    method: 'POST',
    body: JSON.stringify(payload || {}),
  });
}

export async function getBlueprintVersions(projectId: string): Promise<BlueprintVersionResponse[]> {
  return apiFetch<BlueprintVersionResponse[]>(`/api/v1/projects/${projectId}/blueprint-versions`);
}

export async function getBlueprintVersion(
  projectId: string,
  versionNumber: number
): Promise<BlueprintVersionResponse> {
  return apiFetch<BlueprintVersionResponse>(`/api/v1/projects/${projectId}/blueprint-versions/${versionNumber}`);
}

// Phase 7 — Supervise Workplace API Client Methods
export async function getMentorOverview(): Promise<MentorOverviewResponse> {
  return apiFetch<MentorOverviewResponse>('/api/v1/mentors/overview');
}

export async function getMentorGroups(): Promise<GroupResponse[]> {
  return apiFetch<GroupResponse[]>('/api/v1/groups');
}

export async function createMentorGroup(payload: GroupCreatePayload): Promise<GroupResponse> {
  return apiFetch<GroupResponse>('/api/v1/groups', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getMentorGroup(groupId: string): Promise<GroupResponse> {
  return apiFetch<GroupResponse>(`/api/v1/groups/${groupId}`);
}

export async function getGroupStudents(groupId: string): Promise<GroupStudentResponse[]> {
  return apiFetch<GroupStudentResponse[]>(`/api/v1/groups/${groupId}/students`);
}

export async function getGroupProjects(groupId: string): Promise<ProjectResponse[]> {
  return apiFetch<ProjectResponse[]>(`/api/v1/groups/${groupId}/projects`);
}

export async function getStudentGroups(): Promise<GroupResponse[]> {
  return apiFetch<GroupResponse[]>('/api/v1/groups');
}

export async function joinGroup(joinCode: string): Promise<GroupMembershipResponse> {
  return apiFetch<GroupMembershipResponse>('/api/v1/groups/join', {
    method: 'POST',
    body: JSON.stringify({ join_code: joinCode }),
  });
}

/* =========================================================================
   Mentor Communication (M33 Help Requests & M34 Notes)
   ========================================================================= */

export async function getMentorHelpRequests(params?: {
  status?: string;
  group_id?: string;
}): Promise<MentorHelpRequestSummary[]> {
  const query = new URLSearchParams();
  if (params?.status && params.status !== 'ALL') query.set('status', params.status);
  if (params?.group_id) query.set('group_id', params.group_id);
  const qs = query.toString();
  return apiFetch<MentorHelpRequestSummary[]>(`/api/v1/mentors/help-requests${qs ? `?${qs}` : ''}`);
}

export async function getMentorHelpRequest(requestId: string): Promise<MentorHelpRequestSummary> {
  return apiFetch<MentorHelpRequestSummary>(`/api/v1/mentors/help-requests/${requestId}`);
}

export async function respondMentorHelpRequest(
  requestId: string,
  payload: HelpRequestRespondPayload
): Promise<MentorHelpRequestSummary> {
  return apiFetch<MentorHelpRequestSummary>(`/api/v1/mentors/help-requests/${requestId}/respond`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function createMentorNote(payload: MentorNoteCreatePayload): Promise<MentorNoteItem> {
  return apiFetch<MentorNoteItem>('/api/v1/mentors/notes', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getMentorProjectNotes(projectId: string): Promise<MentorNoteItem[]> {
  return apiFetch<MentorNoteItem[]>(`/api/v1/mentors/project-instances/${projectId}/notes`);
}

/* =========================================================================
   Mentor Project Definitions & Assignment (M17–M21)
   ========================================================================= */

export async function getMentorDefinitions(): Promise<ProjectDefinition[]> {
  return apiFetch<ProjectDefinition[]>('/api/v1/project-definitions');
}

export async function getMentorDefinition(definitionId: string): Promise<ProjectDefinition> {
  return apiFetch<ProjectDefinition>(`/api/v1/project-definitions/${definitionId}`);
}

export async function createMentorDefinition(
  payload: ProjectDefinitionCreatePayload
): Promise<ProjectDefinition> {
  return apiFetch<ProjectDefinition>('/api/v1/project-definitions', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateMentorDefinition(
  definitionId: string,
  payload: ProjectDefinitionUpdatePayload
): Promise<ProjectDefinition> {
  return apiFetch<ProjectDefinition>(`/api/v1/project-definitions/${definitionId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function getDefinitionVersions(
  definitionId: string
): Promise<ProjectDefinitionVersion[]> {
  return apiFetch<ProjectDefinitionVersion[]>(`/api/v1/project-definitions/${definitionId}/versions`);
}

export async function getDefinitionVersion(
  definitionId: string,
  versionId: string
): Promise<ProjectDefinitionVersion> {
  return apiFetch<ProjectDefinitionVersion>(
    `/api/v1/project-definitions/${definitionId}/versions/${versionId}`
  );
}

export async function assignMentorDefinition(
  definitionId: string,
  payload: ProjectDefinitionAssignPayload
): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(`/api/v1/project-definitions/${definitionId}/assign`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getMentorStudents(params?: {
  search?: string;
  group_id?: string;
}): Promise<MentorStudentSummary[]> {
  const query = new URLSearchParams();
  if (params?.search) query.set('search', params.search);
  if (params?.group_id) query.set('group_id', params.group_id);
  const qs = query.toString();
  return apiFetch<MentorStudentSummary[]>(`/api/v1/mentors/students${qs ? `?${qs}` : ''}`);
}

export async function getMentorStudent(studentId: string): Promise<MentorStudentDetail> {
  return apiFetch<MentorStudentDetail>(`/api/v1/mentors/students/${studentId}`);
}

export async function getMentorStudentProjects(
  studentId: string
): Promise<MentorProjectInstanceSummary[]> {
  return apiFetch<MentorProjectInstanceSummary[]>(`/api/v1/mentors/students/${studentId}/projects`);
}

export async function getMentorProjects(params?: {
  search?: string;
  status?: string;
  phase?: string;
  health?: string;
  group_id?: string;
}): Promise<MentorProjectInstanceSummary[]> {
  const query = new URLSearchParams();
  if (params?.search) query.set('search', params.search);
  if (params?.status) query.set('status', params.status);
  if (params?.phase) query.set('phase', params.phase);
  if (params?.health) query.set('health', params.health);
  if (params?.group_id) query.set('group_id', params.group_id);
  const qs = query.toString();
  return apiFetch<MentorProjectInstanceSummary[]>(
    `/api/v1/mentors/projects/instances${qs ? `?${qs}` : ''}`
  );
}

export async function getMentorProjectInstances(params?: {
  search?: string;
  status?: string;
  phase?: string;
  health?: string;
  group_id?: string;
}): Promise<MentorProjectInstanceSummary[]> {
  const query = new URLSearchParams();
  if (params?.search) query.set('search', params.search);
  if (params?.status) query.set('status', params.status);
  if (params?.phase) query.set('phase', params.phase);
  if (params?.health) query.set('health', params.health);
  if (params?.group_id) query.set('group_id', params.group_id);
  const qs = query.toString();
  return apiFetch<MentorProjectInstanceSummary[]>(
    `/api/v1/mentors/project-instances${qs ? `?${qs}` : ''}`
  );
}

export async function getMentorProjectInstance(
  projectId: string
): Promise<MentorProjectInstanceDetail> {
  return apiFetch<MentorProjectInstanceDetail>(`/api/v1/mentors/project-instances/${projectId}`);
}

export async function getMentorAtRiskProjects(params?: {
  group_id?: string;
  health?: string;
}): Promise<MentorProjectInstanceSummary[]> {
  const query = new URLSearchParams();
  if (params?.health) query.set('health', params.health);
  if (params?.group_id) query.set('group_id', params.group_id);
  const qs = query.toString();
  return apiFetch<MentorProjectInstanceSummary[]>(
    `/api/v1/mentors/at-risk${qs ? `?${qs}` : ''}`
  );
}

export async function getMentorAtRiskProject(
  projectId: string
): Promise<MentorProjectInstanceDetail> {
  return apiFetch<MentorProjectInstanceDetail>(`/api/v1/mentors/at-risk/${projectId}`);
}

// ============================================================================
// Phase 7 Batch 4: Mentor Project Instance Deep Inspection (M24–M30)
// ============================================================================

export async function getMentorInstanceBlueprint(
  projectId: string
): Promise<MentorBlueprintInspectionResponse> {
  return apiFetch<MentorBlueprintInspectionResponse>(
    `/api/v1/mentors/project-instances/${projectId}/blueprint`
  );
}

export async function getMentorInstanceTasks(
  projectId: string,
  params?: {
    status?: string;
    priority?: string;
    milestone_id?: string;
    phase?: string;
    search?: string;
  }
): Promise<TaskResponse[]> {
  const query = new URLSearchParams();
  if (params?.status) query.set('status', params.status);
  if (params?.priority) query.set('priority', params.priority);
  if (params?.milestone_id) query.set('milestone_id', params.milestone_id);
  if (params?.phase) query.set('phase', params.phase);
  if (params?.search) query.set('search', params.search);
  const qs = query.toString();
  return apiFetch<TaskResponse[]>(
    `/api/v1/mentors/project-instances/${projectId}/tasks${qs ? `?${qs}` : ''}`
  );
}

export async function getMentorInstanceMilestones(
  projectId: string
): Promise<MilestoneResponse[]> {
  return apiFetch<MilestoneResponse[]>(
    `/api/v1/mentors/project-instances/${projectId}/milestones`
  );
}

export async function getMentorInstanceRisks(
  projectId: string,
  params?: {
    status?: string;
    severity?: string;
    search?: string;
  }
): Promise<RiskResponse[]> {
  const query = new URLSearchParams();
  if (params?.status) query.set('status', params.status);
  if (params?.severity) query.set('severity', params.severity);
  if (params?.search) query.set('search', params.search);
  const qs = query.toString();
  return apiFetch<RiskResponse[]>(
    `/api/v1/mentors/project-instances/${projectId}/risks${qs ? `?${qs}` : ''}`
  );
}

export async function getMentorInstanceDocuments(
  projectId: string,
  params?: {
    doc_type?: string;
    status?: string;
    search?: string;
  }
): Promise<DocumentResponse[]> {
  const query = new URLSearchParams();
  if (params?.doc_type) query.set('doc_type', params.doc_type);
  if (params?.status) query.set('status', params.status);
  if (params?.search) query.set('search', params.search);
  const qs = query.toString();
  return apiFetch<DocumentResponse[]>(
    `/api/v1/mentors/project-instances/${projectId}/documents${qs ? `?${qs}` : ''}`
  );
}

export async function getMentorInstanceGitHub(
  projectId: string
): Promise<GitHubIntegrationResponse> {
  return apiFetch<GitHubIntegrationResponse>(
    `/api/v1/mentors/project-instances/${projectId}/github`
  );
}

export async function getMentorInstanceActivity(
  projectId: string,
  params?: {
    limit?: number;
    offset?: number;
  }
): Promise<ActivityItemResponse[]> {
  const query = new URLSearchParams();
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.offset) query.set('offset', String(params.offset));
  const qs = query.toString();
  return apiFetch<ActivityItemResponse[]>(
    `/api/v1/mentors/project-instances/${projectId}/activity${qs ? `?${qs}` : ''}`
  );
}

// ============================================================================
// Phase 7 Batch 6: Mentor Scoped Activity & Mentor AI Supervision
// ============================================================================

export async function getGroupActivity(
  groupId: string,
  params?: { limit?: number; offset?: number }
): Promise<ActivityItemResponse[]> {
  const query = new URLSearchParams();
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.offset) query.set('offset', String(params.offset));
  const qs = query.toString();
  return apiFetch<ActivityItemResponse[]>(
    `/api/v1/groups/${groupId}/activity${qs ? `?${qs}` : ''}`
  );
}

export async function getMentorStudentActivity(
  studentId: string,
  params?: { limit?: number; offset?: number }
): Promise<ActivityItemResponse[]> {
  const query = new URLSearchParams();
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.offset) query.set('offset', String(params.offset));
  const qs = query.toString();
  return apiFetch<ActivityItemResponse[]>(
    `/api/v1/mentors/students/${studentId}/activity${qs ? `?${qs}` : ''}`
  );
}

export async function getMentorPortfolioActivity(
  params?: { limit?: number; offset?: number }
): Promise<ActivityItemResponse[]> {
  const query = new URLSearchParams();
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.offset) query.set('offset', String(params.offset));
  const qs = query.toString();
  return apiFetch<ActivityItemResponse[]>(
    `/api/v1/mentors/activity${qs ? `?${qs}` : ''}`
  );
}

export async function getGroupAIStatus(
  groupId: string
): Promise<MentorAIStatusResponse> {
  return apiFetch<MentorAIStatusResponse>(
    `/api/v1/groups/${groupId}/ai/status`
  );
}

export async function sendGroupAIMessage(
  groupId: string,
  payload: MentorAIChatPayload | string
): Promise<MentorAIChatResponse> {
  const body = typeof payload === 'string' ? { message: payload } : payload;
  return apiFetch<MentorAIChatResponse>(
    `/api/v1/groups/${groupId}/ai/chat`,
    {
      method: 'POST',
      body: JSON.stringify(body),
    }
  );
}

export async function getMentorAIStatus(): Promise<MentorAIStatusResponse> {
  return apiFetch<MentorAIStatusResponse>(
    `/api/v1/mentors/ai/status`
  );
}

export async function sendMentorAIMessage(
  payload: MentorAIChatPayload | string
): Promise<MentorAIChatResponse> {
  const body = typeof payload === 'string' ? { message: payload } : payload;
  return apiFetch<MentorAIChatResponse>(
    `/api/v1/mentors/ai/chat`,
    {
      method: 'POST',
      body: JSON.stringify(body),
    }
  );
}

/**
 * Get authenticated mentor profile context.
 * GET /api/v1/mentors/me
 */
export async function getMentorProfile(): Promise<MentorProfileResponse> {
  return apiFetch<MentorProfileResponse>('/api/v1/mentors/me');
}

/**
 * Update authenticated mentor profile context.
 * PATCH /api/v1/mentors/me
 */
export async function updateMentorProfile(
  payload: MentorProfileUpdatePayload,
): Promise<MentorProfileResponse> {
  return apiFetch<MentorProfileResponse>('/api/v1/mentors/me', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

/**
 * Get current user preferences.
 * GET /api/v1/users/me/preferences
 */
export async function getUserPreferences(): Promise<UserPreferencesResponse> {
  return apiFetch<UserPreferencesResponse>('/api/v1/users/me/preferences');
}

/**
 * Update current user preferences.
 * PATCH /api/v1/users/me/preferences
 */
export async function updateUserPreferences(
  payload: UserPreferencesUpdatePayload,
): Promise<UserPreferencesResponse> {
  return apiFetch<UserPreferencesResponse>('/api/v1/users/me/preferences', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

/**
 * Get platform overview metrics (AD01).
 * GET /api/v1/admin/overview
 */
export async function getAdminOverview(): Promise<AdminOverviewResponse> {
  return apiFetch<AdminOverviewResponse>('/api/v1/admin/overview');
}

/**
 * List platform mentors (AD02).
 * GET /api/v1/admin/mentors
 */
export async function getAdminMentors(params?: {
  search?: string;
  status?: string;
}): Promise<AdminMentorSummary[]> {
  const query = new URLSearchParams();
  if (params?.search) query.set('search', params.search);
  if (params?.status) query.set('status', params.status);
  const qs = query.toString();
  return apiFetch<AdminMentorSummary[]>(`/api/v1/admin/mentors${qs ? `?${qs}` : ''}`);
}

/**
 * Get mentor details for governance (AD03).
 * GET /api/v1/admin/mentors/:mentorId
 */
export async function getAdminMentor(mentorId: string): Promise<AdminMentorDetail> {
  return apiFetch<AdminMentorDetail>(`/api/v1/admin/mentors/${mentorId}`);
}

/**
 * List platform students (AD04).
 * GET /api/v1/admin/students
 */
export async function getAdminStudents(params?: {
  search?: string;
  track?: string;
  status?: string;
}): Promise<AdminStudentSummary[]> {
  const query = new URLSearchParams();
  if (params?.search) query.set('search', params.search);
  if (params?.track) query.set('track', params.track);
  if (params?.status) query.set('status', params.status);
  const qs = query.toString();
  return apiFetch<AdminStudentSummary[]>(`/api/v1/admin/students${qs ? `?${qs}` : ''}`);
}

/**
 * Get student details for governance (AD05).
 * GET /api/v1/admin/students/:studentId
 */
export async function getAdminStudent(studentId: string): Promise<AdminStudentDetail> {
  return apiFetch<AdminStudentDetail>(`/api/v1/admin/students/${studentId}`);
}

/**
 * List platform cohorts/groups (AD06).
 * GET /api/v1/admin/groups
 */
export async function getAdminGroups(params?: {
  search?: string;
  status?: string;
}): Promise<AdminGroupSummary[]> {
  const query = new URLSearchParams();
  if (params?.search) query.set('search', params.search);
  if (params?.status) query.set('status', params.status);
  const qs = query.toString();
  return apiFetch<AdminGroupSummary[]>(`/api/v1/admin/groups${qs ? `?${qs}` : ''}`);
}

/**
 * Get single cohort/group governance detail (AD07).
 * GET /api/v1/admin/groups/:groupId
 */
export async function getAdminGroup(groupId: string): Promise<AdminGroupDetail> {
  return apiFetch<AdminGroupDetail>(`/api/v1/admin/groups/${groupId}`);
}

/**
 * List platform project instances (AD08).
 * GET /api/v1/admin/projects
 */
export async function getAdminProjects(params?: {
  search?: string;
  phase?: string;
  health?: string;
  status?: string;
}): Promise<AdminProjectSummary[]> {
  const query = new URLSearchParams();
  if (params?.search) query.set('search', params.search);
  if (params?.phase) query.set('phase', params.phase);
  if (params?.health) query.set('health', params.health);
  if (params?.status) query.set('status', params.status);
  const qs = query.toString();
  return apiFetch<AdminProjectSummary[]>(`/api/v1/admin/projects${qs ? `?${qs}` : ''}`);
}

/**
 * List project definitions for governance monitoring (AD09).
 * GET /api/v1/admin/definitions
 */
export async function getAdminDefinitions(params?: {
  search?: string;
  status?: string;
}): Promise<AdminProjectDefinitionSummary[]> {
  const query = new URLSearchParams();
  if (params?.search) query.set('search', params.search);
  if (params?.status) query.set('status', params.status);
  const qs = query.toString();
  return apiFetch<AdminProjectDefinitionSummary[]>(`/api/v1/admin/definitions${qs ? `?${qs}` : ''}`);
}

/**
 * Get project definition detail with version tree and adoptions (AD09).
 * GET /api/v1/admin/definitions/:definitionId
 */
export async function getAdminDefinition(definitionId: string): Promise<AdminProjectDefinitionDetail> {
  return apiFetch<AdminProjectDefinitionDetail>(`/api/v1/admin/definitions/${definitionId}`);
}

/**
 * Get platform-wide instances monitoring data & summary KPIs (AD10).
 * GET /api/v1/admin/instances
 */
export async function getAdminInstancesMonitoring(params?: {
  search?: string;
  phase?: string;
  health?: string;
  status?: string;
}): Promise<AdminInstanceMonitoringResponse> {
  const query = new URLSearchParams();
  if (params?.search) query.set('search', params.search);
  if (params?.phase) query.set('phase', params.phase);
  if (params?.health) query.set('health', params.health);
  if (params?.status) query.set('status', params.status);
  const qs = query.toString();
  return apiFetch<AdminInstanceMonitoringResponse>(`/api/v1/admin/instances${qs ? `?${qs}` : ''}`);
}

/**
 * Get canonical project instance governance detail (AD10).
 * GET /api/v1/admin/instances/:projectId
 */
export async function getAdminInstanceDetail(projectId: string): Promise<AdminProjectInstanceDetail> {
  return apiFetch<AdminProjectInstanceDetail>(`/api/v1/admin/instances/${projectId}`);
}

/**
 * Get platform administrative system health (AD19).
 * GET /api/v1/admin/health
 */
export async function getAdminSystemHealth(): Promise<AdminSystemHealthResponse> {
  return apiFetch<AdminSystemHealthResponse>('/api/v1/admin/health');
}

/**
 * Get system component diagnostic detail (AD20).
 * GET /api/v1/admin/health/:componentId
 */
export async function getAdminComponentDetail(componentId: string): Promise<AdminSubsystemDetail> {
  return apiFetch<AdminSubsystemDetail>(`/api/v1/admin/health/${componentId}`);
}

/**
 * Get platform security & audit overview (AD24).
 * GET /api/v1/admin/security/overview
 */
export async function getAdminSecurityOverview(): Promise<AdminSecurityOverview> {
  return apiFetch<AdminSecurityOverview>('/api/v1/admin/security/overview');
}

/**
 * Get platform canonical audit log (AD25).
 * GET /api/v1/admin/security/audit
 */
export async function getAdminAuditLog(params?: {
  search?: string;
  actor_role?: string;
  event_type?: string;
  resource_type?: string;
  limit?: number;
  offset?: number;
}): Promise<AdminAuditLogResponse> {
  const query = new URLSearchParams();
  if (params?.search) query.set('search', params.search);
  if (params?.actor_role && params.actor_role !== 'ALL') query.set('actor_role', params.actor_role);
  if (params?.event_type && params.event_type !== 'ALL') query.set('event_type', params.event_type);
  if (params?.resource_type && params.resource_type !== 'ALL') query.set('resource_type', params.resource_type);
  if (params?.limit !== undefined) query.set('limit', String(params.limit));
  if (params?.offset !== undefined) query.set('offset', String(params.offset));
  const qs = query.toString();
  return apiFetch<AdminAuditLogResponse>(`/api/v1/admin/security/audit${qs ? `?${qs}` : ''}`);
}

/**
 * Get governed investigation candidate inspection targets (AD26).
 * GET /api/v1/admin/security/investigations
 */
export async function getAdminInvestigations(): Promise<AdminInvestigationOverviewResponse> {
  return apiFetch<AdminInvestigationOverviewResponse>('/api/v1/admin/security/investigations');
}

/**
 * Get governed investigation inspection detail (AD27).
 * GET /api/v1/admin/security/investigations/:investigationId
 */
export async function getAdminInvestigationDetail(investigationId: string): Promise<any> {
  return apiFetch<any>(`/api/v1/admin/security/investigations/${investigationId}`);
}

// ============================================================================
// Batch 9: AD21–AD23 Documents, RAG & Generation Management
// ============================================================================

/**
 * Get platform-wide documents with bounded pagination and filters (AD21).
 * GET /api/v1/admin/documents
 */
export async function getAdminDocuments(params?: {
  search?: string;
  doc_type?: string;
  status?: string;
  project_id?: string;
  limit?: number;
  offset?: number;
}): Promise<AdminDocumentsResponse> {
  const query = new URLSearchParams();
  if (params?.search) query.set('search', params.search);
  if (params?.doc_type && params.doc_type !== 'ALL') query.set('doc_type', params.doc_type);
  if (params?.status && params.status !== 'ALL') query.set('status', params.status);
  if (params?.project_id) query.set('project_id', params.project_id);
  if (params?.limit !== undefined) query.set('limit', String(params.limit));
  if (params?.offset !== undefined) query.set('offset', String(params.offset));
  const qs = query.toString();
  return apiFetch<AdminDocumentsResponse>(`/api/v1/admin/documents${qs ? `?${qs}` : ''}`);
}

/**
 * Get RAG subsystem posture and diagnostics (AD22).
 * GET /api/v1/admin/documents/rag
 */
export async function getAdminRAGDiagnostics(): Promise<AdminRAGDiagnostics> {
  return apiFetch<AdminRAGDiagnostics>('/api/v1/admin/documents/rag');
}

/**
 * Get document generation runs from blueprint_jobs (AD23).
 * GET /api/v1/admin/documents/generation
 */
export async function getAdminGenerationJobs(params?: {
  status?: string;
  job_type?: string;
  project_id?: string;
  limit?: number;
  offset?: number;
}): Promise<AdminGenerationJobsResponse> {
  const query = new URLSearchParams();
  if (params?.status && params.status !== 'ALL') query.set('status', params.status);
  if (params?.job_type && params.job_type !== 'ALL') query.set('job_type', params.job_type);
  if (params?.project_id) query.set('project_id', params.project_id);
  if (params?.limit !== undefined) query.set('limit', String(params.limit));
  if (params?.offset !== undefined) query.set('offset', String(params.offset));
  const qs = query.toString();
  return apiFetch<AdminGenerationJobsResponse>(`/api/v1/admin/documents/generation${qs ? `?${qs}` : ''}`);
}

// ============================================================================
// Batch 9: AD28–AD29 Platform Analytics & Dimensional Detail
// ============================================================================

/**
 * Get macro platform analytics and canonical distributions (AD28).
 * GET /api/v1/admin/analytics
 */
export async function getAdminAnalytics(): Promise<AdminPlatformAnalyticsResponse> {
  return apiFetch<AdminPlatformAnalyticsResponse>('/api/v1/admin/analytics');
}

/**
 * Get dimensional drilldown analytics for a specific canonical domain (AD29).
 * GET /api/v1/admin/analytics/:dimension
 */
export async function getAdminAnalyticsDimension(
  dimension: string
): Promise<AdminAnalyticsDimensionDetail> {
  return apiFetch<AdminAnalyticsDimensionDetail>(
    `/api/v1/admin/analytics/${encodeURIComponent(dimension)}`
  );
}

// ============================================================================
// Batch 10: AD11–AD18 AI Observability, Quality, Cost & Key Pool Monitoring
// ============================================================================

/**
 * Get AI Observatory macro status, gateway posture, and running jobs (AD11).
 * GET /api/v1/admin/ai/observatory
 */
export async function getAdminAIObservatory(): Promise<AdminAIObservatoryResponse> {
  return apiFetch<AdminAIObservatoryResponse>('/api/v1/admin/ai/observatory');
}

/**
 * Get AI Usage transaction volumes, time-trend, and capability distributions (AD12).
 * GET /api/v1/admin/ai/usage
 */
export async function getAdminAIUsage(): Promise<AdminAIUsageResponse> {
  return apiFetch<AdminAIUsageResponse>('/api/v1/admin/ai/usage');
}

/**
 * List paginated canonical AI execution records with filters (AD13).
 * GET /api/v1/admin/ai/executions
 */
export async function getAdminAIExecutions(params?: {
  status?: string;
  job_type?: string;
  project_id?: string;
  limit?: number;
  offset?: number;
}): Promise<AdminAIExecutionsResponse> {
  const query = new URLSearchParams();
  if (params?.status && params.status !== 'ALL') query.set('status', params.status);
  if (params?.job_type && params.job_type !== 'ALL') query.set('job_type', params.job_type);
  if (params?.project_id) query.set('project_id', params.project_id);
  if (params?.limit !== undefined) query.set('limit', String(params.limit));
  if (params?.offset !== undefined) query.set('offset', String(params.offset));
  const qs = query.toString();
  return apiFetch<AdminAIExecutionsResponse>(`/api/v1/admin/ai/executions${qs ? `?${qs}` : ''}`);
}

/**
 * Get detailed partial trace and stage execution milestones for a job (AD14).
 * GET /api/v1/admin/ai/executions/:executionId
 */
export async function getAdminAITraceDetail(
  executionId: string
): Promise<AdminAITraceDetailResponse> {
  return apiFetch<AdminAITraceDetailResponse>(
    `/api/v1/admin/ai/executions/${encodeURIComponent(executionId)}`
  );
}

/**
 * Get AI Quality and QA Judge evaluation metrics and score distributions (AD15).
 * GET /api/v1/admin/ai/quality
 */
export async function getAdminAIQuality(): Promise<AdminAIQualityResponse> {
  return apiFetch<AdminAIQualityResponse>('/api/v1/admin/ai/quality');
}

/**
 * Get AI Cost & Capacity accounting and provider billing posture (AD16).
 * GET /api/v1/admin/ai/cost
 */
export async function getAdminAICost(): Promise<AdminAICostResponse> {
  return apiFetch<AdminAICostResponse>('/api/v1/admin/ai/cost');
}

/**
 * Get dimensional usage volume drilldown (AD17).
 * GET /api/v1/admin/ai/cost/:dimension
 */
export async function getAdminAICostDimension(
  dimension: string
): Promise<AdminAICostDimensionResponse> {
  return apiFetch<AdminAICostDimensionResponse>(
    `/api/v1/admin/ai/cost/${encodeURIComponent(dimension)}`
  );
}

/**
 * Get safe OpenRouter API Key Pool monitoring slots (AD18).
 * GET /api/v1/admin/ai/keys
 */
export async function getAdminAIKeys(): Promise<AdminAIKeysResponse> {
  return apiFetch<AdminAIKeysResponse>('/api/v1/admin/ai/keys');
}

/**
 * Role-aware Global Search (Phase 8 Batch 3).
 * GET /api/v1/search?q=&category=&limit=
 */
export async function searchWorkspace(params: {
  q: string;
  category?: string;
  limit?: number;
}): Promise<SearchResponseData> {
  const query = new URLSearchParams();
  query.append('q', params.q);
  if (params.category) query.append('category', params.category);
  if (params.limit !== undefined) query.append('limit', String(params.limit));

  return apiFetch<SearchResponseData>(`/api/v1/search?${query.toString()}`);
}

/**
 * List Authenticated User Notifications (Phase 8 Batch 3).
 * GET /api/v1/notifications?limit=&offset=&unread_only=
 */
export async function getNotifications(params?: {
  limit?: number;
  offset?: number;
  unread_only?: boolean;
}): Promise<NotificationItem[]> {
  const query = new URLSearchParams();
  if (params?.limit !== undefined) query.append('limit', String(params.limit));
  if (params?.offset !== undefined) query.append('offset', String(params.offset));
  if (params?.unread_only !== undefined) query.append('unread_only', String(params.unread_only));

  const qs = query.toString();
  return apiFetch<NotificationItem[]>(`/api/v1/notifications${qs ? `?${qs}` : ''}`);
}

/**
 * Get Unread Notification Count (Phase 8 Batch 3).
 * GET /api/v1/notifications/unread-count
 */
export async function getUnreadNotificationCount(): Promise<UnreadCountResponse> {
  return apiFetch<UnreadCountResponse>('/api/v1/notifications/unread-count');
}

/**
 * Mark Single Notification As Read (Phase 8 Batch 3).
 * PATCH /api/v1/notifications/:id/read
 */
export async function markNotificationRead(id: string): Promise<NotificationItem> {
  return apiFetch<NotificationItem>(`/api/v1/notifications/${id}/read`, {
    method: 'PATCH',
  });
}

/**
 * Mark All Notifications As Read for Authenticated User (Phase 8 Batch 3).
 * POST /api/v1/notifications/mark-all-read
 */
export async function markAllNotificationsRead(): Promise<MarkAllReadResponse> {
  return apiFetch<MarkAllReadResponse>('/api/v1/notifications/mark-all-read', {
    method: 'POST',
  });
}

// Append Batch 06, Batch 07, Batch 08, Batch 09, Batch 10 to default export
Object.assign(apiClient, {
  searchWorkspace,
  getNotifications,
  getUnreadNotificationCount,
  markNotificationRead,
  markAllNotificationsRead,
  getMentorProfile,
  updateMentorProfile,
  getUserPreferences,
  updateUserPreferences,
  getGitHubIntegration,
  connectGitHub,
  syncGitHub,
  disconnectGitHub,
  getProjectActivity,
  getAIMentorHistory,
  sendAIMentorMessage,
  executeAIOperation,
  getHelpRequests,
  createHelpRequest,
  getHelpRequest,
  getMentorNotes,
  acknowledgeMentorNote,
  getProjectChanges,
  getProjectChange,
  analyzeProjectChange,
  confirmProjectChange,
  getBlueprintVersions,
  getBlueprintVersion,
  getMentorOverview,
  getMentorGroups,
  createMentorGroup,
  getMentorGroup,
  getGroupStudents,
  getGroupProjects,
  getMentorDefinitions,
  getMentorDefinition,
  createMentorDefinition,
  updateMentorDefinition,
  getDefinitionVersions,
  getDefinitionVersion,
  assignMentorDefinition,
  getMentorStudents,
  getMentorStudent,
  getMentorStudentProjects,
  getMentorProjects,
  getMentorProjectInstances,
  getMentorProjectInstance,
  getMentorAtRiskProjects,
  getMentorAtRiskProject,
  getMentorInstanceBlueprint,
  getMentorInstanceTasks,
  getMentorInstanceMilestones,
  getMentorInstanceRisks,
  getMentorInstanceDocuments,
  getMentorInstanceGitHub,
  getMentorInstanceActivity,
  getGroupActivity,
  getMentorStudentActivity,
  getMentorPortfolioActivity,
  getGroupAIStatus,
  sendGroupAIMessage,
  getMentorAIStatus,
  sendMentorAIMessage,
  getAdminOverview,
  getAdminMentors,
  getAdminMentor,
  getAdminStudents,
  getAdminStudent,
  getAdminGroups,
  getAdminGroup,
  getAdminProjects,
  getAdminDefinitions,
  getAdminDefinition,
  getAdminInstancesMonitoring,
  getAdminInstanceDetail,
  getAdminSystemHealth,
  getAdminComponentDetail,
  getAdminSecurityOverview,
  getAdminAuditLog,
  getAdminInvestigations,
  getAdminInvestigationDetail,
  getAdminDocuments,
  getAdminRAGDiagnostics,
  getAdminGenerationJobs,
  getAdminAnalytics,
  getAdminAnalyticsDimension,
  getAdminAIObservatory,
  getAdminAIUsage,
  getAdminAIExecutions,
  getAdminAITraceDetail,
  getAdminAIQuality,
  getAdminAICost,
  getAdminAICostDimension,
  getAdminAIKeys,
});







