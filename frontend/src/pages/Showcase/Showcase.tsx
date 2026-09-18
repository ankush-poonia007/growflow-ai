import { useEffect } from 'react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { SectionReveal } from '@/components/ui/SectionReveal';
import './Showcase.css';

/**
 * P05 — Public Project / Architecture Showcase
 *
 * Route: /showcase
 * Audience: Public / unauthenticated
 * Purpose: Credible visual window into the GrowFlow system, demonstrating the
 *          relationship between lifecycle, workspace, connected tasks, 13 AI agents,
 *          context hierarchy, persistent workers, three perspectives, and layered architecture.
 */
export function Showcase() {
  useEffect(() => {
    document.title = 'See the System Behind the Flow — GrowFlow';
    const metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc) {
      metaDesc.setAttribute(
        'content',
        'Explore how GrowFlow connects project lifecycle, AI agents, execution, knowledge, mentorship, and observability.',
      );
    }
  }, []);

  return (
    <div className="p05-page">
      {/* 1. Hero */}
      <HeroSection />

      {/* 2. From Idea to Execution (Lifecycle) */}
      <LifecycleSection />

      {/* 3. A Glimpse Inside the Workspace */}
      <WorkspaceGlimpseSection />

      {/* 4. Everything Connects (Canonical Chain) */}
      <EverythingConnectsSection />

      {/* 5. AI Works as a System (13 Agents) */}
      <AiSystemSection />

      {/* 6. Knowledge Stays in Context (Context Stack) */}
      <KnowledgeContextSection />

      {/* 7. Work Continues Even When You Leave (Persistence) */}
      <PersistentWorkSection />

      {/* 8. Three Perspectives. One System. */}
      <ThreePerspectivesSection />

      {/* 9. Architecture at a Glance */}
      <ArchitectureGlanceSection />

      {/* 10. Closing CTA */}
      <FinalCtaSection />
    </div>
  );
}

/* ==========================================================================
   1. Hero Section
   ========================================================================== */

