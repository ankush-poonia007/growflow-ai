import { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams } from 'react-router';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import { getMentorNotes, acknowledgeMentorNote } from '@/lib/api';
import type { MentorNoteResponse } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import './StudentMentorFeedback.css';

export function StudentMentorFeedback() {
  const { projectId } = useParams<{ projectId: string }>();
  const { project, isLoading: isProjectLoading, error: projectError } = useProjectWorkspace(projectId);

  const [notes, setNotes] = useState<MentorNoteResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [acknowledgingId, setAcknowledgingId] = useState<string | null>(null);

  // Filter
  const [filter, setFilter] = useState<'ALL' | 'UNREAD' | 'ACKNOWLEDGED'>('ALL');

  const fetchNotes = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getMentorNotes(projectId);
      setNotes(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load mentor feedback notes.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void fetchNotes();
  }, [fetchNotes]);

  const handleAcknowledge = async (noteId: string) => {
    if (!projectId) return;
    setAcknowledgingId(noteId);
    setError(null);
    try {
      const updated = await acknowledgeMentorNote(projectId, noteId);
      setNotes((prev) => prev.map((n) => (n.id === noteId ? updated : n)));
    } catch (err: any) {
      setError(err?.message || 'Failed to acknowledge note.');
    } finally {
      setAcknowledgingId(null);
    }
  };

  const unreadCount = useMemo(() => {
    return notes.filter((n) => n.status === 'UNREAD').length;
  }, [notes]);

  const filteredNotes = useMemo(() => {
    if (filter === 'UNREAD') return notes.filter((n) => n.status === 'UNREAD');
    if (filter === 'ACKNOWLEDGED') return notes.filter((n) => n.status === 'ACKNOWLEDGED');
    return notes;
  }, [notes, filter]);

  const getNoteTypeBadge = (noteType: string) => {
    switch (noteType?.toUpperCase()) {
      case 'ACTIONABLE':
        return <Badge variant="warning">Actionable</Badge>;
      case 'FEEDBACK':
        return <Badge variant="accent">Feedback</Badge>;
      default:
        return <Badge variant="info">Informational</Badge>;
    }
  };

  if (isProjectLoading || (isLoading && notes.length === 0)) {
    return (
      <div className="gf-feedback-page">
        <div className="gf-feedback-page__loading" role="status">
          <div className="gf-feedback-page__spinner" />
          <p>Loading mentor feedback notes...</p>
        </div>
      </div>
    );
  }

  if (projectError || !project) {
    return (
      <div className="gf-feedback-page">
        <div className="gf-feedback-page__error" role="alert">
          <h2>Error Loading Project</h2>
          <p>{(typeof projectError === 'string' ? projectError : projectError?.message) || 'Project not found.'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-feedback-page" id="student-mentor-feedback-screen">
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={Boolean(project.group_id)}
      />

      <div className="gf-feedback-page__container">
        <header className="gf-feedback-page__header">
          <div className="gf-feedback-page__header-text">
            <h2 className="gf-feedback-page__title">Mentor Feedback & Guidance Notes</h2>
            <p className="gf-feedback-page__subtitle">
              Formal mentor reviews, critique, and actionable notes communicated directly to you.
            </p>
          </div>
          <div className="gf-feedback-page__status">
            {unreadCount > 0 ? (
              <Badge variant="warning" dot>
                {unreadCount} Unread Note{unreadCount > 1 ? 's' : ''}
              </Badge>
            ) : (
              <Badge variant="success">All Notes Acknowledged</Badge>
            )}
          </div>
        </header>

        {error && (
          <div className="gf-feedback-page__alert gf-feedback-page__alert--danger" role="alert">
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Filter buttons */}
        <div className="gf-feedback-filters">
          {(['ALL', 'UNREAD', 'ACKNOWLEDGED'] as const).map((tab) => (
            <button
              key={tab}
              type="button"
              className={`gf-feedback-tab-btn ${filter === tab ? 'gf-feedback-tab-btn--active' : ''}`}
              onClick={() => setFilter(tab)}
            >
              {tab === 'ALL'
                ? `All Notes (${notes.length})`
                : tab === 'UNREAD'
                ? `Unread (${unreadCount})`
                : 'Acknowledged'}
            </button>
          ))}
        </div>

        {/* Notes list */}
        <div className="gf-feedback-list" id="mentor-notes-list">
          {filteredNotes.length > 0 ? (
            filteredNotes.map((note) => {
              const isUnread = note.status === 'UNREAD';
              return (
                <div
                  key={note.id}
                  className={`gf-feedback-card ${isUnread ? 'gf-feedback-card--unread' : ''}`}
                >
                  <div className="gf-feedback-card__top">
                    <div className="gf-feedback-card__badges">
                      {getNoteTypeBadge(note.note_type)}
                      {isUnread ? (
                        <Badge variant="warning" dot>
                          Unread
                        </Badge>
                      ) : (
                        <Badge variant="success">Acknowledged</Badge>
                      )}
                      {note.related_resource_type && (
                        <span className="gf-feedback-resource">
                          Ref: {note.related_resource_type}
                        </span>
                      )}
                    </div>
                    <time className="gf-feedback-card__time">
                      {note.created_at ? new Date(note.created_at).toLocaleDateString() : ''}
                    </time>
                  </div>

                  <h3 className="gf-feedback-card__title">{note.title}</h3>
                  <p className="gf-feedback-card__message">{note.message}</p>

                  <div className="gf-feedback-card__footer">
                    <span className="gf-feedback-card__footer-meta">
                      Faculty Guidance • Informational record
                    </span>
                    {isUnread && (
                      <Button
                        size="sm"
                        variant="primary"
                        onClick={() => handleAcknowledge(note.id)}
                        disabled={acknowledgingId === note.id}
                        id={`ack-note-btn-${note.id}`}
                      >
                        {acknowledgingId === note.id ? 'Acknowledging...' : 'Acknowledge Note'}
                      </Button>
                    )}
                  </div>
                </div>
              );
            })
          ) : (
            <EmptyState
              title="No mentor notes found"
              description={
                filter === 'ALL'
                  ? 'Your mentor has not posted any notes or feedback for this project yet.'
                  : `No notes match the '${filter}' filter.`
              }
            />
          )}
        </div>
      </div>
    </div>
  );
}
