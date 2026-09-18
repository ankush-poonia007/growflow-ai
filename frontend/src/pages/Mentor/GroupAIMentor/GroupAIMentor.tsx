import { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router';
import { getMentorGroup, getGroupAIStatus, sendGroupAIMessage } from '@/lib/api/client';
import type { GroupResponse, MentorAIStatusResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import './GroupAIMentor.css';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{ title: string; section?: string }>;
  created_at: string;
}

export function GroupAIMentor() {
  const { groupId } = useParams<{ groupId: string }>();
  const [group, setGroup] = useState<GroupResponse | null>(null);
  const [aiStatus, setAiStatus] = useState<MentorAIStatusResponse | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    if (typeof messagesEndRef.current?.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    if (!groupId) return;
    let mounted = true;

    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const [gRes, sRes] = await Promise.all([
          getMentorGroup(groupId!),
          getGroupAIStatus(groupId!),
        ]);

        if (mounted) {
          setGroup(gRes);
          setAiStatus(sRes);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : 'Failed to connect to Group AI Mentor.';
          setError(msg);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadData();
    return () => {
      mounted = false;
    };
  }, [groupId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!groupId || !inputText.trim() || isSending) return;

    const queryText = inputText.trim();
    setIsSending(true);
    setError(null);

    const tempUserMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: queryText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setInputText('');

    try {
      const historyPayload = messages.map((m) => ({ role: m.role, content: m.content }));
      const resp = await sendGroupAIMessage(groupId, { message: queryText, history: historyPayload });

      setAiStatus((prev) => prev ? { ...prev, ai_available: resp.ai_available } : null);

      setMessages((prev) => {
        const withoutTemp = prev.filter((m) => m.id !== tempUserMsg.id);
        return [
          ...withoutTemp,
          {
            id: resp.user_message.id,
            role: 'user',
            content: resp.user_message.content,
            created_at: resp.user_message.created_at,
          },
          {
            id: resp.assistant_message.id,
            role: 'assistant',
            content: resp.assistant_message.content,
            sources: resp.assistant_message.sources,
            created_at: resp.assistant_message.created_at,
          },
        ];
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to consult Group AI Mentor.';
      setError(msg);
    } finally {
      setIsSending(false);
    }
  };

  if (loading) {
    return (
      <div className="gf-group-ai-page" id="group-ai-loading">
        <Skeleton height="60px" style={{ borderRadius: '12px', marginBottom: '1.5rem' }} />
        <Skeleton height="40px" style={{ borderRadius: '8px', marginBottom: '1.5rem', width: '380px' }} />
        <Skeleton height="400px" style={{ borderRadius: '16px' }} />
      </div>
    );
  }

  if (error && !group) {
    return (
      <div className="gf-group-ai-page" id="group-ai-error">
        <PageHeader
          eyebrow="COHORT SUPERVISION"
          title="AI Consultation Unavailable"
          breadcrumbs={[
            { label: 'Groups', to: '/mentor/groups' },
            { label: 'AI Mentor' },
          ]}
        />
        <div className="gf-group-ai__error-card" role="alert">
          <h3>Supervision Access Restricted</h3>
          <p>{error || 'This student group does not exist or you do not have permission to access Group AI.'}</p>
          <Button as="link" to="/mentor/groups" variant="secondary">
            Return to Groups Directory
          </Button>
        </div>
      </div>
    );
  }

  const isOffline = aiStatus ? !aiStatus.ai_available : false;

  return (
    <div className="gf-group-ai-page" id="group-ai-container">
      <PageHeader
        eyebrow={`AI MENTOR · ${group?.name || 'COHORT'}`}
        title={`AI Mentor · ${group?.name}`}
        breadcrumbs={[
          { label: 'Groups', to: '/mentor/groups' },
          { label: group?.name || 'Cohort', to: `/mentor/groups/${groupId}` },
          { label: 'AI Mentor' },
        ]}
        badge={
          <div className="gf-group-ai__badges">
            <Badge variant="info">Group Scope: {group?.name}</Badge>
            {isOffline && <Badge variant="warning">AI Offline</Badge>}
          </div>
        }
      />

      {/* Cohort Subnav Tabs */}
      <nav className="gf-group-workspace__tabs" aria-label="Cohort sections">
        <Link to={`/mentor/groups/${groupId}`} className="gf-group-workspace__tab">
          Overview
        </Link>
        <Link to={`/mentor/groups/${groupId}/students`} className="gf-group-workspace__tab">
          Students
        </Link>
        <Link to={`/mentor/groups/${groupId}/projects`} className="gf-group-workspace__tab">
          Projects
        </Link>
        <Link to={`/mentor/groups/${groupId}/at-risk`} className="gf-group-workspace__tab">
          At-Risk
        </Link>
        <Link to={`/mentor/groups/${groupId}/activity`} className="gf-group-workspace__tab">
          Activity
        </Link>
        <Link
          to={`/mentor/groups/${groupId}/ai`}
          className="gf-group-workspace__tab gf-group-workspace__tab--active"
          aria-current="page"
        >
          AI Mentor
        </Link>
      </nav>

      {/* Offline Truthful Banner */}
      {isOffline && (
        <div className="gf-group-ai__offline-banner" role="alert" id="group-ai-offline-banner">
          <div className="gf-group-ai__offline-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <div className="gf-group-ai__offline-text">
            <strong>AI Provider Offline:</strong> OpenRouter provider keys are missing from server configuration. Live AI consultations are unavailable until valid credentials are configured.
          </div>
        </div>
      )}

      {/* Chat Container */}
      <div className="gf-group-ai__chat-card" id="group-ai-chat-card">
        <div className="gf-group-ai__chat-header">
          <div>
            <span className="gf-group-ai__scope-tag">BOUNDED TO THIS COHORT ONLY</span>
            <h2 className="gf-group-ai__chat-title">Cohort Supervisory Consultation</h2>
          </div>
          <span className="gf-group-ai__read-only-tag">READ-ONLY SUPERVISION</span>
        </div>

        {/* Message Thread */}
        <div className="gf-group-ai__messages" id="group-ai-messages" role="log" aria-live="polite">
          {messages.length === 0 ? (
            <div className="gf-group-ai__empty" id="group-ai-empty">
              <div className="gf-group-ai__empty-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="1.75">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
              </div>
              <h3 className="gf-group-ai__empty-title">Ask Group AI Mentor</h3>
              <p className="gf-group-ai__empty-desc">
                Inquire about project milestone progress, risk tracking, or student participation trends specifically within <strong>{group?.name}</strong>.
              </p>
              <div className="gf-group-ai__prompt-suggestions">
                <button
                  type="button"
                  className="gf-group-ai__suggestion-btn"
                  onClick={() => setInputText('Summarize the current progress and phases of all projects in this cohort.')}
                >
                  "Summarize current project phases & progress"
                </button>
                <button
                  type="button"
                  className="gf-group-ai__suggestion-btn"
                  onClick={() => setInputText('Which projects in this group currently have open risks or help requests?')}
                >
                  "Identify projects with open risks or help requests"
                </button>
              </div>
            </div>
          ) : (
            messages.map((m) => (
              <div
                key={m.id}
                className={`gf-group-ai-message gf-group-ai-message--${m.role}`}
                id={`group-ai-msg-${m.id}`}
              >
                <div className="gf-group-ai-message__header">
                  <span className="gf-group-ai-message__author">
                    {m.role === 'user' ? 'You (Mentor)' : 'AI Mentor'}
                  </span>
                </div>
                <div className="gf-group-ai-message__body">
                  <p>{m.content}</p>
                  {m.sources && m.sources.length > 0 && (
                    <div className="gf-group-ai-message__sources">
                      <span className="gf-group-ai-message__sources-label">Grounded in:</span>
                      {m.sources.map((s, idx) => (
                        <span key={idx} className="gf-group-ai-message__source-badge">
                          {s.title} {s.section ? `(${s.section})` : ''}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {isSending && (
            <div className="gf-group-ai-message gf-group-ai-message--assistant gf-group-ai-message--loading">
              <div className="gf-group-ai-message__author">AI Mentor</div>
              <div className="gf-group-ai-message__typing">
                <span>Analyzing cohort context...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form className="gf-group-ai__input-form" onSubmit={handleSendMessage} id="group-ai-form">
          <input
            type="text"
            className="gf-group-ai__input"
            id="group-ai-input"
            placeholder={`Ask about ${group?.name || 'this cohort'}...`}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={isSending}
            aria-label="Message Group AI Mentor"
          />
          <Button
            type="submit"
            variant="primary"
            disabled={isSending || !inputText.trim()}
            id="group-ai-send-btn"
          >
            {isSending ? 'Analyzing...' : 'Send'}
          </Button>
        </form>
      </div>
    </div>
  );
}
