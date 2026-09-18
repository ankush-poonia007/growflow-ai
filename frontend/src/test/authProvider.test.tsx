import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import { AuthProvider } from '@/auth/AuthProvider';
import { useAuth } from '@/auth/useAuth';
import { supabase } from '@/lib/supabase';
import { API_BASE_URL } from '@/lib/api/client';
import type { Session, AuthChangeEvent } from '@supabase/supabase-js';

// Helper component to observe AuthContext values
function AuthConsumer() {
  const { status, isAuthenticated, isLoading, user, session, signOut, signIn } = useAuth();
  return (
    <div>
      <div data-testid="status">{status}</div>
      <div data-testid="is-authenticated">{String(isAuthenticated)}</div>
      <div data-testid="is-loading">{String(isLoading)}</div>
      <div data-testid="user-role">{user?.role || 'NONE'}</div>
      <div data-testid="user-status">{user?.status || 'NONE'}</div>
      <div data-testid="user-email">{user?.email || 'NONE'}</div>
      <div data-testid="session-exists">{session ? 'YES' : 'NO'}</div>
      <button onClick={() => void signOut()} data-testid="sign-out-btn">
        Sign Out
      </button>
      <button
        onClick={() => void signIn({ email: 'test@growflow.ai', password: 'password123' })}
        data-testid="sign-in-btn"
      >
        Sign In
      </button>
    </div>
  );
}

describe('AuthProvider & Session Lifecycle', () => {
  let authChangeCallback: ((event: AuthChangeEvent, session: Session | null) => void) | null = null;

  beforeEach(() => {
    vi.restoreAllMocks();
    authChangeCallback = null;

    vi.spyOn(supabase.auth, 'onAuthStateChange').mockImplementation((cb) => {
      authChangeCallback = cb;
      return {
        data: {
          subscription: {
            id: 'test-sub',
            callback: cb,
            unsubscribe: vi.fn(),
          },
        },
      };
    });
  });

  it('initializes to UNAUTHENTICATED when no active session exists', async () => {
    vi.spyOn(supabase.auth, 'getSession').mockResolvedValue({
      data: { session: null },
      error: null,
    });

    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>,
    );

    // Initial render is in INITIALIZING status
    expect(screen.getByTestId('status')).toHaveTextContent('INITIALIZING');
    expect(screen.getByTestId('is-loading')).toHaveTextContent('true');

    // After getSession resolves
    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('UNAUTHENTICATED');
    });

    expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
    expect(screen.getByTestId('is-loading')).toHaveTextContent('false');
    expect(screen.getByTestId('session-exists')).toHaveTextContent('NO');
  });

  it('restores session and resolves authoritative role from backend', async () => {
    const mockSession = {
      access_token: 'valid-jwt-token',
      user: { id: 'user-uuid-1', email: 'student@university.edu' },
    } as unknown as Session;

    vi.spyOn(supabase.auth, 'getSession').mockResolvedValue({
      data: { session: mockSession },
      error: null,
    });

    // Mock backend /api/v1/auth/me response
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        message: 'Authenticated user identity retrieved successfully.',
        data: {
          id: 'user-uuid-1',
          email: 'student@university.edu',
          role: 'STUDENT',
          status: 'ACTIVE',
          full_name: 'Alex Rivera',
        },
      }),
    } as Response);

    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('AUTHENTICATED');
    });

    expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true');
    expect(screen.getByTestId('user-role')).toHaveTextContent('STUDENT');
    expect(screen.getByTestId('user-status')).toHaveTextContent('ACTIVE');
    expect(screen.getByTestId('user-email')).toHaveTextContent('student@university.edu');

    // Verify Bearer token was forwarded to backend
    expect(fetchSpy).toHaveBeenCalledWith(
      `${API_BASE_URL}/api/v1/auth/me`,
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer valid-jwt-token',
        }),
      }),
    );
  });

  it('handles auth state listener SIGNED_OUT event', async () => {
    const mockSession = {
      access_token: 'valid-jwt-token',
      user: { id: 'user-uuid-1', email: 'student@university.edu' },
    } as unknown as Session;

    vi.spyOn(supabase.auth, 'getSession').mockResolvedValue({
      data: { session: mockSession },
      error: null,
    });

    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: {
          id: 'user-uuid-1',
          email: 'student@university.edu',
          role: 'STUDENT',
          status: 'ACTIVE',
        },
      }),
    } as Response);

    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('AUTHENTICATED');
    });

    // Simulate SIGNED_OUT event from Supabase auth listener
    act(() => {
      authChangeCallback?.('SIGNED_OUT', null);
    });

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('UNAUTHENTICATED');
    });
    expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
  });

  it('signOut clears frontend state and calls supabase.auth.signOut', async () => {
    const mockSession = {
      access_token: 'valid-jwt-token',
      user: { id: 'user-uuid-1', email: 'student@university.edu' },
    } as unknown as Session;

    vi.spyOn(supabase.auth, 'getSession').mockResolvedValue({
      data: { session: mockSession },
      error: null,
    });

    const signOutSpy = vi.spyOn(supabase.auth, 'signOut').mockResolvedValue({ error: null });

    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: {
          id: 'user-uuid-1',
          email: 'student@university.edu',
          role: 'STUDENT',
          status: 'ACTIVE',
        },
      }),
    } as Response);

    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('AUTHENTICATED');
    });

    // Click sign out
    act(() => {
      screen.getByTestId('sign-out-btn').click();
    });

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('UNAUTHENTICATED');
    });

    expect(signOutSpy).toHaveBeenCalledTimes(1);
    expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
  });
});
