import { useState, type FormEvent, type ChangeEvent } from 'react';
import { API_BASE_URL } from '@/lib/api/client';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { SectionReveal } from '@/components/ui/SectionReveal';
import { cn } from '@/utils/cn';
import './Contact.css';

interface FormData {
  name: string;
  email: string;
  reason: string;
  message: string;
}

interface FormErrors {
  name?: string;
  email?: string;
  reason?: string;
  message?: string;
}

const DISCUSSION_TOPICS = [
  {
    tag: 'Product',
    title: 'Product Inquiries',
    desc: 'Questions regarding GrowFlow workflows, agent capabilities, and project progression gates.',
  },
  {
    tag: 'Projects',
    title: 'Project Development',
    desc: 'Ideas for building disciplined, multi-agent structured projects and blueprint specifications.',
  },
  {
    tag: 'Mentorship',
    title: 'Mentorship & Supervision',
    desc: 'Inquiries about student cohort supervision, milestone review protocols, and mentor tooling.',
  },
  {
    tag: 'Engineering',
    title: 'Technical Discussion',
    desc: 'In-depth dialogue on architecture, LangGraph orchestration, RAG partitioning, and reliability.',
  },
  {
    tag: 'Feedback',
    title: 'Platform Feedback',
    desc: 'Constructive suggestions for platform design, usability, developer experience, and documentation.',
  },
] as const;

const REASON_OPTIONS = [
  { value: '', label: 'Select a discussion topic...' },
  { value: 'general', label: 'General question' },
  { value: 'product', label: 'Product' },
  { value: 'project', label: 'Project' },
  { value: 'mentorship', label: 'Mentorship' },
  { value: 'engineering', label: 'Engineering' },
  { value: 'feedback', label: 'Feedback' },
  { value: 'other', label: 'Other' },
] as const;

type SubmitStatus = 'idle' | 'submitting' | 'success' | 'error';

/**
 * P04 — Contact
 *
 * Route: /contact
 * Audience: Public / unauthenticated
 * Purpose: Focused, calm, editorial contact experience and inquiry interface.
 * Authoritative Mailbox: neurachat.support@gmail.com
 */
