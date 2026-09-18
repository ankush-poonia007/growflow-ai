import { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { SectionReveal } from '@/components/ui/SectionReveal';
import { cn } from '@/utils/cn';
import './Features.css';

/**
 * P02 — Features
 *
 * Route: /features
 * Primary Purpose: Explain GrowFlow's major product capabilities through
 * a guided visual product story.
 *
 * Reuses Gate 06 shared components: Button, Badge, SectionReveal, tokens.
 */
export function Features() {
  const [activeSection, setActiveSection] = useState<string>('understand');

  useEffect(() => {
    const sectionIds = [
      'understand',
      'assessment',
      'blueprint',
      'execute',
      'monitor',
      'guide',
      'collaborate',
    ];

    const observers: IntersectionObserver[] = [];

    sectionIds.forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;

      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry?.isIntersecting) {
            setActiveSection(id);
          }
        },
        { rootMargin: '-30% 0px -50% 0px' },
      );

      observer.observe(el);
      observers.push(observer);
    });

    return () => {
      observers.forEach((obs) => obs.disconnect());
    };
  }, []);

  return (
    <div className="p02-page">
      <HeroSection />

      {/* Feature Flow container: scopes the sticky subnav so it only sticks during features */}
      <div className="p02-features-flow">
        <FeatureIndexNav activeSection={activeSection} />
        <UnderstandSection />
        <AssessmentSection />
        <BlueprintSection />
        <TasksMilestonesSection />
        <RoadmapSection />
        <RisksHealthSection />
        <DocumentsSection />
        <GitHubSection />
        <ActivitySection />
        <AiMentorSection />
        <MentorCollaborationSection />
      </div>

      {/* Synthesis & Governance sections */}
      <ThreePerspectivesSection />
      <AiStructureSection />
      <PersistentBackgroundSection />
      <TrustSection />
      <FinalCtaSection />
    </div>
  );
}

/* ==========================================================================
   Hero Section
   ========================================================================== */

