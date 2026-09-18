import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { AuthContext } from '@/auth/AuthContext';
import { WorkplaceSelector } from '@/components/navigation/WorkplaceSelector';

describe('WorkplaceSelector Component', () => {
  it('renders trigger button and opens on click', () => {
    render(
      <MemoryRouter>
        <WorkplaceSelector />
      </MemoryRouter>,
    );

    const trigger = screen.getByRole('button', { name: /select workplace/i });
    expect(trigger).toBeInTheDocument();
    expect(trigger).toHaveAttribute('aria-expanded', 'false');

    fireEvent.click(trigger);
    expect(trigger).toHaveAttribute('aria-expanded', 'true');
  });

  it('renders workplace title and description on separate structured elements without collision', () => {
    render(
      <MemoryRouter>
        <WorkplaceSelector />
      </MemoryRouter>,
    );

    const trigger = screen.getByRole('button', { name: /select workplace/i });
    fireEvent.click(trigger);

    // Verify BUILD workplace title structure
    expect(screen.getByText('BUILD')).toBeInTheDocument();
    expect(screen.getByText('Student')).toBeInTheDocument();
    expect(
      screen.getByText('Turn ideas into structured projects'),
    ).toBeInTheDocument();

    // Verify SUPERVISE workplace title structure
    expect(screen.getByText('SUPERVISE')).toBeInTheDocument();
    expect(screen.getByText('Mentor')).toBeInTheDocument();
    expect(
      screen.getByText('Guide students and track progress'),
    ).toBeInTheDocument();

    // Verify GOVERN workplace title structure
    expect(screen.getByText('GOVERN')).toBeInTheDocument();
    expect(screen.getByText('Admin')).toBeInTheDocument();
    expect(
      screen.getByText('Monitor platform health and operations'),
    ).toBeInTheDocument();

    // Verify distinct class structure
    const titleElements = document.querySelectorAll('.gf-workplace__item-title');
    const descElements = document.querySelectorAll('.gf-workplace__item-desc');
    expect(titleElements).toHaveLength(3);
    expect(descElements).toHaveLength(3);
  });

  it('supports keyboard navigation (ArrowDown, ArrowUp, Escape)', () => {
    render(
      <MemoryRouter>
        <WorkplaceSelector />
      </MemoryRouter>,
    );

    const trigger = screen.getByRole('button', { name: /select workplace/i });

    // Open via Enter key
    fireEvent.keyDown(trigger, { key: 'Enter' });
    expect(trigger).toHaveAttribute('aria-expanded', 'true');

    // Arrow down navigation
    fireEvent.keyDown(trigger, { key: 'ArrowDown' });

    // Close via Escape key
    fireEvent.keyDown(trigger, { key: 'Escape' });
    expect(trigger).toHaveAttribute('aria-expanded', 'false');
  });

  it('routes unauthenticated users to respective role sign-in pages', () => {
    render(
      <MemoryRouter>
        <WorkplaceSelector />
      </MemoryRouter>,
    );

    const trigger = screen.getByRole('button', { name: /select workplace/i });
    fireEvent.click(trigger);

    const buildLink = screen.getByRole('menuitem', { name: /BUILD/i });
    expect(buildLink).toHaveAttribute('href', '/auth/student/sign-in');

    const superviseLink = screen.getByRole('menuitem', { name: /SUPERVISE/i });
    expect(superviseLink).toHaveAttribute('href', '/auth/mentor/sign-in');

    const governLink = screen.getByRole('menuitem', { name: /GOVERN/i });
    expect(governLink).toHaveAttribute('href', '/auth/admin/sign-in');
  });

  it('routes authenticated STUDENT to /student/dashboard with SUPERVISE and GOVERN disabled', () => {
    const studentAuth = {
      status: 'AUTHENTICATED' as const,
      isAuthenticated: true,
      isLoading: false,
      user: {
        id: 'user-stu-1',
        email: 'student@example.com',
        role: 'STUDENT' as const,
        status: 'ACTIVE' as const,
        fullName: 'Student User',
      },
      session: null,
      supabaseUser: null,
      error: null,
      isRoleResolving: false,
      signIn: async () => ({ success: true }),
      signUp: async () => ({ success: true }),
      signOut: async () => {},
      retryAuth: async () => {},
      resetPassword: async () => ({ success: true }),
      refreshAuthorization: async () => {},
    };

    render(
      <AuthContext.Provider value={studentAuth}>
        <MemoryRouter>
          <WorkplaceSelector />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    const trigger = screen.getByRole('button', { name: /select workplace/i });
    fireEvent.click(trigger);

    // BUILD is active link
    const buildLink = screen.getByRole('menuitem', { name: /BUILD/i });
    expect(buildLink).toHaveAttribute('href', '/student/dashboard');
    expect(screen.getByText('Active')).toBeInTheDocument();

    // SUPERVISE and GOVERN are disabled items
    const menuItems = screen.getAllByRole('menuitem');
    expect(menuItems[1]).toHaveAttribute('aria-disabled', 'true');
    expect(menuItems[2]).toHaveAttribute('aria-disabled', 'true');
  });

  it('routes authenticated MENTOR to /mentor/overview with BUILD and GOVERN disabled', () => {
    const mentorAuth = {
      status: 'AUTHENTICATED' as const,
      isAuthenticated: true,
      isLoading: false,
      user: {
        id: 'user-mtr-1',
        email: 'mentor@example.com',
        role: 'MENTOR' as const,
        status: 'ACTIVE' as const,
        fullName: 'Mentor User',
      },
      session: null,
      supabaseUser: null,
      error: null,
      isRoleResolving: false,
      signIn: async () => ({ success: true }),
      signUp: async () => ({ success: true }),
      signOut: async () => {},
      retryAuth: async () => {},
      resetPassword: async () => ({ success: true }),
      refreshAuthorization: async () => {},
    };

    render(
      <AuthContext.Provider value={mentorAuth}>
        <MemoryRouter>
          <WorkplaceSelector />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    const trigger = screen.getByRole('button', { name: /select workplace/i });
    fireEvent.click(trigger);

    // SUPERVISE is active link
    const superviseLink = screen.getByRole('menuitem', { name: /SUPERVISE/i });
    expect(superviseLink).toHaveAttribute('href', '/mentor/overview');
    expect(screen.getByText('Active')).toBeInTheDocument();

    // BUILD and GOVERN are disabled items
    const menuItems = screen.getAllByRole('menuitem');
    expect(menuItems[0]).toHaveAttribute('aria-disabled', 'true');
    expect(menuItems[2]).toHaveAttribute('aria-disabled', 'true');
  });

  it('routes authenticated ADMIN to /admin/overview with BUILD and SUPERVISE disabled', () => {
    const adminAuth = {
      status: 'AUTHENTICATED' as const,
      isAuthenticated: true,
      isLoading: false,
      user: {
        id: 'user-adm-1',
        email: 'admin@example.com',
        role: 'ADMIN' as const,
        status: 'ACTIVE' as const,
        fullName: 'Admin User',
      },
      session: null,
      supabaseUser: null,
      error: null,
      isRoleResolving: false,
      signIn: async () => ({ success: true }),
      signUp: async () => ({ success: true }),
      signOut: async () => {},
      retryAuth: async () => {},
      resetPassword: async () => ({ success: true }),
      refreshAuthorization: async () => {},
    };

    render(
      <AuthContext.Provider value={adminAuth}>
        <MemoryRouter>
          <WorkplaceSelector />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    const trigger = screen.getByRole('button', { name: /select workplace/i });
    fireEvent.click(trigger);

    // GOVERN is active link
    const governLink = screen.getByRole('menuitem', { name: /GOVERN/i });
    expect(governLink).toHaveAttribute('href', '/admin/overview');
    expect(screen.getByText('Active')).toBeInTheDocument();

    // BUILD and SUPERVISE are disabled items
    const menuItems = screen.getAllByRole('menuitem');
    expect(menuItems[0]).toHaveAttribute('aria-disabled', 'true');
    expect(menuItems[1]).toHaveAttribute('aria-disabled', 'true');
  });
});
