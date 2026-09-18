import { useEffect, useState, useCallback, useRef } from 'react';
import { Link } from 'react-router';
import { getMentorGroups } from '@/lib/api/client';
import type { GroupResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './GroupsDirectory.css';

export function GroupsDirectory() {
  const [groups, setGroups] = useState<GroupResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const copiedTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const loadGroups = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getMentorGroups();
      setGroups(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve groups.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadGroups();
  }, [loadGroups]);

  useEffect(() => {
    return () => {
      if (copiedTimerRef.current) {
        clearTimeout(copiedTimerRef.current);
      }
    };
  }, []);

  const handleCopyCode = async (code: string, id: string) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopiedId(id);
      if (copiedTimerRef.current) {
        clearTimeout(copiedTimerRef.current);
      }
      copiedTimerRef.current = setTimeout(() => {
        setCopiedId(null);
        copiedTimerRef.current = null;
      }, 2000);
    } catch {
      // ignore clipboard error
    }
  };

  const filteredGroups = groups.filter((g) => {
    const q = search.toLowerCase().trim();
    if (!q) return true;
    return g.name.toLowerCase().includes(q) || g.join_code.toLowerCase().includes(q);
  });

  return (
    <div className="gf-groups-directory">
      <PageHeader
        eyebrow="SUPERVISE"
        title="Student Groups"
        description="Manage supervised student cohorts, access workspaces, and track progress."
        actions={
          <Button as="link" to="/mentor/groups/new" variant="primary">
            + Create Group
          </Button>
        }
      />

      {error && (
        <div style={{ marginBottom: '1.5rem' }}>
          <InlineErrorState error={error} onRetry={loadGroups} />
        </div>
      )}

      <div className="gf-groups-directory__toolbar">
        <div className="gf-groups-directory__search-wrap">
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by cohort name or join code..."
            aria-label="Filter groups"
          />
        </div>
      </div>

      {loading ? (
        <div className="gf-groups-directory__list">
          <Skeleton height="80px" />
          <Skeleton height="80px" />
          <Skeleton height="80px" />
        </div>
      ) : groups.length === 0 ? (
        <EmptyState
          title="No Cohorts Found"
          description="You haven't established any student groups yet. Create a group to receive a join code for student enrollment."
          action={
            <Button as="link" to="/mentor/groups/new" variant="primary">
              Create Your First Group
            </Button>
          }
        />
      ) : filteredGroups.length === 0 ? (
        <EmptyState
          title="No Matching Cohorts"
          description={`No student groups matched "${search}". Try a different search term.`}
          action={
            <Button variant="secondary" onClick={() => setSearch('')}>
              Clear Filter
            </Button>
          }
        />
      ) : (
        <div className="gf-groups-directory__list" role="feed" aria-label="Groups list">
          {filteredGroups.map((group) => (
            <Card key={group.id} className="gf-groups-directory__item">
              <div className="gf-groups-directory__item-left">
                <div className="gf-groups-directory__item-title-row">
                  <Link to={`/mentor/groups/${group.id}`} className="gf-groups-directory__name-link">
                    {group.name}
                  </Link>
                  <Badge variant={group.status === 'ACTIVE' ? 'success' : 'neutral'}>
                    {group.status}
                  </Badge>
                </div>

                <div className="gf-groups-directory__item-meta">
                  <div className="gf-groups-directory__join-pill">
                    <span className="gf-groups-directory__pill-label">JOIN CODE:</span>
                    <code className="gf-groups-directory__pill-code">{group.join_code}</code>
                    <button
                      type="button"
                      className="gf-groups-directory__copy-btn"
                      onClick={() => handleCopyCode(group.join_code, group.id)}
                      aria-label={copiedId === group.id ? 'Copied join code' : 'Copy join code'}
                      title="Copy join code to clipboard"
                    >
                      {copiedId === group.id ? (
                        <span className="gf-groups-directory__copied-tag">Copied!</span>
                      ) : (
                        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2">
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                        </svg>
                      )}
                    </button>
                  </div>

                  {group.created_at && (
                    <span className="gf-groups-directory__date">
                      Created {new Date(group.created_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>

              <div className="gf-groups-directory__item-actions">
                <Button
                  as="link"
                  to={`/mentor/groups/${group.id}`}
                  variant="secondary"
                  size="sm"
                >
                  Open Workspace &rarr;
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
