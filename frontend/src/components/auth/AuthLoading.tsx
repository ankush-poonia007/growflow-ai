import './AuthLoading.css';

interface AuthLoadingProps {
  message?: string;
}

export function AuthLoading({ message = 'Verifying GrowFlow session...' }: AuthLoadingProps) {
  return (
    <div className="gf-auth-loading" role="status" aria-live="polite">
      <div className="gf-auth-loading__indicator" aria-hidden="true">
        <div className="gf-auth-loading__pulse" />
        <div className="gf-auth-loading__ring" />
      </div>
      <p className="gf-auth-loading__text">{message}</p>
    </div>
  );
}