function HeroSection() {
  return (
    <section className="p05-hero" aria-labelledby="showcase-hero-heading">
      <div className="p05-hero__inner">
        <div className="p05-hero__header">
          <span className="p05-hero__eyebrow">
            <span className="p05-hero__eyebrow-dot" aria-hidden="true" />
            PROJECT SHOWCASE
          </span>
          <h1 id="showcase-hero-heading" className="p05-hero__h1">
            See the system behind the flow.
          </h1>
          <p className="p05-hero__copy">
            GrowFlow connects project definition, AI-assisted planning, execution, mentorship,
            and observability into one continuous system.
          </p>

          <div className="p05-hero__actions">
            <Button as="link" to="/documentation" size="lg">
              Explore the documentation
            </Button>
            <Button as="link" to="/auth/student/register" variant="secondary" size="lg">
              Enter the workspace
            </Button>
          </div>
        </div>

        {/* Hero Composed Product Artifact */}
        <div className="p05-hero-artifact" aria-label="Illustrative system preview">
          <div className="p05-artifact-bar">
            <div className="p05-artifact-controls" aria-hidden="true">
              <span className="p05-control-dot" />
              <span className="p05-control-dot" />
              <span className="p05-control-dot" />
            </div>
            <span className="p05-artifact-title">GrowFlow System Preview · Connected Architecture</span>
            <span className="p05-artifact-badge">Illustrative system view</span>
          </div>

          <div className="p05-artifact-body">
            {/* Artifact Pillar 1: Lifecycle Track */}
            <div className="p05-artifact-card" tabIndex={0} role="region" aria-label="Hero Artifact: Lifecycle Position">
              <div className="p05-card-head">
                <span className="p05-card-tag">LIFECYCLE POSITION</span>
                <Badge variant="accent">Implementation</Badge>
              </div>
              <p className="p05-card-lead">AI-Powered Research Workspace</p>
              <div className="p05-lifecycle-mini-track" aria-hidden="true">
                <span className="p05-mini-step p05-mini-step--done">Assessment</span>
                <span className="p05-mini-sep">→</span>
                <span className="p05-mini-step p05-mini-step--done">Blueprint</span>
                <span className="p05-mini-sep">→</span>
                <span className="p05-mini-step p05-mini-step--active">Build</span>
                <span className="p05-mini-sep">→</span>
                <span className="p05-mini-step">Release</span>
              </div>
            </div>

            {/* Artifact Pillar 2: Connected Chain */}
            <div className="p05-artifact-card" tabIndex={0} role="region" aria-label="Hero Artifact: Execution Chain">
              <div className="p05-card-head">
                <span className="p05-card-tag">EXECUTION CHAIN</span>
                <Badge variant="success" dot>Healthy</Badge>
              </div>
              <p className="p05-card-lead">Task → Milestone → Phase</p>
              <div className="p05-artifact-chain-metric">
                <div className="p05-chain-bar-track">
                  <div className="p05-chain-bar-fill" style={{ width: '72%' }} />
                </div>
                <div className="p05-chain-bar-meta">
                  <span>Milestone: Intelligence Layer</span>
                  <strong>72%</strong>
                </div>
              </div>
            </div>

            {/* Artifact Pillar 3: Agent Orchestration */}
            <div className="p05-artifact-card" tabIndex={0} role="region" aria-label="Hero Artifact: AI Orchestration">
              <div className="p05-card-head">
                <span className="p05-card-tag">AI ORCHESTRATION</span>
                <Badge variant="info">13 Agents</Badge>
              </div>
              <p className="p05-card-lead">LangGraph Directed Pipeline</p>
              <p className="p05-card-caption">
                Deterministic structured output validated through PostgreSQL canonical state.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ==========================================================================
   2. From Idea to Execution (Canonical Lifecycle — Serpentine Connected Track)
   ========================================================================== */

const STAGE_ROW_1 = [
  { id: 'idea', step: '01', name: 'IDEA', desc: 'Define what is worth building.' },
  { id: 'assessment', step: '02', name: 'ASSESSMENT', desc: 'Understand the project and its constraints.' },
  { id: 'blueprint', step: '03', name: 'BLUEPRINT', desc: 'Turn understanding into structured direction.' },
  { id: 'planning', step: '04', name: 'PLANNING', desc: 'Translate direction into executable work.' },
] as const;

const STAGE_ROW_2 = [
  { id: 'implementation', step: '05', name: 'IMPLEMENTATION', desc: 'Build against the planned system.' },
  { id: 'testing', step: '06', name: 'TESTING', desc: 'Validate the result.' },
  { id: 'deployment', step: '07', name: 'DEPLOYMENT', desc: 'Move the project toward release.' },
  { id: 'completed', step: '08', name: 'COMPLETED', desc: 'Close the loop with a finished system.' },
] as const;

function LifecycleSection() {
  return (
    <SectionReveal className="p05-section" id="showcase-lifecycle">
      <div className="p05-section__inner">
        <div className="p05-section__header">
          <span className="p05-eyebrow">CANONICAL LIFECYCLE</span>
          <h2 className="p05-h2">From idea to execution.</h2>
          <p className="p05-copy">
            Every project moves through a defined lifecycle, keeping planning and execution connected.
          </p>
        </div>

        <div className="p05-lifecycle-serpentine" role="list" aria-label="8-stage project lifecycle sequence">
          {/* Row 1: Forward Path (01 to 04) */}
          <div className="p05-lifecycle-row p05-lifecycle-row--forward">
            {STAGE_ROW_1.map((stg, idx) => (
              <div key={stg.id} className="p05-stage-wrapper">
                <div
                  className="p05-stage-item"
                  role="listitem"
                  tabIndex={0}
                  aria-label={`Stage ${stg.step}: ${stg.name} — ${stg.desc}`}
                >
                  <div className="p05-stage-node">
                    <span className="p05-stage-num">{stg.step}</span>
                  </div>
                  <div className="p05-stage-content">
                    <strong className="p05-stage-name">{stg.name}</strong>
                    <p className="p05-stage-desc">{stg.desc}</p>
                  </div>
                </div>

                {idx < STAGE_ROW_1.length - 1 && (
                  <div className="p05-stage-connector p05-stage-connector--right" aria-hidden="true">
                    <span className="p05-connector-arrow p05-connector-arrow--desktop">→</span>
                    <span className="p05-connector-arrow p05-connector-arrow--mobile">↓</span>
                  </div>
                )}
                {idx === STAGE_ROW_1.length - 1 && (
                  <div className="p05-stage-connector p05-stage-connector--turn" aria-hidden="true">
                    <span className="p05-turn-arrow">↓</span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Row 2: Reverse Path on desktop (05 to 08, flowing left to terminal 08 COMPLETED) */}
          <div className="p05-lifecycle-row p05-lifecycle-row--reverse">
            {STAGE_ROW_2.map((stg, idx) => {
              const isTerminal = stg.id === 'completed';
              return (
                <div
                  key={stg.id}
                  className={`p05-stage-wrapper ${isTerminal ? 'p05-stage-wrapper--terminal' : ''}`}
                >
                  <div
                    className={`p05-stage-item ${isTerminal ? 'p05-stage-item--terminal' : ''}`}
                    role="listitem"
                    tabIndex={0}
                    aria-label={`Stage ${stg.step}: ${stg.name} — ${stg.desc}`}
                  >
                    <div className={`p05-stage-node ${isTerminal ? 'p05-stage-node--terminal' : ''}`}>
                      <span className="p05-stage-num">{isTerminal ? '✓' : stg.step}</span>
                    </div>
                    <div className="p05-stage-content">
                      <div className="p05-stage-title-row">
                        <strong className="p05-stage-name">{stg.name}</strong>
                        {isTerminal && <Badge variant="success" dot>Final Destination</Badge>}
                      </div>
                      <p className="p05-stage-desc">{stg.desc}</p>
                    </div>
                  </div>

                  {idx < STAGE_ROW_2.length - 1 && (
                    <div className="p05-stage-connector p05-stage-connector--left" aria-hidden="true">
                      <span className="p05-connector-arrow p05-connector-arrow--desktop">←</span>
                      <span className="p05-connector-arrow p05-connector-arrow--mobile">↓</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   3. A Glimpse Inside the Workspace (Illustrative Workspace Preview)
   ========================================================================== */

function WorkspaceGlimpseSection() {
  return (
    <SectionReveal className="p05-section p05-section--alt" id="showcase-workspace">
      <div className="p05-section__inner">
        <div className="p05-section__header">
          <span className="p05-eyebrow">WORKPLACE PREVIEW</span>
          <h2 className="p05-h2">A glimpse inside the workspace.</h2>
          <p className="p05-copy">
            Projects become tangible when the system turns planning into visible, connected work.
          </p>
        </div>

        <div className="p05-workspace-frame" aria-label="Illustrative student workspace preview">
          {/* Window Header */}
          <div className="p05-workspace-bar">
            <div className="p05-workspace-crumb">
              <span className="p05-crumb-root">Projects</span>
              <span className="p05-crumb-sep">/</span>
              <span className="p05-crumb-active">AI-Powered Research Workspace</span>
              <span className="p05-illustrative-tag">Illustrative workspace preview</span>
            </div>

            <div className="p05-workspace-badges">
              <Badge variant="success" dot>Healthy</Badge>
              <Badge variant="accent">Implementation</Badge>
              <span className="p05-progress-metric">Progress: 72%</span>
            </div>
          </div>

          {/* Workspace Layout Grid */}
          <div className="p05-workspace-grid">
            {/* Left Column: Tasks & Milestones */}
            <div className="p05-workspace-col">
              {/* Task Checklist */}
              <div className="p05-panel" tabIndex={0} role="region" aria-label="Workspace Tasks Panel">
                <div className="p05-panel-head">
                  <h3 className="p05-panel-title">Active Tasks</h3>
                  <span className="p05-panel-counter">2 of 4 Completed</span>
                </div>
                <div className="p05-task-list">
                  <div className="p05-task-item p05-task-item--done" tabIndex={0} role="checkbox" aria-checked="true" aria-label="Task: Define ingestion pipeline (Completed)">
                    <span className="p05-task-check" aria-hidden="true">✓</span>
                    <span className="p05-task-name">Define ingestion pipeline</span>
                    <Badge variant="neutral">Task</Badge>
                  </div>
                  <div className="p05-task-item p05-task-item--done" tabIndex={0} role="checkbox" aria-checked="true" aria-label="Task: Validate document indexing (Completed)">
                    <span className="p05-task-check" aria-hidden="true">✓</span>
                    <span className="p05-task-name">Validate document indexing</span>
                    <Badge variant="neutral">Task</Badge>
                  </div>
                  <div className="p05-task-item p05-task-item--active" tabIndex={0} role="checkbox" aria-checked="false" aria-label="Task: Build retrieval evaluation (In Progress)">
                    <span className="p05-task-bullet" aria-hidden="true" />
                    <span className="p05-task-name">Build retrieval evaluation</span>
                    <Badge variant="accent">In Progress</Badge>
                  </div>
                  <div className="p05-task-item p05-task-item--pending" tabIndex={0} role="checkbox" aria-checked="false" aria-label="Task: Prepare deployment checklist (Pending)">
                    <span className="p05-task-bullet" aria-hidden="true" />
                    <span className="p05-task-name">Prepare deployment checklist</span>
                    <Badge variant="neutral">Pending</Badge>
                  </div>
                </div>
              </div>

              {/* Milestones Flow */}
              <div className="p05-panel" tabIndex={0} role="region" aria-label="Workspace Milestones Panel">
                <div className="p05-panel-head">
                  <h3 className="p05-panel-title">Milestone Progress</h3>
                  <span className="p05-panel-counter">Milestone 2 of 4</span>
                </div>
                <div className="p05-milestones-row">
                  <div className="p05-milestone-pill p05-milestone-pill--done" tabIndex={0} aria-label="Milestone 1: Foundation (Completed)">
                    <span className="p05-pill-state" aria-hidden="true">✓</span>
                    <span className="p05-pill-name">Foundation</span>
                  </div>
                  <div className="p05-milestone-pill p05-milestone-pill--active" tabIndex={0} aria-label="Milestone 2: Intelligence Layer (Active)">
                    <span className="p05-pill-state" aria-hidden="true">●</span>
                    <span className="p05-pill-name">Intelligence Layer</span>
                  </div>
                  <div className="p05-milestone-pill" tabIndex={0} aria-label="Milestone 3: Validation (Upcoming)">
                    <span className="p05-pill-state" aria-hidden="true">○</span>
                    <span className="p05-pill-name">Validation</span>
                  </div>
                  <div className="p05-milestone-pill" tabIndex={0} aria-label="Milestone 4: Release (Upcoming)">
                    <span className="p05-pill-state" aria-hidden="true">○</span>
                    <span className="p05-pill-name">Release</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: AI Mentor & Recent Activity */}
            <div className="p05-workspace-col">
              {/* AI Mentor Panel */}
              <div className="p05-panel p05-panel--ai" tabIndex={0} role="region" aria-label="AI Mentor Guidance Panel">
                <div className="p05-panel-head">
                  <div className="p05-ai-tag">
                    <span className="p05-ai-dot" />
                    <h3 className="p05-panel-title">AI Mentor</h3>
                  </div>
                  <Badge variant="info">Continuous Guidance</Badge>
                </div>
                <div className="p05-ai-message">
                  <p className="p05-ai-text">
                    "Your current milestone is approaching completion. Review the remaining validation tasks before moving toward release."
                  </p>
                  <span className="p05-ai-hint">Suggested checkpoint: Run retrieval test benchmark</span>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="p05-panel" tabIndex={0} role="region" aria-label="Workspace Recent Activity Panel">
                <div className="p05-panel-head">
                  <h3 className="p05-panel-title">Recent Activity</h3>
                  <span className="p05-panel-counter">Illustrative Events</span>
                </div>
                <div className="p05-activity-list">
                  <div className="p05-activity-item" tabIndex={0} aria-label="Activity: Architecture specification approved by Mentor">
                    <span className="p05-activity-dot" aria-hidden="true" />
                    <div className="p05-activity-content">
                      <p className="p05-activity-msg">Architecture specification approved by Mentor</p>
                      <span className="p05-activity-time">Milestone 01 Verified</span>
                    </div>
                  </div>
                  <div className="p05-activity-item" tabIndex={0} aria-label="Activity: Vector partition benchmark passed deterministic check">
                    <span className="p05-activity-dot" aria-hidden="true" />
                    <div className="p05-activity-content">
                      <p className="p05-activity-msg">Vector partition benchmark passed deterministic check</p>
                      <span className="p05-activity-time">Automated QA</span>
                    </div>
                  </div>
                  <div className="p05-activity-item" tabIndex={0} aria-label="Activity: Task graph synced to PostgreSQL canonical state">
                    <span className="p05-activity-dot" aria-hidden="true" />
                    <div className="p05-activity-content">
                      <p className="p05-activity-msg">Task graph synced to PostgreSQL canonical state</p>
                      <span className="p05-activity-time">System Persistence</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="p05-workspace-footer">
            <span className="p05-footer-caption">
              Illustrative workspace preview · Non-live product simulation demonstrating connected execution data
            </span>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   4. Everything Connects (Canonical Chain)
   ========================================================================== */

const CHAIN_LEVELS = [
  {
    level: 'LEVEL 01',
    entity: 'TASK',
    example: 'Finish retrieval evaluation',
    role: 'Atomic unit of work executed by student or agent.',
  },
  {
    level: 'LEVEL 02',
    entity: 'MILESTONE',
    example: 'Intelligence Layer',
    role: 'Structured checkpoint aggregating completed tasks.',
  },
  {
    level: 'LEVEL 03',
    entity: 'PROGRESS',
    example: '72% Complete',
    role: 'Deterministic progress calculated from completed milestones.',
  },
  {
    level: 'LEVEL 04',
    entity: 'PHASE',
    example: 'Phase 05 · Implementation',
    role: 'Project progression gate enforced by validation.',
  },
  {
    level: 'LEVEL 05',
    entity: 'HEALTH',
    example: 'Healthy',
    role: 'Holistic evaluation synthesizing milestone velocity and blockers.',
  },
] as const;

function EverythingConnectsSection() {
  return (
    <SectionReveal className="p05-section" id="showcase-connections">
      <div className="p05-section__inner">
        <div className="p05-section__header">
          <span className="p05-eyebrow">CANONICAL PROJECT CHAIN</span>
          <h2 className="p05-h2">Everything connects.</h2>
          <p className="p05-copy">
            A task is not isolated. Execution rolls upward into milestones, progress, phases,
            and overall project health.
          </p>
        </div>

        <div className="p05-chain-grid">
          {CHAIN_LEVELS.map((item, idx) => (
            <div
              key={item.entity}
              className="p05-chain-node"
              tabIndex={0}
              role="listitem"
              aria-label={`${item.level}: ${item.entity} — ${item.role}`}
            >
              <div className="p05-chain-header">
                <span className="p05-chain-level">{item.level}</span>
                <strong className="p05-chain-entity">{item.entity}</strong>
              </div>
              <div className="p05-chain-example">
                <span className="p05-example-label">Example</span>
                <span className="p05-example-val">"{item.example}"</span>
              </div>
              <p className="p05-chain-role">{item.role}</p>

              {idx < CHAIN_LEVELS.length - 1 && (
                <div className="p05-chain-arrow" aria-hidden="true">
                  <span className="p05-arrow-line" />
                  <span className="p05-arrow-head">↓</span>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="p05-chain-notice">
          <span className="p05-notice-tag">DETERMINISTIC AGGREGATION</span>
          <p className="p05-notice-text">
            Progress and health are not subjective estimates. They are derived bottom-up from concrete task completion,
            milestone validation rubrics, and mentor approvals.
          </p>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   5. AI Works as a System (Exactly 13 Agents)
   ========================================================================== */

const AGENT_STAGES = [
  {
    phase: 'STAGE 1 · INITIATION SEQUENCE',
    agents: [
      { num: '01', name: 'Idea Agent', desc: 'Ingestion, problem definition & core concept formulation' },
      { num: '02', name: 'Scope Agent', desc: 'Boundaries, constraints, non-goals & project feasibility' },
      { num: '03', name: 'Project Profile Agent', desc: 'Persona, target domain, stakeholder alignment & archetype' },
    ],
  },
  {
    phase: 'STAGE 2 · PARALLEL ANALYSIS BRANCH',
    branching: true,
    agents: [
      { num: '04', name: 'Technology Agent', desc: 'Stack selection, dependencies & architectural tradeoffs' },
      { num: '05', name: 'Features Agent', desc: 'Core capabilities, user stories & capability decomposition' },
      { num: '06', name: 'MVP Agent', desc: 'Minimal viable slice grounded with web evidence via Tavily' },
    ],
  },
  {
    phase: 'STAGE 3 · SPECIFICATION & BLUEPRINT SYNTHESIS',
    agents: [
      { num: '07', name: 'Specification Agent', desc: 'Technical contract, schemas & system blueprint synthesis' },
      { num: '08', name: 'Timeline / Duration Agent', desc: 'Realistic pacing, milestone duration & effort estimation' },
      { num: '09', name: 'Risk Agent', desc: 'Failure modes, technical debt & risk mitigation strategies' },
      { num: '10', name: 'Task Agent', desc: 'Decomposes blueprint into atomic, actionable task graphs' },
      { num: '11', name: 'Milestone Agent', desc: 'Aggregates tasks into verifiable milestone checkpoints' },
      { num: '12', name: 'README Agent', desc: 'Comprehensive architectural README & developer documentation' },
    ],
  },
  {
    phase: 'STAGE 4 · QUALITY & VERIFICATION GATE',
    agents: [
      { num: '13', name: 'QA / Judge Agent', desc: 'Deterministic evaluation against blueprint rubric & acceptance gates' },
    ],
  },
] as const;

function AiSystemSection() {
  return (
    <SectionReveal className="p05-section p05-section--alt" id="showcase-ai-system">
      <div className="p05-section__inner">
        <div className="p05-section__header">
          <span className="p05-eyebrow">SPECIALIZED AGENT PIPELINE</span>
          <h2 className="p05-h2">AI works as a system.</h2>
          <p className="p05-copy">
            GrowFlow uses specialized agents across the project lifecycle instead of treating
            AI as a single undifferentiated assistant.
          </p>
        </div>

        <div className="p05-agents-map">
          {AGENT_STAGES.map((stage) => (
            <div key={stage.phase} className="p05-agent-phase-group">
              <div className="p05-agent-phase-head">
                <span className="p05-agent-phase-title">{stage.phase}</span>
                {'branching' in stage && stage.branching && (
                  <Badge variant="accent">Parallel Branching</Badge>
                )}
              </div>

              <div className={`p05-agents-cards ${stage.agents.length === 3 ? 'p05-agents-cards--3' : ''}`}>
                {stage.agents.map((ag) => (
                  <div
                    key={ag.num}
                    className="p05-agent-card"
                    tabIndex={0}
                    role="listitem"
                    aria-label={`Agent ${ag.num}: ${ag.name} — ${ag.desc}`}
                  >
                    <div className="p05-agent-card-head">
                      <span className="p05-agent-num">{ag.num}</span>
                      <strong className="p05-agent-title">{ag.name}</strong>
                    </div>
                    <p className="p05-agent-desc">{ag.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Architecture Governance Note */}
        <div className="p05-callout-card">
          <span className="p05-callout-tag">ARCHITECTURAL BOUNDARY</span>
          <p className="p05-callout-text">
            <strong>Exactly 13 agents.</strong> GrowFlow does not invent ad-hoc agent personas or use a dedicated
            Change Impact Agent. Tavily is utilized strictly for external web evidence during the MVP analysis branch,
            never as canonical project state.
          </p>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   6. Knowledge Stays in Context (Context Hierarchy)
   ========================================================================== */

const CONTEXT_TIERS = [
  {
    tier: 'TIER 01',
    badge: 'PRIMARY AUTHORITY',
    name: 'Canonical Project State / PostgreSQL',
    desc: 'Versioned entity records, approved phase transitions, and immutable snapshots. Overrides all other sources.',
  },
  {
    tier: 'TIER 02',
    badge: 'BLUEPRINT AUTHORITY',
    name: 'Latest Approved Structured Output',
    desc: 'Verified JSON schemas, frozen specifications, and officially accepted milestone task graphs.',
  },
  {
    tier: 'TIER 03',
    badge: 'DOCUMENTED AUTHORITY',
    name: 'Validated Documents',
    desc: 'Curated architectural decision records, mentor feedback notes, and verified repository specifications.',
  },
  {
    tier: 'TIER 04',
    badge: 'RETRIEVAL CONTEXT',
    name: 'Project-Scoped RAG',
    desc: 'Vector partitions isolated strictly to the project tenant. Zero cross-project or cross-user context leakage.',
  },
  {
    tier: 'TIER 05',
    badge: 'FACTUAL EVIDENCE',
    name: 'Web Evidence / Tavily',
    desc: 'Targeted external library search and technical documentation. Informational evidence; never canonical state.',
  },
  {
    tier: 'TIER 06',
    badge: 'FOUNDATIONAL REASONING',
    name: 'Model Knowledge',
    desc: 'General language model parametric understanding; explicitly overridden whenever in conflict with higher tiers.',
  },
] as const;

function KnowledgeContextSection() {
  return (
    <SectionReveal className="p05-section" id="showcase-knowledge">
      <div className="p05-section__inner">
        <div className="p05-section__header">
          <span className="p05-eyebrow">CONTEXT PRECEDENCE</span>
          <h2 className="p05-h2">Knowledge stays in context.</h2>
          <p className="p05-copy">
            AI decisions are grounded through a defined context hierarchy rather than treating
            every source as equally authoritative.
          </p>
        </div>

        <div className="p05-context-stack">
          {CONTEXT_TIERS.map((tier) => (
            <div
              key={tier.tier}
              className="p05-context-layer"
              tabIndex={0}
              role="listitem"
              aria-label={`${tier.tier}: ${tier.name} (${tier.badge}) — ${tier.desc}`}
            >
              <div className="p05-context-head">
                <div className="p05-context-rank">
                  <span className="p05-rank-tier">{tier.tier}</span>
                  <strong className="p05-rank-name">{tier.name}</strong>
                </div>
                <Badge variant={tier.tier === 'TIER 01' ? 'accent' : 'neutral'}>{tier.badge}</Badge>
              </div>
              <p className="p05-context-desc">{tier.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   7. Work Continues Even When You Leave (Persistence)
   ========================================================================== */

const WORKER_STEPS = [
  { step: '01', title: 'User Starts Generation', desc: 'Visitor or student triggers an asynchronous blueprint or task workflow.' },
  { step: '02', title: 'Background Execution', desc: 'Job is queued in the transactional outbox table inside PostgreSQL.' },
  { step: '03', title: 'Agent Processing', desc: 'Independent background workers process LangGraph agent graphs.' },
  { step: '04', title: 'Validation / QA', desc: 'QA Judge evaluates output against strict Pydantic schemas and rubric.' },
  { step: '05', title: 'Persistence', desc: 'Results atomically committed to PostgreSQL canonical records.' },
  { step: '06', title: 'Workspace Updated', desc: 'SSE delivers real-time delta when browser is connected; persists if closed.' },
] as const;

const EXECUTION_STATES = [
  { state: 'QUEUED', desc: 'Enqueued in transactional outbox' },
  { state: 'RUNNING', desc: 'Worker executing LangGraph graph' },
  { state: 'VALIDATING', desc: 'QA Judge validating output rubric' },
  { state: 'COMPLETED', desc: 'State committed to PostgreSQL' },
] as const;

function PersistentWorkSection() {
  return (
    <SectionReveal className="p05-section p05-section--alt" id="showcase-persistence">
      <div className="p05-section__inner">
        <div className="p05-section__header">
          <span className="p05-eyebrow">PERSISTENT EXECUTION</span>
          <h2 className="p05-h2">Work continues even when you leave.</h2>
          <p className="p05-copy">
            Long-running work is designed to persist independently of the browser connection.
          </p>
        </div>

        {/* 6-step Flow */}
        <div className="p05-worker-flow" role="list">
          {WORKER_STEPS.map((ws) => (
            <div
              key={ws.step}
              className="p05-worker-step"
              role="listitem"
              tabIndex={0}
              aria-label={`Step ${ws.step}: ${ws.title} — ${ws.desc}`}
            >
              <span className="p05-worker-num">{ws.step}</span>
              <strong className="p05-worker-title">{ws.title}</strong>
              <p className="p05-worker-desc">{ws.desc}</p>
            </div>
          ))}
        </div>

        {/* Execution States Bar */}
        <div className="p05-states-card">
          <div className="p05-states-head">
            <span className="p05-states-tag">ILLUSTRATIVE EXECUTION STATES</span>
            <span className="p05-states-caption">SSE is delivery · Not the job lifetime</span>
          </div>
          <div className="p05-states-row">
            {EXECUTION_STATES.map((es, idx) => (
              <div
                key={es.state}
                className="p05-state-pill"
                tabIndex={0}
                aria-label={`State: ${es.state} — ${es.desc}`}
              >
                <span className="p05-state-label">{es.state}</span>
                <span className="p05-state-desc">{es.desc}</span>
                {idx < EXECUTION_STATES.length - 1 && (
                  <span className="p05-state-arrow" aria-hidden="true">→</span>
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
   8. Three Perspectives. One System. (Build / Supervise / Govern)
   ========================================================================== */

const PERSPECTIVES = [
  {
    role: 'STUDENT',
    tag: 'BUILD',
    headline: 'Execution & Guided Creation',
    copy: 'Students navigate concrete milestones, execute verified tasks, and receive real-time AI mentor feedback grounded in the project blueprint.',
    surfaces: [
      'Project workspace & task checklist',
      'Milestone submission & gate reviews',
      'AI Mentor dialogue & assistance',
      'Architecture specification view',
    ],
  },
  {
    role: 'MENTOR',
    tag: 'SUPERVISE',
    headline: 'Cohort Oversight & Review Gates',
    copy: 'Mentors supervise student cohorts across progression milestones, review structured project definitions, and provide guidance notes.',
    surfaces: [
      'Student cohort & group dashboard',
      'Milestone approval & review gates',
      'Help request queue & mentor notes',
      'Project health & velocity tracking',
    ],
  },
  {
    role: 'ADMINISTRATOR',
    tag: 'GOVERN',
    headline: 'System Health & Institutional Integrity',
    copy: 'Administrators maintain institutional standards, monitor AI token usage, verify system health, and inspect audit logs.',
    surfaces: [
      'System health & liveness probes',
      'AI observability & provider latency',
      'Security posture & audit logging',
      'Departmental usage analytics',
    ],
  },
] as const;

function ThreePerspectivesSection() {
  return (
    <SectionReveal className="p05-section" id="showcase-perspectives">
      <div className="p05-section__inner">
        <div className="p05-section__header">
          <span className="p05-eyebrow">UNIFIED OPERATIONAL ROLES</span>
          <h2 className="p05-h2">Three perspectives. One system.</h2>
          <p className="p05-copy">
            Students build, mentors supervise, and administrators govern—while the underlying system remains connected.
          </p>
        </div>

        <div className="p05-perspectives-grid">
          {PERSPECTIVES.map((p) => (
            <div
              key={p.role}
              className="p05-perspective-card"
              tabIndex={0}
              role="region"
              aria-label={`Perspective ${p.role} (${p.tag}): ${p.headline}`}
            >
              <div className="p05-perspective-head">
                <span className="p05-perspective-tag">{p.tag}</span>
                <strong className="p05-perspective-role">{p.role}</strong>
              </div>
              <h3 className="p05-perspective-headline">{p.headline}</h3>
              <p className="p05-perspective-copy">{p.copy}</p>

              <div className="p05-perspective-surfaces">
                <span className="p05-surfaces-label">OPERATIONAL SURFACES</span>
                <ul className="p05-surfaces-list">
                  {p.surfaces.map((s) => (
                    <li key={s} className="p05-surface-item">
                      <span className="p05-surface-bullet" aria-hidden="true" />
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>

        <div className="p05-perspectives-footer">
          <p className="p05-perspectives-note">
            One shared PostgreSQL data model and one cohesive Soft Intelligence visual identity connect all three lenses.
            Roles reflect authorization scope, not siloed applications.
          </p>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   9. Architecture at a Glance (Layered Diagram)
   ========================================================================== */

function ArchitectureGlanceSection() {
  return (
    <SectionReveal className="p05-section p05-section--alt" id="showcase-architecture">
      <div className="p05-section__inner">
        <div className="p05-section__header">
          <span className="p05-eyebrow">SYSTEM ARCHITECTURE</span>
          <h2 className="p05-h2">Architecture at a glance.</h2>
          <p className="p05-copy">
            Under the workspace is a layered system designed to keep canonical state, AI execution,
            documents, and delivery concerns separated.
          </p>
        </div>

        <div className="p05-arch-grid">
          {/* Column 1: Core Application Path */}
          <div className="p05-arch-col" tabIndex={0} role="region" aria-label="Architecture Column: Core Application Path">
            <div className="p05-arch-col-head">
              <span className="p05-arch-tag">APPLICATION PATH</span>
              <strong className="p05-arch-title">Core Application</strong>
            </div>
            <div className="p05-arch-stack">
              <div className="p05-arch-box" tabIndex={0}>Frontend (React 19 / Vite)</div>
              <div className="p05-arch-down" aria-hidden="true">↓</div>
              <div className="p05-arch-box" tabIndex={0}>FastAPI Application (/api/v1)</div>
              <div className="p05-arch-down" aria-hidden="true">↓</div>
              <div className="p05-arch-box" tabIndex={0}>Application Services (Domain Logic)</div>
              <div className="p05-arch-down" aria-hidden="true">↓</div>
              <div className="p05-arch-box" tabIndex={0}>Domain Entities & Progression Rules</div>
              <div className="p05-arch-down" aria-hidden="true">↓</div>
              <div className="p05-arch-box p05-arch-box--primary" tabIndex={0}>PostgreSQL Canonical State</div>
            </div>
          </div>

          {/* Column 2: AI Execution Path */}
          <div className="p05-arch-col" tabIndex={0} role="region" aria-label="Architecture Column: AI Execution Path">
            <div className="p05-arch-col-head">
              <span className="p05-arch-tag">AI EXECUTION PATH</span>
              <strong className="p05-arch-title">Orchestrated AI</strong>
            </div>
            <div className="p05-arch-stack">
              <div className="p05-arch-box" tabIndex={0}>AI Orchestrator (LangGraph)</div>
              <div className="p05-arch-down" aria-hidden="true">↓</div>
              <div className="p05-arch-box" tabIndex={0}>13 Specialized Agents</div>
              <div className="p05-arch-down" aria-hidden="true">↓</div>
              <div className="p05-arch-box" tabIndex={0}>Authorized Tools (Tavily Evidence)</div>
              <div className="p05-arch-down" aria-hidden="true">↓</div>
              <div className="p05-arch-box" tabIndex={0}>Structured Output Pydantic Parser</div>
              <div className="p05-arch-down" aria-hidden="true">↓</div>
              <div className="p05-arch-box p05-arch-box--accent" tabIndex={0}>QA / Judge Acceptance Gate</div>
            </div>
          </div>

          {/* Column 3: Platform Infrastructure */}
          <div className="p05-arch-col" tabIndex={0} role="region" aria-label="Architecture Column: Platform Infrastructure">
            <div className="p05-arch-col-head">
              <span className="p05-arch-tag">PLATFORM LAYER</span>
              <strong className="p05-arch-title">Infrastructure</strong>
            </div>
            <div className="p05-arch-stack">
              <div className="p05-arch-box" tabIndex={0}>Background Workers & Outbox</div>
              <div className="p05-arch-down" aria-hidden="true">↓</div>
              <div className="p05-arch-box" tabIndex={0}>Project-Scoped Vector RAG</div>
              <div className="p05-arch-down" aria-hidden="true">↓</div>
              <div className="p05-arch-box" tabIndex={0}>Curated Documents & Assets</div>
              <div className="p05-arch-down" aria-hidden="true">↓</div>
              <div className="p05-arch-box" tabIndex={0}>Structured Logs & Correlation IDs</div>
              <div className="p05-arch-down" aria-hidden="true">↓</div>
              <div className="p05-arch-box p05-arch-box--info" tabIndex={0}>Real-time SSE Notification Pipe</div>
            </div>
          </div>
        </div>

        <div className="p05-arch-footer">
          <p className="p05-arch-note">
            Simplified architectural overview. For comprehensive contracts, schemas, and service definitions,
            refer to the full <a href="/documentation" className="p05-inline-link">GrowFlow Documentation</a>.
          </p>
        </div>
      </div>
    </SectionReveal>
  );
}

/* ==========================================================================
   10. Closing CTA Section (Preserving P02/P03 Spacing & Rhythm)
   ========================================================================== */

function FinalCtaSection() {
  return (
    <section className="p05-final-cta" aria-labelledby="showcase-final-cta-heading">
      <div className="p05-final-cta__inner">
        <h2 id="showcase-final-cta-heading" className="p05-final-cta__h2">
          Now you know what's behind the flow.
        </h2>
        <p className="p05-final-cta__copy">
          Explore the architecture, understand the system, and see how GrowFlow connects the pieces.
        </p>
        <div className="p05-final-cta__actions">
          <Button as="link" to="/documentation" size="lg">
            Read the documentation
          </Button>
          <Button as="link" to="/auth/student/register" variant="secondary" size="lg">
            Enter the workspace
          </Button>
        </div>
      </div>
    </section>
  );
}
