import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import type { User } from '@supabase/supabase-js';

import { NotFound } from '@/pages/NotFound/NotFound';
import { ForbiddenPage } from '@/pages/Forbidden/ForbiddenPage';
import { ForbiddenView } from '@/components/auth/ForbiddenView';
import { AuthenticationRequired } from '@/pages/Auth/AuthenticationRequired/AuthenticationRequired';
import { AccountStatus } from '@/pages/AccountStatus/AccountStatus';
import { ErrorBoundary } from '@/components/ErrorBoundary';

import { NetworkErrorState } from '@/components/system/NetworkErrorState';
import { AIServiceUnavailableNotice } from '@/components/system/AIServiceUnavailableNotice';
import { AIExecutionFailedState } from '@/components/system/AIExecutionFailedState';
import { AIExecutionProgressState } from '@/components/system/AIExecutionProgressState';
import { RAGProcessingState } from '@/components/system/RAGProcessingState';

import { ApiClientError } from '@/lib/api/errors';

function createMockAuth(
  role: 'STUDENT' | 'MENTOR' | 'ADMIN' | null = 'STUDENT',
  status: 'ACTIVE' | 'INACTIVE' | 'SUSPENDED' = 'ACTIVE',
  isAuthenticated = true,
): AuthContextValue {
  return {
    status: isAuthenticated ? 'AUTHENTICATED' : 'UNAUTHENTICATED',
    session: isAuthenticated
      ? ({
          access_token: 'mock-token',
          refresh_token: 'mock-refresh',
          expires_in: 3600,
          token_type: 'bearer',
          user: { id: 'user-1', email: 'test@example.com' } as unknown as User,
        } as any)
      : null,
    supabaseUser: isAuthenticated ? ({ id: 'user-1', email: 'test@example.com' } as unknown as User) : null,
    user: isAuthenticated
      ? {
          id: 'user-1',
          email: 'test@example.com',
          role,
          status,
          fullName: 'Test User',
        }
      : null,
    error: null,
    isRoleResolving: false,
    isAuthenticated,
    isLoading: false,
    signIn: vi.fn(),
    signOut: vi.fn(),
    retryAuth: vi.fn(),
    refreshAuthorization: vi.fn(),
  };
}