function HeroSection() {
  return (
    <section className="p02-hero" aria-labelledby="features-hero-title">
      <div className="p02-hero__inner">
        <div className="p02-hero__header">
          <span className="p02-hero__eyebrow">
            <span className="p02-hero__eyebrow-dot" />
            THE GROWFLOW WORKSPACE
          </span>
          <h1 id="features-hero-title" className="p02-hero__h1">
            Everything your project needs to move forward.
          </h1>
          <p className="p02-hero__copy">
            GrowFlow connects assessment, planning, execution, project health, mentor supervision,
            and intelligent guidance into one structured project experience.
          </p>
          <div className="p02-hero__actions">
            <Button as="link" to="/auth/student/register" size="lg">
              Start Building
            </Button>
            <Button as="link" to="/documentation" variant="secondary" size="lg">
              Explore Documentation
            </Button>
          </div>
        </div>

        {/* Connected Multi-Surface Workspace Visual */}
        <div className="p02-hero__system" aria-label="GrowFlow workspace preview surfaces">
          <div className="p02-hero__system-bar">
            <div className="p02-hero__system-meta">
              <span>Project: BuildFlow</span>
              <span style={{ opacity: 0.4 }}>/</span>
              <span style={{ fontWeight: 400 }}>Workspace BUILD</span>
            </div>
            <Badge variant="success">Active Execution</Badge>
          </div>

          <div className="p02-hero__system-grid">
            {/* Overview Surface */}
            <div className="p02-hero__surface">
              <div className="p02-surface-label">
                <span>Overview</span>
                <span className="gf-font-mono" style={{ fontSize: '10px' }}>ID: PRJ-014</span>
              </div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--gf-color-text-primary)' }}>
                Intelligent Project Platform
              </div>
              <div style={{ fontSize: '12px', color: 'var(--gf-color-text-secondary)', lineHeight: 1.4 }}>
                Full-stack workspace with adaptive assessments and grounded AI mentor guidance.
              </div>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: 'auto' }}>
                <Badge variant="neutral">Python</Badge>
                <Badge variant="neutral">FastAPI</Badge>
                <Badge variant="neutral">PostgreSQL</Badge>
              </div>
            </div>

            {/* Tasks & Milestones Surface */}
            <div className="p02-hero__surface">
              <div className="p02-surface-label">
                <span>Milestone 03</span>
                <span style={{ color: 'var(--gf-color-accent)', fontWeight: 700 }}>75%</span>
              </div>
              <div className="p02-progress-track">
                <div className="p02-progress-fill" style={{ width: '75%' }} />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '4px' }}>
                <div style={{ fontSize: '12px', color: 'var(--gf-color-text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ color: 'var(--gf-color-success)' }}>✓</span> Define retrieval strategy
                </div>
                <div style={{ fontSize: '12px', color: 'var(--gf-color-text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ color: 'var(--gf-color-success)' }}>✓</span> Prepare document pipeline
                </div>
                <div style={{ fontSize: '12px', color: 'var(--gf-color-accent-active)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span>→</span> Implement project-scoped RAG
                </div>
              </div>
            </div>

            {/* AI Mentor Context Surface */}
            <div className="p02-hero__surface">
              <div className="p02-surface-label">
                <span>AI Mentor</span>
                <Badge variant="accent">Grounded</Badge>
              </div>
              <div style={{ fontSize: '11px', color: 'var(--gf-color-text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Context Analysis
              </div>
              <div style={{ fontSize: '12px', color: 'var(--gf-color-text-secondary)', lineHeight: 1.4, backgroundColor: 'var(--gf-color-secondary)', padding: '8px', borderRadius: '4px' }}>
                Next recommended action: Complete RAG vector indexing before proceeding to Milestone 04 evaluation.
              </div>
              <div style={{ fontSize: '11px', color: 'var(--gf-color-accent)', fontWeight: 600, marginTop: 'auto' }}>
                2 documents referenced
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ==========================================================================
   Feature Index (Sub-navigation)
   ========================================================================== */

const FEATURE_ANCHORS = [
  { label: 'Understand', href: '#understand' },
  { label: 'Assessment', href: '#assessment' },
  { label: 'Blueprint', href: '#blueprint' },
  { label: 'Execute', href: '#execute' },
  { label: 'Monitor', href: '#monitor' },
  { label: 'Guide', href: '#guide' },
  { label: 'Collaborate', href: '#collaborate' },
] as const;

function FeatureIndexNav({ activeSection }: { activeSection: string }) {
  return (
    <nav className="p02-index-nav" aria-label="Feature navigation">
      <div className="p02-index-nav__inner">
        {FEATURE_ANCHORS.map(({ label, href }) => {
          const id = href.replace('#', '');
          const isActive = activeSection === id;
          return (
            <a
              key={href}
              href={href}
              className={cn(
                'p02-index-nav__link',
                isActive && 'p02-index-nav__link--active',
              )}
              aria-current={isActive ? 'true' : undefined}
            >
              {label}
            </a>
          );
        })}
      </div>
    </nav>
  );
}

/* ==========================================================================
   01 — UNDERSTAND
   ========================================================================== */

function UnderstandSection() {
  return (
    <SectionReveal id="understand" className="p02-section">
      <div className="p02-section__inner">
        <div className="p02-split">
          <div className="p02-split__content">
            <span className="p02-split__eyebrow">01 / UNDERSTAND</span>
            <h2 className="p02-split__heading">Start with understanding, not assumptions.</h2>
            <p className="p02-split__copy">
              Every project begins with context. GrowFlow uses project information and assessment
              results to build a clearer understanding of what you're building, why you're building
              it, and what you already know.
            </p>
          </div>

          <div className="p02-split__visual">
            <div className="p02-card" role="region" aria-label="Project Profile preview">
              <div className="p02-card__header">
                <span className="p02-card__title">Project Profile</span>
                <Badge variant="neutral">Verified Context</Badge>
              </div>

              <div style={{ fontSize: 'var(--gf-text-h4-size)', fontWeight: 700, color: 'var(--gf-color-text-primary)' }}>
                BuildFlow
              </div>

              <div className="p02-profile-grid">
                <div className="p02-profile-item">
                  <span className="p02-profile-label">Project Complexity</span>
                  <div style={{ marginTop: '2px' }}>
                    <Badge variant="accent">Advanced</Badge>
                  </div>
                </div>

                <div className="p02-profile-item">
                  <span className="p02-profile-label">Student Skill Level</span>
                  <div style={{ marginTop: '2px' }}>
                    <Badge variant="info">Intermediate</Badge>
                  </div>
                </div>

                <div className="p02-profile-item p02-profile-item--full">
                  <span className="p02-profile-label">Technologies</span>
                  <div className="p02-profile-val gf-font-mono" style={{ fontSize: '13px' }}>
                    Python · FastAPI · PostgreSQL
                  </div>
                </div>

                <div className="p02-profile-item p02-profile-item--full">
                  <span className="p02-profile-label">Project Goal</span>
                  <div className="p02-profile-val">
                    Build an intelligent project workspace
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   02 — ASSESSMENT
   ========================================================================== */

function AssessmentSection() {
  return (
    <SectionReveal id="assessment" className="p02-section p02-section--alt">
      <div className="p02-section__inner">
        <div className="p02-split p02-split--reverse">
          <div className="p02-split__content">
            <span className="p02-split__eyebrow">02 / ASSESSMENT</span>
            <h2 className="p02-split__heading">A project assessment that adapts to the project.</h2>
            <p className="p02-split__copy">
              GrowFlow combines core assessment questions with project-specific questions so the
              assessment can account for the project you're actually planning to build.
            </p>
          </div>

          <div className="p02-split__visual">
            <div className="p02-card" role="region" aria-label="Assessment questionnaire fragment">
              <div className="p02-card__header">
                <span className="p02-card__title">ASSESSMENT</span>
                <div className="p02-assess-breakdown">
                  <Badge variant="neutral">10 core</Badge>
                  <span style={{ color: 'var(--gf-color-text-tertiary)', alignSelf: 'center' }}>+</span>
                  <Badge variant="accent">5 project-specific</Badge>
                </div>
              </div>

              <div className="p02-assess-header">
                <span className="p02-assess-qcount">Question 12 / 15</span>
                <span style={{ fontSize: '11px', color: 'var(--gf-color-text-tertiary)', textTransform: 'uppercase' }}>
                  Architecture & Data
                </span>
              </div>

              <div className="p02-assess-question">
                How do you plan to isolate user document collections during vector search?
              </div>

              <div className="p02-assess-options">
                <div className="p02-assess-opt">
                  <span>A.</span> Single tenant database per user
                </div>
                <div className="p02-assess-opt p02-assess-opt--selected">
                  <span>B.</span> Multi-tenant with metadata-filtered embeddings
                </div>
                <div className="p02-assess-opt">
                  <span>C.</span> Client-side ephemeral index
                </div>
              </div>

              <div className="p02-assess-note">
                Adaptive question generated based on your PostgreSQL and RAG architecture profile.
              </div>
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   03 — BLUEPRINT
   ========================================================================== */

interface BlueprintDoc {
  id: string;
  title: string;
  snippet: string;
}

const BLUEPRINT_DOCS: readonly BlueprintDoc[] = [
  { id: 'profile', title: 'Project Profile', snippet: 'Target architecture, objective, stakeholder profiles, and boundary definitions.' },
  { id: 'stack', title: 'Technology Stack', snippet: 'FastAPI, PostgreSQL with pgvector, React 19, TypeScript, and Docker containerization.' },
  { id: 'specs', title: 'Features & Specifications', snippet: 'Deterministic execution pipeline, grounded AI assistant, and mentor oversight module.' },
  { id: 'mvp', title: 'MVP Definition', snippet: 'Phase 1 core deliverables: student sign-in, project profile setup, assessment, and blueprint.' },
  { id: 'duration', title: 'Project Duration', snippet: '12-week development cycle with 5 major milestones and bi-weekly mentor review checkpoints.' },
  { id: 'risks', title: 'Risk Documentation', snippet: 'Identified retrieval degradation and prompt regression risks with mitigation strategies.' },
  { id: 'readme', title: 'README', snippet: 'Repository onboarding, local setup instructions, test commands, and environment variables.' },
  { id: 'tasks', title: 'Tasks & Milestones', snippet: '28 structured work packages mapped across canonical lifecycle phases.' },
];

function BlueprintSection() {
  const [activeDoc, setActiveDoc] = useState<BlueprintDoc>(BLUEPRINT_DOCS[1]!);

  return (
    <SectionReveal id="blueprint" className="p02-section">
      <div className="p02-section__inner">
        <div className="p02-split">
          <div className="p02-split__content">
            <span className="p02-split__eyebrow">03 / BLUEPRINT</span>
            <h2 className="p02-split__heading">Turn an idea into a blueprint you can build from.</h2>
            <p className="p02-split__copy">
              GrowFlow transforms project context and assessment results into a structured blueprint
              covering the key decisions needed to move from an idea toward implementation.
            </p>
          </div>

          <div className="p02-split__visual">
            <div className="p02-blueprint-composition" role="region" aria-label="Blueprint document suite preview">
              <div className="p02-blueprint-index">
                <span className="p02-surface-label" style={{ padding: '4px 8px', marginBottom: '4px' }}>
                  Documents
                </span>
                {BLUEPRINT_DOCS.map((doc) => (
                  <button
                    key={doc.id}
                    type="button"
                    className={cn(
                      'p02-blueprint-doc-btn',
                      activeDoc.id === doc.id && 'p02-blueprint-doc-btn--active',
                    )}
                    onClick={() => setActiveDoc(doc)}
                  >
                    <span>📄</span>
                    <span>{doc.title}</span>
                  </button>
                ))}
              </div>

              <div className="p02-blueprint-sheet">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className="p02-surface-label">Generated Artifact</span>
                  <Badge variant="success">Ready for Review</Badge>
                </div>
                <div className="p02-blueprint-sheet-title">{activeDoc.title}</div>
                <p style={{ fontSize: 'var(--gf-text-body-size)', color: 'var(--gf-color-text-secondary)', lineHeight: 1.6 }}>
                  {activeDoc.snippet}
                </p>
                <div style={{ marginTop: 'auto', paddingTop: 'var(--gf-space-4)', borderTop: '1px solid var(--gf-color-border-subtle)', display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--gf-color-text-tertiary)' }}>
                  <span>Version 2.0</span>
                  <span>Deterministic Validation Passed</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   04 — TASKS & MILESTONES
   ========================================================================== */

function TasksMilestonesSection() {
  return (
    <SectionReveal id="execute" className="p02-section p02-section--alt">
      <div className="p02-section__inner">
        <div className="p02-split p02-split--reverse">
          <div className="p02-split__content">
            <span className="p02-split__eyebrow">04 / TASKS & MILESTONES</span>
            <h2 className="p02-split__heading">Know what needs to happen next.</h2>
            <p className="p02-split__copy">
              Break the project into meaningful work. Tasks connect to milestones, outcomes,
              completion criteria, dependencies, and dates so progress has context.
            </p>
          </div>

          <div className="p02-split__visual">
            <div className="p02-card" role="region" aria-label="Task and milestone hierarchy">
              <div className="p02-card__header">
                <span className="p02-card__title">MILESTONE</span>
                <Badge variant="accent">In Progress</Badge>
              </div>

              <div className="p02-milestone-box">
                <div className="p02-milestone-info">
                  <span>Knowledge Layer</span>
                  <span className="gf-font-mono" style={{ color: 'var(--gf-color-accent)' }}>75%</span>
                </div>
                <div className="p02-progress-track">
                  <div className="p02-progress-fill" style={{ width: '75%' }} />
                </div>
              </div>

              <div className="p02-surface-label" style={{ marginBottom: '8px' }}>
                <span>TASKS</span>
                <span className="gf-font-mono">3 / 4</span>
              </div>

              <div className="p02-task-list">
                <div className="p02-task-item">
                  <span className="p02-task-icon" style={{ color: 'var(--gf-color-success)' }}>✓</span>
                  <span style={{ color: 'var(--gf-color-text-secondary)', textDecoration: 'line-through' }}>
                    Define retrieval strategy
                  </span>
                </div>

                <div className="p02-task-item">
                  <span className="p02-task-icon" style={{ color: 'var(--gf-color-success)' }}>✓</span>
                  <span style={{ color: 'var(--gf-color-text-secondary)', textDecoration: 'line-through' }}>
                    Prepare document pipeline
                  </span>
                </div>

                <div className="p02-task-item p02-task-item--active">
                  <span className="p02-task-icon" style={{ color: 'var(--gf-color-accent)' }}>→</span>
                  <span style={{ color: 'var(--gf-color-text-primary)' }}>
                    Implement project-scoped RAG
                  </span>
                </div>

                <div className="p02-task-item">
                  <span className="p02-task-icon" style={{ color: 'var(--gf-color-text-tertiary)' }}>○</span>
                  <span style={{ color: 'var(--gf-color-text-tertiary)' }}>
                    Validate retrieval quality
                  </span>
                </div>
              </div>

              <div className="p02-task-flow-banner">
                <span>Task</span>
                <span>→</span>
                <span>Milestone</span>
                <span>→</span>
                <span>Progress</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   05 — ROADMAP
   ========================================================================== */

const LIFECYCLE_STEPS = [
  { num: '01', name: 'IDEA', current: false },
  { num: '02', name: 'ASSESSMENT', current: false },
  { num: '03', name: 'BLUEPRINT', current: false },
  { num: '04', name: 'PLANNING', current: false },
  { num: '05', name: 'IMPLEMENTATION', current: true },
  { num: '06', name: 'TESTING', current: false },
  { num: '07', name: 'DEPLOYMENT', current: false },
  { num: '08', name: 'COMPLETED', current: false },
];

function RoadmapSection() {
  return (
    <SectionReveal className="p02-section">
      <div className="p02-section__inner">
        <div className="p02-roadmap-wrap">
          <div className="p02-roadmap-head">
            <span className="p02-split__eyebrow">05 / ROADMAP</span>
            <h2 className="p02-split__heading">See the project beyond today.</h2>
            <p className="p02-split__copy">
              Understand when phases begin and end, what depends on what, and where the project is heading.
            </p>
          </div>

          <div className="p02-roadmap-steps" role="list" aria-label="Canonical 8-step project lifecycle">
            {LIFECYCLE_STEPS.map((step) => (
              <div
                key={step.num}
                role="listitem"
                className={cn(
                  'p02-roadmap-step',
                  step.current && 'p02-roadmap-step--current',
                )}
              >
                <span className="p02-roadmap-step-num">{step.num}</span>
                <span>{step.name}</span>
                {step.current && (
                  <Badge variant="accent">
                    Active
                  </Badge>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   06 — RISKS & HEALTH
   ========================================================================== */

function RisksHealthSection() {
  return (
    <SectionReveal id="monitor" className="p02-section p02-section--alt">
      <div className="p02-section__inner">
        <div className="p02-split">
          <div className="p02-split__content">
            <span className="p02-split__eyebrow">06 / RISKS & HEALTH</span>
            <h2 className="p02-split__heading">See problems before they become surprises.</h2>
            <p className="p02-split__copy">
              GrowFlow keeps project risks visible alongside progress, deadlines, milestones, and
              project health. Health is calculated deterministically from active tasks and risks, not
              an opaque score.
            </p>
          </div>

          <div className="p02-split__visual">
            <div className="p02-card" role="region" aria-label="Project health and risk register">
              <div className="p02-card__header">
                <span className="p02-card__title">PROJECT HEALTH</span>
                <Badge variant="success">Healthy</Badge>
              </div>

              <div className="p02-health-metrics">
                <div className="p02-metric-box">
                  <div className="p02-metric-label">Progress</div>
                  <div className="p02-metric-val">68%</div>
                </div>
                <div className="p02-metric-box">
                  <div className="p02-metric-label">Milestones</div>
                  <div className="p02-metric-val">3 / 5</div>
                </div>
                <div className="p02-metric-box">
                  <div className="p02-metric-label">Active Risks</div>
                  <div className="p02-metric-val" style={{ color: 'var(--gf-color-warning)' }}>2</div>
                </div>
              </div>

              <div className="p02-surface-label" style={{ marginBottom: '8px' }}>
                <span>ACTIVE RISK</span>
                <span className="gf-font-mono">RSK-04</span>
              </div>

              <div className="p02-risk-card">
                <div style={{ fontWeight: 700, color: 'var(--gf-color-text-primary)' }}>
                  Retrieval quality
                </div>
                <div className="p02-risk-meta">
                  <span>Probability: <strong>Medium</strong></span>
                  <span>·</span>
                  <span>Impact: <strong style={{ color: 'var(--gf-color-danger)' }}>High</strong></span>
                </div>
                <div style={{ fontSize: '12px', color: 'var(--gf-color-text-secondary)', marginTop: '4px' }}>
                  <strong>Prevention:</strong> Define evaluation criteria before implementation.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   07 — DOCUMENTS
   ========================================================================== */

function DocumentsSection() {
  return (
    <SectionReveal className="p02-section">
      <div className="p02-section__inner">
        <div className="p02-split p02-split--reverse">
          <div className="p02-split__content">
            <span className="p02-split__eyebrow">07 / DOCUMENTS</span>
            <h2 className="p02-split__heading">Keep project knowledge organized.</h2>
            <p className="p02-split__copy">
              Blueprint documents are generated, versioned, and kept aligned with the project's
              current state. Workspaces track whether documents are current, regenerating, or require attention.
            </p>
          </div>

          <div className="p02-split__visual">
            <div className="p02-card" role="region" aria-label="Versioned project documents">
              <div className="p02-card__header">
                <span className="p02-card__title">PROJECT DOCUMENTS</span>
                <Badge variant="neutral">Version Controlled</Badge>
              </div>

              <div className="p02-doc-list">
                <div className="p02-doc-row">
                  <div>
                    <div className="p02-doc-name">README.md</div>
                    <div style={{ fontSize: '11px', color: 'var(--gf-color-text-tertiary)' }}>v3 Current</div>
                  </div>
                  <Badge variant="success">Current</Badge>
                </div>

                <div className="p02-doc-row">
                  <div>
                    <div className="p02-doc-name">Technology Stack</div>
                    <div style={{ fontSize: '11px', color: 'var(--gf-color-text-tertiary)' }}>v2 Current</div>
                  </div>
                  <Badge variant="success">Current</Badge>
                </div>

                <div className="p02-doc-row">
                  <div>
                    <div className="p02-doc-name">Features & Specifications</div>
                    <div style={{ fontSize: '11px', color: 'var(--gf-color-text-tertiary)' }}>v4 Current</div>
                  </div>
                  <Badge variant="success">Current</Badge>
                </div>

                <div className="p02-doc-row">
                  <div>
                    <div className="p02-doc-name">Risk Documentation</div>
                    <div style={{ fontSize: '11px', color: 'var(--gf-color-text-tertiary)' }}>v3 Current</div>
                  </div>
                  <Badge variant="success">Current</Badge>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   08 — GITHUB
   ========================================================================== */

function GitHubSection() {
  return (
    <SectionReveal className="p02-section p02-section--alt">
      <div className="p02-section__inner">
        <div className="p02-split">
          <div className="p02-split__content">
            <span className="p02-split__eyebrow">08 / GITHUB</span>
            <h2 className="p02-split__heading">Connect the work to the repository.</h2>
            <p className="p02-split__copy">
              GrowFlow can provide lightweight GitHub project activity so the workspace can reflect
              what is happening around the repository without becoming a full GitHub management tool.
            </p>
          </div>

          <div className="p02-split__visual">
            <div className="p02-gh-card" role="region" aria-label="Repository activity monitor">
              <div className="p02-card__header">
                <span className="p02-card__title">GITHUB ACTIVITY</span>
                <Badge variant="info">Synced</Badge>
              </div>

              <div className="p02-gh-repo">
                <span>📁</span>
                <span>growflow-demo</span>
              </div>

              <div className="p02-gh-commit">
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--gf-color-text-primary)' }}>
                    Implement retrieval pipeline
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--gf-color-text-tertiary)' }}>
                    Branch: <strong>main</strong> · commit a4f92d
                  </div>
                </div>
                <Badge variant="neutral">Updated today</Badge>
              </div>

              <div style={{ fontSize: '12px', color: 'var(--gf-color-text-tertiary)', fontStyle: 'italic' }}>
                Read-only repository observation connects pull requests and commits to active milestones.
              </div>
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   09 — ACTIVITY
   ========================================================================== */

function ActivitySection() {
  return (
    <SectionReveal className="p02-section">
      <div className="p02-section__inner">
        <div className="p02-split p02-split--reverse">
          <div className="p02-split__content">
            <span className="p02-split__eyebrow">09 / ACTIVITY</span>
            <h2 className="p02-split__heading">Understand what changed.</h2>
            <p className="p02-split__copy">
              A project timeline keeps important changes visible without turning the workspace into a
              stream of noise.
            </p>
          </div>

          <div className="p02-split__visual">
            <div className="p02-card" role="region" aria-label="Project activity timeline">
              <div className="p02-card__header">
                <span className="p02-card__title">PROJECT TIMELINE</span>
                <Badge variant="neutral">Recent Events</Badge>
              </div>

              <div className="p02-activity-timeline">
                <div className="p02-activity-item">
                  <div className="p02-activity-dot" />
                  <div className="p02-activity-time">Today · 10:45 AM</div>
                  <div className="p02-activity-desc">Task completed: <strong>Define retrieval strategy</strong></div>
                </div>

                <div className="p02-activity-item">
                  <div className="p02-activity-dot" />
                  <div className="p02-activity-time">Yesterday · 4:20 PM</div>
                  <div className="p02-activity-desc">Blueprint updated: <strong>Technology Stack v2 generated</strong></div>
                </div>

                <div className="p02-activity-item">
                  <div className="p02-activity-dot" />
                  <div className="p02-activity-time">Sep 10 · 2:15 PM</div>
                  <div className="p02-activity-desc">Milestone progress: <strong>Knowledge Layer reached 75%</strong></div>
                </div>

                <div className="p02-activity-item">
                  <div className="p02-activity-dot" />
                  <div className="p02-activity-time">Sep 08 · 11:00 AM</div>
                  <div className="p02-activity-desc">Risk registered: <strong>Retrieval quality added to risk register</strong></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   10 — AI MENTOR
   ========================================================================== */

function AiMentorSection() {
  return (
    <SectionReveal id="guide" className="p02-section p02-section--alt">
      <div className="p02-section__inner">
        <div className="p02-split">
          <div className="p02-split__content">
            <span className="p02-split__eyebrow">10 / AI MENTOR</span>
            <h2 className="p02-split__heading">Guidance that knows the project.</h2>
            <p className="p02-split__copy">
              Ask questions using the context of your project, its documents, connected knowledge,
              and available repository information. The AI mentor operates inside the workspace structure.
            </p>
          </div>

          <div className="p02-split__visual">
            <div className="p02-card" role="region" aria-label="AI Mentor conversation preview">
              <div className="p02-card__header">
                <span className="p02-card__title">AI MENTOR</span>
                <Badge variant="accent">Context Aware</Badge>
              </div>

              <div className="p02-mentor-chat">
                <div className="p02-chat-bubble p02-chat-bubble--user">
                  <span style={{ fontWeight: 600, display: 'block', marginBottom: '2px' }}>User</span>
                  What should I work on next?
                </div>

                <div className="p02-chat-bubble p02-chat-bubble--ai">
                  <span style={{ fontWeight: 600, display: 'block', marginBottom: '4px', color: 'var(--gf-color-accent-active)' }}>AI Mentor</span>
                  Based on your current milestone, two tasks are ready to continue:
                  <ol style={{ paddingLeft: '16px', margin: '6px 0' }}>
                    <li>Implement retrieval pipeline</li>
                    <li>Define evaluation criteria</li>
                  </ol>
                  <strong>Recommended next step:</strong> Implement retrieval pipeline.
                </div>
              </div>

              <div className="p02-context-pipeline">
                <span>PROJECT CONTEXT</span>
                <span>+</span>
                <span>PROJECT DOCUMENTS</span>
                <span>+</span>
                <span>PROJECT-SCOPED KNOWLEDGE</span>
                <span>+</span>
                <span>CONNECTED INFORMATION</span>
                <span>→</span>
                <strong style={{ color: 'var(--gf-color-accent)' }}>AI MENTOR</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   11 — MENTOR COLLABORATION
   ========================================================================== */

function MentorCollaborationSection() {
  return (
    <SectionReveal id="collaborate" className="p02-section">
      <div className="p02-section__inner">
        <div className="p02-split p02-split--reverse">
          <div className="p02-split__content">
            <span className="p02-split__eyebrow">11 / MENTOR COLLABORATION</span>
            <h2 className="p02-split__heading">Build independently. Stay connected to your mentor.</h2>
            <p className="p02-split__copy">
              Students retain ownership of their project workspace while mentors gain the visibility
              they need to provide meaningful supervision.
            </p>
          </div>

          <div className="p02-split__visual">
            <div className="p02-collab-box" role="region" aria-label="Mentor feedback note">
              <div className="p02-card__header">
                <span className="p02-card__title">MENTOR SUPERVISION</span>
                <Badge variant="info">Human Checkpoint</Badge>
              </div>

              <div className="p02-collab-note">
                "Reviewed Milestone 3 plan. The metadata filtering approach for vector collections is solid.
                Ensure test coverage for edge queries before moving to Milestone 4."
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px' }}>
                <span style={{ color: 'var(--gf-color-text-secondary)' }}>
                  <strong>Dr. Elena Vance</strong> · Lead Technical Mentor
                </span>
                <Badge variant="neutral">Non-Intrusive Supervision</Badge>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   12 — THREE PERSPECTIVES
   ========================================================================== */

function ThreePerspectivesSection() {
  return (
    <SectionReveal className="p02-section p02-section--alt">
      <div className="p02-section__inner">
        <div style={{ textAlign: 'center', maxWidth: '680px', margin: '0 auto var(--gf-space-8)' }}>
          <span className="p02-split__eyebrow">12 / THREE PERSPECTIVES</span>
          <h2 className="p02-split__heading">One system. Three perspectives.</h2>
          <p className="p02-split__copy">
            A cohesive environment designed around the distinct needs of students, mentors, and administrators.
          </p>
        </div>

        <div className="p02-perspectives-grid">
          {/* BUILD */}
          <div className="p02-perspective-card">
            <span className="p02-perspective-role">BUILD</span>
            <div className="p02-perspective-title">For students</div>
            <p className="p02-perspective-quote">"Create, understand, plan, and execute."</p>
            <div style={{ fontSize: '13px', color: 'var(--gf-color-text-secondary)', marginTop: 'auto' }}>
              Full project ownership from ideation to deployment with structured artifacts.
            </div>
          </div>

          {/* SUPERVISE */}
          <div className="p02-perspective-card">
            <span className="p02-perspective-role">SUPERVISE</span>
            <div className="p02-perspective-title">For mentors</div>
            <p className="p02-perspective-quote">"Observe progress, identify risks, and support students."</p>
            <div style={{ fontSize: '13px', color: 'var(--gf-color-text-secondary)', marginTop: 'auto' }}>
              Deep visibility into student milestones without disrupting their autonomous workflow.
            </div>
          </div>

          {/* GOVERN */}
          <div className="p02-perspective-card">
            <span className="p02-perspective-role">GOVERN</span>
            <div className="p02-perspective-title">For administrators</div>
            <p className="p02-perspective-quote">"Monitor the platform, AI systems, infrastructure, security, and usage."</p>
            <div style={{ fontSize: '13px', color: 'var(--gf-color-text-secondary)', marginTop: 'auto' }}>
              Centralized platform observability, system health, and token economics monitoring.
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   13 — AI STRUCTURE
   ========================================================================== */

function AiStructureSection() {
  return (
    <SectionReveal className="p02-section">
      <div className="p02-section__inner">
        <div className="p02-split">
          <div className="p02-split__content">
            <span className="p02-split__eyebrow">13 / AI STRUCTURE</span>
            <h2 className="p02-split__heading">AI works inside the structure of the project.</h2>
            <p className="p02-split__copy">
              GrowFlow separates intelligent generation from canonical project state. AI can reason,
              propose, and generate structured outputs — while validation and deterministic services
              keep the project state consistent.
            </p>
          </div>

          <div className="p02-split__visual">
            <div className="p02-card" role="region" aria-label="AI architecture pipeline">
              <div className="p02-card__header">
                <span className="p02-card__title">GENERATION PIPELINE</span>
                <Badge variant="accent">Deterministic QA</Badge>
              </div>

              <div className="p02-pipeline-chain">
                <div className="p02-pipeline-node">Project Context</div>
                <div className="p02-pipeline-arrow">→</div>
                <div className="p02-pipeline-node">AI Workflow</div>
                <div className="p02-pipeline-arrow">→</div>
                <div className="p02-pipeline-node">Structured Output</div>
                <div className="p02-pipeline-arrow">→</div>
                <div className="p02-pipeline-node">Validation</div>
                <div className="p02-pipeline-arrow">→</div>
                <div className="p02-pipeline-node">QA</div>
                <div className="p02-pipeline-arrow">→</div>
                <div className="p02-pipeline-node" style={{ borderColor: 'var(--gf-color-accent)', color: 'var(--gf-color-accent-active)' }}>
                  Project State
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   14 — PERSISTENT BACKGROUND WORK
   ========================================================================== */

function PersistentBackgroundSection() {
  return (
    <SectionReveal className="p02-section p02-section--alt">
      <div className="p02-section__inner">
        <div className="p02-split p02-split--reverse">
          <div className="p02-split__content">
            <span className="p02-split__eyebrow">14 / BACKGROUND WORK</span>
            <h2 className="p02-split__heading">Work continues even when you leave the screen.</h2>
            <p className="p02-split__copy">
              Blueprint generation, document generation, and other long-running operations are handled
              as persistent background work rather than depending on an open browser session.
            </p>
          </div>

          <div className="p02-split__visual">
            <div className="p02-job-card" role="region" aria-label="Background blueprint generation job">
              <div className="p02-card__header">
                <span className="p02-card__title">BLUEPRINT GENERATION</span>
                <Badge variant="accent">Async Worker</Badge>
              </div>

              <div className="p02-job-steps">
                <div className="p02-job-step" style={{ color: 'var(--gf-color-success)' }}>
                  <span>✓</span> Project context
                </div>
                <div className="p02-job-step" style={{ color: 'var(--gf-color-success)' }}>
                  <span>✓</span> Assessment
                </div>
                <div className="p02-job-step" style={{ color: 'var(--gf-color-accent-active)', fontWeight: 700 }}>
                  <span>●</span> AI workflow (orchestrating)
                </div>
                <div className="p02-job-step" style={{ color: 'var(--gf-color-text-tertiary)' }}>
                  <span>○</span> Validation
                </div>
                <div className="p02-job-step" style={{ color: 'var(--gf-color-text-tertiary)' }}>
                  <span>○</span> Documents
                </div>
              </div>

              <div className="p02-job-callout">
                "You can leave this page. GrowFlow will keep the job running."
              </div>
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   15 — TRUST
   ========================================================================== */

function TrustSection() {
  return (
    <SectionReveal className="p02-section p02-trust-section">
      <div className="p02-section__inner">
        <div style={{ textAlign: 'center', maxWidth: '680px', margin: '0 auto var(--gf-space-8)' }}>
          <span className="p02-split__eyebrow">15 / TRUST</span>
          <h2 className="p02-split__heading">Designed to keep intelligence accountable.</h2>
          <p className="p02-split__copy">
            Built from the foundation up with strict boundaries, auditability, and deterministic safeguards.
          </p>
        </div>

        <div className="p02-trust-grid">
          <div className="p02-trust-card">
            <div className="p02-trust-title">STRUCTURED</div>
            <p className="p02-trust-copy">
              AI outputs use defined structures before they become project representations.
            </p>
          </div>

          <div className="p02-trust-card">
            <div className="p02-trust-title">CONTEXTUAL</div>
            <p className="p02-trust-copy">
              Project knowledge remains scoped to the project.
            </p>
          </div>

          <div className="p02-trust-card">
            <div className="p02-trust-title">OBSERVABLE</div>
            <p className="p02-trust-copy">
              AI executions, usage, failures, retries, and operational state can be observed by the
              appropriate platform layer.
            </p>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   Final CTA
   ========================================================================== */

function FinalCtaSection() {
  return (
    <section className="p02-final-cta" aria-labelledby="features-final-cta-heading">
      <div className="p02-final-cta__inner">
        <h2 id="features-final-cta-heading" className="p02-final-cta__h2">
          Ready to give your project a path forward?
        </h2>
        <p className="p02-final-cta__copy">
          Start with your idea. Let GrowFlow help structure what comes next.
        </p>
        <div className="p02-final-cta__actions">
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
