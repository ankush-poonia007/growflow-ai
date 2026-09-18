import { useEffect, useState, useRef } from 'react';
import { getMentorAIStatus, sendMentorAIMessage } from '@/lib/api/client';
import type { MentorAIStatusResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import './MentorAI.css';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{ title: string; section?: string }>;
  created_at: string;
}

export function MentorAI() {
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
    let mounted = true;

    async function loadStatus() {
      try {
        setLoading(true);
        setError(null);
        const sRes = await getMentorAIStatus();
        if (mounted) {
          setAiStatus(sRes);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : 'Failed to connect to Mentor Portfolio AI.';
          setError(msg);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadStatus();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputText.trim() || isSending) return;

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
      const resp = await sendMentorAIMessage({ message: queryText, history: historyPayload });

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
      const msg = err instanceof Error ? err.message : 'Failed to consult Mentor AI.';
      setError(msg);
    } finally {
      setIsSending(false);
    }
  };

  if (loading) {
    return (
      <div className="gf-mentor-ai-page" id="mentor-ai-loading">
        <Skeleton width="300px" height="32px" style={{ marginBottom: '1rem' }} />
        <Skeleton width="480px" height="20px" style={{ marginBottom: '2rem' }} />
        <Skeleton height="500px" style={{ borderRadius: '16px' }} />
      </div>
    );
  }

  if (error && !aiStatus) {
    return (
      <div className="gf-mentor-ai-page" id="mentor-ai-error">
        <PageHeader
          eyebrow="SUPERVISORY INTELLIGENCE"
          title="Mentor AI Unavailable"
          breadcrumbs={[
            { label: 'Overview', to: '/mentor/overview' },
            { label: 'AI Mentor' },
          ]}
        />
        <div className="gf-mentor-ai__error-card" role="alert">
          <h3>Supervision Connection Error</h3>
          <p>{error}</p>
          <Button as="link" to="/mentor/overview" variant="secondary">
            Return to Overview
          </Button>
        </div>
      </div>
    );
  }

  const isOffline = aiStatus ? !aiStatus.ai_available : false;

  return (
    <div className="gf-mentor-ai-page" id="mentor-ai-container">
      <PageHeader
        eyebrow="SUPERVISORY INTELLIGENCE · PORTFOLIO SCOPE"
        title="Mentor Portfolio AI"
        description="Cross-cohort supervisory intelligence synthesizing progress, risks, and trends across all your supervised groups, students, and projects."
        badge={
          <div className="gf-mentor-ai__badges">
            <Badge variant="info">Portfolio Scope: All Cohorts</Badge>
            {isOffline && <Badge variant="warning">AI Provider Offline</Badge>}
          </div>
        }
      />

      {/* Offline Truthful Banner */}
      {isOffline && (
        <div className="gf-mentor-ai__offline-banner" role="alert" id="mentor-ai-offline-banner">
          <div className="gf-mentor-ai__offline-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <div className="gf-mentor-ai__offline-text">
            <strong>AI Provider Offline:</strong> OpenRouter provider keys are missing from server configuration. Live portfolio AI consultations are unavailable until valid credentials are configured.
          </div>
        </div>
      )}

      {/* Chat Card */}
      <div className="gf-mentor-ai__chat-card" id="mentor-ai-chat-card">
        <div className="gf-mentor-ai__chat-header">
          <div>
            <span className="gf-mentor-ai__scope-pill">PORTFOLIO-WIDE SUPERVISION</span>
            <h2 className="gf-mentor-ai__chat-title">Cross-Cohort Supervisory Copilot</h2>
          </div>
          <span className="gf-mentor-ai__read-only-pill">READ-ONLY SUPERVISION</span>
        </div>

        {/* Message Thread */}
        <div className="gf-mentor-ai__messages" id="mentor-ai-messages" role="log" aria-live="polite">
          {messages.length === 0 ? (
            <div className="gf-mentor-ai__empty" id="mentor-ai-empty">
              <div className="gf-mentor-ai__empty-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" strokeWidth="1.75">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                </svg>
              </div>
              <h3 className="gf-mentor-ai__empty-title">Mentor Portfolio Intelligence</h3>
              <p className="gf-mentor-ai__empty-desc">
                Ask strategic portfolio-level questions synthesizing status, blockers, and at-risk projects across all your cohorts and supervised students.
              </p>
              <div className="gf-mentor-ai__prompt-suggestions">
                <button
                  type="button"
                  className="gf-mentor-ai__suggestion-btn"
                  onClick={() => setInputText('Which projects across all my cohorts currently require immediate mentor attention?')}
                >
                  "Which projects across all cohorts require immediate attention?"
                </button>
                <button
                  type="button"
                  className="gf-mentor-ai__suggestion-btn"
                  onClick={() => setInputText('Provide a high-level summary of active cohorts, student enrollment, and milestone progress.')}
                >
                  "Provide a high-level summary of cohorts, enrollment & progress"
                </button>
              </div>
            </div>
          ) : (
            messages.map((m) => (
              <div
                key={m.id}
                className={`gf-mentor-ai-message gf-mentor-ai-message--${m.role}`}
                id={`mentor-ai-msg-${m.id}`}
              >
                <div className="gf-mentor-ai-message__header">
                  <span className="gf-mentor-ai-message__author">
                    {m.role === 'user' ? 'You (Mentor)' : 'Portfolio AI Mentor'}
                  </span>
                </div>
                <div className="gf-mentor-ai-message__body">
                  <p>{m.content}</p>
                  {m.sources && m.sources.length > 0 && (
                    <div className="gf-mentor-ai-message__sources">
                      <span className="gf-mentor-ai-message__sources-label">Synthesized from:</span>
                      {m.sources.map((s, idx) => (
                        <span key={idx} className="gf-mentor-ai-message__source-badge">
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
            <div className="gf-mentor-ai-message gf-mentor-ai-message--assistant gf-mentor-ai-message--loading">
              <div className="gf-mentor-ai-message__author">Portfolio AI Mentor</div>
              <div className="gf-mentor-ai-message__typing">
                <span>Synthesizing portfolio intelligence...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form className="gf-mentor-ai__input-form" onSubmit={handleSendMessage} id="mentor-ai-form">
          <input
            type="text"
            className="gf-mentor-ai__input"
            id="mentor-ai-input"
            placeholder="Ask questions across your entire supervised portfolio..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={isSending}
            aria-label="Message Mentor Portfolio AI"
          />
          <Button
            type="submit"
            variant="primary"
            disabled={isSending || !inputText.trim()}
            id="mentor-ai-send-btn"
          >
            {isSending ? 'Synthesizing...' : 'Send'}
          </Button>
        </form>
      </div>
    </div>
  );
}