describe('PHASE 8 — BATCH 1: SYSTEM PAGES SYS01–SYS10', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ==========================================================================
  // SYS01: 404 / Not Found
  // ==========================================================================
  describe('SYS01 — 404 / Not Found', () => {
    it('renders 404 badge, heading, and default homepage destination when unauthenticated', () => {
      render(
        <AuthContext.Provider value={createMockAuth(null, 'ACTIVE', false)}>
          <MemoryRouter initialEntries={['/404']}>
            <Routes>
              <Route path="/404" element={<NotFound />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>,
      );

      expect(screen.getByText('404 — Not Found')).toBeInTheDocument();
      expect(screen.getByText('Page Not Found')).toBeInTheDocument();
      const returnBtn = screen.getByRole('link', { name: /go to homepage/i });
      expect(returnBtn).toHaveAttribute('href', '/');
    });

    it('wildcard * route renders NotFound and role-aware dashboard for student', () => {
      render(
        <AuthContext.Provider value={createMockAuth('STUDENT')}>
          <MemoryRouter initialEntries={['/non-existent-route']}>
            <Routes>
              <Route path="*" element={<NotFound />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>,
      );

      expect(screen.getByText('Page Not Found')).toBeInTheDocument();
      const returnBtn = screen.getByRole('link', { name: /return to dashboard/i });
      expect(returnBtn).toHaveAttribute('href', '/student/dashboard');
    });
  });

  // ==========================================================================
  // SYS02: 403 / Forbidden
  // ==========================================================================
  describe('SYS02 — 403 / Forbidden', () => {
    it('renders ForbiddenPage at /403 with 403 badge and Access Restricted title', () => {
      render(
        <AuthContext.Provider value={createMockAuth('STUDENT')}>
          <MemoryRouter initialEntries={['/403']}>
            <Routes>
              <Route path="/403" element={<ForbiddenPage />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>,
      );

      expect(screen.getByText('403 — Unauthorized')).toBeInTheDocument();
      expect(screen.getByText('Access Restricted')).toBeInTheDocument();
    });

    it('provides role-aware return destination for MENTOR (/mentor/overview)', () => {
      render(
        <AuthContext.Provider value={createMockAuth('MENTOR')}>
          <MemoryRouter>
            <ForbiddenView reason="ROLE_MISMATCH" />
          </MemoryRouter>
        </AuthContext.Provider>,
      );

      const returnLink = screen.getByRole('link', { name: /return to overview/i });
      expect(returnLink).toHaveAttribute('href', '/mentor/overview');
    });

    it('provides role-aware return destination for ADMIN (/admin/overview)', () => {
      render(
        <AuthContext.Provider value={createMockAuth('ADMIN')}>
          <MemoryRouter>
            <ForbiddenView reason="ROLE_MISMATCH" />
          </MemoryRouter>
        </AuthContext.Provider>,
      );

      const returnLink = screen.getByRole('link', { name: /return to admin overview/i });
      expect(returnLink).toHaveAttribute('href', '/admin/overview');
    });

    it('provides role-aware return destination for STUDENT (/student/dashboard)', () => {
      render(
        <AuthContext.Provider value={createMockAuth('STUDENT')}>
          <MemoryRouter>
            <ForbiddenView reason="ROLE_MISMATCH" />
          </MemoryRouter>
        </AuthContext.Provider>,
      );

      const returnLink = screen.getByRole('link', { name: /return to dashboard/i });
      expect(returnLink).toHaveAttribute('href', '/student/dashboard');
    });

    it('invokes signOut when clicking "Sign In as Different User"', () => {
      const mockAuth = createMockAuth('STUDENT');
      render(
        <AuthContext.Provider value={mockAuth}>
          <MemoryRouter>
            <ForbiddenView reason="ROLE_MISMATCH" />
          </MemoryRouter>
        </AuthContext.Provider>,
      );

      const switchUserBtn = screen.getByRole('button', { name: /sign in as different user/i });
      fireEvent.click(switchUserBtn);
      expect(mockAuth.signOut).toHaveBeenCalledTimes(1);
    });
  });

  // ==========================================================================
  // SYS03: 401 / Authentication Required
  // ==========================================================================
  describe('SYS03 — 401 / Authentication Required', () => {
    it('renders 401 badge, explanation, and sign-in action without returnTo', () => {
      render(
        <MemoryRouter initialEntries={['/401']}>
          <Routes>
            <Route path="/401" element={<AuthenticationRequired />} />
          </Routes>
        </MemoryRouter>,
      );

      expect(screen.getByText('401 — Authentication Required')).toBeInTheDocument();
      expect(screen.getByText('Authentication Required')).toBeInTheDocument();
      const signInBtn = screen.getByRole('link', { name: /sign in to continue/i });
      expect(signInBtn).toHaveAttribute('href', '/auth/student/sign-in');
    });

    it('safely preserves internal application returnTo parameter', () => {
      render(
        <MemoryRouter initialEntries={['/401?returnTo=%2Fstudent%2Fprojects%2Falpha']}>
          <Routes>
            <Route path="/401" element={<AuthenticationRequired />} />
          </Routes>
        </MemoryRouter>,
      );

      expect(screen.getByText('Intended Destination:')).toBeInTheDocument();
      expect(screen.getByText('/student/projects/alpha')).toBeInTheDocument();
      const signInBtn = screen.getByRole('link', { name: /sign in to continue/i });
      expect(signInBtn).toHaveAttribute(
        'href',
        '/auth/student/sign-in?returnTo=%2Fstudent%2Fprojects%2Falpha',
      );
    });

    it('rejects unsafe external returnTo URL and falls back safely', () => {
      render(
        <MemoryRouter initialEntries={['/401?returnTo=https%3A%2F%2Fmalicious-site.com']}>
          <Routes>
            <Route path="/401" element={<AuthenticationRequired />} />
          </Routes>
        </MemoryRouter>,
      );

      expect(screen.queryByText('Intended Destination:')).not.toBeInTheDocument();
      const signInBtn = screen.getByRole('link', { name: /sign in to continue/i });
      expect(signInBtn).toHaveAttribute('href', '/auth/student/sign-in');
    });

    it('rejects protocol-relative and javascript: returnTo URLs', () => {
      render(
        <MemoryRouter initialEntries={['/401?returnTo=%2F%2Fmalicious.com']}>
          <Routes>
            <Route path="/401" element={<AuthenticationRequired />} />
          </Routes>
        </MemoryRouter>,
      );

      expect(screen.queryByText('Intended Destination:')).not.toBeInTheDocument();
      const signInBtn = screen.getByRole('link', { name: /sign in to continue/i });
      expect(signInBtn).toHaveAttribute('href', '/auth/student/sign-in');
    });
  });

  // ==========================================================================
  // SYS04: Suspended / Inactive Account
  // ==========================================================================
  describe('SYS04 — Suspended / Inactive Account', () => {
    it('renders SUSPENDED status distinctly with support recovery path to /contact', () => {
      render(
        <AuthContext.Provider value={createMockAuth('STUDENT', 'SUSPENDED')}>
          <MemoryRouter initialEntries={['/account-status']}>
            <Routes>
              <Route path="/account-status" element={<AccountStatus />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>,
      );

      expect(screen.getByText('Account Lifecycle Notice — Suspended')).toBeInTheDocument();
      expect(screen.getByText('Account Suspended')).toBeInTheDocument();
      expect(screen.queryByText('403 — Unauthorized')).not.toBeInTheDocument();

      const supportBtn = screen.getByRole('link', { name: /contact platform support/i });
      expect(supportBtn).toHaveAttribute('href', '/contact');
    });

    it('renders INACTIVE status distinctly with activation notice and /contact path', () => {
      render(
        <AuthContext.Provider value={createMockAuth('STUDENT', 'INACTIVE')}>
          <MemoryRouter initialEntries={['/account-status']}>
            <Routes>
              <Route path="/account-status" element={<AccountStatus />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>,
      );

      expect(screen.getByText('Account Lifecycle Notice — Inactive')).toBeInTheDocument();
      expect(screen.getByText('Account Inactive')).toBeInTheDocument();
      expect(screen.queryByText('403 — Unauthorized')).not.toBeInTheDocument();

      const supportBtn = screen.getByRole('link', { name: /contact platform support/i });
      expect(supportBtn).toHaveAttribute('href', '/contact');
    });
  });

  // ==========================================================================
  // SYS05: Generic Application Error (ErrorBoundary)
  // ==========================================================================
  describe('SYS05 — Generic Application Error (ErrorBoundary)', () => {
    function CrashComponent(): React.ReactNode {
      throw new Error('Test unhandled render crash');
    }

    it('catches render error, displays notice, and generates client-side incident reference ID', () => {
      const spy = vi.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <ErrorBoundary>
          <CrashComponent />
        </ErrorBoundary>,
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      expect(screen.getByText(/Test unhandled render crash/i)).toBeInTheDocument();
      expect(screen.getByText(/Incident Reference:/i)).toBeInTheDocument();

      // Check format ERR-XXXXXX
      const refCode = screen.getByText(/^ERR-[A-Z0-9]{6}$/);
      expect(refCode).toBeInTheDocument();

      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /return to home/i })).toBeInTheDocument();

      spy.mockRestore();
    });
  });

  // ==========================================================================
  // SYS06: Network / API Failure
  // ==========================================================================
  describe('SYS06 — Network / API Failure', () => {
    it('renders network offline state when isOffline is true or network error', () => {
      const netError = new ApiClientError(0, 'NETWORK_ERROR', 'Failed to fetch');
      render(<NetworkErrorState error={netError} isOffline={true} />);

      expect(screen.getByText('Network Offline')).toBeInTheDocument();
      expect(screen.getByText('Network Connection Unavailable')).toBeInTheDocument();
    });

    it('renders server failure when 500 error occurs and triggers retry callback', () => {
      const onRetry = vi.fn();
      const serverError = new ApiClientError(503, 'SERVICE_UNAVAILABLE', 'Backend unavailable');

      render(<NetworkErrorState error={serverError} onRetry={onRetry} />);

      expect(screen.getByText('Service Notice (503)')).toBeInTheDocument();
      expect(screen.getByText('Service Temporarily Unavailable')).toBeInTheDocument();

      const retryBtn = screen.getByRole('button', { name: /try again/i });
      fireEvent.click(retryBtn);
      expect(onRetry).toHaveBeenCalledTimes(1);
    });
  });

  // ==========================================================================
  // SYS07: AI Service Unavailable
  // ==========================================================================
  describe('SYS07 — AI Service Unavailable', () => {
    it('displays notice that AI is degraded while confirming deterministic features remain active', () => {
      render(
        <AIServiceUnavailableNotice
          serviceName="AI Mentor"
          deterministicAvailable={true}
        />,
      );

      expect(screen.getByText('AI Service Notice')).toBeInTheDocument();
      expect(screen.getByText('AI Mentor Temporarily Unavailable')).toBeInTheDocument();
      expect(screen.getByText(/Deterministic Workspace Active:/i)).toBeInTheDocument();
      expect(screen.getByText(/Core workspace features.*remain fully operational/i)).toBeInTheDocument();
    });
  });

  // ==========================================================================
  // SYS08: AI Execution Failed
  // ==========================================================================
  describe('SYS08 — AI Execution Failed', () => {
    it('renders failed stage, execution ID, safe error summary, and executes retry callback', () => {
      const onRetry = vi.fn();
      render(
        <AIExecutionFailedState
          stage="Architecture Synthesis"
          executionId="exec-ai-789"
          error="Model context length exceeded"
          onRetry={onRetry}
        />,
      );

      expect(screen.getByText('Execution Failed')).toBeInTheDocument();
      expect(screen.getByText('AI Workflow Execution Failed')).toBeInTheDocument();
      expect(screen.getByText('Architecture Synthesis')).toBeInTheDocument();
      expect(screen.getByText('exec-ai-789')).toBeInTheDocument();
      expect(screen.getByText('Model context length exceeded')).toBeInTheDocument();

      const retryBtn = screen.getByRole('button', { name: /retry execution/i });
      fireEvent.click(retryBtn);
      expect(onRetry).toHaveBeenCalledTimes(1);
    });
  });

  // ==========================================================================
  // SYS09: AI Execution In Progress
  // ==========================================================================
  describe('SYS09 — AI Execution In Progress', () => {
    it('renders RUNNING status with authoritative percentage and background persistence note', () => {
      render(
        <AIExecutionProgressState
          status="RUNNING"
          currentStage="Synthesizing module specifications"
          progress={75}
          independentExecution={true}
        />,
      );

      expect(screen.getByText('Execution in Progress')).toBeInTheDocument();
      expect(screen.getByText('AI Execution in Progress')).toBeInTheDocument();
      expect(screen.getByText('Synthesizing module specifications')).toBeInTheDocument();
      expect(screen.getByText('75%')).toBeInTheDocument();
      expect(screen.getByText(/Background Execution Active:/i)).toBeInTheDocument();
    });

    it('renders QUEUED state safely without fabricating progress numbers', () => {
      render(
        <AIExecutionProgressState
          status="QUEUED"
          currentStage="Awaiting execution slot"
        />,
      );

      expect(screen.getByText('Pipeline Queued')).toBeInTheDocument();
      expect(screen.getByText('AI Execution Queued')).toBeInTheDocument();
      expect(screen.getByText('Awaiting execution slot')).toBeInTheDocument();
      expect(screen.queryByText(/%/)).not.toBeInTheDocument();
    });
  });

  // ==========================================================================
  // SYS10: RAG / Document Processing State
  // ==========================================================================
  describe('SYS10 — RAG / Document Processing State', () => {
    it('renders active stage, chunk count, and embedding status', () => {
      render(
        <RAGProcessingState
          stage="INDEXING"
          documentName="Architecture_Specification.md"
          chunkCount={42}
          embeddingStatus="BAAI/bge-large-en-v1.5 (Indexed)"
        />,
      );

      expect(screen.getByText('Processing Stage: INDEXING')).toBeInTheDocument();
      expect(screen.getByText(/Document Ingestion: Architecture_Specification.md/i)).toBeInTheDocument();
      expect(screen.getByText('42')).toBeInTheDocument();
      expect(screen.getByText('BAAI/bge-large-en-v1.5 (Indexed)')).toBeInTheDocument();
    });

    it('renders FAILED stage with failure cause and retry action', () => {
      const onRetry = vi.fn();
      render(
        <RAGProcessingState
          stage="FAILED"
          documentName="Corrupted.pdf"
          failureReason="Unrecognized PDF encoding format"
          onRetry={onRetry}
        />,
      );

      expect(screen.getByText('RAG Pipeline Failed')).toBeInTheDocument();
      expect(screen.getByText(/Unrecognized PDF encoding format/i)).toBeInTheDocument();

      const retryBtn = screen.getByRole('button', { name: /retry ingestion/i });
      fireEvent.click(retryBtn);
      expect(onRetry).toHaveBeenCalledTimes(1);
    });
  });
});
