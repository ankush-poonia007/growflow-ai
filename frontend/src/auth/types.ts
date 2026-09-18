import type { Session, User as SupabaseUser } from '@supabase/supabase-js';

/**
 * Deterministic authentication statuses.
 * - INITIALIZING: Initial session restoration or verification in progress.
 * - AUTHENTICATED: Active session confirmed and identity established.
 * - UNAUTHENTICATED: No valid session exists.
 * - ERROR: Session initialization or unrecoverable auth bootstrap failed.
 */
export type AuthStatus = 'INITIALIZING' | 'AUTHENTICATED' | 'UNAUTHENTICATED' | 'ERROR';

/**
 * Canonical GrowFlow application roles enforced by backend.
 */
export type UserRole = 'STUDENT' | 'MENTOR' | 'ADMIN';

/**
 * Canonical account lifecycle statuses enforced by backend.
 */
export type AccountStatus = 'ACTIVE' | 'INACTIVE' | 'SUSPENDED';

/**
 * GrowFlow authenticated user profile resolved authoritatively by backend (/api/v1/auth/me).
 */
export interface GrowFlowUser {
  id: string;
  email: string;
  role: UserRole | null;
  status: AccountStatus | null;
  fullName?: string;
  avatarUrl?: string;
}

/**
 * Centralized authentication state.
 */
export interface AuthState {
  status: AuthStatus;
  session: Session | null;
  supabaseUser: SupabaseUser | null;
  user: GrowFlowUser | null;
  error: string | null;
  isRoleResolving: boolean;
}

export interface SignInCredentials {
  email: string;
  password: string;
}

export interface AuthResult {
  success: boolean;
  error?: string;
  errorCode?: string;
  user?: GrowFlowUser | null;
}

export interface AuthContextValue extends AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  signIn: (credentials: SignInCredentials) => Promise<AuthResult>;
  signOut: () => Promise<void>;
  retryAuth: () => Promise<void>;
  refreshAuthorization: () => Promise<void>;
}
