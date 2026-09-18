import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, act, renderHook } from '@testing-library/react';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import { EmptyState } from '@/components/ui/EmptyState';
import { useOnlineStatus } from '@/hooks/useOnlineStatus';
import { OfflineBanner } from '@/components/system/OfflineBanner';
import { ApiClientError } from '@/lib/api/errors';

describe('Global State UI Primitives', () => {
  describe('LoadingSpinner', () => {
    it('renders with accessible status semantics and default label', () => {
      render(<LoadingSpinner />);

      const spinner = screen.getByRole('status');
      expect(spinner).toBeInTheDocument();
      expect(spinner).toHaveAttribute('aria-live', 'polite');
      expect(spinner).toHaveAttribute('aria-label', 'Loading...');
      expect(screen.getByText('Loading...')).toHaveClass('gf-loading-spinner__sr-only');
    });

    it('supports custom accessible labels', () => {
      render(<LoadingSpinner label="Fetching project milestones..." />);

      const spinner = screen.getByRole('status');
      expect(spinner).toHaveAttribute('aria-label', 'Fetching project milestones...');
      expect(screen.getByText('Fetching project milestones...')).toBeInTheDocument();
    });

    it('renders sm, md, and lg size variants correctly', () => {
      const { rerender } = render(<LoadingSpinner size="sm" />);
      expect(screen.getByRole('status')).toHaveClass('gf-loading-spinner--sm');

      rerender(<LoadingSpinner size="md" />);
      expect(screen.getByRole('status')).toHaveClass('gf-loading-spinner--md');

      rerender(<LoadingSpinner size="lg" />);
      expect(screen.getByRole('status')).toHaveClass('gf-loading-spinner--lg');
    });

    it('supports inline rendering modifier', () => {
      render(<LoadingSpinner inline size="sm" />);
      expect(screen.getByRole('status')).toHaveClass('gf-loading-spinner--inline');
    });
  });

  describe('InlineErrorState', () => {
    it('renders a string error with role="alert"', () => {
      render(<InlineErrorState error="Custom validation failed." />);

      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
      expect(screen.getByText('Custom validation failed.')).toBeInTheDocument();
    });

    it('formats ApiClientError into user-safe messages without leaking internals', () => {
      // Network Error (status 0)
      const netError = new ApiClientError(0, 'NETWORK_ERROR', 'Failed to fetch');
      const { rerender } = render(<InlineErrorState error={netError} />);
      expect(screen.getByText(/unable to reach growflow services/i)).toBeInTheDocument();

      // Unauthorized (401)
      const authError = new ApiClientError(401, 'AUTH_UNAUTHORIZED', 'Internal token validation failed');
      rerender(<InlineErrorState error={authError} />);
      expect(screen.getByText(/session has expired or requires authentication/i)).toBeInTheDocument();

      // Forbidden (403)
      const forbiddenError = new ApiClientError(403, 'AUTH_FORBIDDEN', 'Access denied to resource');
      rerender(<InlineErrorState error={forbiddenError} />);
      expect(screen.getByText(/do not have permission to access or modify/i)).toBeInTheDocument();

      // Not Found (404)
      const notFoundError = new ApiClientError(404, 'NOT_FOUND', 'Record missing');
      rerender(<InlineErrorState error={notFoundError} />);
      expect(screen.getByText(/requested resource or workspace could not be found/i)).toBeInTheDocument();

      // Rate Limited (429)
      const rateLimitError = new ApiClientError(429, 'RATE_LIMIT_EXCEEDED', 'Too many calls');
      rerender(<InlineErrorState error={rateLimitError} />);
      expect(screen.getByText(/too many requests/i)).toBeInTheDocument();

      // Server Error (500)
      const serverError = new ApiClientError(500, 'SERVER_ERROR', 'Traceback on db.py:42');
      rerender(<InlineErrorState error={serverError} />);
      expect(screen.getByText(/growflow service encountered an unexpected problem/i)).toBeInTheDocument();
      expect(screen.queryByText(/traceback/i)).not.toBeInTheDocument();
    });

    it('renders retry button only when onRetry callback exists and fires callback on click', () => {
      const retryMock = vi.fn();
      const { rerender } = render(
        <InlineErrorState error="Connection timeout." onRetry={retryMock} retryLabel="Try Again" />,
      );

      const retryBtn = screen.getByRole('button', { name: 'Try Again' });
      expect(retryBtn).toBeInTheDocument();

      fireEvent.click(retryBtn);
      expect(retryMock).toHaveBeenCalledTimes(1);

      // Re-render without onRetry
      rerender(<InlineErrorState error="Connection timeout." />);
      expect(screen.queryByRole('button')).not.toBeInTheDocument();
    });

    it('renders custom title and action when provided', () => {
      render(
        <InlineErrorState
          title="Milestone Sync Failed"
          error="Network error"
          action={<button type="button">Dismiss</button>}
        />,
      );

      expect(screen.getByRole('heading', { name: 'Milestone Sync Failed' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Dismiss' })).toBeInTheDocument();
    });
  });

  describe('EmptyState Component', () => {
    it('renders normal mode with standard structure and preserved caller behavior', () => {
      const { container } = render(
        <EmptyState
          title="No Active Roadmaps"
          description="Generate your first roadmap to start building."
          action={<button type="button">Generate Roadmap</button>}
        />,
      );

      expect(screen.getByRole('heading', { level: 3, name: 'No Active Roadmaps' })).toBeInTheDocument();
      expect(screen.getByText('Generate Roadmap')).toBeInTheDocument();
      expect(container.firstChild).not.toHaveClass('gf-empty-state--compact');
    });

    it('supports compact mode appropriate for cards, widgets, and tables', () => {
      const { container } = render(
        <EmptyState
          compact
          title="No Tasks Found"
          description="There are no tasks assigned to this milestone."
        />,
      );

      expect(container.firstChild).toHaveClass('gf-empty-state--compact');
      expect(screen.getByRole('heading', { level: 3, name: 'No Tasks Found' })).toBeInTheDocument();
    });
  });

  describe('useOnlineStatus Hook', () => {
    let addEventListenerSpy: any;
    let removeEventListenerSpy: any;
    let originalNavigatorOnLine: boolean;

    beforeEach(() => {
      originalNavigatorOnLine = navigator.onLine;
      addEventListenerSpy = vi.spyOn(window, 'addEventListener');
      removeEventListenerSpy = vi.spyOn(window, 'removeEventListener');
    });

    afterEach(() => {
      Object.defineProperty(navigator, 'onLine', {
        value: originalNavigatorOnLine,
        configurable: true,
      });
      vi.restoreAllMocks();
    });

    it('initializes from navigator.onLine and reacts to online/offline window events', () => {
      Object.defineProperty(navigator, 'onLine', { value: true, configurable: true });

      const { result, unmount } = renderHook(() => useOnlineStatus());
      expect(result.current).toBe(true);

      // Trigger offline event
      act(() => {
        window.dispatchEvent(new Event('offline'));
      });
      expect(result.current).toBe(false);

      // Trigger online event
      act(() => {
        window.dispatchEvent(new Event('online'));
      });
      expect(result.current).toBe(true);

      expect(addEventListenerSpy).toHaveBeenCalledWith('online', expect.any(Function));
      expect(addEventListenerSpy).toHaveBeenCalledWith('offline', expect.any(Function));

      // Cleanup
      unmount();
      expect(removeEventListenerSpy).toHaveBeenCalledWith('online', expect.any(Function));
      expect(removeEventListenerSpy).toHaveBeenCalledWith('offline', expect.any(Function));
    });
  });

  describe('OfflineBanner Component', () => {
    let originalNavigatorOnLine: boolean;

    beforeEach(() => {
      originalNavigatorOnLine = navigator.onLine;
    });

    afterEach(() => {
      Object.defineProperty(navigator, 'onLine', {
        value: originalNavigatorOnLine,
        configurable: true,
      });
    });

    it('renders null when browser is online', () => {
      Object.defineProperty(navigator, 'onLine', { value: true, configurable: true });
      const { container } = render(<OfflineBanner />);
      expect(container).toBeEmptyDOMElement();
    });

    it('renders calm status banner when browser reports offline', () => {
      Object.defineProperty(navigator, 'onLine', { value: false, configurable: true });
      render(<OfflineBanner />);

      const banner = screen.getByRole('status');
      expect(banner).toBeInTheDocument();
      expect(banner).toHaveAttribute('aria-live', 'polite');
      expect(screen.getByText('Connection Lost')).toBeInTheDocument();
      expect(screen.getByText(/operations and syncing are paused/i)).toBeInTheDocument();
    });

    it('disappears naturally when online event fires', () => {
      Object.defineProperty(navigator, 'onLine', { value: false, configurable: true });
      const { container } = render(<OfflineBanner />);
      expect(screen.getByText('Connection Lost')).toBeInTheDocument();

      act(() => {
        window.dispatchEvent(new Event('online'));
      });

      expect(container).toBeEmptyDOMElement();
    });
  });

  describe('Non-Destructive Scoped Retry Integration', () => {
    it('executes scoped refetch instead of window.location.reload', () => {
      const reloadSpy = vi.fn();
      Object.defineProperty(window, 'location', {
        value: { reload: reloadSpy },
        writable: true,
      });

      const scopedRefetch = vi.fn();

      render(
        <InlineErrorState
          title="Overview Data Unavailable"
          error="Network connection interrupted."
          onRetry={scopedRefetch}
        />,
      );

      const retryBtn = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(retryBtn);

      expect(scopedRefetch).toHaveBeenCalledTimes(1);
      expect(reloadSpy).not.toHaveBeenCalled();
    });
  });
});

