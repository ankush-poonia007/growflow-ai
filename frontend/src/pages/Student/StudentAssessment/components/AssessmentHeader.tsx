import { Link } from 'react-router';
import { Badge } from '@/components/ui';
import type { AssessmentStatus, AssessmentReadinessTier } from '@/lib/api/types';
import { getReadinessTierBadgeVariant } from '../utils';

interface AssessmentHeaderProps {
  projectId: string;
  projectName?: string;
  viewMode: 'INTRO' | 'QUESTION' | 'COMPLETION' | 'RESULT';
  status: AssessmentStatus | null;
  currentQuestionIndex?: number;
  totalQuestions?: number;
  readinessTier?: AssessmentReadinessTier;
}

export function AssessmentHeader({
  projectId,
  projectName,
  viewMode,
  status,
  currentQuestionIndex = 1,
  totalQuestions = 15,
  readinessTier,
}: AssessmentHeaderProps) {
  const showProgress = viewMode === 'QUESTION' || viewMode === 'COMPLETION';
  const progressPercent = viewMode === 'COMPLETION' 
    ? 100 
    : Math.min(100, Math.round((currentQuestionIndex / totalQuestions) * 100));

  const isAdaptivePhase = currentQuestionIndex > 10;

  return (
    <header className="gf-assessment-header">
      <nav className="gf-assessment-header__nav" aria-label="Breadcrumb">
        <Link
          to={`/student/projects/${projectId}/profile`}
          className="gf-assessment-header__back-link"
          id="assessment-back-to-project-link"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <polyline points="15 18 9 12 15 6" />
          </svg>
          Back to Project Profile
        </Link>
      </nav>

      <div className="gf-assessment-header__top">
        <div className="gf-assessment-header__title-wrap">
          <span className="gf-assessment-header__eyebrow">
            Stage 2: Technical Assessment
          </span>
          <h1 className="gf-assessment-header__title">
            {projectName ? `${projectName} — Assessment` : 'Project Assessment'}
          </h1>
        </div>

        <div className="gf-assessment-header__badges">
          {status === 'COMPLETED' && readinessTier ? (
            <Badge variant={getReadinessTierBadgeVariant(readinessTier)}>
              Readiness: {readinessTier.replace('_', ' ')}
            </Badge>
          ) : status === 'IN_PROGRESS' ? (
            <Badge variant="accent" dot>
              {isAdaptivePhase ? 'Adaptive Phase' : 'Core Assessment'}
            </Badge>
          ) : (
            <Badge variant="neutral">Not Started</Badge>
          )}
        </div>
      </div>

      {showProgress && (
        <div className="gf-assessment-progress">
          <div className="gf-assessment-progress__label-row">
            <span className="gf-assessment-progress__label">
              {viewMode === 'COMPLETION'
                ? 'All Questions Completed'
                : isAdaptivePhase
                ? 'Adaptive Questions (Tailored to Project)'
                : 'Core Architecture Questions'}
            </span>
            <span className="gf-assessment-progress__count">
              {viewMode === 'COMPLETION'
                ? `${totalQuestions} / ${totalQuestions} answered`
                : `Question ${currentQuestionIndex} of ${totalQuestions}`}
            </span>
          </div>
          <div
            className="gf-assessment-progress__track"
            role="progressbar"
            aria-valuenow={currentQuestionIndex}
            aria-valuemin={1}
            aria-valuemax={totalQuestions}
            aria-label="Assessment progress"
          >
            <div
              className="gf-assessment-progress__fill"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      )}
    </header>
  );
}
