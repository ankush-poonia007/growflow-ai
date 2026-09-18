import { Link } from 'react-router';
import { GrowFlowBrand } from '@/components/ui/Logo';
import './Footer.css';

const FOOTER_LINKS = {
  Product: [
    { label: 'Features', to: '/features' },
    { label: 'Showcase', to: '/showcase' },
    { label: 'Documentation', to: '/documentation' },
    { label: 'Contact', to: '/contact' },
  ],
  Workplaces: [
    { label: 'BUILD — Student', to: '/auth/student/sign-in' },
    { label: 'SUPERVISE — Mentor', to: '/auth/mentor/sign-in' },
  ],
  Company: [
    { label: 'Contact & Inquiries', to: '/contact' },
  ],
} as const;

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="gf-footer" role="contentinfo">
      <div className="gf-footer__inner">
        <div className="gf-footer__grid">
          {/* Brand column */}
          <div className="gf-footer__brand-col">
            <Link to="/" aria-label="GrowFlow home">
              <GrowFlowBrand />
            </Link>
            <p className="gf-footer__tagline">
              Structured planning, intelligent guidance, and mentor collaboration — all in one project workspace.
            </p>
          </div>

          {/* Link columns */}
          {Object.entries(FOOTER_LINKS).map(([title, links]) => (
            <div key={title} className="gf-footer__col">
              <span className="gf-footer__col-title">{title}</span>
              {links.map(({ label, to }) => (
                <Link key={label} to={to} className="gf-footer__link">
                  {label}
                </Link>
              ))}
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="gf-footer__bottom">
          <span className="gf-footer__copyright">
            © {year} GrowFlow. All rights reserved.
          </span>
        </div>
      </div>
    </footer>
  );
}
