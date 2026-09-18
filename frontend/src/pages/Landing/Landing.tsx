import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { SectionReveal } from '@/components/ui/SectionReveal';
import './Landing.css';

/**
 * P01 — Landing / Hero
 *
 * Primary public entry point. Unauthenticated.
 * Purpose: Explain GrowFlow quickly and create curiosity about the actual product.
 *
 * Source: Phase 01 (P01), Phase 02 (routes), Master Design (visual),
 *         Phase 06C (tokens), Phase 06D (components), Phase 06E (shell)
 */
export function Landing() {
  return (
    <>
      <HeroSection />
      <PhilosophySection />
      <LifecycleSection />
      <ProductStoriesSection />
      <WorkplacesSection />
      <ConnectionSection />
      <DesignPhilosophySection />
      <TechnicalSection />
      <FinalCtaSection />
    </>
  );
}

/* ==========================================================================
   Hero Section
   ========================================================================== */

function HeroSection() {
  return (
    <section className="hero" aria-labelledby="hero-headline">
      <div className="hero__inner">
        <div className="hero__content">
          <span className="hero__label" aria-hidden="true">
            <span className="hero__label-dot" />
            Project Workspace
          </span>

          <h1 id="hero-headline" className="hero__headline">
            Turn your project idea into a path forward.
          </h1>

          <p className="hero__description">
            GrowFlow helps you move from idea to execution with structured planning,
            intelligent guidance, progress tracking, and mentor collaboration — all
            in one project workspace.
          </p>

          <div className="hero__actions">
            <Button as="link" to="/auth/student/register" size="lg">
              Start Building
            </Button>
            <Button as="anchor" href="#lifecycle" variant="secondary" size="lg">
              See How GrowFlow Works
            </Button>
          </div>
        </div>

        <div className="hero__visual">
          <ProductGlimpse />
        </div>
      </div>
    </section>
  );
}

/* ==========================================================================
   Product Glimpse — Static illustrative BUILD workspace teaser
   All data here is controlled static presentation data.
   It does NOT represent live backend state.
   ========================================================================== */

function ProductGlimpse() {
  return (
    <div className="product-glimpse" role="img" aria-label="GrowFlow project workspace preview showing a sample project overview with progress tracking and task management">
      {/* Header */}
      <div className="product-glimpse__header">
        <span className="product-glimpse__project-name">BuildFlow</span>
        <Badge variant="success" dot>Healthy</Badge>
      </div>

      {/* Metrics Grid */}
      <div className="product-glimpse__metrics">
        <div className="product-glimpse__metric">
          <span className="product-glimpse__metric-label">Phase</span>
          <span className="product-glimpse__metric-value">Implementation</span>
        </div>
        <div className="product-glimpse__metric">
          <span className="product-glimpse__metric-label">Tasks</span>
          <span className="product-glimpse__metric-value">12 / 18</span>
        </div>
        <div className="product-glimpse__metric">
          <span className="product-glimpse__metric-label">Milestones</span>
          <span className="product-glimpse__metric-value">3 / 5</span>
        </div>
        <div className="product-glimpse__metric">
          <span className="product-glimpse__metric-label">Active Risks</span>
          <span className="product-glimpse__metric-value">2</span>
        </div>

        {/* Progress bar */}
        <div className="product-glimpse__progress-bar">
          <span className="product-glimpse__metric-label">Progress</span>
          <div className="product-glimpse__progress-track">
            <div
              className="product-glimpse__progress-fill"
              style={{ width: '68%' }}
              role="progressbar"
              aria-valuenow={68}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label="Project progress: 68%"
            />
          </div>
        </div>
      </div>

      {/* Next Action */}
      <div className="product-glimpse__next-action">
        <div className="product-glimpse__next-label">Next Action</div>
        <div className="product-glimpse__next-value">
          Implement project-scoped RAG
        </div>
      </div>
    </div>
  );
}

