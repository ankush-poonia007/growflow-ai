import { useState, useEffect, useRef, useCallback } from 'react';
import { Outlet, useLocation } from 'react-router';
import { AuthHeader } from '@/components/navigation/AuthHeader';
import { AdminSidebar } from '@/components/navigation/AdminSidebar';
import { MobileWorkspaceDrawer } from '@/components/navigation/MobileWorkspaceDrawer';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { OfflineBanner } from '@/components/system/OfflineBanner';
import './AdminLayout.css';

const ADMIN_SIDEBAR_COLLAPSE_STORAGE_KEY = 'growflow_admin_sidebar_collapsed';

/**
 * AdminLayout — Canonical Application Shell for Admin GOVERN workplace.
 *
 * Adheres to GrowFlow Application Shell Specification:
 * - Fixed top navigation (64px) with GOVERN context indicator
 * - Persistent admin navigation sidebar (248px desktop / 72px collapsed / mobile drawer)
 * - Viewport with independent vertical scrolling
 * - Top-level Error Boundary isolating crashes within views
 */
export function AdminLayout() {
  const location = useLocation();
  const viewportRef = useRef<HTMLDivElement>(null);

  // Sidebar collapse state
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem(ADMIN_SIDEBAR_COLLAPSE_STORAGE_KEY) === 'true';
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
        localStorage.setItem(ADMIN_SIDEBAR_COLLAPSE_STORAGE_KEY, String(next));
      } catch {
        // ignore storage errors
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
    <div className="gf-admin-layout">
      <AuthHeader
        workplace="GOVERN"
        onToggleMobileNav={toggleMobileNav}
        isMobileNavOpen={isMobileNavOpen}
      />

      <div className="gf-admin-layout__body">
        <AdminSidebar
          isCollapsed={isCollapsed}
          onToggleCollapse={toggleCollapse}
        />

        <MobileWorkspaceDrawer
          workplace="GOVERN"
          isOpen={isMobileNavOpen}
          onClose={closeMobileNav}
        />

        <div
          ref={viewportRef}
          className="gf-admin-layout__viewport"
          tabIndex={-1}
        >
          <OfflineBanner />
          <main id="main-content" className="gf-admin-layout__content">
            <ErrorBoundary>
              <Outlet />
            </ErrorBoundary>
          </main>
        </div>
      </div>
    </div>
  );
}
