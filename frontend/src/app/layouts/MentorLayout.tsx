import { useState, useEffect, useRef, useCallback } from 'react';
import { Outlet, useLocation } from 'react-router';
import { AuthHeader } from '@/components/navigation/AuthHeader';
import { MentorSidebar } from '@/components/navigation/MentorSidebar';
import { MobileWorkspaceDrawer } from '@/components/navigation/MobileWorkspaceDrawer';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { OfflineBanner } from '@/components/system/OfflineBanner';
import './MentorLayout.css';

const MENTOR_SIDEBAR_COLLAPSE_STORAGE_KEY = 'growflow_mentor_sidebar_collapsed';

/**
 * MentorLayout — Canonical Application Shell for Mentor SUPERVISE workplace.
 *
 * Adheres to Phase 06E / Phase 07 Application Shell Specification:
 * - Fixed top navigation (64px) with SUPERVISE context indicator
 * - Persistent mentor navigation sidebar with contextual group navigation
 * - Viewport with independent vertical scrolling
 * - Top-level Error Boundary isolating crashes within views
 */
export function MentorLayout() {
  const location = useLocation();
  const viewportRef = useRef<HTMLDivElement>(null);

  // Sidebar collapse state
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem(MENTOR_SIDEBAR_COLLAPSE_STORAGE_KEY) === 'true';
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
        localStorage.setItem(MENTOR_SIDEBAR_COLLAPSE_STORAGE_KEY, String(next));
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
    <div className="gf-mentor-layout">
      <AuthHeader
        workplace="SUPERVISE"
        onToggleMobileNav={toggleMobileNav}
        isMobileNavOpen={isMobileNavOpen}
      />

      <div className="gf-mentor-layout__body">
        <MentorSidebar
          isCollapsed={isCollapsed}
          onToggleCollapse={toggleCollapse}
        />

        <MobileWorkspaceDrawer
          workplace="SUPERVISE"
          isOpen={isMobileNavOpen}
          onClose={closeMobileNav}
        />

        <div
          ref={viewportRef}
          className="gf-mentor-layout__viewport"
          tabIndex={-1}
        >
          <OfflineBanner />
          <main id="main-content" className="gf-mentor-layout__content">
            <ErrorBoundary>
              <Outlet />
            </ErrorBoundary>
          </main>
        </div>
      </div>
    </div>
  );
}
