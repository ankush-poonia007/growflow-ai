import { useState, useEffect, useRef, useCallback } from 'react';
import { Outlet, useLocation } from 'react-router';
import { AuthHeader } from '@/components/navigation/AuthHeader';
import { Sidebar } from '@/components/navigation/Sidebar';
import { MobileWorkspaceDrawer } from '@/components/navigation/MobileWorkspaceDrawer';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { OfflineBanner } from '@/components/system/OfflineBanner';
import './AuthenticatedLayout.css';

const SIDEBAR_COLLAPSE_STORAGE_KEY = 'growflow_sidebar_collapsed';

/**
 * AuthenticatedLayout — Canonical Application Shell for protected workspaces.
 *
 * Adheres to Phase 06E Application Shell Specification:
 * - Layer 1: Global browser frame
 * - Layer 2: Fixed authenticated top navigation (64px)
 * - Layer 3/4: Persistent role-specific sidebar (248px desktop / 72px collapsed / mobile drawer)
 * - Layer 5: Workspace Viewport with independent vertical scrolling
 */
export function AuthenticatedLayout() {
  const location = useLocation();
  const viewportRef = useRef<HTMLDivElement>(null);

  // Sidebar collapse state (persistent UI state in localStorage)
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem(SIDEBAR_COLLAPSE_STORAGE_KEY) === 'true';
    } catch {
      return false;
    }
  });

  // Mobile drawer state
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);

  const toggleCollapse = useCallback(() => {
    setIsCollapsed((prev) => {
      const next = !prev;
      try {
        localStorage.setItem(SIDEBAR_COLLAPSE_STORAGE_KEY, String(next));
      } catch {
        // ignore localStorage access errors
      }
      return next;
    });
  }, []);

  const toggleMobileNav = useCallback(() => {
    setIsMobileNavOpen((prev) => !prev);
  }, []);

  const closeMobileNav = useCallback(() => {
    setIsMobileNavOpen(false);
  }, []);

  // Ensure content starts at top on cross-route navigation
  useEffect(() => {
    if (viewportRef.current) {
      viewportRef.current.scrollTop = 0;
    }
  }, [location.pathname]);

  return (
    <div className="gf-auth-layout">
      <AuthHeader
        onToggleMobileNav={toggleMobileNav}
        isMobileNavOpen={isMobileNavOpen}
      />

      <div className="gf-auth-layout__body">
        <Sidebar
          isCollapsed={isCollapsed}
          onToggleCollapse={toggleCollapse}
        />

        <MobileWorkspaceDrawer
          workplace="BUILD"
          isOpen={isMobileNavOpen}
          onClose={closeMobileNav}
        />

        <div
          ref={viewportRef}
          className="gf-auth-layout__viewport"
          tabIndex={-1}
        >
          <OfflineBanner />
          <main id="main-content" className="gf-auth-layout__content">
            <ErrorBoundary>
              <Outlet />
            </ErrorBoundary>
          </main>
        </div>
      </div>
    </div>
  );
}