export function Contact() {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    reason: '',
    message: '',
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [status, setStatus] = useState<SubmitStatus>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const validate = (): boolean => {
    const nextErrors: FormErrors = {};

    if (!formData.name.trim()) {
      nextErrors.name = 'Please provide your full name.';
    } else if (formData.name.trim().length < 2) {
      nextErrors.name = 'Name must be at least 2 characters.';
    }

    if (!formData.email.trim()) {
      nextErrors.email = 'Please provide an email address.';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim())) {
      nextErrors.email = 'Please enter a valid email address.';
    }

    if (!formData.reason) {
      nextErrors.reason = 'Please select a topic for your inquiry.';
    }

    if (!formData.message.trim()) {
      nextErrors.message = 'Please enter a message.';
    } else if (formData.message.trim().length < 10) {
      nextErrors.message = 'Message must be at least 10 characters.';
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleTopicClick = (tag: string) => {
    const topicMap: Record<string, string> = {
      Product: 'product',
      Projects: 'project',
      Mentorship: 'mentorship',
      Engineering: 'engineering',
      Feedback: 'feedback',
    };
    const val = topicMap[tag] || tag.toLowerCase();
    setFormData((prev) => ({ ...prev, reason: val }));
    if (errors.reason) {
      setErrors((prev) => ({ ...prev, reason: undefined }));
    }
  };

  const handleReset = () => {
    setFormData({
      name: '',
      email: '',
      reason: '',
      message: '',
    });
    setErrors({});
    setStatus('idle');
    setErrorMessage(null);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!validate()) {
      return;
    }

    setStatus('submitting');
    setErrorMessage(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/contact`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name.trim(),
          email: formData.email.trim(),
          discussion_topic: formData.reason,
          message: formData.message.trim(),
        }),
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        if (response.status === 409) {
          setErrorMessage(
            'This message has already been received. Please allow a moment before submitting another inquiry.',
          );
        } else if (response.status === 422) {
          setErrorMessage('Please check your inputs and ensure all fields are valid.');
        } else {
          setErrorMessage(
            data?.error?.message || "We couldn't submit your message. Please try again in a moment.",
          );
        }
        setStatus('error');
        return;
      }

      setStatus('success');
    } catch {
      setStatus('error');
      setErrorMessage(
        "We couldn't submit your message. Please check your connection and try again in a moment.",
      );
    }
  };

  return (
    <div className="p04-page">
      {/* 1. Hero */}
      <HeroSection />

      {/* 2. Composition Section: Left = Topics, Right = Form */}
      <SectionReveal className="p04-section">
        <div className="p04-section__inner">
          <div className="p04-editorial-grid">
            {/* Left Column: Topics */}
            <div className="p04-topics-col">
              <div className="p04-col-head">
                <span className="p04-eyebrow">WHAT CAN WE TALK ABOUT?</span>
                <h2 className="p04-col-h2">What can we talk about?</h2>
                <p className="p04-col-copy">
                  Whether you are evaluating GrowFlow for your university, exploring a project idea,
                  or interested in our multi-agent architecture, we welcome disciplined technical conversations.
                </p>
              </div>

              <div className="p04-topics-list" role="list">
                {DISCUSSION_TOPICS.map((topic) => {
                  const topicValue =
                    topic.tag === 'Product'
                      ? 'product'
                      : topic.tag === 'Projects'
                        ? 'project'
                        : topic.tag === 'Mentorship'
                          ? 'mentorship'
                          : topic.tag === 'Engineering'
                            ? 'engineering'
                            : 'feedback';
                  const isSelected = formData.reason === topicValue;

                  return (
                    <div
                      key={topic.tag}
                      className={cn(
                        'p04-topic-item gf-interactive',
                        isSelected && 'p04-topic-item--selected',
                      )}
                      role="button"
                      tabIndex={0}
                      aria-pressed={isSelected}
                      onClick={() => handleTopicClick(topic.tag)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          handleTopicClick(topic.tag);
                        }
                      }}
                    >
                      <div className="p04-topic-header">
                        <strong className="p04-topic-title">{topic.title}</strong>
                        <Badge variant={isSelected ? 'accent' : 'neutral'}>{topic.tag}</Badge>
                      </div>
                      <p className="p04-topic-desc">{topic.desc}</p>
                    </div>
                  );
                })}
              </div>

              <div className="p04-channels-card">
                <span className="p04-channels-tag">COLLABORATION DIRECTIVE</span>
                <p className="p04-channels-text">
                  GrowFlow is built as a deterministic platform for structured project development.
                  Architecture specifications and roadmap items are version-controlled and frozen at
                  milestone gates.
                </p>
              </div>

              {/* Direct Mailbox Correspondence */}
              <div className="p04-direct-card">
                <span className="p04-direct-tag">PREFER DIRECT EMAIL?</span>
                <p className="p04-direct-text">
                  You can reach our team directly at{' '}
                  <a href="mailto:neurachat.support@gmail.com" className="p04-direct-link">
                    neurachat.support@gmail.com
                  </a>
                </p>
              </div>
            </div>

            {/* Right Column: Contact Form */}
            <div className="p04-form-col">
              <div className="p04-form-box">
                {status === 'success' ? (
                  <div className="p04-success-state" role="status" aria-live="polite">
                    <div className="p04-success-badge">
                      <Badge variant="accent">MESSAGE RECEIVED</Badge>
                    </div>
                    <h3 className="p04-success-title">Message received.</h3>
                    <p className="p04-success-copy">
                      Thanks for reaching out. Your message has been submitted to the GrowFlow team.
                    </p>
                    <div className="p04-success-actions">
                      <Button variant="secondary" size="md" onClick={handleReset}>
                        Send Another Message
                      </Button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="p04-form-head">
                      <h3 className="p04-form-title">Send a message</h3>
                      <p className="p04-form-sub">
                        Fill out the fields below with your context or inquiry.
                      </p>
                    </div>

                    <form className="p04-form" onSubmit={handleSubmit} noValidate>
                      {/* Name */}
                      <div className="p04-field">
                        <label htmlFor="contact-name" className="p04-label">
                          Your Name <span className="p04-required" aria-hidden="true">*</span>
                        </label>
                        <input
                          id="contact-name"
                          name="name"
                          type="text"
                          disabled={status === 'submitting'}
                          className={`p04-input ${errors.name ? 'p04-input--error' : ''}`}
                          placeholder="Jane Doe"
                          value={formData.name}
                          onChange={handleChange}
                          aria-required="true"
                          aria-invalid={!!errors.name}
                          aria-describedby={errors.name ? 'name-error' : undefined}
                        />
                        {errors.name && (
                          <span id="name-error" className="p04-error" role="alert">
                            {errors.name}
                          </span>
                        )}
                      </div>

                      {/* Email */}
                      <div className="p04-field">
                        <label htmlFor="contact-email" className="p04-label">
                          Email Address <span className="p04-required" aria-hidden="true">*</span>
                        </label>
                        <input
                          id="contact-email"
                          name="email"
                          type="email"
                          disabled={status === 'submitting'}
                          className={`p04-input ${errors.email ? 'p04-input--error' : ''}`}
                          placeholder="jane@example.com"
                          value={formData.email}
                          onChange={handleChange}
                          aria-required="true"
                          aria-invalid={!!errors.email}
                          aria-describedby={errors.email ? 'email-error' : undefined}
                        />
                        {errors.email && (
                          <span id="email-error" className="p04-error" role="alert">
                            {errors.email}
                          </span>
                        )}
                      </div>

                      {/* Reason */}
                      <div className="p04-field">
                        <label htmlFor="contact-reason" className="p04-label">
                          Discussion Topic <span className="p04-required" aria-hidden="true">*</span>
                        </label>
                        <select
                          id="contact-reason"
                          name="reason"
                          disabled={status === 'submitting'}
                          className={`p04-select ${errors.reason ? 'p04-input--error' : ''}`}
                          value={formData.reason}
                          onChange={handleChange}
                          aria-required="true"
                          aria-invalid={!!errors.reason}
                          aria-describedby={errors.reason ? 'reason-error' : undefined}
                        >
                          {REASON_OPTIONS.map((opt) => (
                            <option key={opt.value} value={opt.value} disabled={opt.value === ''}>
                              {opt.label}
                            </option>
                          ))}
                        </select>
                        {errors.reason && (
                          <span id="reason-error" className="p04-error" role="alert">
                            {errors.reason}
                          </span>
                        )}
                      </div>

                      {/* Message */}
                      <div className="p04-field">
                        <div className="p04-label-row">
                          <label htmlFor="contact-message" className="p04-label">
                            Message <span className="p04-required" aria-hidden="true">*</span>
                          </label>
                          <span className="p04-char-count">{formData.message.length} / 2000</span>
                        </div>
                        <textarea
                          id="contact-message"
                          name="message"
                          rows={5}
                          maxLength={2000}
                          disabled={status === 'submitting'}
                          className={`p04-textarea ${errors.message ? 'p04-input--error' : ''}`}
                          placeholder="Tell us what you're working on or what you'd like to discuss..."
                          value={formData.message}
                          onChange={handleChange}
                          aria-required="true"
                          aria-invalid={!!errors.message}
                          aria-describedby={errors.message ? 'message-error' : undefined}
                        />
                        {errors.message && (
                          <span id="message-error" className="p04-error" role="alert">
                            {errors.message}
                          </span>
                        )}
                      </div>

                      {/* Failure / Error Banner */}
                      {status === 'error' && (
                        <div className="p04-notice p04-notice--error" role="alert" aria-live="assertive">
                          <span className="p04-notice-icon" aria-hidden="true">⚠</span>
                          <div className="p04-notice-content">
                            <strong className="p04-notice-title">We couldn't submit your message.</strong>
                            <p className="p04-notice-desc">
                              {errorMessage || 'Please try again in a moment.'}
                            </p>
                          </div>
                        </div>
                      )}

                      {/* CTA Submit Button */}
                      <div className="p04-form-actions">
                        <Button type="submit" size="lg" disabled={status === 'submitting'}>
                          {status === 'submitting' ? 'Submitting Message...' : 'Send Message'}
                        </Button>
                      </div>
                    </form>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </SectionReveal>

      {/* 5. Closing Statement */}
      <ClosingStatementSection />

      {/* 6. Final CTA */}
      <FinalCtaSection />
    </div>
  );
}

/* ==========================================================================
   1. Hero Section
   ========================================================================== */

function HeroSection() {
  return (
    <section className="p04-hero" aria-labelledby="contact-hero-heading">
      <div className="p04-hero__inner">
        <div className="p04-hero__header">
          <span className="p04-hero__eyebrow">
            <span className="p04-hero__eyebrow-dot" />
            LET'S TALK
          </span>
          <h1 id="contact-hero-heading" className="p04-hero__h1">
            Have something worth building?
          </h1>
          <p className="p04-hero__copy">
            Whether you're exploring GrowFlow, building a project, thinking about mentorship,
            or want to understand the system more deeply, we'd love to hear what you're working on.
          </p>

          <div className="p04-hero__chips">
            <Badge variant="accent">Structured Development</Badge>
            <Badge variant="neutral">Mentorship Alignment</Badge>
            <Badge variant="info">Technical Architecture</Badge>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ==========================================================================
   5. Closing Contact Statement
   ========================================================================== */

function ClosingStatementSection() {
  return (
    <SectionReveal className="p04-section p04-section--alt">
      <div className="p04-section__inner">
        <div className="p04-closing-banner">
          <span className="p04-closing-eyebrow">BUILD · SUPERVISE · GOVERN</span>
          <h2 className="p04-closing-h2">Good systems start with good conversations.</h2>
          <p className="p04-closing-copy">
            GrowFlow bridges the gap between ambitious project concepts and disciplined software engineering.
            We believe transparent, thoughtful dialogue is the foundation of every successful system.
          </p>
          <span className="p04-closing-author">
            GrowFlow Engineering Team · Collaboration Directive
          </span>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   6. Final CTA Section
   ========================================================================== */

function FinalCtaSection() {
  return (
    <section className="p04-final-cta" aria-labelledby="contact-final-cta-heading">
      <div className="p04-final-cta__inner">
        <h2 id="contact-final-cta-heading" className="p04-final-cta__h2">
          Ready to explore the workspace?
        </h2>
        <p className="p04-final-cta__copy">
          Start building your project with guided intelligence and structured execution.
        </p>
        <div className="p04-final-cta__actions">
          <Button as="link" to="/auth/student/register" size="lg">
            Start Building
          </Button>
          <Button as="link" to="/documentation" variant="secondary" size="lg">
            Explore Documentation
          </Button>
        </div>
      </div>
    </section>
  );
}