/* ==========================================================================
   Philosophy Section
   ========================================================================== */

function PhilosophySection() {
  return (
    <SectionReveal className="gf-section philosophy">
      <div className="gf-container">
        <blockquote className="philosophy__quote">
          Projects rarely fail because the idea wasn&apos;t good enough.
          They fail when the path from idea to execution isn&apos;t clear.
          <span className="philosophy__emphasis">
            GrowFlow gives that path structure.
          </span>
        </blockquote>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   Lifecycle Section
   ========================================================================== */

const LIFECYCLE_STEPS = [
  { number: '01', name: 'Idea' },
  { number: '02', name: 'Assessment' },
  { number: '03', name: 'Blueprint' },
  { number: '04', name: 'Planning' },
  { number: '05', name: 'Implementation' },
  { number: '06', name: 'Testing' },
  { number: '07', name: 'Deployment' },
  { number: '08', name: 'Completed' },
] as const;

function LifecycleSection() {
  return (
    <SectionReveal className="gf-section lifecycle" id="lifecycle">
      <div className="gf-container">
        <div className="lifecycle__header">
          <h2 className="lifecycle__title">The project lifecycle</h2>
          <p className="lifecycle__subtitle">
            Every project moves through a structured sequence — from an initial idea
            to a completed, deployable result.
          </p>
        </div>

        <div className="lifecycle__steps">
          {LIFECYCLE_STEPS.map((step) => (
            <div key={step.number} className="lifecycle__step">
              <span className="lifecycle__step-number">{step.number}</span>
              <span className="lifecycle__step-name">{step.name}</span>
            </div>
          ))}
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   Product Stories — Four alternating editorial compositions
   ========================================================================== */

function ProductStoriesSection() {
  return (
    <SectionReveal className="gf-section stories" as="section">
      <div className="gf-container">

        {/* Story 1: Understand the Project — TEXT | VISUAL */}
        <div className="stories__item">
          <div className="stories__item-content">
            <span className="stories__item-number">01</span>
            <h3 className="stories__item-title">Understand the project</h3>
            <p className="stories__item-description">
              Before planning begins, GrowFlow builds an understanding of the
              project and the person building it.
            </p>
          </div>
          <div className="stories__item-visual" aria-hidden="true">
            <span className="stories__fragment-label">Assessment</span>
            <div className="stories__fragment-item">
              <span className="stories__fragment-text">Project scope and objectives</span>
            </div>
            <div className="stories__fragment-item">
              <span className="stories__fragment-text">Technical requirements</span>
            </div>
            <div className="stories__fragment-item">
              <span className="stories__fragment-text">Experience and constraints</span>
            </div>
            <div className="stories__fragment-item">
              <span className="stories__fragment-text">Risk factors</span>
            </div>
          </div>
        </div>

        {/* Story 2: Build the Blueprint — VISUAL | TEXT */}
        <div className="stories__item stories__item--reversed">
          <div className="stories__item-content">
            <span className="stories__item-number">02</span>
            <h3 className="stories__item-title">Build the blueprint</h3>
            <p className="stories__item-description">
              Turn an idea into a practical blueprint covering technology, features,
              specifications, MVP, timeline, risks, tasks, milestones, and project documentation.
            </p>
          </div>
          <div className="stories__item-visual" aria-hidden="true">
            <span className="stories__fragment-label">Blueprint</span>
            <div className="stories__fragment-item">
              <CheckIcon done />
              <span className="stories__fragment-text">Technology stack</span>
            </div>
            <div className="stories__fragment-item">
              <CheckIcon done />
              <span className="stories__fragment-text">Feature specification</span>
            </div>
            <div className="stories__fragment-item">
              <CheckIcon done />
              <span className="stories__fragment-text">MVP definition</span>
            </div>
            <div className="stories__fragment-item">
              <CheckIcon />
              <span className="stories__fragment-text stories__fragment-text--muted">Risk analysis</span>
            </div>
          </div>
        </div>

        {/* Story 3: Execute with Direction — TEXT | VISUAL */}
        <div className="stories__item">
          <div className="stories__item-content">
            <span className="stories__item-number">03</span>
            <h3 className="stories__item-title">Execute with direction</h3>
            <p className="stories__item-description">
              Know what to work on, what is blocked, what changed, and where the project stands.
            </p>
          </div>
          <div className="stories__item-visual" aria-hidden="true">
            <span className="stories__fragment-label">Tasks &amp; Progress</span>
            <div className="stories__fragment-item">
              <CheckIcon done />
              <span className="stories__fragment-text">Set up project repository</span>
            </div>
            <div className="stories__fragment-item">
              <CheckIcon done />
              <span className="stories__fragment-text">Implement authentication</span>
            </div>
            <div className="stories__fragment-item">
              <CheckIcon />
              <span className="stories__fragment-text stories__fragment-text--muted">Build data models</span>
            </div>
            <div className="stories__fragment-item">
              <CheckIcon />
              <span className="stories__fragment-text stories__fragment-text--muted">Create API endpoints</span>
            </div>
          </div>
        </div>

        {/* Story 4: Get Intelligent Guidance — VISUAL | TEXT */}
        <div className="stories__item stories__item--reversed">
          <div className="stories__item-content">
            <span className="stories__item-number">04</span>
            <h3 className="stories__item-title">Get intelligent guidance</h3>
            <p className="stories__item-description">
              Ask questions against your project context, documents, and connected
              information without losing the structure of the project itself.
            </p>
          </div>
          <div className="stories__item-visual stories__ai-fragment" aria-hidden="true">
            <div className="stories__ai-header">
              <span className="stories__ai-icon" aria-hidden="true">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                  <path d="M8 1v14M1 8h14M3.5 3.5l9 9M12.5 3.5l-9 9" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
              </span>
              <span className="stories__ai-label">AI Mentor</span>
            </div>
            <p className="stories__ai-text">
              Based on your project blueprint and current progress, the next
              milestone focuses on completing the data access layer. Consider
              prioritizing the repository pattern implementation before moving
              to API integration tests.
            </p>
          </div>
        </div>

      </div>
    </SectionReveal>
  );
}

/** Small check icon for story visuals */
function CheckIcon({ done = false }: { done?: boolean }) {
  return (
    <span className={`stories__fragment-check ${done ? 'stories__fragment-check--done' : ''}`}>
      {done && (
        <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M2.5 6l2.5 2.5 4.5-5" />
        </svg>
      )}
    </span>
  );
}

/* ==========================================================================
   Workplaces Section
   ========================================================================== */

const WORKPLACES = [
  {
    key: 'build',
    name: 'BUILD',
    audience: 'For students',
    description: 'Turn an idea into a structured project and execute it with direction.',
    icon: 'B',
  },
  {
    key: 'supervise',
    name: 'SUPERVISE',
    audience: 'For mentors',
    description: 'Understand your students, projects, progress, risks, and support needs in one place.',
    icon: 'S',
  },
  {
    key: 'govern',
    name: 'GOVERN',
    audience: 'For platform administrators',
    description: 'Monitor the health, usage, AI systems, security, and operational state of GrowFlow.',
    icon: 'G',
  },
] as const;

function WorkplacesSection() {
  return (
    <SectionReveal className="gf-section">
      <div className="gf-container">
        <div className="workplaces__header">
          <h2 className="workplaces__title">Three workplaces. One system.</h2>
          <p className="workplaces__subtitle">
            GrowFlow serves different roles through one unified design and architecture.
          </p>
        </div>

        <div className="workplaces__grid">
          {WORKPLACES.map((wp) => (
            <div key={wp.key} className="workplaces__card">
              <span className="workplaces__card-icon" aria-hidden="true">{wp.icon}</span>
              <h3 className="workplaces__card-name">{wp.name}</h3>
              <span className="workplaces__card-audience">{wp.audience}</span>
              <p className="workplaces__card-description">{wp.description}</p>
            </div>
          ))}
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   Connection Section — "Everything connects."
   ========================================================================== */

const CONNECTION_NODES = ['Tasks', 'Milestones', 'Progress', 'Phase', 'Health'] as const;

function ConnectionSection() {
  return (
    <SectionReveal className="gf-section connection">
      <div className="gf-container">
        <h2 className="connection__title">Everything connects.</h2>
        <p className="connection__description">
          Tasks inform milestones. Milestones shape progress. Progress influences
          project state. Your project context stays connected as you build.
        </p>

        <div className="connection__flow" aria-label="Connection flow: Tasks to Milestones to Progress to Phase to Health">
          {CONNECTION_NODES.map((node, i) => (
            <span key={node}>
              <span className="connection__node">{node}</span>
              {i < CONNECTION_NODES.length - 1 && (
                <span className="connection__arrow" aria-hidden="true"> → </span>
              )}
            </span>
          ))}
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   Design Philosophy Section — "Less noise. More direction."
   ========================================================================== */

const PRINCIPLES = [
  {
    name: 'Structured',
    description: 'Important project information has a place.',
  },
  {
    name: 'Contextual',
    description: 'Guidance is grounded in the project you\'re actually working on.',
  },
  {
    name: 'Human',
    description: 'The system supports the work without trying to replace the person doing it.',
  },
] as const;

function DesignPhilosophySection() {
  return (
    <SectionReveal className="gf-section design-philosophy">
      <div className="gf-container">
        <div className="design-philosophy__header">
          <h2 className="design-philosophy__title">Less noise. More direction.</h2>
          <p className="design-philosophy__subtitle">
            GrowFlow is designed to keep project information connected without
            overwhelming the person building it.
          </p>
        </div>

        <div className="design-philosophy__principles">
          {PRINCIPLES.map((p) => (
            <div key={p.name} className="design-philosophy__principle">
              <h3 className="design-philosophy__principle-name">{p.name}</h3>
              <p className="design-philosophy__principle-desc">{p.description}</p>
            </div>
          ))}
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   Technical Credibility Section
   ========================================================================== */

const PIPELINE_STAGES = [
  'Project State',
  'Structured Context',
  'AI Workflow',
  'Validation',
  'Persisted Result',
] as const;

function TechnicalSection() {
  return (
    <SectionReveal className="gf-section technical">
      <div className="gf-container">
        <h2 className="technical__title">Intelligence with structure underneath.</h2>
        <p className="technical__description">
          GrowFlow combines deterministic project state, structured AI workflows,
          project-scoped knowledge, background execution, and observable infrastructure.
        </p>

        <div className="technical__pipeline" aria-label="Technical pipeline: Project State to Structured Context to AI Workflow to Validation to Persisted Result">
          {PIPELINE_STAGES.map((stage, i) => (
            <span key={stage}>
              <span className="technical__stage">{stage}</span>
              {i < PIPELINE_STAGES.length - 1 && (
                <span className="technical__stage-arrow" aria-hidden="true"> → </span>
              )}
            </span>
          ))}
        </div>

        <Button as="link" to="/documentation" variant="secondary" size="lg">
          Explore the architecture →
        </Button>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   Final CTA Section
   ========================================================================== */

function FinalCtaSection() {
  return (
    <SectionReveal className="gf-section final-cta">
      <div className="gf-container">
        <h2 className="final-cta__title">
          Your next project deserves more than a blank page.
        </h2>
        <p className="final-cta__description">
          Start with an idea. Grow it into something you can actually build.
        </p>
        <div className="final-cta__actions">
          <Button as="link" to="/auth/student/register" size="lg">
            Start Building
          </Button>
          <Button as="link" to="/features" variant="secondary" size="lg">
            Explore GrowFlow
          </Button>
        </div>
      </div>
    </SectionReveal>
  );
}
