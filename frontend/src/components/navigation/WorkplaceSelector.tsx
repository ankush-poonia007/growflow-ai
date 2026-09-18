import { useState, useCallback, useRef, useEffect, useContext } from 'react';
import { Link } from 'react-router';
import { AuthContext } from '@/auth/AuthContext';
import { useClickOutside } from '@/hooks/useClickOutside';
import { cn } from '@/utils/cn';
import './WorkplaceSelector.css';

interface WorkplaceConfig {
  key: string;
  name: string;
  role: string;
  description: string;
  to: string;
  icon: string;
  disabled?: boolean;
  tag?: string;
}

export function WorkplaceSelector() {
  const auth = useContext(AuthContext);
  const user = auth?.user;
  const isAuthenticated = auth?.isAuthenticated ?? false;
  const currentRole = user?.role ? String(user.role).toUpperCase() : null;
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState<number>(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const itemRefs = useRef<(HTMLElement | null)[]>([]);

  const close = useCallback(() => {
    setIsOpen(false);
    setActiveIndex(-1);
  }, []);

  const toggle = useCallback(() => {
    setIsOpen((o) => {
      const next = !o;
      if (next) {
        setActiveIndex(0);
      } else {
        setActiveIndex(-1);
      }
      return next;
    });
  }, []);

  useClickOutside(containerRef, close);

  // Compute available workplaces based on authentication and active role
  const workplaces: WorkplaceConfig[] = [
    {
      key: 'build',
      name: 'BUILD',
      role: 'Student',
      description: 'Turn ideas into structured projects',
      icon: 'B',
      to: !isAuthenticated
        ? '/auth/student/sign-in'
        : currentRole === 'STUDENT'
        ? '/student/dashboard'
        : '',
      disabled: isAuthenticated && currentRole !== 'STUDENT',
      tag: isAuthenticated && currentRole === 'STUDENT' ? 'Active' : undefined,
    },
    {
      key: 'supervise',
      name: 'SUPERVISE',
      role: 'Mentor',
      description: 'Guide students and track progress',
      icon: 'S',
      to: !isAuthenticated
        ? '/auth/mentor/sign-in'
        : currentRole === 'MENTOR'
        ? '/mentor/overview'
        : '',
      disabled: isAuthenticated && currentRole !== 'MENTOR',
      tag: isAuthenticated && currentRole === 'MENTOR' ? 'Active' : undefined,
    },
    {
      key: 'govern',
      name: 'GOVERN',
      role: 'Admin',
      description: 'Monitor platform health and operations',
      icon: 'G',
      to: !isAuthenticated
        ? '/auth/admin/sign-in'
        : currentRole === 'ADMIN'
        ? '/admin/overview'
        : '',
      disabled: isAuthenticated && currentRole !== 'ADMIN',
      tag: isAuthenticated && currentRole === 'ADMIN' ? 'Active' : undefined,
    },
  ];

  // Focus the active item when roving tabindex changes
  useEffect(() => {
    if (isOpen && activeIndex >= 0 && itemRefs.current[activeIndex]) {
      itemRefs.current[activeIndex]?.focus();
    }
  }, [isOpen, activeIndex]);

  // Handle keyboard navigation on trigger and menu
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) {
      if (e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        setIsOpen(true);
        setActiveIndex(0);
      }
      return;
    }

    switch (e.key) {
      case 'Escape':
        e.preventDefault();
        close();
        triggerRef.current?.focus();
        break;
      case 'ArrowDown':
        e.preventDefault();
        setActiveIndex((prev) => (prev + 1) % workplaces.length);
        break;
      case 'ArrowUp':
        e.preventDefault();
        setActiveIndex((prev) => (prev - 1 + workplaces.length) % workplaces.length);
        break;
      case 'Home':
        e.preventDefault();
        setActiveIndex(0);
        break;
      case 'End':
        e.preventDefault();
        setActiveIndex(workplaces.length - 1);
        break;
      case 'Tab':
        close();
        break;
    }
  };

  return (
    <div className="gf-workplace" ref={containerRef} onKeyDown={handleKeyDown}>
      <button
        ref={triggerRef}
        type="button"
        className="gf-header__workplace-trigger"
        onClick={toggle}
        aria-expanded={isOpen}
        aria-haspopup="menu"
        aria-label="Select workplace"
      >
        Workplace
        <svg className="gf-header__workplace-chevron" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <path d="M4 6l4 4 4-4" />
        </svg>
      </button>

      <div
        className={cn('gf-workplace__dropdown', isOpen && 'gf-workplace__dropdown--open')}
        role="menu"
        aria-label="Workplaces"
      >
        <div className="gf-workplace__label" role="presentation">Workplaces</div>

        {workplaces.map((wp, idx) => {
          if (wp.disabled || !wp.to) {
            return (
              <div
                key={wp.key}
                ref={(el) => {
                  itemRefs.current[idx] = el;
                }}
                className={cn('gf-workplace__item', 'gf-workplace__item--disabled')}
                role="menuitem"
                aria-disabled="true"
                tabIndex={isOpen && activeIndex === idx ? 0 : -1}
              >
                <span className="gf-workplace__item-icon" aria-hidden="true">
                  {wp.icon}
                </span>
                <span className="gf-workplace__item-content">
                  <span className="gf-workplace__item-title">
                    <span className="gf-workplace__item-name">{wp.name}</span>
                    <span className="gf-workplace__item-sep" aria-hidden="true"> — </span>
                    <span className="gf-workplace__item-role">{wp.role}</span>
                    {wp.tag && <span className="gf-workplace__item-tag">{wp.tag}</span>}
                  </span>
                  <span className="gf-workplace__item-desc">{wp.description}</span>
                </span>
              </div>
            );
          }

          return (
            <Link
              key={wp.key}
              ref={(el) => {
                itemRefs.current[idx] = el;
              }}
              to={wp.to}
              className="gf-workplace__item"
              role="menuitem"
              onClick={close}
              tabIndex={isOpen && activeIndex === idx ? 0 : -1}
            >
              <span className="gf-workplace__item-icon" aria-hidden="true">
                {wp.icon}
              </span>
              <span className="gf-workplace__item-content">
                <span className="gf-workplace__item-title">
                  <span className="gf-workplace__item-name">{wp.name}</span>
                  <span className="gf-workplace__item-sep" aria-hidden="true"> — </span>
                  <span className="gf-workplace__item-role">{wp.role}</span>
                  {wp.tag && <span className="gf-workplace__item-tag">{wp.tag}</span>}
                </span>
                <span className="gf-workplace__item-desc">{wp.description}</span>
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
