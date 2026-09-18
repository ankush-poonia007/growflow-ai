import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router';
import { getMentorProjectInstance, getMentorProjectNotes, createMentorNote } from '@/lib/api/client';
import type { MentorProjectInstanceDetail, MentorNoteItem } from '@/lib/api/types';
import { MentorInstanceHeader } from '@/components/navigation/MentorInstanceHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './MentorInstanceNotes.css';

export function MentorInstanceNotes() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<MentorProjectInstanceDetail | null>(null);
  const [notes, setNotes] = useState<MentorNoteItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [title, setTitle] = useState<string>('');
  const [message, setMessage] = useState<string>('');
  const [noteType, setNoteType] = useState<'INFORMATIONAL' | 'ACTIONABLE' | 'FEEDBACK' | 'INTERNAL'>('FEEDBACK');
  const [relatedType, setRelatedType] = useState<string>('PROJECT');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [modalError, setModalError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!projectId) return;
    try {
      setLoading(true);
      setError(null);
      const [projData, notesData] = await Promise.all([
        getMentorProjectInstance(projectId),
        getMentorProjectNotes(projectId),
      ]);
      setProject(projData);
      setNotes(notesData || []);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve project instance notes.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const handleOpenModal = () => {
    setTitle('');
    setMessage('');
    setNoteType('FEEDBACK');
    setRelatedType('PROJECT');
    setModalError(null);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setTitle('');
    setMessage('');
    setModalError(null);
  };

  const handleCreateNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) return;

    if (!title.trim() || !message.trim()) {
      setModalError('Title and message are required.');
      return;
    }

    setIsSubmitting(true);
    setModalError(null);

    try {
      const created = await createMentorNote({
        project_instance_id: projectId,
        title: title.trim(),
        message: message.trim(),
        note_type: noteType,
        related_resource_type: relatedType === 'NONE' ? null : relatedType,
      });

      setNotes((prev) => [created, ...prev]);
      handleCloseModal();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to create mentor note.';
      setModalError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getNoteTypeBadge = (type: string) => {
    switch (type?.toUpperCase()) {
      case 'INTERNAL':
        return <Badge variant="neutral">🔒 Internal (Mentor Only)</Badge>;
      case 'ACTIONABLE':
        return <Badge variant="warning">Actionable</Badge>;
      case 'FEEDBACK':
        return <Badge variant="accent">Feedback</Badge>;
      case 'INFORMATIONAL':
      default:
        return <Badge variant="info">Informational</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="gf-mentor-notes-page" id="instance-notes-loading">
        <Skeleton width="60%" height="32px" />
        <Skeleton width="100%" height="180px" style={{ borderRadius: '12px', margin: '1.5rem 0' }} />
        <Skeleton width="100%" height="120px" style={{ borderRadius: '12px' }} />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="gf-mentor-notes-page" id="instance-notes-error">
        <div className="gf-mentor-notes-page__alert" role="alert">
          <h3>Supervision Access Restriction</h3>
          <p>{error || 'Project not found or access denied.'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-mentor-notes-page" id="instance-notes-screen">
      <MentorInstanceHeader project={project} activeTab="notes" />

      <div className="gf-mentor-notes-content">
        <header className="gf-mentor-notes-header">
          <div>
            <h2 className="gf-mentor-notes-title">Mentor Notes & Feedback</h2>
            <p className="gf-mentor-notes-subtitle">
              Communicate guidance, review critiques, and maintain internal mentor supervisory records for this project.
            </p>
          </div>
          <Button variant="primary" onClick={handleOpenModal} id="add-mentor-note-btn">
            + Add Note / Feedback
          </Button>
        </header>

        {notes.length === 0 ? (
          <div className="gf-mentor-notes-empty" id="instance-notes-empty">
            <EmptyState
              title="No mentor notes recorded yet"
              description="Deliver advisory feedback, actionable critiques, or record internal mentor notes for this student project."
              action={
                <Button variant="primary" onClick={handleOpenModal} id="empty-add-note-btn">
                  Create First Note
                </Button>
              }
            />
          </div>
        ) : (
          <div className="gf-mentor-notes-list" id="instance-notes-list">
            {notes.map((n) => (
              <div
                key={n.id}
                className={`gf-mentor-note-card ${n.note_type === 'INTERNAL' ? 'gf-mentor-note-card--internal' : ''}`}
                id={`note-card-${n.id}`}
              >
                <div className="gf-mentor-note-card__top">
                  <div className="gf-mentor-note-card__badges">
                    {getNoteTypeBadge(n.note_type)}
                    {n.note_type !== 'INTERNAL' && (
                      <Badge variant={n.status === 'ACKNOWLEDGED' ? 'success' : 'neutral'}>
                        {n.status === 'ACKNOWLEDGED' ? 'Acknowledged by Student' : 'Unread / Pending'}
                      </Badge>
                    )}
                    {n.related_resource_type && (
                      <span className="gf-mentor-note-card__resource">
                        Target: {n.related_resource_type}
                      </span>
                    )}
                  </div>
                  <span className="gf-mentor-note-card__date">
                    {n.created_at ? new Date(n.created_at).toLocaleDateString() : ''}
                  </span>
                </div>

                <h3 className="gf-mentor-note-card__title">{n.title}</h3>
                <p className="gf-mentor-note-card__message">{n.message}</p>

                {n.note_type === 'INTERNAL' && (
                  <div className="gf-mentor-note-card__internal-tag">
                    ℹ️ Internal note — this record is private to mentors and never exposed to the student workspace.
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Note Modal */}
      {isModalOpen && (
        <div className="gf-modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="create-note-title">
          <div className="gf-modal-card gf-modal-card--lg">
            <div className="gf-modal-header">
              <h2 id="create-note-title" className="gf-modal-title">
                Create Mentor Note / Feedback
              </h2>
              <button
                type="button"
                className="gf-modal-close"
                onClick={handleCloseModal}
                aria-label="Close dialog"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateNote} className="gf-modal-form" id="create-mentor-note-form">
              {modalError && (
                <div className="gf-modal-error" role="alert" id="note-modal-error">
                  <span>⚠️</span> {modalError}
                </div>
              )}

              <div className="gf-modal-field">
                <label htmlFor="note-title-input" className="gf-modal-label">
                  Note Title <span className="gf-modal-required">*</span>
                </label>
                <input
                  id="note-title-input"
                  type="text"
                  className="gf-modal-input"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Architecture Critique — Milestone 2"
                  maxLength={255}
                  disabled={isSubmitting}
                  autoFocus
                />
              </div>

              <div className="gf-modal-field">
                <label htmlFor="note-type-select" className="gf-modal-label">
                  Note Type & Visibility <span className="gf-modal-required">*</span>
                </label>
                <select
                  id="note-type-select"
                  className="gf-modal-select"
                  value={noteType}
                  onChange={(e) => setNoteType(e.target.value as any)}
                  disabled={isSubmitting}
                >
                  <option value="FEEDBACK">Student Feedback (Constructive review/critique)</option>
                  <option value="ACTIONABLE">Actionable Guidance (Specific changes requested)</option>
                  <option value="INFORMATIONAL">Informational (General guidance note)</option>
                  <option value="INTERNAL">🔒 Internal Mentor Note (Private, hidden from student)</option>
                </select>
                <small className="gf-modal-hint">
                  {noteType === 'INTERNAL'
                    ? '🔒 Private to mentors only. Will NOT appear on the student workspace.'
                    : 'Delivered directly to the student under Mentor Feedback.'}
                </small>
              </div>

              <div className="gf-modal-field">
                <label htmlFor="note-resource-select" className="gf-modal-label">
                  Related Resource Focus
                </label>
                <select
                  id="note-resource-select"
                  className="gf-modal-select"
                  value={relatedType}
                  onChange={(e) => setRelatedType(e.target.value)}
                  disabled={isSubmitting}
                >
                  <option value="PROJECT">General Project</option>
                  <option value="BLUEPRINT">Blueprint Specification</option>
                  <option value="MILESTONE">Milestone</option>
                  <option value="TASK">Task Execution</option>
                  <option value="RISK">Risk Mitigation</option>
                </select>
              </div>

              <div className="gf-modal-field">
                <label htmlFor="note-message-input" className="gf-modal-label">
                  Message Content <span className="gf-modal-required">*</span>
                </label>
                <textarea
                  id="note-message-input"
                  className="gf-modal-textarea"
                  rows={5}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Enter detailed feedback, critique, recommendations, or internal observations..."
                  disabled={isSubmitting}
                />
              </div>

              <div className="gf-modal-actions">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={handleCloseModal}
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  disabled={isSubmitting || !title.trim() || !message.trim()}
                  id="submit-note-btn"
                >
                  {isSubmitting ? 'Saving...' : 'Create Note'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
