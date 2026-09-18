import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams } from 'react-router';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import {
  getAIMentorHistory,
  sendAIMentorMessage,
  executeAIOperation,
} from '@/lib/api';
import type { AIMentorConversationResponse, AIMentorMessage } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import './StudentAIMentor.css';

export function StudentAIMentor() {
  const { projectId } = useParams<{ projectId: string }>();
  const { project, isLoading: isProjectLoading, error: projectError } = useProjectWorkspace(projectId);

  const [conversation, setConversation] = useState<AIMentorConversationResponse | null>(null);
  const [messages, setMessages] = useState<AIMentorMessage[]>([]);
  const [aiAvailable, setAiAvailable] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSending, setIsSending] = useState<boolean>(false);
  const [inputText, setInputText] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [operationSuccess, setOperationSuccess] = useState<string | null>(null);
  const [executingActionId, setExecutingActionId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    if (typeof messagesEndRef.current?.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const fetchHistory = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getAIMentorHistory(projectId);
      setConversation(data);
      setMessages(data.messages || []);
      setAiAvailable(data.ai_available);
    } catch (err: any) {
      setError(err?.message || 'Failed to initialize AI Mentor conversation.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void fetchHistory();
  }, [fetchHistory]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (textToSend?: string) => {
    const text = textToSend || inputText;
    if (!projectId || !text.trim() || isSending) return;

    setIsSending(true);
    setError(null);
    setOperationSuccess(null);

    // Optimistic user message
    const tempUserMsg: AIMentorMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: text.trim(),
      sources: [],
      suggested_action: null,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    if (!textToSend) setInputText('');

    try {
      const resp = await sendAIMentorMessage(projectId, text.trim());
      setAiAvailable(resp.ai_available);
      // Replace optimistic or append server responses
      setMessages((prev) => {
        const withoutTemp = prev.filter((m) => m.id !== tempUserMsg.id);
        return [...withoutTemp, resp.user_message, resp.assistant_message];
      });
    } catch (err: any) {
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMsg.id));
      setInputText(text);
      setError(err?.message || 'Failed to send message to AI Mentor.');
    } finally {
      setIsSending(false);
    }
  };

  const handleExecuteAction = async (msg: AIMentorMessage) => {
    if (!projectId || !msg.suggested_action) return;

    const action = msg.suggested_action;
    const confirmMsg = `Do you want to confirm and execute this action?\n\nAction: ${action.label} (${action.action_type})`;
    if (!window.confirm(confirmMsg)) return;

    setExecutingActionId(msg.id);
    setError(null);
    setOperationSuccess(null);

    try {
      const res = await executeAIOperation(projectId, action.action_type, action.payload);

      setOperationSuccess(
        res?.status
          ? `Successfully executed: ${action.label} (${res.status})`
          : `Successfully executed: ${action.label}`
      );
    } catch (err: any) {
      setError(err?.message || 'Failed to execute proposed AI operation.');
    } finally {
      setExecutingActionId(null);
    }
  };

  if (isProjectLoading || (isLoading && !conversation)) {
    return (
      <div className="gf-ai-mentor-page">
        <div className="gf-ai-mentor-page__loading" role="status">
          <div className="gf-ai-mentor-page__spinner" />
          <p>Connecting to AI Project Mentor...</p>
        </div>
      </div>
    );
  }

  if (projectError || !project) {
    return (
      <div className="gf-ai-mentor-page">
        <div className="gf-ai-mentor-page__error" role="alert">
          <h2>Error Loading Project</h2>
          <p>{(typeof projectError === 'string' ? projectError : projectError?.message) || 'Project not found.'}</p>
        </div>
      </div>
    );
  }

  const promptSuggestions = [
    'How should I prioritize my upcoming sprint tasks?',
    'Analyze my current project risks and recommend mitigation steps.',
    'Review my system architecture and technical stack choices.',
    'What documentation should I prepare for mentor review?',
  ];

  return (
    <div className="gf-ai-mentor-page" id="student-ai-mentor-screen">
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={Boolean(project.group_id)}
      />

      <div className="gf-ai-mentor-page__container">
        <header className="gf-ai-mentor-page__header">
          <div className="gf-ai-mentor-page__header-text">
            <h2 className="gf-ai-mentor-page__title">AI Project Mentor</h2>
            <p className="gf-ai-mentor-page__subtitle">
              Context-aware guidance grounded directly in your project blueprint, tasks, and deliverables.
            </p>
          </div>
          <div className="gf-ai-mentor-page__status">
            {aiAvailable ? (
              <Badge variant="success" dot>
                AI Mentor Connected
              </Badge>
            ) : (
              <Badge variant="warning" dot>
                AI Mentor Offline (Truthful Fallback)
              </Badge>
            )}
          </div>
        </header>

        {operationSuccess && (
          <div className="gf-ai-mentor-page__alert gf-ai-mentor-page__alert--success" role="alert">
            <span>✓</span> {operationSuccess}
          </div>
        )}

        {error && (
          <div className="gf-ai-mentor-page__alert gf-ai-mentor-page__alert--danger" role="alert">
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Chat Area */}
        <div className="gf-ai-mentor-chat-card">
          <div className="gf-ai-mentor-messages" id="ai-mentor-messages-list">
            {messages.length > 0 ? (
              messages.map((msg) => {
                const isUser = msg.role === 'user';
                return (
                  <div
                    key={msg.id}
                    className={`gf-ai-mentor-bubble-wrapper ${
                      isUser ? 'gf-ai-mentor-bubble-wrapper--user' : 'gf-ai-mentor-bubble-wrapper--assistant'
                    }`}
                  >
                    <div className="gf-ai-mentor-bubble-meta">
                      <span className="gf-ai-mentor-bubble-sender">
                        {isUser ? 'You' : 'AI Mentor'}
                      </span>
                      {msg.created_at && (
                        <span className="gf-ai-mentor-bubble-time">
                          {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      )}
                    </div>

                    <div className="gf-ai-mentor-bubble-content">
                      <p className="gf-ai-mentor-bubble-text">{msg.content}</p>

                      {/* Source citations */}
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="gf-ai-mentor-sources">
                          <span className="gf-ai-mentor-sources-title">Grounded in:</span>
                          {msg.sources.map((src, sIdx) => (
                            <span key={sIdx} className="gf-ai-mentor-source-chip">
                              📄 {src.title || src.section}
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Suggested Action Card */}
                      {msg.suggested_action && (
                        <div className="gf-ai-mentor-action-box">
                          <div className="gf-ai-mentor-action-box__header">
                            <span className="gf-ai-mentor-action-badge">Suggested Action</span>
                            <span className="gf-ai-mentor-action-type">
                              {msg.suggested_action.action_type}
                            </span>
                          </div>
                          <p className="gf-ai-mentor-action-label">{msg.suggested_action.label}</p>
                          <Button
                            size="sm"
                            variant="primary"
                            onClick={() => handleExecuteAction(msg)}
                            disabled={executingActionId === msg.id}
                            id={`ai-action-btn-${msg.id}`}
                          >
                            {executingActionId === msg.id ? 'Executing...' : 'Confirm & Execute Action'}
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            ) : (
              <EmptyState
                title="Start a conversation with your AI Mentor"
                description="Ask anything regarding your project roadmap, sprint deliverables, architectural trade-offs, or blueprint specifications."
              />
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Prompt Suggestions */}
          <div className="gf-ai-mentor-suggestions">
            <span className="gf-ai-mentor-suggestions-label">Suggested questions:</span>
            <div className="gf-ai-mentor-suggestions-list">
              {promptSuggestions.map((sug, i) => (
                <button
                  key={i}
                  type="button"
                  className="gf-ai-mentor-suggestion-chip"
                  onClick={() => handleSendMessage(sug)}
                  disabled={isSending}
                >
                  {sug}
                </button>
              ))}
            </div>
          </div>

          {/* Input Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void handleSendMessage();
            }}
            className="gf-ai-mentor-input-form"
            id="ai-mentor-send-form"
          >
            <input
              type="text"
              placeholder={
                aiAvailable
                  ? 'Ask a question about your project blueprint or sprint...'
                  : 'AI Mentor is currently in fallback mode (truthful status)...'
              }
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="gf-ai-mentor-input"
              id="ai-mentor-prompt-input"
              disabled={isSending}
            />
            <Button
              type="submit"
              variant="primary"
              disabled={!inputText.trim() || isSending}
              id="ai-mentor-send-btn"
            >
              {isSending ? 'Sending...' : 'Send'}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
