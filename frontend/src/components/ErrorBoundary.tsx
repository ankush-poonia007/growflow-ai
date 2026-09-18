import { Component, type ErrorInfo, type ReactNode } from 'react';
import { Button } from './ui/Button';
import './ErrorBoundary.css';

function generateIncidentId(): string {
  const chars = '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ';
  let rand = '';
  for (let i = 0; i < 6; i++) {
    rand += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return `ERR-${rand}`;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  showDetails: boolean;
  referenceId: string | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
      referenceId: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
      referenceId: generateIncidentId(),
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({ errorInfo });
    // In production, send to telemetry/logging service
    console.error('[ErrorBoundary caught error]', error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
      referenceId: null,
    });
  };

  handleGoHome = (): void => {
    window.location.href = '/';
  };

  toggleDetails = (): void => {
    this.setState((prev) => ({ showDetails: !prev.showDetails }));
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const errorMessage = this.state.error?.message || 'An unexpected application error occurred.';

      return (
        <div className="gf-error-boundary" role="alert" aria-live="assertive">
          <div className="gf-error-boundary__container">
            <div className="gf-error-boundary__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </div>

            <div className="gf-error-boundary__header">
              <span className="gf-error-boundary__badge">Application Notice</span>
              <h1 className="gf-error-boundary__title">Something went wrong</h1>
              <p className="gf-error-boundary__description">
                GrowFlow encountered an unexpected issue while rendering this view. Your session data remains safe.
              </p>
            </div>

            {this.state.referenceId && (
              <div className="gf-error-boundary__reference">
                <span className="gf-error-boundary__reference-label">Incident Reference:</span>
                <code className="gf-error-boundary__reference-code">{this.state.referenceId}</code>
              </div>
            )}

            <div className="gf-error-boundary__error-banner">
              <span className="gf-error-boundary__error-label">Error Details:</span>
              <code className="gf-error-boundary__error-msg">{errorMessage}</code>
            </div>

            <div className="gf-error-boundary__actions">
              <Button
                variant="primary"
                onClick={this.handleReset}
                className="gf-error-boundary__btn"
              >
                Try Again
              </Button>
              <Button
                variant="secondary"
                onClick={this.handleGoHome}
                className="gf-error-boundary__btn"
              >
                Return to Home
              </Button>
              {import.meta.env.DEV && (
                <Button
                  variant="tertiary"
                  onClick={this.toggleDetails}
                  className="gf-error-boundary__btn"
                >
                  {this.state.showDetails ? 'Hide Diagnostics' : 'View Diagnostics'}
                </Button>
              )}
            </div>

            {import.meta.env.DEV && this.state.showDetails && (
              <div className="gf-error-boundary__diagnostics">
                <h2 className="gf-error-boundary__diagnostics-heading">Stack Trace & Component Stack</h2>
                <pre className="gf-error-boundary__stack">
                  {this.state.error?.stack || 'No stack trace available.'}
                  {'\n\nComponent Stack:\n'}
                  {this.state.errorInfo?.componentStack || 'No component stack available.'}
                </pre>
              </div>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
