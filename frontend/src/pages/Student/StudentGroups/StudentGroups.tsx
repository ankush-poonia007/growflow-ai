import React, { useState, useEffect, useCallback } from 'react';
import { getStudentGroups, joinGroup } from '@/lib/api/client';
import type { GroupResponse, GroupMembershipResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './StudentGroups.css';

export function StudentGroups() {
  const [groups, setGroups] = useState<GroupResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Join modal state
  const [isJoinModalOpen, setIsJoinModalOpen] = useState<boolean>(false);
  const [joinCode, setJoinCode] = useState<string>('');
  const [isJoining, setIsJoining] = useState<boolean>(false);
  const [joinError, setJoinError] = useState<string | null>(null);
  const [joinSuccess, setJoinSuccess] = useState<GroupMembershipResponse | null>(null);

  const fetchGroups = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getStudentGroups();
      setGroups(data || []);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve your student groups.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchGroups();
  }, [fetchGroups]);

  const handleOpenJoinModal = () => {
    setJoinCode('');
    setJoinError(null);
    setJoinSuccess(null);
    setIsJoinModalOpen(true);
  };

  const handleCloseJoinModal = () => {
    setIsJoinModalOpen(false);
    setJoinCode('');
    setJoinError(null);
    setJoinSuccess(null);
  };

  const handleJoinSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanCode = joinCode.trim();
    if (!cleanCode) {
      setJoinError('Please enter a group join code.');
      return;
    }
    if (cleanCode.length < 3) {
      setJoinError('Join code must be at least 3 characters.');
      return;
    }

    setIsJoining(true);
    setJoinError(null);
    setJoinSuccess(null);

    try {
      const result = await joinGroup(cleanCode);
      setJoinSuccess(result);
      await fetchGroups();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unable to join group.';
      setJoinError(msg);
    } finally {
      setIsJoining(false);
    }
  };

  return (
    <div className="gf-student-groups" id="student-groups-screen">
      <PageHeader
        title="My Cohort Groups"
        description="View your active student cohort memberships and join mentor-supervised cohorts."
        action={
          <Button
            variant="primary"
            onClick={handleOpenJoinModal}
            id="join-group-button"
          >
            + Join a Group
          </Button>
        }
      />

      {error && (
        <div className="gf-student-groups__error" role="alert" id="student-groups-error">
          <p>⚠️ {error}</p>
          <Button variant="secondary" size="sm" onClick={() => void fetchGroups()}>
            Retry
          </Button>
        </div>
      )}

      {isLoading && groups.length === 0 ? (
        <div className="gf-student-groups__loading" id="student-groups-loading">
          <Skeleton height="140px" style={{ borderRadius: '12px', marginBottom: '1rem' }} />
          <Skeleton height="140px" style={{ borderRadius: '12px', marginBottom: '1rem' }} />
        </div>
      ) : groups.length === 0 ? (
        <div className="gf-student-groups__empty" id="student-groups-empty">
          <EmptyState
            title="You haven't joined any groups yet."
            description="Enter a unique group join code provided by your mentor to enroll in a project cohort."
            action={
              <Button variant="primary" onClick={handleOpenJoinModal} id="empty-state-join-btn">
                Join a Group
              </Button>
            }
          />
        </div>
      ) : (
        <div className="gf-student-groups__grid" id="student-groups-grid">
          {groups.map((group) => (
            <div key={group.id} className="gf-student-groups__card" id={`group-card-${group.id}`}>
              <div className="gf-student-groups__card-header">
                <div>
                  <h3 className="gf-student-groups__card-title">{group.name}</h3>
                  <p className="gf-student-groups__card-mentor">
                    Mentor: <strong>{group.mentor_name || 'Assigned Mentor'}</strong>
                  </p>
                </div>
                <Badge variant={group.status === 'ACTIVE' ? 'success' : 'neutral'}>
                  {group.status === 'ACTIVE' ? 'Active Member' : group.status}
                </Badge>
              </div>

              <div className="gf-student-groups__card-meta">
                <div className="gf-student-groups__meta-item">
                  <span className="gf-student-groups__meta-label">Join Code:</span>
                  <code className="gf-student-groups__meta-code">{group.join_code}</code>
                </div>
                {group.created_at && (
                  <div className="gf-student-groups__meta-item">
                    <span className="gf-student-groups__meta-label">Member Since:</span>
                    <span>{new Date(group.created_at).toLocaleDateString()}</span>
                  </div>
                )}
              </div>

              <div className="gf-student-groups__card-actions">
                <Button
                  as="link"
                  to={`/student/projects?group_id=${group.id}`}
                  variant="secondary"
                  size="sm"
                  id={`view-projects-${group.id}`}
                >
                  View Cohort Projects
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Join Group Modal Dialog */}
      {isJoinModalOpen && (
        <div className="gf-modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="join-modal-title">
          <div className="gf-modal-card">
            <div className="gf-modal-header">
              <h2 id="join-modal-title" className="gf-modal-title">Join a Cohort Group</h2>
              <button
                type="button"
                className="gf-modal-close"
                onClick={handleCloseJoinModal}
                aria-label="Close dialog"
              >
                ✕
              </button>
            </div>

            {joinSuccess ? (
              <div className="gf-modal-success" id="join-success-container">
                <div className="gf-modal-success__icon" aria-hidden="true">✓</div>
                <h3>Successfully Joined Group!</h3>
                <div className="gf-modal-success__details">
                  <p><strong>Cohort:</strong> {joinSuccess.group_name || 'Group'}</p>
                  <p><strong>Status:</strong> Active Member</p>
                  {joinSuccess.join_code && (
                    <p><strong>Code:</strong> <code>{joinSuccess.join_code}</code></p>
                  )}
                </div>
                <div className="gf-modal-actions">
                  <Button variant="primary" onClick={handleCloseJoinModal} id="join-success-close-btn">
                    Done
                  </Button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleJoinSubmit} className="gf-modal-form" id="join-group-form">
                <p className="gf-modal-description">
                  Enter the group join code provided by your mentor to join their cohort.
                </p>

                {joinError && (
                  <div className="gf-modal-error" role="alert" id="join-error-alert">
                    <span>⚠️</span> {joinError}
                  </div>
                )}

                <div className="gf-modal-field">
                  <label htmlFor="join-code-input" className="gf-modal-label">
                    Group Join Code <span className="gf-modal-required">*</span>
                  </label>
                  <input
                    id="join-code-input"
                    type="text"
                    className="gf-modal-input"
                    value={joinCode}
                    onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                    placeholder="e.g. ELENA001"
                    maxLength={50}
                    autoFocus
                    disabled={isJoining}
                  />
                  <small className="gf-modal-hint">Join codes are alphanumeric uppercase strings.</small>
                </div>

                <div className="gf-modal-actions">
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={handleCloseJoinModal}
                    disabled={isJoining}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={isJoining || !joinCode.trim()}
                    id="submit-join-code-btn"
                  >
                    {isJoining ? 'Joining...' : 'Join Group'}
                  </Button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
