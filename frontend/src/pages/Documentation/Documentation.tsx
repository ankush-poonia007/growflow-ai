import { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { SectionReveal } from '@/components/ui/SectionReveal';
import { cn } from '@/utils/cn';
import './Documentation.css';

/**
 * P03 — Documentation
 *
 * Route: /documentation
 * Audience: Public / unauthenticated
 * Purpose: Public technical documentation and engineering showcase.
 *
 * Implements the 15 canonical sections in strict sequential order.
 * Reuses Gate 06 shared components: Button, Badge, SectionReveal, tokens.
 */
export function Documentation() {
  const [activeSection, setActiveSection] = useState<string>('architecture');

  useEffect(() => {
    const sectionIds = [
      'architecture',
      'lifecycle',
      'ai-architecture',
      'agents',
      'rag',
      'workers',
      'security',
      'observability',
      'principles',
      'at-a-glance',
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
    <div className="p03-page">
      {/* 1. Hero */}
      <HeroSection />

      {/* Scoped flow container ensures sticky sub-nav unpins gracefully before closing sections */}
      <div className="p03-docs-flow">
        {/* 2. Documentation Index */}
        <DocumentationIndexNav activeSection={activeSection} />

        {/* 3. Architecture */}
        <ArchitectureSection />

        {/* 4. Project Lifecycle */}
        <ProjectLifecycleSection />

        {/* 5. AI Architecture */}
        <AiArchitectureSection />

        {/* 6. 13-Agent Architecture */}
        <ThirteenAgentsSection />

        {/* 7. Knowledge & RAG */}
        <KnowledgeRagSection />

        {/* 8. Persistent Background Work / Reliability */}
        <BackgroundWorkSection />

        {/* 9. Security */}
        <SecuritySection />

        {/* 10. Observability */}
        <ObservabilitySection />

        {/* 11. Engineering Principles */}
        <EngineeringPrinciplesSection />

        {/* 12. Architecture at a Glance */}
        <ArchitectureGlanceSection />
      </div>

      {/* 13. Documentation Philosophy */}
      <DocumentationPhilosophySection />

      {/* 14. Trust / Closing Statement */}
      <TrustStatementSection />

      {/* 15. Final CTA */}
      <FinalCtaSection />
    </div>
  );
}

/* ==========================================================================
   1. Hero Section
   ========================================================================== */

function HeroSection() {
  return (
    <section className="p03-hero" aria-labelledby="docs-hero-heading">
      <div className="p03-hero__inner">
        <div className="p03-hero__header">
          <span className="p03-hero__eyebrow">
            <span className="p03-hero__eyebrow-dot" />
            SYSTEM ARCHITECTURE & ENGINEERING
          </span>
          <h1 id="docs-hero-heading" className="p03-hero__h1">
            Understand the system behind the flow.
          </h1>
          <p className="p03-hero__copy">
            GrowFlow is designed as a deterministic, reliable project execution engine where specialized
            AI agents reason inside strict boundaries, while PostgreSQL owns canonical state, persistent
            background workers power durable execution, and validation gates protect project integrity.
          </p>

          <div className="p03-hero__chips">
            <Badge variant="accent">13 Canonical Agents</Badge>
            <Badge variant="neutral">Deterministic State Authority</Badge>
            <Badge variant="info">Durable Background Workers</Badge>
            <Badge variant="success">Zero Direct Client-AI Calls</Badge>
          </div>

          <div className="p03-hero__actions">
            <Button as="anchor" href="#architecture" size="lg">
              Explore Architecture
            </Button>
            <Button as="anchor" href="#agents" variant="secondary" size="lg">
              View 13-Agent System
            </Button>
          </div>
        </div>

        {/* Hero Architecture Glimpse */}
        <div className="p03-hero__glimpse gf-interactive-group">
          <div className="p03-glimpse-card gf-interactive">
            <div className="p03-glimpse-head">
              <span className="p03-glimpse-tag">SYSTEM EXECUTION TOPOLOGY</span>
              <span className="p03-glimpse-badge">Deterministic Control Flow</span>
            </div>
            <div className="p03-glimpse-schematic">
              <div className="p03-glimpse-node gf-interactive--subtle">
                <span className="p03-glimpse-node-step">01. INGESTION</span>
                <strong className="p03-glimpse-node-title">Application Layer</strong>
                <span className="p03-glimpse-node-meta">Vite · REST / SSE · RLS</span>
              </div>
              <div className="p03-glimpse-arrow" aria-hidden="true">→</div>
              <div className="p03-glimpse-node p03-glimpse-node--accent gf-interactive--subtle">
                <span className="p03-glimpse-node-step">02. REASONING</span>
                <strong className="p03-glimpse-node-title">Bounded AI Mesh</strong>
                <span className="p03-glimpse-node-meta">13 Agents · LangGraph · QA Gate</span>
              </div>
              <div className="p03-glimpse-arrow" aria-hidden="true">→</div>
              <div className="p03-glimpse-node gf-interactive--subtle">
                <span className="p03-glimpse-node-step">03. PERSISTENCE</span>
                <strong className="p03-glimpse-node-title">PostgreSQL Core</strong>
                <span className="p03-glimpse-node-meta">ACID Authority · Durable Jobs</span>
              </div>
            </div>
            <div className="p03-glimpse-footer">
              <span className="p03-glimpse-pulse" aria-hidden="true" />
              <span className="p03-glimpse-status">Deterministic State Authority: Enforced across all lifecycle gates</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ==========================================================================
   2. Documentation Index (Sticky Navigation)
   ========================================================================== */

const DOC_NAV_LINKS = [
  { label: 'Architecture', href: '#architecture' },
  { label: 'Lifecycle', href: '#lifecycle' },
  { label: 'AI Pipeline', href: '#ai-architecture' },
  { label: '13 Agents', href: '#agents' },
  { label: 'Knowledge & RAG', href: '#rag' },
  { label: 'Reliability', href: '#workers' },
  { label: 'Security', href: '#security' },
  { label: 'Observability', href: '#observability' },
  { label: 'Principles', href: '#principles' },
  { label: 'At a Glance', href: '#at-a-glance' },
] as const;

function DocumentationIndexNav({ activeSection }: { activeSection: string }) {
  return (
    <nav className="p03-index-nav" aria-label="Documentation navigation">
      <div className="p03-index-nav__inner">
        {DOC_NAV_LINKS.map(({ label, href }) => {
          const id = href.replace('#', '');
          const isActive = activeSection === id;
          return (
            <a
              key={href}
              href={href}
              className={cn(
                'p03-index-nav__link',
                isActive && 'p03-index-nav__link--active',
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
   3. Architecture Section
   ========================================================================== */

function ArchitectureSection() {
  return (
    <SectionReveal id="architecture" className="p03-section">
      <div className="p03-section__inner">
        <div className="p03-section-head">
          <span className="p03-eyebrow">03 / SYSTEM ARCHITECTURE</span>
          <h2 className="p03-heading">System Architecture</h2>
          <p className="p03-subheading">
            A decoupled client-server platform designed for deterministic state authority and strictly
            governed artificial intelligence.
          </p>
        </div>

        <div className="p03-diagram-box" role="region" aria-label="Multi-tier system architecture">
          <div className="p03-tier-stack">
            {/* Layer 1: Client Tier */}
            <div className="p03-tier-layer">
              <div className="p03-tier-meta">
                <span className="p03-tier-name">1. Presentation Tier</span>
                <span className="p03-tier-tech">Vite + React 19 + TypeScript</span>
              </div>
              <div className="p03-tier-content">
                <div className="p03-tier-item">BUILD (Student Workspace)</div>
                <div className="p03-tier-item">SUPERVISE (Mentor Workspace)</div>
                <div className="p03-tier-item">GOVERN (Admin Platform)</div>
                <Badge variant="accent">Vanilla CSS Tokens</Badge>
              </div>
            </div>

            <div className="p03-tier-connector" aria-hidden="true">
              ↓ REST Endpoints & SSE Streaming Channels (Stateless JWT Boundary) ↓
            </div>

            {/* Layer 2: API Gateway Tier */}
            <div className="p03-tier-layer">
              <div className="p03-tier-meta">
                <span className="p03-tier-name">2. Application Gateway</span>
                <span className="p03-tier-tech">FastAPI + Python 3.12</span>
              </div>
              <div className="p03-tier-content">
                <div className="p03-tier-item">Bcrypt Auth & JWT RBAC</div>
                <div className="p03-tier-item">Pydantic Request Validation</div>
                <div className="p03-tier-item">Domain Service Layer</div>
                <div className="p03-tier-item">SSE Broadcast Engine</div>
              </div>
            </div>

            <div className="p03-tier-connector" aria-hidden="true">
              ↓ Async Task Dispatch & Centralized AI Gateway ↓
            </div>

            {/* Layer 3: Worker & AI Gateway Tier */}
            <div className="p03-tier-layer">
              <div className="p03-tier-meta">
                <span className="p03-tier-name">3. Execution & AI Gateway</span>
                <span className="p03-tier-tech">Persistent Workers + LangGraph</span>
              </div>
              <div className="p03-tier-content">
                <div className="p03-tier-item">Durable Task Queues & Workers</div>
                <div className="p03-tier-item">AI Provider Gateway (OpenAI / OpenRouter)</div>
                <div className="p03-tier-item">LangGraph 13-Agent Orchestrator</div>
                <Badge variant="info">Transactional Outbox & Durable Jobs</Badge>
              </div>
            </div>

            <div className="p03-tier-connector" aria-hidden="true">
              ↓ ACID State Mutations & Filtered Embeddings ↓
            </div>

            {/* Layer 4: Persistence Tier */}
            <div className="p03-tier-layer">
              <div className="p03-tier-meta">
                <span className="p03-tier-name">4. Data & Persistence</span>
                <span className="p03-tier-tech">PostgreSQL + pgvector + Redis</span>
              </div>
              <div className="p03-tier-content">
                <div className="p03-tier-item" style={{ borderColor: 'var(--gf-color-accent)', fontWeight: 700 }}>
                  PostgreSQL (Canonical Source of Truth)
                </div>
                <div className="p03-tier-item">pgvector (Project-Scoped RAG)</div>
                <div className="p03-tier-item">Redis (Session & Ephemeral Cache)</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   4. Project Lifecycle Section
   ========================================================================== */

const LIFECYCLE_GATES = [
  { num: '01', name: 'IDEA', desc: 'Context capture, domain problem structuring, and stakeholder intent extraction.' },
  { num: '02', name: 'ASSESSMENT', desc: 'Dual-layer diagnostic questionnaire adapting dynamically to the technical stack.' },
  { num: '03', name: 'BLUEPRINT', desc: 'Multi-agent orchestration producing verified architectural specifications and artifacts.' },
  { num: '04', name: 'PLANNING', desc: 'Work package decomposition into interdependent tasks, milestones, and deliverable fences.' },
  { num: '05', name: 'IMPLEMENTATION', desc: 'Active student development supported by lightweight repository activity monitoring.' },
  { num: '06', name: 'TESTING', desc: 'Formal criteria validation, test plan execution, and defect risk verification.' },
  { num: '07', name: 'DEPLOYMENT', desc: 'Environment configuration, build packaging, and operational staging.' },
  { num: '08', name: 'COMPLETED', desc: 'Final milestone sign-off, retrospective analysis, and canonical artifact lock.' },
];

function ProjectLifecycleSection() {
  return (
    <SectionReveal id="lifecycle" className="p03-section p03-section--alt">
      <div className="p03-section__inner">
        <div className="p03-section-head">
          <span className="p03-eyebrow">04 / PROJECT LIFECYCLE</span>
          <h2 className="p03-heading">The Canonical Project Lifecycle</h2>
          <p className="p03-subheading">
            Projects progress through eight deterministic milestone gates. Progression requires criteria
            fulfillment and schema-validated deliverables.
          </p>
        </div>

        <div className="p03-lifecycle-grid">
          {LIFECYCLE_GATES.map((gate) => (
            <div key={gate.num} className="p03-gate-card">
              <span className="p03-gate-num">GATE {gate.num}</span>
              <div className="p03-gate-title">{gate.name}</div>
              <p className="p03-gate-desc">{gate.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   5. AI Architecture Section
   ========================================================================== */

const AI_PIPELINE_STEPS = [
  { step: '1', title: 'Project Context', desc: 'Scoped student inputs, assessment answers, existing blueprint docs' },
  { step: '2', title: 'AI Workflow', desc: 'LangGraph orchestrated reasoning with tool constraints' },
  { step: '3', title: 'Structured Output', desc: 'Strict Pydantic models preventing loose hallucination' },
  { step: '4', title: 'Schema Validation', desc: 'Deterministic type verification and schema enforcement' },
  { step: '5', title: 'Business Validation', desc: 'Domain constraint checks (dates, prerequisites, scope)' },
  { step: '6', title: 'QA/Judge', desc: 'Semantic evaluation agent scoring consistency and feasibility' },
  { step: '7', title: 'Project State', desc: 'ACID transaction committed to PostgreSQL database' },
];

function AiArchitectureSection() {
  return (
    <SectionReveal id="ai-architecture" className="p03-section">
      <div className="p03-section__inner">
        <div className="p03-section-head">
          <span className="p03-eyebrow">05 / AI ARCHITECTURE & GOVERNANCE</span>
          <h2 className="p03-heading">AI Architecture & Governance</h2>
          <p className="p03-subheading">
            GrowFlow separates generative reasoning from canonical project state. AI proposes structured
            candidates, but only deterministic validation gates mutate authoritative database records.
          </p>
        </div>

        <div className="p03-pipeline-container" role="region" aria-label="AI generation pipeline flow">
          {AI_PIPELINE_STEPS.map((s, idx) => (
            <div key={s.step} style={{ display: 'flex', alignItems: 'center', gap: 'var(--gf-space-2)' }}>
              <div className={cn('p03-pipeline-step', idx === AI_PIPELINE_STEPS.length - 1 && 'p03-pipeline-step--terminal')}>
                <span className="gf-font-mono" style={{ fontSize: '11px', color: 'var(--gf-color-accent)', fontWeight: 700 }}>
                  STEP 0{s.step}
                </span>
                <strong style={{ fontSize: '13px', color: 'var(--gf-color-text-primary)' }}>{s.title}</strong>
                <span style={{ fontSize: '11px', color: 'var(--gf-color-text-secondary)', lineHeight: 1.4 }}>
                  {s.desc}
                </span>
              </div>
              {idx < AI_PIPELINE_STEPS.length - 1 && <span className="p03-pipeline-arrow" aria-hidden="true">→</span>}
            </div>
          ))}
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   6. 13-Agent Architecture Section
   ========================================================================== */

const THIRTEEN_AGENTS = [
  { id: '01', name: 'Idea Agent', desc: 'Synthesizes raw student concepts into structured problem/solution statements.', input: 'Prompt / Vision', output: 'ProblemDefinition' },
  { id: '02', name: 'Scope Agent', desc: 'Defines project boundaries, technical constraints, out-of-scope exclusions, and deliverable fences.', input: 'ProblemDefinition', output: 'ScopeBoundaries' },
  { id: '03', name: 'Project Profile Agent', desc: 'Establishes project metadata, complexity tier, domain classification, and target outcomes.', input: 'ScopeBoundaries', output: 'ProjectProfile' },
  { id: '04', name: 'Technology Agent', desc: 'Selects and justifies programming languages, frameworks, databases, and dependencies.', input: 'ProjectProfile', output: 'TechStackSpec' },
  { id: '05', name: 'Features Agent', desc: 'Generates prioritized feature hierarchies, user stories, and acceptance criteria.', input: 'TechStackSpec', output: 'FeatureHierarchy' },
  { id: '06', name: 'MVP Agent', desc: 'Distills minimum viable product definitions to ensure feasible initial delivery, leveraging web evidence for market grounding.', input: 'FeatureHierarchy', output: 'MvpSpecification' },
  { id: '07', name: 'Specification Agent', desc: 'Formalizes architectural specifications, API signatures, and data contracts.', input: 'MvpSpecification', output: 'TechnicalSpec' },
  { id: '08', name: 'Timeline Agent', desc: 'Projects realistic phase durations, critical paths, and review intervals.', input: 'TechnicalSpec', output: 'ProjectTimeline' },
  { id: '09', name: 'Risk Agent', desc: 'Identifies technical, operational, and architectural risks with prevention protocols.', input: 'ProjectTimeline', output: 'RiskRegister' },
  { id: '10', name: 'Task Agent', desc: 'Decomposes features into discrete, actionable work packages with completion criteria.', input: 'RiskRegister', output: 'TaskPackages' },
  { id: '11', name: 'Milestone Agent', desc: 'Bundles tasks into sequential milestone gates and measurable review checkpoints.', input: 'TaskPackages', output: 'MilestonePlan' },
  { id: '12', name: 'README Agent', desc: 'Assembles comprehensive onboarding, installation, and usage documentation.', input: 'MilestonePlan', output: 'ReadmeArtifact' },
  { id: '13', name: 'QA/Judge Agent', desc: 'Evaluates generated blueprint outputs against consistency and quality standards before persistence.', input: 'All Artifacts', output: 'QualityVerdict' },
];

function ThirteenAgentsSection() {
  return (
    <SectionReveal id="agents" className="p03-section p03-section--alt">
      <div className="p03-section__inner">
        <div className="p03-section-head">
          <span className="p03-eyebrow">06 / MULTI-AGENT SYSTEM</span>
          <h2 className="p03-heading">The 13-Agent Architecture</h2>
          <p className="p03-subheading">
            GrowFlow utilizes exactly thirteen specialized single-responsibility agents orchestrated
            through LangGraph. No agent acts as an unconstrained general-purpose engine.
          </p>
        </div>

        <div className="p03-agents-grid">
          {THIRTEEN_AGENTS.map((agent) => (
            <div key={agent.id} className="p03-agent-card">
              <div className="p03-agent-head">
                <span className="p03-agent-title">{agent.name}</span>
                <Badge variant={agent.id === '13' ? 'accent' : 'neutral'}>Agent {agent.id}</Badge>
              </div>
              <p className="p03-agent-desc">{agent.desc}</p>
              <div className="p03-agent-contract">
                <span>In: {agent.input}</span>
                <span>Out: {agent.output}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   7. Knowledge & RAG Section
   ========================================================================== */

function KnowledgeRagSection() {
  return (
    <SectionReveal id="rag" className="p03-section">
      <div className="p03-section__inner">
        <div className="p03-section-head">
          <span className="p03-eyebrow">07 / KNOWLEDGE & RETRIEVAL</span>
          <h2 className="p03-heading">Knowledge Architecture & RAG</h2>
          <p className="p03-subheading">
            Strict separation between authoritative relational records and derived semantic knowledge.
            Vector embeddings are completely rebuildable from canonical state.
          </p>
        </div>

        <div className="p03-rag-split">
          {/* Canonical State */}
          <div className="p03-rag-col">
            <div className="p03-card__head">
              <span className="p03-card__title">PostgreSQL (Canonical State)</span>
              <Badge variant="success">Authoritative</Badge>
            </div>
            <div className="p03-rag-feature-list">
              <div className="p03-rag-feature">
                <span>✓</span>
                <div><strong>ACID-Compliant Relational Store:</strong> Owns users, workspaces, projects, milestones, tasks, and audit logs.</div>
              </div>
              <div className="p03-rag-feature">
                <span>✓</span>
                <div><strong>Unalterable Audit Trails:</strong> Every project transition, state change, and mentor review is permanently recorded.</div>
              </div>
              <div className="p03-rag-feature">
                <span>✓</span>
                <div><strong>Independent Survivability:</strong> If vector caches or RAG databases are purged, canonical state remains 100% intact.</div>
              </div>
            </div>
          </div>

          {/* Derived RAG */}
          <div className="p03-rag-col">
            <div className="p03-card__head">
              <span className="p03-card__title">pgvector + LlamaIndex (RAG)</span>
              <Badge variant="accent">Derived & Ephemeral</Badge>
            </div>
            <div className="p03-rag-feature-list">
              <div className="p03-rag-feature">
                <span>⚡</span>
                <div><strong>Project-Scoped Embeddings:</strong> Vector queries are strictly partitioned by <code>project_id</code> metadata filters.</div>
              </div>
              <div className="p03-rag-feature">
                <span>⚡</span>
                <div><strong>Zero Cross-Tenant Leakage:</strong> Semantic searches never retrieve document fragments across tenant boundaries.</div>
              </div>
              <div className="p03-rag-feature">
                <span>⚡</span>
                <div><strong>Deterministic Regeneration:</strong> RAG indices can be fully rebuilt on-demand from canonical markdown documents.</div>
              </div>
            </div>
          </div>
        </div>

        {/* Canonical Context Priority Hierarchy */}
        <div className="p03-context-hierarchy" role="region" aria-label="Canonical context priority hierarchy">
          <div className="p03-card__head">
            <div>
              <span className="p03-card__title">Canonical Context Priority Hierarchy</span>
              <p style={{ fontSize: '13px', color: 'var(--gf-color-text-secondary)', marginTop: '4px' }}>
                Resolution order for agent reasoning and artifact generation. Web evidence informs the MVP workflow but never mutates canonical state.
              </p>
            </div>
            <Badge variant="neutral">Deterministic Governance</Badge>
          </div>
          <div className="p03-priority-steps">
            <div className="p03-priority-step p03-priority-step--highlight">
              <span className="p03-priority-rank">1</span>
              <div>
                <strong>Canonical Project State</strong>
                <span>PostgreSQL database of record · Absolute authority for all project entities</span>
              </div>
            </div>
            <div className="p03-priority-step">
              <span className="p03-priority-rank">2</span>
              <div>
                <strong>Latest Approved Structured Output</strong>
                <span>Pydantic-validated domain schemas approved by deterministic gates</span>
              </div>
            </div>
            <div className="p03-priority-step">
              <span className="p03-priority-rank">3</span>
              <div>
                <strong>Validated Documents</strong>
                <span>Architectural blueprints, milestone schedules, and task specifications</span>
              </div>
            </div>
            <div className="p03-priority-step">
              <span className="p03-priority-rank">4</span>
              <div>
                <strong>Project-Scoped RAG</strong>
                <span>pgvector embeddings partitioned by project tenancy · Derived & rebuildable</span>
              </div>
            </div>
            <div className="p03-priority-step">
              <span className="p03-priority-rank">5</span>
              <div>
                <strong>Web Evidence (Tavily Search)</strong>
                <span>External web research utilized by MVP workflow · Strictly non-canonical</span>
              </div>
            </div>
            <div className="p03-priority-step">
              <span className="p03-priority-rank">6</span>
              <div>
                <strong>Model Knowledge</strong>
                <span>Foundation LLM parametric weights · Constrained by system prompts</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   8. Persistent Background Work / Reliability Section
   ========================================================================== */

function BackgroundWorkSection() {
  return (
    <SectionReveal id="workers" className="p03-section p03-section--alt">
      <div className="p03-section__inner">
        <div className="p03-section-head">
          <span className="p03-eyebrow">08 / RELIABILITY & WORKERS</span>
          <h2 className="p03-heading">Persistent Background Work & Reliability</h2>
          <p className="p03-subheading">
            Long-running operations run independently of browser connections via durable worker queues.
            Server-Sent Events (SSE) serve as a live delivery mechanism, not the source of truth.
          </p>
        </div>

        <div className="p03-worker-flow">
          <div>
            <h3 style={{ fontSize: 'var(--gf-text-h4-size)', fontWeight: 700, color: 'var(--gf-color-text-primary)', marginBottom: 'var(--gf-space-4)' }}>
              Durable Job Lifecycle
            </h3>
            <p style={{ fontSize: 'var(--gf-text-body-size)', color: 'var(--gf-color-text-secondary)', lineHeight: 1.6, marginBottom: 'var(--gf-space-5)' }}>
              When a blueprint or document generation is requested, the API dispatches a durable background job
              via the transactional outbox pattern. Persistent background workers pick up the task and execute
              the multi-agent graph. If the client disconnects, the worker completes execution, commits results
              to PostgreSQL, and updates job state for seamless reconnection.
            </p>
            <div style={{ display: 'flex', gap: 'var(--gf-space-2)', flexWrap: 'wrap' }}>
              <Badge variant="neutral">Auto-Retry with Backoff</Badge>
              <Badge variant="neutral">Transactional Outbox</Badge>
              <Badge variant="accent">SSE Reconnection Safe</Badge>
            </div>
          </div>

          <div className="p03-job-box" role="region" aria-label="Illustrative worker execution state">
            <div className="p03-card__head">
              <span className="p03-card__title">Worker Execution: Job #9024</span>
              <Badge variant="info">In Progress</Badge>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div className="p03-job-step-row">
                <span>1. Load Project Context</span>
                <span style={{ color: 'var(--gf-color-success)' }}>Completed ✓</span>
              </div>
              <div className="p03-job-step-row">
                <span>2. Agent Graph Orchestration</span>
                <span style={{ color: 'var(--gf-color-accent)' }}>Running ●</span>
              </div>
              <div className="p03-job-step-row">
                <span>3. Schema & Constraint QA</span>
                <span style={{ color: 'var(--gf-color-text-tertiary)' }}>Queued ○</span>
              </div>
              <div className="p03-job-step-row">
                <span>4. Canonical DB Persistence</span>
                <span style={{ color: 'var(--gf-color-text-tertiary)' }}>Queued ○</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   9. Security Section
   ========================================================================== */

const SECURITY_PILLARS = [
  { title: 'Authentication & RBAC', desc: 'Secure JWT handling, Bcrypt password hashing, and strict role segregation across Student (BUILD), Mentor (SUPERVISE), and Administrator (GOVERN).' },
  { title: 'Workspace Isolation', desc: 'Strict multi-tenant partitioning at the database layer. Foreign-key tenancy ensures students and mentors only access authorized project boundaries.' },
  { title: 'RAG Context Partitioning', desc: 'Embeddings are strictly filtered by project identifier. Semantic similarity searches cannot cross-reference unauthorized project vectors.' },
  { title: 'Server-Side Secret Protection', desc: 'AI provider API keys and model credentials reside strictly on the server-side gateway. No provider credentials ever reach the client application.' },
];

function SecuritySection() {
  return (
    <SectionReveal id="security" className="p03-section">
      <div className="p03-section__inner">
        <div className="p03-section-head">
          <span className="p03-eyebrow">09 / SECURITY & ISOLATION</span>
          <h2 className="p03-heading">Security & Isolation Architecture</h2>
          <p className="p03-subheading">
            Enterprise-grade isolation boundaries protect student workspaces, mentor reviews, and AI
            credentials against unauthorized access.
          </p>
        </div>

        <div className="p03-security-grid">
          {SECURITY_PILLARS.map((p) => (
            <div key={p.title} className="p03-security-card">
              <div className="p03-security-title">
                <span>🔒</span>
                <span>{p.title}</span>
              </div>
              <p className="p03-security-desc">{p.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   10. Observability Section
   ========================================================================== */

function ObservabilitySection() {
  const illustrativeFields = [
    { label: 'EXECUTION', val: 'Completed', sub: 'Lifecycle terminal state' },
    { label: 'AGENT', val: 'Technology Agent', sub: 'Bounded single role' },
    { label: 'MODEL', val: 'Configured Provider', sub: 'Centralized AI gateway' },
    { label: 'LATENCY', val: 'Observed', sub: 'Per-step telemetry' },
    { label: 'TOKENS', val: 'Tracked', sub: 'Usage accounting' },
    { label: 'RETRIES', val: '0', sub: 'Deterministic schema hit' },
    { label: 'QA VERDICT', val: 'Passed', sub: 'Quality gate verified' },
    { label: 'PERSISTENCE', val: 'Committed', sub: 'PostgreSQL ACID write' },
  ];

  return (
    <SectionReveal id="observability" className="p03-section p03-section--alt">
      <div className="p03-section__inner">
        <div className="p03-section-head">
          <span className="p03-eyebrow">10 / OBSERVABILITY & TELEMETRY</span>
          <h2 className="p03-heading">Platform Observability</h2>
          <p className="p03-subheading">
            Structured execution telemetry across API gateways, durable background jobs, schema validation gates, and AI provider interactions.
          </p>
        </div>

        <div className="p03-obs-surface" role="region" aria-label="Illustrative execution telemetry">
          <div className="p03-obs-surface-head">
            <div className="p03-obs-surface-title">
              <span className="p03-obs-surface-dot" />
              <span>ILLUSTRATIVE EXECUTION</span>
            </div>
            <Badge variant="neutral">Sample Trace Metadata</Badge>
          </div>

          <div className="p03-obs-grid">
            {illustrativeFields.map((field) => (
              <div key={field.label} className="p03-obs-stat">
                <span className="p03-obs-label">{field.label}</span>
                <span className="p03-obs-val p03-obs-val--meta">{field.val}</span>
                <span className="p03-obs-sub">{field.sub}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   11. Engineering Principles Section
   ========================================================================== */

const PRINCIPLES = [
  { num: '01', title: 'Deterministic State Authority', copy: 'AI agents generate proposals; deterministic domain services and relational schemas hold the authority to commit changes.' },
  { num: '02', title: 'Separation of Concerns', copy: 'Client renders; FastAPI governs and authenticates; Persistent background workers execute durable jobs; PostgreSQL persists.' },
  { num: '03', title: 'Bounded Single Responsibility', copy: 'Every agent has one explicit role with strict Pydantic input/output contracts. No unconstrained generalist models.' },
  { num: '04', title: 'Fail-Safe Asynchrony', copy: 'Long operations survive client disconnections, network dropouts, and page refreshes via durable background workers.' },
  { num: '05', title: 'Zero-Trust AI Gatekeeping', copy: 'Every generative artifact undergoes schema verification, business logic checks, and independent QA evaluation before state mutation.' },
  { num: '06', title: 'Rebuildable Vector Intelligence', copy: 'Vector indexes are derived artifacts. If all embeddings are lost, canonical PostgreSQL records allow instant complete re-indexing.' },
];

function EngineeringPrinciplesSection() {
  return (
    <SectionReveal id="principles" className="p03-section">
      <div className="p03-section__inner">
        <div className="p03-section-head">
          <span className="p03-eyebrow">11 / CORE VALUES</span>
          <h2 className="p03-heading">Engineering Principles</h2>
          <p className="p03-subheading">
            The architectural commitments that guide every decision in the GrowFlow platform.
          </p>
        </div>

        <div className="p03-principles-grid">
          {PRINCIPLES.map((p) => (
            <div key={p.num} className="p03-principle-card">
              <span className="p03-principle-num">{p.num}</span>
              <div className="p03-principle-title">{p.title}</div>
              <p className="p03-principle-copy">{p.copy}</p>
            </div>
          ))}
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   12. Architecture at a Glance (Matrix Table)
   ========================================================================== */

function ArchitectureGlanceSection() {
  return (
    <SectionReveal id="at-a-glance" className="p03-section p03-section--alt">
      <div className="p03-section__inner">
        <div className="p03-section-head">
          <span className="p03-eyebrow">12 / ARCHITECTURE AT A GLANCE</span>
          <h2 className="p03-heading">Architecture at a Glance</h2>
          <p className="p03-subheading">
            A comprehensive matrix of system tiers, technology selections, operational roles, and state authority.
          </p>
        </div>

        <div className="p03-table-wrap">
          <table className="p03-table" aria-label="System architecture overview matrix">
            <thead>
              <tr>
                <th>Component</th>
                <th>Technology</th>
                <th>Primary Role</th>
                <th>State Authority</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Frontend Client</strong></td>
                <td>React 19 + TypeScript + Vite</td>
                <td>Presentational UI, user interactions, local view state</td>
                <td>Ephemeral / UI Only</td>
              </tr>
              <tr>
                <td><strong>API Gateway</strong></td>
                <td>FastAPI + Python 3.12</td>
                <td>Authentication, request validation, SSE streaming, domain logic</td>
                <td>Stateless Gateway</td>
              </tr>
              <tr>
                <td><strong>Agent Orchestrator</strong></td>
                <td>LangGraph + LangChain</td>
                <td>Coordination of 13 single-purpose reasoning agents</td>
                <td>Transient Execution State</td>
              </tr>
              <tr>
                <td><strong>Background Workers</strong></td>
                <td>Persistent Background Workers</td>
                <td>Durable, connection-independent asynchronous execution</td>
                <td>Ephemeral Job & Outbox State</td>
              </tr>
              <tr>
                <td><strong>Primary Database</strong></td>
                <td>PostgreSQL</td>
                <td>ACID relational data, users, project state, immutable audit logs</td>
                <td><strong>Canonical Source of Truth</strong></td>
              </tr>
              <tr>
                <td><strong>Semantic Vector Store</strong></td>
                <td>pgvector + LlamaIndex</td>
                <td>Project-scoped embedding indexes for contextual RAG</td>
                <td>Derived / Fully Rebuildable</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   13. Documentation Philosophy Section
   ========================================================================== */

function DocumentationPhilosophySection() {
  return (
    <SectionReveal className="p03-section">
      <div className="p03-section__inner">
        <div className="p03-section-head p03-section-head--center">
          <span className="p03-eyebrow">13 / PHILOSOPHY</span>
          <h2 className="p03-heading">Documentation Philosophy</h2>
          <p className="p03-subheading">
            Documentation is code. In GrowFlow, specifications are frozen at architectural development gates
            to prevent drift, enforce alignment between backend and frontend, and ensure long-term maintainability.
          </p>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   14. Trust / Closing Statement Section
   ========================================================================== */

function TrustStatementSection() {
  return (
    <SectionReveal className="p03-section p03-section--alt">
      <div className="p03-section__inner">
        <div className="p03-trust-banner">
          <div className="p03-trust-quote">
            "GrowFlow was built to replace unstructured project chaos with clarity and rigor. By grounding
            artificial intelligence inside deterministic software engineering, students build with confidence,
            mentors supervise with precision, and projects reach completion."
          </div>
          <div className="p03-trust-author">
            GrowFlow Engineering Team · Core Architecture Directive
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   15. Final CTA Section
   ========================================================================== */

function FinalCtaSection() {
  return (
    <section className="p03-final-cta" aria-labelledby="docs-final-cta-heading">
      <div className="p03-final-cta__inner">
        <h2 id="docs-final-cta-heading" className="p03-final-cta__h2">
          Ready to explore the workspace?
        </h2>
        <p className="p03-final-cta__copy">
          Start building your project with guided intelligence and structured execution.
        </p>
        <div className="p03-final-cta__actions">
          <Button as="link" to="/auth/student/register" size="lg">
            Start Building
          </Button>
          <Button as="link" to="/features" variant="secondary" size="lg">
            Explore Features
          </Button>
        </div>
      </div>
    </section>
  );
}
