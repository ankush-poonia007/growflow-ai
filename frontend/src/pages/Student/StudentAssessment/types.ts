/**
 * GrowFlow Student Assessment Component Types.
 */

import type {
  AssessmentQuestion,
  AssessmentAnswer,
  AssessmentSessionStatus,
  AssessmentResultResponse,
} from '@/lib/api/types';

export type AssessmentViewMode = 'INTRO' | 'QUESTION' | 'COMPLETION' | 'RESULT';

export interface AssessmentFormState {
  selectedOption: string;
  textResponse: string;
}

export interface AssessmentFormErrors {
  answer?: string;
  submit?: string;
}

export interface AssessmentContextState {
  status: AssessmentSessionStatus | null;
  currentQuestion: AssessmentQuestion | null;
  currentAnswer: AssessmentAnswer | null;
  result: AssessmentResultResponse | null;
  isLoading: boolean;
  isSubmitting: boolean;
  error: string | null;
}
