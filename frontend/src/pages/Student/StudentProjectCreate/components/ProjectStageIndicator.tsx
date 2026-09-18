interface ProjectStageIndicatorProps {
  currentStep?: 'define' | 'create' | 'assess';
}

export function ProjectStageIndicator({ currentStep = 'define' }: ProjectStageIndicatorProps) {
  const steps = [
    { number: '01', label: 'Define', status: 'current', hint: 'Detail problem & solution' },
    { number: '02', label: 'Create', status: 'upcoming', hint: 'Commit canonical instance' },
    { number: '03', label: 'Assess', status: 'future', hint: 'Feasibility evaluation' },
  ];

  return (
    <div
      className="gf-stage-indicator"
      role="region"
      aria-label="Build progression orientation"
    >
      <div className="gf-stage-indicator__track">
        {steps.map((step) => {
          const isCurrent =
            (currentStep === 'define' && step.number === '01') ||
            (currentStep === 'create' && step.number === '02') ||
            (currentStep === 'assess' && step.number === '03');

          return (
            <div
              key={step.number}
              className={`gf-stage-indicator__item ${
                isCurrent ? 'gf-stage-indicator__item--active' : ''
              }`}
            >
              <div className="gf-stage-indicator__marker">
                <span className="gf-stage-indicator__num">{step.number}</span>
              </div>
              <div className="gf-stage-indicator__text">
                <span className="gf-stage-indicator__label">{step.label}</span>
                <span className="gf-stage-indicator__hint">{step.hint}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
