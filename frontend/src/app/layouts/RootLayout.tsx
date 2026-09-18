import { Outlet } from 'react-router';
import { ScrollToTop } from '@/components/navigation/ScrollToTop';
import { AuthProvider } from '@/auth/AuthProvider';
import { ErrorBoundary } from '@/components/ErrorBoundary';

/**
 * RootLayout — Global application wrapper.
 * Mounts AuthProvider, centralized ScrollToTop restoration, and root-level ErrorBoundary for all child routes and layouts.
 */
export function RootLayout() {
  return (
    <AuthProvider>
      <ScrollToTop />
      <ErrorBoundary>
        <Outlet />
      </ErrorBoundary>
    </AuthProvider>
  );
}

