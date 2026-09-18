interface ProjectCreateErrorProps {
  message: string;
}

export function ProjectCreateError({ message }: ProjectCreateErrorProps) {
  return (
    <div
      className="gf-project-create-error"
      role="alert"
      aria-live="assertive"
    >
      <div className="gf-project-create-error__icon" aria-hidden="true">
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>
      <div className="gf-project-create-error__content">
        <p className="gf-project-create-error__title">Your project couldn't be created</p>
        <p className="gf-project-create-error__desc">{message}</p>
      </div>
    </div>
  );
}
