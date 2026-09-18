import { useState, useEffect } from 'react';
import { Button } from '@/components/ui';
import type { AssessmentQuestion, AssessmentAnswer } from '@/lib/api/types';
import { AdaptiveIndicator } from './AdaptiveIndicator';

interface AssessmentQuestionCardProps {
  question: AssessmentQuestion;
  totalQuestions?: number;
  persistedAnswer: AssessmentAnswer | null;
  isSubmitting: boolean;
  onAnswerSubmit: (payload: {
    questionId: string;
    questionIndex: number;
    selectedOption?: string;
    textResponse?: string;
  }) => Promise<boolean>;
  onPrevious: () => void;
  canGoPrevious: boolean;
  isLastQuestion: boolean;
}

export function AssessmentQuestionCard({
  question,
  totalQuestions = 15,
  persistedAnswer,
  isSubmitting,
  onAnswerSubmit,
  onPrevious,
  canGoPrevious,
  isLastQuestion,
}: AssessmentQuestionCardProps) {
  const [selectedOption, setSelectedOption] = useState<string>('');
  const [textResponse, setTextResponse] = useState<string>('');
  const [validationError, setValidationError] = useState<string | null>(null);

  // Sync state whenever question or persistedAnswer changes
  useEffect(() => {
    setSelectedOption(persistedAnswer?.selected_option || '');
    setTextResponse(persistedAnswer?.text_response || '');
    setValidationError(null);
  }, [question.id, question.order_index, persistedAnswer]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    // Validate based on question type
    if (question.question_type === 'MULTIPLE_CHOICE') {
      if (!selectedOption || selectedOption.trim() === '') {
        setValidationError('Please select an option before proceeding.');
        return;
      }
    } else if (question.question_type === 'TEXT') {
      if (!textResponse || textResponse.trim().length < 5) {
        setValidationError('Please provide a substantive answer (at least 5 characters).');
        return;
      }
    }

    const success = await onAnswerSubmit({
      questionId: question.id,
      questionIndex: question.order_index,
      selectedOption: question.question_type === 'MULTIPLE_CHOICE' ? selectedOption : undefined,
      textResponse: question.question_type === 'TEXT' ? textResponse : undefined,
    });

    if (!success) {
      setValidationError('Failed to save your answer. Please try again.');
    }
  };

  return (
    <div className="gf-question-card" id={`question-card-${question.order_index}`}>
      {/* Category and Question Count Meta Bar */}
      <div className="gf-question-card__meta-bar">
        <span className="gf-question-card__category">{question.category}</span>
        <span className="gf-question-card__order-badge">
          Question {question.order_index} of {totalQuestions}
        </span>
      </div>

      {/* S09 Adaptive Context Indicator */}
      {question.is_adaptive && (
        <AdaptiveIndicator contextBadge={question.context_badge || undefined} />
      )}

      {/* Question Prompt */}
      <div className="gf-question-card__prompt-wrap">
        <h2 className="gf-question-card__question-text">{question.question_text}</h2>
        {question.help_text && (
          <p className="gf-question-card__help-text">{question.help_text}</p>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} noValidate>
        {question.question_type === 'MULTIPLE_CHOICE' && question.options && (
          <fieldset className="gf-question-options" aria-label={question.question_text}>
            <legend className="sr-only">Select one option</legend>
            {question.options.map((opt) => {
              const isSelected = selectedOption === opt.value;
              return (
                <label
                  key={opt.value}
                  htmlFor={`option-${opt.value}`}
                  className={`gf-question-option ${isSelected ? 'gf-question-option--selected' : ''}`}
                >
                  <input
                    type="radio"
                    id={`option-${opt.value}`}
                    name={`question-${question.order_index}`}
                    value={opt.value}
                    checked={isSelected}
                    onChange={() => {
                      setSelectedOption(opt.value);
                      setValidationError(null);
                    }}
                    disabled={isSubmitting}
                  />
                  <div className="gf-question-option__content">
                    <span className="gf-question-option__label">{opt.label}</span>
                    {opt.description && (
                      <span className="gf-question-option__desc">{opt.description}</span>
                    )}
                  </div>
                </label>
              );
            })}
          </fieldset>
        )}

        {question.question_type === 'TEXT' && (
          <div className="gf-question-text-input">
            <label htmlFor={`text-response-${question.order_index}`} className="sr-only">
              Your architectural answer
            </label>
            <textarea
              id={`text-response-${question.order_index}`}
              className="gf-question-textarea"
              placeholder="Describe your architectural approach, key components, and trade-offs..."
              value={textResponse}
              onChange={(e) => {
                setTextResponse(e.target.value);
                setValidationError(null);
              }}
              disabled={isSubmitting}
              rows={5}
            />
          </div>
        )}

        {/* Validation Error Message */}
        {validationError && (
          <p className="gf-question-card__error-msg" role="alert" style={{ marginTop: '0.75rem' }}>
            {validationError}
          </p>
        )}

        {/* Footer Navigation Controls */}
        <div className="gf-question-card__footer">
          <Button
            type="button"
            variant="secondary"
            size="md"
            onClick={onPrevious}
            disabled={!canGoPrevious || isSubmitting}
            id="question-prev-btn"
          >
            ← Previous
          </Button>

          <div className="gf-question-card__nav-group">
            <Button
              type="submit"
              variant="primary"
              size="md"
              disabled={isSubmitting}
              id="question-submit-btn"
            >
              {isSubmitting
                ? 'Saving Answer...'
                : isLastQuestion
                ? 'Save & Review Completion →'
                : 'Save & Next →'}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}
