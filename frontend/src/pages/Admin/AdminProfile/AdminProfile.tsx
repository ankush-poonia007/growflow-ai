import { useAuth } from '@/auth/useAuth';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import './AdminProfile.css';

/**
 * AdminProfile — Profile view for Platform Administrators.
 */
export function AdminProfile() {
  const { user } = useAuth();

  return (
    <div className="gf-admin-profile">
      <PageHeader
        eyebrow="PLATFORM GOVERNANCE IDENTITY"
        title="Administrator Profile"
        description="System governance credentials and identity metadata."
      />

      <div className="gf-admin-profile__grid">
        <Card className="gf-admin-profile__card">
          <CardHeader>
            <CardTitle>Administrator Identity Card</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="gf-admin-profile__info-list">
              <div className="gf-admin-profile__info-row">
                <span className="gf-admin-profile__label">Full Name</span>
                <span className="gf-admin-profile__value">{user?.fullName?.trim() || user?.email?.trim() || '—'}</span>
              </div>
              <div className="gf-admin-profile__info-row">
                <span className="gf-admin-profile__label">Email Address</span>
                <span className="gf-admin-profile__value">{user?.email}</span>
              </div>
              <div className="gf-admin-profile__info-row">
                <span className="gf-admin-profile__label">Assigned Role</span>
                <Badge variant="accent">ADMIN (Platform Governance)</Badge>
              </div>
              <div className="gf-admin-profile__info-row">
                <span className="gf-admin-profile__label">Account Status</span>
                <Badge variant={user?.status === 'ACTIVE' ? 'success' : 'neutral'}>
                  {user?.status || 'ACTIVE'}
                </Badge>
              </div>
              <div className="gf-admin-profile__info-row">
                <span className="gf-admin-profile__label">Security Identity ID</span>
                <code className="gf-admin-profile__code">{user?.id}</code>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="gf-admin-profile__card">
          <CardHeader>
            <CardTitle>Governance Clearance &amp; Authority</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="gf-admin-profile__clearance-list">
              <div className="gf-admin-profile__clearance-item">
                <span className="gf-admin-profile__clearance-check">✓</span>
                <div>
                  <strong>Platform Oversight (AD01)</strong>
                  <p>Full read access to canonical platform metrics and project lifecycle records.</p>
                </div>
              </div>
              <div className="gf-admin-profile__clearance-item">
                <span className="gf-admin-profile__clearance-check">✓</span>
                <div>
                  <strong>Mentor Supervision (AD02 / AD03)</strong>
                  <p>Authority to inspect registered mentors, supervised cohorts, and student assignments.</p>
                </div>
              </div>
              <div className="gf-admin-profile__clearance-item">
                <span className="gf-admin-profile__clearance-check">✓</span>
                <div>
                  <strong>Student Governance (AD04 / AD05)</strong>
                  <p>Authority to inspect student enrollment, progress tracking, and project instances.</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
