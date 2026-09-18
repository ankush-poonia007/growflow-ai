import { type ReactNode } from 'react';
import { Navigate, useLocation, Outlet } from 'react-router';
import { useAuth } from './useAuth';
import type { UserRole, AccountStatus } from './types';
import { AuthLoading } from '@/components/auth/AuthLoading';
import { ForbiddenView } from '@/components/auth/ForbiddenView';
import { AccountStatus as AccountStatusView } from '@/pages/AccountStatus/AccountStatus';

interface ProtectedRouteProps {
  children?: ReactNode;
  requiredRole?: UserRole;
  requiredStatus?: AccountStatus;
  loginPath?: string;
}

/**
 * Reusable route guard for protected application routes.
 *
 * Rules:
 * 1. If initializing or resolving authorization: render calm AuthLoading.
 * 2. If unauthenticated: redirect to loginPath with safe returnTo query param (HTTP 401 equivalent).
 * 3. If authenticated but account suspended/inactive: render 403 ForbiddenView.
 * 4. If authenticated but role mismatch: render 403 ForbiddenView.
 * 5. If authenticated and authorized: render protected content (children or <Outlet />).
 */
export function ProtectedRoute({
  children,
  requiredRole = 'STUDENT',
  requiredStatus = 'ACTIVE',
  loginPath = '/auth/student/sign-in',
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, isRoleResolving, status, user } = useAuth();
  const location = useLocation();

  // 1. Initializing authentication or awaiting authoritative backend role resolution
  if (isLoading || status === 'INITIALIZING' || isRoleResolving) {
    return <AuthLoading message="Verifying workspace credentials..." />;
  }

  // 2. Unauthenticated: redirect to login preserving current route in returnTo
  if (!isAuthenticated || status === 'UNAUTHENTICATED' || status === 'ERROR') {
    const returnToParam = encodeURIComponent(
      `${location.pathname}${location.search}${location.hash}`,
    );
    return <Navigate to={`${loginPath}?returnTo=${returnToParam}`} replace />;
  }

  // 3. Account lifecycle boundary enforcement
  if (user?.status === 'SUSPENDED') {
    return <AccountStatusView status="SUSPENDED" />;
  }

  if (user?.status === 'INACTIVE') {
    return <AccountStatusView status="INACTIVE" />;
  }

  // 4. Role authorization boundary enforcement
  if (requiredRole && user?.role && user.role !== requiredRole) {
    return (
      <ForbiddenView
        reason="ROLE_MISMATCH"
        message={`This workspace is designated for ${requiredRole} accounts. Your account is currently authorized as ${user.role}.`}
      />
    );
  }

  // If status check required
  if (requiredStatus && user?.status && user.status !== requiredStatus) {
    return <ForbiddenView reason="GENERIC" message="Your account does not meet the status requirements for this workspace." />;
  }

  // 5. Authorized
  return children ? <>{children}</> : <Outlet />;
}
