import { Outlet } from 'react-router';
import { Header } from '@/components/navigation/Header';
import { Footer } from '@/components/navigation/Footer';
import './PublicLayout.css';

/**
 * Public page layout — shared Header + content viewport + Footer.
 * Used for all unauthenticated public pages (P01, Features, Documentation, Contact, etc.).
 */
export function PublicLayout() {
  return (
    <div className="gf-public-layout">
      <Header />
      <main className="gf-public-layout__content">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
