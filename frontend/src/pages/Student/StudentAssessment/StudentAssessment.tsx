import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router';
import {
  getProject,
  getAssessmentStatus,
  startAssessment,
  getAssessmentQuestion,
  submitAssessmentAnswer,
  completeAssessment,
  getAssessmentResult,
} from '@/lib/api';
import type {
  ProjectResponse,
  AssessmentSessionStatus,
  AssessmentQuestion,
  AssessmentAnswer,
  AssessmentResultResponse,
} from '@/lib/api/types';
import {
  AssessmentHeader,
  AssessmentIntro,
  AssessmentQuestionCard,
  AssessmentCompletionCard,
  AssessmentResultView,
  AssessmentLoading,
  AssessmentError,
} from './components';
import type { AssessmentViewMode } from './types';
import './StudentAssessment.css';

export function StudentAssessment() {
  const { projectId } = useParams<{ projectId: string }>();

  const [project, setProject] = useState<ProjectResponse | null>(null);
  const [sessionStatus, setSessionStatus] = useState<AssessmentSessionStatus | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<AssessmentQuestion | null>(null);
  const [persistedAnswer, setPersistedAnswer] = useState<AssessmentAnswer | null>(null);
  const [result, setResult] = useState<AssessmentResultResponse | null>(null);

  const [viewMode, setViewMode] = useState<AssessmentViewMode>('INTRO');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isStarting, setIsStarting] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isCompleting, setIsCompleting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load question and persisted answer for a specific question index
  const loadQuestionByIndex = useCallback(
    async (pid: string, qIndex: number) => {
      try {
        setIsLoading(true);
        setError(null);
        const { question, answer } = await getAssessmentQuestion(pid, qIndex);
        setCurrentQuestion(question);
        setPersistedAnswer(answer);
        setViewMode('QUESTION');
      } catch (err: any) {
        setError(err.message || `Failed to load question ${qIndex}.`);
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  // Initial data loading: project details + assessment status
  const initializeAssessment = useCallback(async () => {
    if (!projectId) {
      setError('Project ID is required.');
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // Fetch project details and assessment status concurrently
      const [projectData, statusData] = await Promise.all([
        getProject(projectId),
        getAssessmentStatus(projectId),
      ]);

      setProject(projectData);
      setSessionStatus(statusData);

      if (statusData.status === 'COMPLETED') {
        const resultData = await getAssessmentResult(projectId);
        setResult(resultData);
        setViewMode('RESULT');
      } else if (statusData.status === 'IN_PROGRESS') {
        // If in progress, check if all questions are answered
        const qIndex = statusData.current_question_index || 1;
        if (statusData.answered_count >= statusData.total_questions) {
          setViewMode('COMPLETION');
        } else {
          await loadQuestionByIndex(projectId, qIndex);
        }
      } else {
        // NOT_STARTED -> present S07 Intro
        setViewMode('INTRO');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to initialize assessment.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId, loadQuestionByIndex]);

  useEffect(() => {
    initializeAssessment();
  }, [initializeAssessment]);

  // S07: Start new assessment
  const handleStart = async () => {
    if (!projectId || isStarting) return;
    try {
      setIsStarting(true);
      setError(null);
      const startData = await startAssessment(projectId);
      setSessionStatus(startData.session);
      setCurrentQuestion(startData.current_question);
      setPersistedAnswer(null);
      setViewMode('QUESTION');
    } catch (err: any) {
      setError(err.message || 'Failed to start assessment.');
    } finally {
      setIsStarting(false);
    }
  };

  // S07: Continue in-progress assessment
  const handleContinue = async () => {
    if (!projectId || !sessionStatus) return;
    if (sessionStatus.answered_count >= sessionStatus.total_questions) {
      setViewMode('COMPLETION');
    } else {
      const qIndex = sessionStatus.current_question_index || 1;
      await loadQuestionByIndex(projectId, qIndex);
    }
  };

  // S07 / S06: View already completed results
  const handleViewResult = async () => {
    if (!projectId) return;
    try {
      setIsLoading(true);
      const resultData = await getAssessmentResult(projectId);
      setResult(resultData);
      setViewMode('RESULT');
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve assessment result.');
    } finally {
      setIsLoading(false);
    }
  };

  // S08 / S09: Submit answer
  const handleAnswerSubmit = async (payload: {
    questionId: string;
    questionIndex: number;
    selectedOption?: string;
    textResponse?: string;
  }): Promise<boolean> => {
    if (!projectId) return false;
    try {
      setIsSubmitting(true);
      const response = await submitAssessmentAnswer(projectId, {
        question_index: payload.questionIndex,
        selected_option: payload.selectedOption,
        text_response: payload.textResponse,
      });

      // Update session status state
      setSessionStatus((prev) =>
        prev
          ? {
              ...prev,
              current_question_index: response.current_question_index,
              answered_count: response.answered_count,
              total_questions: response.total_questions,
            }
          : prev,
      );

      // Advance to next question or completion
      const total = response.total_questions || sessionStatus?.total_questions || 15;
      if (response.next_question_index && response.next_question_index <= total) {
        await loadQuestionByIndex(projectId, response.next_question_index);
      } else if (response.is_complete_eligible || payload.questionIndex >= total) {
        setViewMode('COMPLETION');
      }

      return true;
    } catch (err: any) {
      setError(err.message || 'Failed to persist answer.');
      return false;
    } finally {
      setIsSubmitting(false);
    }
  };

  // Previous question navigation
  const handlePreviousQuestion = async () => {
    if (!projectId || !currentQuestion || currentQuestion.order_index <= 1) return;
    await loadQuestionByIndex(projectId, currentQuestion.order_index - 1);
  };

  // Review questions from completion card
  const handleReviewQuestions = async () => {
    if (!projectId) return;
    const targetIndex = sessionStatus?.total_questions || 15;
    await loadQuestionByIndex(projectId, targetIndex);
  };

  // S10: Finalize and complete assessment
  const handleCompleteAssessment = async () => {
    if (!projectId || isCompleting) return;
    try {
      setIsCompleting(true);
      setError(null);
      const resultData = await completeAssessment(projectId);
      setResult(resultData);
      setSessionStatus((prev) =>
        prev
          ? {
              ...prev,
              status: 'COMPLETED',
            }
          : null,
      );
      setViewMode('RESULT');
    } catch (err: any) {
      setError(err.message || 'Failed to complete assessment.');
    } finally {
      setIsCompleting(false);
    }
  };

  if (isLoading && !currentQuestion && !result && viewMode !== 'INTRO') {
    return <AssessmentLoading />;
  }

  if (error && !currentQuestion && !result && !sessionStatus) {
    return (
      <AssessmentError
        projectId={projectId || ''}
        error={error}
        onRetry={initializeAssessment}
      />
    );
  }

  const projectName = project?.name || 'Project';
  const currentIndex = currentQuestion?.order_index || sessionStatus?.current_question_index || 1;
  const totalCount = sessionStatus?.total_questions || 15;

  return (
    <div className="gf-assessment" id="student-assessment-container">
      <AssessmentHeader
        projectId={projectId || ''}
        projectName={projectName}
        viewMode={viewMode}
        status={sessionStatus?.status || null}
        currentQuestionIndex={currentIndex}
        totalQuestions={totalCount}
        readinessTier={result?.readiness_tier}
      />

      <main id="assessment-main-content">
        {viewMode === 'INTRO' && (
          <AssessmentIntro
            project={project}
            status={sessionStatus?.status || null}
            currentQuestionIndex={sessionStatus?.current_question_index || 1}
            totalQuestions={sessionStatus?.total_questions || 15}
            isStarting={isStarting}
            onStart={handleStart}
            onContinue={handleContinue}
            onViewResult={handleViewResult}
          />
        )}

        {viewMode === 'QUESTION' && currentQuestion && (
          <AssessmentQuestionCard
            question={currentQuestion}
            totalQuestions={totalCount}
            persistedAnswer={persistedAnswer}
            isSubmitting={isSubmitting}
            onAnswerSubmit={handleAnswerSubmit}
            onPrevious={handlePreviousQuestion}
            canGoPrevious={currentQuestion.order_index > 1}
            isLastQuestion={currentQuestion.order_index === totalCount}
          />
        )}

        {viewMode === 'COMPLETION' && (
          <AssessmentCompletionCard
            totalQuestions={totalCount}
            isCompleting={isCompleting}
            onComplete={handleCompleteAssessment}
            onReviewQuestions={handleReviewQuestions}
            error={error}
          />
        )}

        {viewMode === 'RESULT' && result && (
          <AssessmentResultView projectId={projectId || ''} result={result} />
        )}
      </main>
    </div>
  );
}
