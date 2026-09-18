import { useState } from 'react';
import { Button } from '@/components/ui';

interface AssessmentCompletionCardProps {
  totalQuestions: number;
  isCompleting: boolean;
  onComplete: () => Promise<void>;
  onReviewQuestions: () => void;
  error?: string | null;
}

export function AssessmentCompletionCard({
  totalQuestions,
  isCompleting,
  onComplete,
  onReviewQuestions,
  error,
}: AssessmentCompletionCardProps) {
  const [hasTriggered, setHasTriggered] = useState(false);

  const handleFinalize = async () => {
    if (hasTriggered || isCompleting) return;
    setHasTriggered(true);
    try {
      await onComplete();
    } finally {
      setHasTriggered(false);
    }
  };

  return (
    <div className="gf-assessment-completion" id="assessment-completion-view">
      <div className="gf-assessment-completion__header">
        <span className="gf-assessment-intro__eyebrow">Assessment Complete</span>
        <h2 className="gf-assessment-completion__title">Ready to Synthesize Project Understanding</h2>
        <p className="gf-assessment-completion__subtitle">
          You have provided architectural responses to all {totalQuestions} questions. Review your
          submission status below and finalize the assessment to generate your canonical Project
          Understanding and Readiness Profile.
        </p>
      </div>

      {/* Completion Checklist */}
      <div className="gf-assessment-completion__checklist" role="region" aria-label="Completion status">
        <div className="gf-assessment-completion__item">
          <svg
            className="gf-assessment-completion__check-icon"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M20 6 9 17l-5-5" />
          </svg>
          <span><strong>10 / 10</strong> Core Architectural & Feasibility Questions Answered</span>
        </div>

        <div className="gf-assessment-completion__item">
          <svg
            className="gf-assessment-completion__check-icon"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M20 6 9 17l-5-5" />
          </svg>
          <span><strong>5 / 5</strong> Project-Specific Adaptive Questions Answered</span>
        </div>

        <div className="gf-assessment-completion__item">
          <svg
            className="gf-assessment-completion__check-icon"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M20 6 9 17l-5-5" />
          </svg>
          <span>Persisted authoritative state verified across all {totalQuestions} inquiry dimensions</span>
        </div>
      </div>

      {error && (
        <p className="gf-question-card__error-msg" role="alert">
          {error}
        </p>
      )}

      {/* Actions */}
      <div className="gf-assessment-completion__actions">
        <Button
          variant="secondary"
          size="lg"
          onClick={onReviewQuestions}
          disabled={isCompleting || hasTriggered}
          id="assessment-review-questions-btn"
        >
          ← Review Responses
        </Button>

        <Button
          variant="primary"
          size="lg"
          onClick={handleFinalize}
          disabled={isCompleting || hasTriggered}
          id="assessment-finalize-btn"
        >
          {isCompleting || hasTriggered ? 'Synthesizing Results...' : 'Finalize & View Results →'}
        </Button>
      </div>
    </div>
  );
}
