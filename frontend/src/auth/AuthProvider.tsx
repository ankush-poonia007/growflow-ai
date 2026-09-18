import {
  useState,
  useEffect,
  useCallback,
  useRef,
  type ReactNode,
} from 'react';
import type { Session } from '@supabase/supabase-js';
import { supabase } from '@/lib/supabase';
import { API_BASE_URL } from '@/lib/api/client';
import { AuthContext } from './AuthContext';
import type {
  AuthState,
  AuthResult,
  GrowFlowUser,
  SignInCredentials,
  UserRole,
  AccountStatus,
} from './types';

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Resolves application authorization details from backend authoritative endpoint /api/v1/auth/me.
 */
async function fetchUserAuthorization(token: string): Promise<GrowFlowUser | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Unauthenticated or not yet provisioned in application DB
        return null;
      }
      if (response.status === 403) {
        // Account inactive or suspended; parse canonical error response envelope
        try {
          const errData = await response.json();
          const code = errData?.error?.code;
          if (code === 'AUTH_ACCOUNT_SUSPENDED') {
            return {
              id: '',
              email: '',
              role: null,
              status: 'SUSPENDED',
              fullName: '',
            };
          }
          if (code === 'AUTH_ACCOUNT_INACTIVE') {
            return {
              id: '',
              email: '',
              role: null,
              status: 'INACTIVE',
              fullName: '',
            };
          }
          if (errData?.data?.status) {
            return {
              id: errData.data.id || '',
              email: errData.data.email || '',
              role: (errData.data.role as UserRole) || null,
              status: (errData.data.status as AccountStatus) || 'SUSPENDED',
              fullName: errData.data.full_name || '',
            };
          }
        } catch {
          // ignore json parse error
        }
        return null;
      }
      return null;
    }

    const payload = await response.json();
    if (payload.success && payload.data) {
      return {
        id: payload.data.id,
        email: payload.data.email,
        role: payload.data.role as UserRole,
        status: payload.data.status as AccountStatus,
        fullName: payload.data.full_name || '',
      };
    }
    return null;
  } catch (err) {
    // Network or server error; do not throw unhandled exception
    console.warn('[GrowFlow Auth] Failed to fetch backend authorization:', err);
    return null;
  }
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>({
    status: 'INITIALIZING',
    session: null,
    supabaseUser: null,
    user: null,
    error: null,
    isRoleResolving: false,
  });

  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const resolveSessionAndRole = useCallback(async (session: Session | null) => {
    if (!session) {
      if (isMountedRef.current) {
        setState({
          status: 'UNAUTHENTICATED',
          session: null,
          supabaseUser: null,
          user: null,
          error: null,
          isRoleResolving: false,
        });
      }
      return null;
    }

    if (isMountedRef.current) {
      setState((prev) => ({
        ...prev,
        session,
        supabaseUser: session.user,
        isRoleResolving: true,
      }));
    }

    const growFlowUser = await fetchUserAuthorization(session.access_token);

    if (isMountedRef.current) {
      // Backend authorization is authoritative for application roles.
      // If backend authorization returned canonical profile, use it.
      // If backend authorization is temporarily unavailable or not yet provisioned,
      // preserve the authenticated session identity from Supabase (id, email, display name),
      // but DO NOT fabricate or upgrade the user's role (role remains null).
      const resolvedUser: GrowFlowUser | null = growFlowUser ?? {
        id: session.user.id,
        email: session.user.email || '',
        role: null,
        status: null,
        fullName:
          session.user.user_metadata?.full_name ||
          (session.user.user_metadata?.first_name
            ? `${session.user.user_metadata.first_name} ${session.user.user_metadata.last_name || ''}`.trim()
            : ''),
      };

      setState({
        status: 'AUTHENTICATED',
        session,
        supabaseUser: session.user,
        user: resolvedUser,
        error: null,
        isRoleResolving: false,
      });
    }

    return growFlowUser;
  }, []);

  // Initial session restoration & auth listener
  useEffect(() => {
    let isSubscribed = true;

    async function initSession() {
      try {
        const { data, error } = await supabase.auth.getSession();
        if (!isSubscribed) return;

        if (error) {
          console.warn('[GrowFlow Auth] Error restoring session:', error.message);
          setState({
            status: 'ERROR',
            session: null,
            supabaseUser: null,
            user: null,
            error: error.message,
            isRoleResolving: false,
          });
          return;
        }

        await resolveSessionAndRole(data.session);
      } catch (err: unknown) {
        if (!isSubscribed) return;
        const msg = err instanceof Error ? err.message : 'Session initialization failure';
        setState({
          status: 'ERROR',
          session: null,
          supabaseUser: null,
          user: null,
          error: msg,
          isRoleResolving: false,
        });
      }
    }

    initSession();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, newSession) => {
      if (!isSubscribed) return;

      if (event === 'SIGNED_OUT') {
        setState({
          status: 'UNAUTHENTICATED',
          session: null,
          supabaseUser: null,
          user: null,
          error: null,
          isRoleResolving: false,
        });
      } else if (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED' || event === 'USER_UPDATED') {
        await resolveSessionAndRole(newSession);
      }
    });

    return () => {
      isSubscribed = false;
      subscription.unsubscribe();
    };
  }, [resolveSessionAndRole]);

  const signIn = useCallback(
    async ({ email, password }: SignInCredentials): Promise<AuthResult> => {
      try {
        const { data, error } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password,
        });

        if (error) {
          // Map error to safe, user-friendly language without leaking account existence
          let message = 'Sign-in details could not be verified. Check your email and password and try again.';
          const code = error.status ? String(error.status) : error.name;

          if (error.message.toLowerCase().includes('network') || error.message.toLowerCase().includes('fetch')) {
            message = 'Unable to reach GrowFlow right now. Please try again.';
          } else if (error.status === 429) {
            message = 'Too many sign-in attempts. Please wait a few moments and try again.';
          }

          return {
            success: false,
            error: message,
            errorCode: code,
          };
        }

        if (data.session) {
          const resolvedUser = await resolveSessionAndRole(data.session);
          return { success: true, user: resolvedUser };
        }

        return {
          success: false,
          error: 'Something went wrong while signing you in. Please try again.',
        };
      } catch (err: unknown) {
        const isNetwork =
          err instanceof TypeError ||
          (err instanceof Error && err.message.toLowerCase().includes('fetch'));

        return {
          success: false,
          error: isNetwork
            ? 'Unable to reach GrowFlow right now. Please try again.'
            : 'Something went wrong while signing you in. Please try again.',
        };
      }
    },
    [resolveSessionAndRole],
  );

  const signOut = useCallback(async () => {
    try {
      await supabase.auth.signOut();
    } catch (err) {
      console.warn('[GrowFlow Auth] Sign out warning:', err);
    } finally {
      if (isMountedRef.current) {
        setState({
          status: 'UNAUTHENTICATED',
          session: null,
          supabaseUser: null,
          user: null,
          error: null,
          isRoleResolving: false,
        });
      }
    }
  }, []);

  const retryAuth = useCallback(async () => {
    setState((prev) => ({ ...prev, status: 'INITIALIZING', error: null }));
    try {
      const { data, error } = await supabase.auth.getSession();
      if (error) {
        setState({
          status: 'ERROR',
          session: null,
          supabaseUser: null,
          user: null,
          error: error.message,
          isRoleResolving: false,
        });
        return;
      }
      await resolveSessionAndRole(data.session);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Session initialization failure';
      setState({
        status: 'ERROR',
        session: null,
        supabaseUser: null,
        user: null,
        error: msg,
        isRoleResolving: false,
      });
    }
  }, [resolveSessionAndRole]);

  const refreshAuthorization = useCallback(async () => {
    if (state.session) {
      await resolveSessionAndRole(state.session);
    }
  }, [state.session, resolveSessionAndRole]);

  const value = {
    ...state,
    isAuthenticated: state.status === 'AUTHENTICATED' && state.session !== null,
    isLoading: state.status === 'INITIALIZING',
    signIn,
    signOut,
    retryAuth,
    refreshAuthorization,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
