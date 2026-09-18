import { type ReactNode } from 'react';
import { Navigate, useSearchParams, Outlet } from 'react-router';
import { useAuth } from './useAuth';
import { getSafeReturnTo, DEFAULT_STUDENT_DESTINATION } from './returnTo';
import { AuthLoading } from '@/components/auth/AuthLoading';

interface AuthRouteProps {
  children?: ReactNode;
  defaultDestination?: string;
}

/**
 * Route guard for authentication entry pages (e.g. /auth/student/sign-in).
 * If the user already has an active verified session, redirects them to safe returnTo
 * or the default workplace destination to avoid showing a redundant login form.
 */
export function AuthRoute({
  children,
  defaultDestination = DEFAULT_STUDENT_DESTINATION,
}: AuthRouteProps) {
  const { isAuthenticated, isLoading, isRoleResolving, status } = useAuth();
  const [searchParams] = useSearchParams();

  if (isLoading || status === 'INITIALIZING' || isRoleResolving) {
    return <AuthLoading message="Checking authentication status..." />;
  }

  if (isAuthenticated) {
    const destination = getSafeReturnTo(searchParams, defaultDestination);
    return <Navigate to={destination} replace />;
  }

  return children ? <>{children}</> : <Outlet />;
}
