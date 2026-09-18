import { Button } from '@/components/ui';
import type { ProjectResponse, AssessmentStatus } from '@/lib/api/types';

interface AssessmentIntroProps {
  project: ProjectResponse | null;
  status: AssessmentStatus | null;
  currentQuestionIndex: number;
  totalQuestions: number;
  isStarting: boolean;
  onStart: () => void;
  onContinue: () => void;
  onViewResult: () => void;
}

export function AssessmentIntro({
  project,
  status,
  currentQuestionIndex,
  totalQuestions,
  isStarting,
  onStart,
  onContinue,
  onViewResult,
}: AssessmentIntroProps) {
  const isCompleted = status === 'COMPLETED';
  const isInProgress = status === 'IN_PROGRESS';

  const title = project?.name || 'Your Project';
  const problem = project?.problem || 'Clarifying real-world problem scope.';
  const solution = project?.proposed_solution || 'Full-stack software architecture implementation.';
  const complexity = project?.complexity || 'INTERMEDIATE';

  return (
    <div className="gf-assessment-intro" id="assessment-intro-view">
      <div className="gf-assessment-intro__header">
        <span className="gf-assessment-intro__eyebrow">Stage 2 Readiness Assessment</span>
        <h2 className="gf-assessment-intro__title">Technical Readiness & Project Understanding</h2>
        <p className="gf-assessment-intro__desc">
          Before entering Stage 3 (Blueprint Generation), this structured assessment evaluates your
          architectural readiness, design assumptions, and technical trade-offs. Your answers directly
          shape your personalized project roadmap and mentor review criteria.
        </p>
      </div>

      {/* Project Context Box */}
      <div className="gf-assessment-context-box">
        <span className="gf-assessment-context-box__title">Active Project Context</span>
        <div className="gf-assessment-context-box__meta">
          <div className="gf-assessment-context-box__item">
            <span className="gf-assessment-context-box__label">Project Name</span>
            <span className="gf-assessment-context-box__value">{title}</span>
          </div>
          <div className="gf-assessment-context-box__item">
            <span className="gf-assessment-context-box__label">Complexity Level</span>
            <span className="gf-assessment-context-box__value">{complexity}</span>
          </div>
        </div>
        <div className="gf-assessment-context-box__item" style={{ marginTop: '0.25rem' }}>
          <span className="gf-assessment-context-box__label">Core Problem Statement</span>
          <span className="gf-assessment-context-box__value" style={{ fontWeight: 400, fontSize: '0.875rem' }}>
            {problem}
          </span>
        </div>
        <div className="gf-assessment-context-box__item" style={{ marginTop: '0.25rem' }}>
          <span className="gf-assessment-context-box__label">Target Solution Approach</span>
          <span className="gf-assessment-context-box__value" style={{ fontWeight: 400, fontSize: '0.875rem' }}>
            {solution}
          </span>
        </div>
      </div>

      {/* 3 Step Breakdown */}
      <div className="gf-assessment-intro__steps-grid">
        <div className="gf-assessment-intro__step-card">
          <span className="gf-assessment-intro__step-num">Step 1</span>
          <h3 className="gf-assessment-intro__step-heading">10 Core Dimensions</h3>
          <p className="gf-assessment-intro__step-text">
            Standardized questions exploring problem clarity, data schemas, API contracts, security,
            performance constraints, and risk mitigation.
          </p>
        </div>

        <div className="gf-assessment-intro__step-card">
          <span className="gf-assessment-intro__step-num">Step 2</span>
          <h3 className="gf-assessment-intro__step-heading">5 Adaptive Inquiries</h3>
          <p className="gf-assessment-intro__step-text">
            Dynamic questions tailored specifically to your chosen technologies, solution complexity,
            and earlier architectural decisions.
          </p>
        </div>

        <div className="gf-assessment-intro__step-card">
          <span className="gf-assessment-intro__step-num">Step 3</span>
          <h3 className="gf-assessment-intro__step-heading">Project Understanding</h3>
          <p className="gf-assessment-intro__step-text">
            Receive your Readiness Tier, dimensional score breakdown, identified architectural gaps,
            and concrete recommendations for Stage 3 Blueprinting.
          </p>
        </div>
      </div>

      {/* Truthful Note */}
      <div
        style={{
          fontSize: '0.8125rem',
          color: 'var(--gf-text-muted, #73736c)',
          lineHeight: 1.5,
          borderLeft: '2px solid var(--gf-accent, #6f7f63)',
          paddingLeft: '0.75rem',
        }}
      >
        Your answers are automatically saved to the backend as you progress. You can pause, navigate
        away, or refresh at any time without losing your answers.
      </div>

      {/* Action Footer */}
      <div className="gf-assessment-intro__actions">
        {isCompleted ? (
          <Button
            variant="primary"
            size="lg"
            onClick={onViewResult}
            id="assessment-view-results-btn"
          >
            View Assessment Results
          </Button>
        ) : isInProgress ? (
          <Button
            variant="primary"
            size="lg"
            onClick={onContinue}
            id="assessment-continue-btn"
          >
            Continue Assessment (Question {currentQuestionIndex} of {totalQuestions})
          </Button>
        ) : (
          <Button
            variant="primary"
            size="lg"
            onClick={onStart}
            disabled={isStarting}
            id="assessment-start-btn"
          >
            {isStarting ? 'Starting Assessment...' : 'Start Assessment'}
          </Button>
        )}
      </div>
    </div>
  );
}
