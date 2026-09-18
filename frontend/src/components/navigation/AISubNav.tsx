import { Link, useLocation } from 'react-router';
import './AISubNav.css';

interface SubNavItem {
  label: string;
  to: string;
  isActive: (pathname: string) => boolean;
}

const SUB_NAV_ITEMS: SubNavItem[] = [
  {
    label: 'Observatory',
    to: '/admin/ai',
    isActive: (p) => p === '/admin/ai',
  },
  {
    label: 'Usage',
    to: '/admin/ai/usage',
    isActive: (p) => p === '/admin/ai/usage',
  },
  {
    label: 'Executions',
    to: '/admin/ai/executions',
    isActive: (p) => p.startsWith('/admin/ai/executions'),
  },
  {
    label: 'Quality',
    to: '/admin/ai/quality',
    isActive: (p) => p === '/admin/ai/quality',
  },
  {
    label: 'Cost & Capacity',
    to: '/admin/ai/cost',
    isActive: (p) => p.startsWith('/admin/ai/cost'),
  },
  {
    label: 'Key Pool',
    to: '/admin/ai/keys',
    isActive: (p) => p === '/admin/ai/keys',
  },
];

export function AISubNav() {
  const location = useLocation();

  return (
    <nav className="gf-ai-subnav" aria-label="AI Subsystem Navigation">
      <div className="gf-ai-subnav__container">
        {SUB_NAV_ITEMS.map((item) => {
          const active = item.isActive(location.pathname);
          return (
            <Link
              key={item.to}
              to={item.to}
              className={`gf-ai-subnav__tab ${active ? 'gf-ai-subnav__tab--active' : ''}`}
              aria-current={active ? 'page' : undefined}
            >
              {item.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
