import { useState } from 'react';
import { useNavigate } from 'react-router';
import { createMentorGroup } from '@/lib/api/client';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import './GroupCreate.css';

export function GroupCreate() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanName = name.trim();
    if (!cleanName) {
      setError('Please provide a cohort name.');
      return;
    }
    if (cleanName.length < 2) {
      setError('Cohort name must be at least 2 characters.');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      const group = await createMentorGroup({ name: cleanName });
      navigate(`/mentor/groups/${group.id}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to create student group.';
      setError(msg);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="gf-group-create">
      <PageHeader
        eyebrow="SUPERVISE"
        title="Create Student Group"
        description="Establish a new supervised cohort. A unique join code will be generated automatically for student self-enrollment."
        breadcrumbs={[
          { label: 'Groups', to: '/mentor/groups' },
          { label: 'New Cohort' },
        ]}
      />

      <Card className="gf-group-create__card">
        <form onSubmit={handleSubmit} className="gf-group-create__form" noValidate>
          {error && (
            <div className="gf-group-create__error" role="alert">
              {error}
            </div>
          )}

          <div className="gf-group-create__field">
            <label htmlFor="group-name-input" className="gf-group-create__label">
              Cohort / Group Name <span className="gf-group-create__required">*</span>
            </label>
            <Input
              id="group-name-input"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                if (error) setError(null);
              }}
              placeholder="e.g. CS401 Fall 2026 — Section A"
              disabled={isSubmitting}
              autoFocus
              required
            />
            <span className="gf-group-create__help">
              Use a recognizable name for your class, section, or capstone team.
            </span>
          </div>

          <div className="gf-group-create__callout">
            <div className="gf-group-create__callout-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="16" x2="12" y2="12" />
                <line x1="12" y1="8" x2="12.01" y2="8" />
              </svg>
            </div>
            <div className="gf-group-create__callout-text">
              <strong>Automatic Join Code Generation:</strong> Upon creation, GrowFlow generates a unique enrollment code. Share this code with students so they can link their projects to your supervision dashboard.
            </div>
          </div>

          <div className="gf-group-create__actions">
            <Button
              type="submit"
              variant="primary"
              disabled={isSubmitting || !name.trim()}
            >
              {isSubmitting ? 'Creating Cohort...' : 'Create Cohort'}
            </Button>
            <Button
              as="link"
              to="/mentor/groups"
              variant="secondary"
            >
              Cancel
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
