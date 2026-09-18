/**
 * GrowFlow Assessment API Types.
 *
 * Architecture ref:
 *   6N § 16 — Assessment Architecture (10 standardized core + 5 dynamic questions)
 *   5B § 18 & 19 — AI Assessment & Enriched Project Understanding
 *   1 § 31 — Final Student-Side Concept
 */

export type AssessmentStatus = 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED';

export type QuestionType = 'MULTIPLE_CHOICE' | 'TEXT';

export type AssessmentReadinessTier = 'HIGH' | 'MODERATE' | 'NEEDS_REFINEMENT';

export interface AssessmentQuestionOption {
  value: string;
  label: string;
  description: string;
}

export interface AssessmentQuestion {
  id: string;
  order_index: number;
  category: string;
  question_text: string;
  help_text: string;
  question_type: QuestionType;
  options: AssessmentQuestionOption[];
  is_adaptive: boolean;
  context_badge?: string | null;
}

export interface AssessmentAnswer {
  id: string;
  assessment_id: string;
  question_id: string;
  question_index: number;
  question_text: string;
  question_type: QuestionType;
  selected_option?: string | null;
  text_response?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface AssessmentSessionStatus {
  project_id: string;
  project_name: string;
  current_phase: string;
  status: AssessmentStatus;
  current_question_index: number;
  total_questions: number;
  answered_count: number;
  progress_percentage: number;
  started_at?: string | null;
  completed_at?: string | null;
}

export interface AssessmentStartResponse {
  session: AssessmentSessionStatus;
  current_question: AssessmentQuestion;
}

export interface AssessmentQuestionResponse {
  question: AssessmentQuestion;
  answer: AssessmentAnswer | null;
}

export interface AssessmentAnswerSubmitPayload {
  question_index: number;
  selected_option?: string;
  text_response?: string;
}

export interface AssessmentAnswerSubmitResponse {
  answer: AssessmentAnswer;
  current_question_index: number;
  next_question_index: number | null;
  answered_count: number;
  total_questions: number;
  is_complete_eligible: boolean;
}

export interface IdentifiedGap {
  area: string;
  severity: string;
  description: string;
}

export interface AssessmentRecommendation {
  phase: string;
  action: string;
}

export interface AssessmentResultResponse {
  id: string;
  assessment_id: string;
  project_instance_id: string;
  skill_level: string;
  project_complexity: string;
  alignment: string;
  technical_confidence: string;
  learning_depth: string;
  recommended_focus: string;
  summary: string;
  overall_score: number;
  readiness_tier: AssessmentReadinessTier;
  dimension_scores: Record<string, number>;
  identified_gaps: IdentifiedGap[];
  recommendations: AssessmentRecommendation[];
  created_at?: string | null;
}
