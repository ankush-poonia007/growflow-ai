# GrowFlow — Master Design System

**Document:** `Master_Design.md`  
**Status:** AUTHORITATIVE / FOUNDATION  
**Version:** 1.1  
**Purpose:** Single visual source of truth for GrowFlow and all Stitch-generated interfaces  
**Scope:** Brand, visual language, typography, color, surfaces, layout, components, imagery, motion, responsive behavior, accessibility, AI presentation, and visual QA  
**Applies to:** Public website, authentication, BUILD (Student), SUPERVISE (Mentor), GOVERN (Admin), shared authenticated surfaces, system states, and future page compositions

---

## 00. Authority and Design Contract

This document is the master visual contract for GrowFlow.

It consolidates the frozen decisions established in:

- `GrowFlow_DESIGN.md`
- Phase 03 — Frontend Visual Design System and Experience Direction
- Phase 06C — Frontend Design Tokens
- Phase 06D — Core Component System
- Phase 06E — Application Shell
- Phase 06F — Frontend Behavior Foundation
- Phase 06G — Responsive and Accessibility Foundation
- Phase 06H — Stitch Foundation Validation

### Authority hierarchy

When implementing or generating UI:

1. Product/domain architecture remains authoritative for meaning and behavior.
2. This document is authoritative for visual/design decisions.
3. Design tokens are authoritative for exact reusable values.
4. Component specifications must implement the tokens rather than invent replacements.
5. Page specifications may compose the system but may not redefine the system.
6. Stitch prompts must instruct Stitch to follow this system.
7. Reference images are inspiration and evidence of direction, not templates to copy.
8. If a required visual decision is genuinely unspecified, it must be marked `TBD` rather than silently invented.

### Core rule

> **Nothing screams; hierarchy still exists.**

GrowFlow should feel calm, intelligent, structured, precise, human, and quietly sophisticated.

---

# 01. Product Visual Identity

## 01.1 Design identity

**GrowFlow = Soft Intelligence.**

Soft Intelligence means:

- calm visual surfaces
- restrained color
- strong information hierarchy
- generous but disciplined whitespace
- precise typography
- quiet cards
- dense, useful data presentation
- editorial storytelling where appropriate
- subtle physical motion
- intelligent AI presentation without visual noise

The product should communicate:

- growth
- progression
- continuity
- structure
- mentorship
- project execution
- clarity
- intelligence beneath the surface

## 01.2 Brand personality

GrowFlow should feel:

- intelligent
- calm
- capable
- mature
- trustworthy
- human
- structured
- modern
- editorial
- intentional
- technically sophisticated without looking technical for its own sake

GrowFlow should **not** feel:

- childish
- noisy
- gamified by default
- cyberpunk
- futuristic for spectacle
- neon
- robotic
- overly corporate
- generic SaaS
- template-like
- visually overloaded

---

# 02. Core Visual Principles

## 02.1 Principle: hierarchy over decoration

Every visual element must have a reason.

Prioritize:

1. content
2. hierarchy
3. action
4. state
5. context
6. decoration

Decoration must never compete with meaning.

## 02.2 Principle: calm surface, powerful system

The interface should look quiet while supporting complex functionality underneath.

Complexity should be expressed through:

- information architecture
- structured data
- progressive disclosure
- clear state
- precise interaction
- intelligent grouping

not through visual effects.

## 02.3 Principle: restrained color

Color is primarily semantic.

Use the accent to guide attention, not to paint the interface.

## 02.4 Principle: typography carries hierarchy

Do not compensate for weak hierarchy with:

- oversized cards
- excessive color
- heavy shadows
- gradients
- glowing effects
- decorative icons

Typography, spacing, alignment, and density should do most of the work.

## 02.5 Principle: surfaces remain quiet

Cards are tools for grouping.

Do not place every element inside a card.

Prefer:

- sections
- dividers
- grouped rows
- integrated tables
- whitespace
- subtle surface changes

when those communicate hierarchy better.

---

# 03. Brand System

## 03.1 Primary identity direction

**Connected Flow + Abstract G**

The GrowFlow mark should subtly communicate:

- a flowing path
- continuity
- progression
- structured movement
- an abstract `G`
- growth without a literal leaf

## 03.2 Brand metaphor

The visual metaphor is:

> **A structured flow that continuously moves forward.**

The mark should not literally depict:

- a brain
- circuit board
- robot
- AI chip
- generic leaf
- rocket
- spark
- glowing orb

## 03.3 Role branding

There are **no separate visual themes** for:

- BUILD
- SUPERVISE
- GOVERN

All three use the same GrowFlow design system.

Role personality is expressed through:

- information
- navigation
- density
- contextual language
- workflow
- permissions

not separate colors or brand identities.

---

# 04. Typography System

## 04.1 Typography authority

Typography is a core part of GrowFlow's identity and must be treated as a design-system primitive rather than a page-level styling choice.

The canonical typography architecture contains **two font families only**:

```text
GROWFLOW TYPOGRAPHY
│
├── Manrope
│   └── Primary / universal GrowFlow typeface
│
└── JetBrains Mono
    └── Technical / monospace content only
```

### Hard rule

> **Manrope is used for all normal GrowFlow interface and editorial text. JetBrains Mono is used only when the content itself is technical and benefits from monospace presentation.**

No third primary font is part of the GrowFlow V1 visual system.

## 04.2 Canonical primary typeface

**Family:** Manrope

Manrope is the canonical GrowFlow typeface for:

- public website
- landing pages
- hero copy
- marketing sections
- features
- documentation interface
- contact
- footer
- authentication
- registration
- recovery
- onboarding
- BUILD / Student workplace
- SUPERVISE / Mentor workplace
- GOVERN / Admin workplace
- dashboards
- navigation
- sidebar
- workplace selector
- search
- notifications
- profile
- settings
- projects
- project definitions
- project instances
- tasks
- milestones
- risks
- roadmap
- documents
- Markdown prose
- AI Mentor
- AI responses
- workflow interfaces
- assessment
- blueprint review
- project changes
- help requests
- mentor notes
- status labels
- system states
- empty states
- loading states
- error states
- success states
- ordinary metadata

### Universal UI rule

If the content is ordinary human-readable GrowFlow content, it uses **Manrope**.

This includes technical products surfaces that are still ordinary prose. A technical page does **not** automatically become monospace.

For example:

- `Project Overview` → Manrope
- `Generate Blueprint` → Manrope
- `AI Mentor` → Manrope
- `Project: Campus Green Initiative` → Manrope
- `Status: Running` → Manrope
- `Execution ID: 8f29...` → JetBrains Mono

## 04.3 Manrope font weights

The approved Manrope weight set is:

| Numeric weight | Name | Primary use |
|---:|---|---|
| 400 | Regular | Body, prose, descriptions, normal UI text |
| 500 | Medium | Metadata, labels, secondary emphasis |
| 600 | SemiBold | Buttons, controls, navigation labels, compact headings |
| 700 | Bold | Headings, major hierarchy, display |
| 800 | ExtraBold | Selective display emphasis and high-impact public typography |

### Weight discipline

Weight must communicate hierarchy.

Use:

- 400 for reading
- 500 for supporting emphasis
- 600 for controls and compact structural labels
- 700 for headings
- 800 only when the composition benefits from stronger display emphasis

Do not make an entire page 600/700 merely to make it feel "premium."

Do not use 800 for ordinary body text, metadata, tables, or navigation.

## 04.4 Manrope typography scale

The following scale is canonical.

| Token | Font family | Size | Line height | Weight | Letter spacing |
|---|---|---:|---:|---:|---:|
| Display XL | Manrope | 64px | 1.05 | 700 | -0.03em |
| Display L | Manrope | 56px | 1.08 | 700 | -0.03em |
| Display M | Manrope | 48px | 1.10 | 700 | -0.025em |
| H1 | Manrope | 40px | 1.15 | 700 | -0.02em |
| H2 | Manrope | 32px | 1.20 | 700 | -0.015em |
| H3 | Manrope | 26px | 1.25 | 700 | -0.01em |
| H4 | Manrope | 22px | 1.30 | 600 | -0.005em |
| H5 | Manrope | 18px | 1.35 | 600 | 0 |
| H6 | Manrope | 16px | 1.40 | 600 | 0 |
| Body Large | Manrope | 17px | 1.60 | 400 | 0 |
| Body | Manrope | 15px | 1.55 | 400 | 0 |
| Body Small | Manrope | 14px | 1.50 | 400 | 0 |
| Caption | Manrope | 13px | 1.45 | 400 | 0 |
| Metadata | Manrope | 12px | 1.40 | 500 | 0 |

## 04.5 Typography hierarchy

### Display XL — 64px

Use for:

- exceptional public hero statements
- major brand-level statements
- very large editorial compositions

Do not use in dense workplace screens.

### Display L — 56px

Use for:

- major public hero headings
- large editorial section statements

### Display M — 48px

Use for:

- secondary public hero compositions
- major public section headings

### H1 — 40px

Use for:

- primary page headings
- major authenticated page titles
- substantial public sections

### H2 — 32px

Use for:

- primary content section headings
- major dashboard sections
- large feature sections

### H3 — 26px

Use for:

- important subsections
- prominent cards where a card heading genuinely requires it
- major workflow sections

### H4 — 22px

Use for:

- component groups
- compact section headings
- important detail sections

### H5 — 18px

Use for:

- smaller component headings
- grouped content
- meaningful secondary hierarchy

### H6 — 16px

Use for:

- compact headings
- dense workplace sections
- table/group headings where appropriate

### Body Large — 17px

Use for:

- public explanatory copy
- introductory descriptions
- hero supporting copy
- important long-form supporting content

### Body — 15px

Primary ordinary UI reading size.

Use for:

- descriptions
- form content
- task/project text
- AI responses
- documentation prose
- ordinary interface content

### Body Small — 14px

Use for:

- compact supporting content
- secondary descriptions
- dense UI
- supporting controls where appropriate

### Caption — 13px

Use for:

- secondary contextual information
- helper information
- small explanatory labels

### Metadata — 12px / 500

Use for:

- timestamps
- compact metadata
- secondary identifiers when not technical
- table metadata
- supplementary labels

Metadata must remain subordinate.

## 04.6 Manrope usage by product area

### Public website

Use the complete Manrope scale, with emphasis on:

- Display XL
- Display L
- Display M
- H1
- H2
- H3
- Body Large
- Body

The public website may use larger typography because its composition is more editorial.

### Authentication

Prefer:

- H1/H2
- Body
- Body Small
- Caption
- Metadata

Avoid oversized marketing typography in focused authentication workflows.

### BUILD

Prefer:

- H1/H2 for page-level hierarchy
- H3/H4 for major sections
- H5/H6 for dense subgroups
- Body / Body Small for content
- Caption / Metadata for supporting information

### SUPERVISE

Use the same hierarchy as BUILD but support higher information density.

### GOVERN

Use compact typography more heavily:

- H1/H2 for major views
- H4/H5/H6 for operational groupings
- Body Small
- Caption
- Metadata

The admin interface must remain readable even when data density is high.

## 04.7 Buttons and controls

Buttons:

- Standard: 14px / 600
- Large CTA: 15–16px / 600
- Compact: 13px / 600

Control labels should generally use 500–600 depending on importance.

Do not use 700/800 simply to make controls appear stronger.

## 04.8 Navigation typography

Top navigation and sidebar labels should generally use:

- 14–15px
- 500–600

Selected navigation may increase weight or contrast but should not become oversized.

## 04.9 Table typography

Recommended hierarchy:

- table header: 12–13px / 500–600
- primary row content: 14–15px / 400–500
- secondary row metadata: 12–13px / 400–500
- status labels: 12–13px / 500–600

Avoid making every table value bold.

## 04.10 Form typography

Forms should generally use:

- field label: 13–14px / 500–600
- input text: 14px / 400
- helper text: 13px / 400
- validation/error text: 13–14px / 400–500
- section heading: H4–H5 depending on hierarchy

Visible labels are required for accessible form design.

## 04.11 AI typography

AI responses use Manrope by default.

AI must not automatically use monospace.

Use:

- response prose → Body
- AI section title → H4/H5
- contextual metadata → Caption/Metadata
- tool/execution labels → Body Small / Metadata
- technical payload → JetBrains Mono

## 04.12 Documentation typography

Documentation prose uses Manrope.

Headings use the canonical heading hierarchy.

Technical content inside documentation may use JetBrains Mono.

This creates a clear distinction between:

```text
Explanation
→ Manrope

Technical artifact
→ JetBrains Mono
```

## 04.13 Brand display typography

GrowFlow's brand identity is supported by the same Manrope family.

The logo itself is a vector asset and is not governed by normal text rendering.

The wordmark must use the approved logo asset rather than being recreated as arbitrary HTML text.

## 04.14 Secondary / decorative fonts

No secondary decorative font is part of the GrowFlow UI system.

Do not introduce:

- handwritten UI fonts
- script fonts
- decorative display fonts
- serif fonts as a second brand family
- novelty fonts

### Editorial handwriting exception

A handwritten appearance may exist **inside an approved editorial image or illustration** when it is part of the image composition.

That does not authorize a handwritten web font in the product UI.

Example:

```text
Approved:
Editorial image containing handwritten "Ideas today. Impact tomorrow."

Not approved:
HTML interface text rendered in a handwritten font.
```

## 04.15 Monospace family

**Family:** JetBrains Mono

Purpose:

> Technical content that benefits from fixed-width character alignment.

JetBrains Mono is a supporting technical typeface, not a second general-purpose UI typeface.

## 04.16 JetBrains Mono approved uses

JetBrains Mono may be used for:

- code blocks
- inline code
- terminal commands
- API examples
- JSON
- YAML
- XML
- SQL
- configuration snippets
- stack traces
- technical logs
- execution traces
- correlation IDs
- execution IDs
- trace IDs
- hashes
- Git commit SHAs
- file paths
- technical payloads
- machine-oriented structured output
- other explicitly technical representations

## 04.17 JetBrains Mono prohibited uses

Do not use JetBrains Mono for:

- page headings
- hero headings
- body prose
- navigation
- sidebar labels
- buttons
- ordinary form labels
- project names
- task names
- milestone names
- risk names
- ordinary status labels
- ordinary metadata
- AI conversational responses
- mentor notes
- student-facing instructional copy
- public marketing copy

A page being technical does not mean all of its text should become monospace.

## 04.18 JetBrains Mono scale

| Token | Font family | Size | Line height | Weight |
|---|---|---:|---:|---:|
| Code Large | JetBrains Mono | 15px | 1.60 | 400 |
| Code | JetBrains Mono | 14px | 1.60 | 400 |
| Code Small | JetBrains Mono | 13px | 1.50 | 400 |
| Code Metadata | JetBrains Mono | 12px | 1.45 | 400 |

A stronger technical weight may be introduced only if required by the component specification; it is not part of the default typography hierarchy.

## 04.19 Technical data distinction

The following distinction is mandatory:

```text
Human meaning
    ↓
Manrope

Machine representation
    ↓
JetBrains Mono
```

Examples:

```text
"Blueprint generation completed"       → Manrope

"execution_id=9d31..."                → JetBrains Mono

"Project roadmap is ready to review"  → Manrope

{
  "status": "COMPLETED"
}                                      → JetBrains Mono
```

## 04.20 Font-family boundaries

### Family 1 — Manrope

Authority:

**Universal GrowFlow visual language**

### Family 2 — JetBrains Mono

Authority:

**Technical representation only**

### Family 3+

Authority:

**Not allowed by default**

Any future third family requires explicit design-system change control.

## 04.21 Font file package

The planned font asset package is:

```text
FONTS/
├── Manrope/
│   ├── Manrope-Regular
│   ├── Manrope-Medium
│   ├── Manrope-SemiBold
│   ├── Manrope-Bold
│   └── Manrope-ExtraBold
│
└── JetBrainsMono/
    └── JetBrainsMono-Regular
```

A technical medium/bold weight may be added only if a concrete component requires it.

Actual file extensions and packaging format are implementation/package decisions and must comply with the applicable font licensing terms.

## 04.22 Font loading principles

Production implementation should:

- load only required weights
- avoid unnecessary font variants
- avoid blocking the interface unnecessarily
- provide reliable fallback behavior
- prevent layout instability where practical
- keep public and authenticated bundles efficient

The exact loading mechanism belongs to frontend implementation documentation.

## 04.23 Font fallback strategy

### Manrope

Intended conceptual stack:

```css
"Manrope",
system-ui,
-apple-system,
BlinkMacSystemFont,
"Segoe UI",
sans-serif
```

### JetBrains Mono

Intended conceptual stack:

```css
"JetBrains Mono",
ui-monospace,
SFMono-Regular,
Menlo,
Monaco,
Consolas,
monospace
```

The fallback must preserve the semantic distinction between normal UI text and technical content.

## 04.24 Typography and responsive behavior

Responsive changes may alter:

- display size
- line wrapping
- max text width
- composition
- spacing around text

Responsive changes must not arbitrarily change:

- font family
- semantic hierarchy
- readability
- accessibility

Public display typography may scale down on mobile.

Dense workplace typography should prioritize readability over aggressive compression.

## 04.25 Typography and dark mode

Font family and hierarchy remain the same in light and dark themes.

Dark mode changes:

- color
- surface
- contrast
- surrounding composition

It does not introduce a different typography identity.

## 04.26 Typography and accessibility

Typography must support:

- readable line height
- clear hierarchy
- sufficient contrast
- text resizing
- responsive reflow
- keyboard focus readability
- screen-reader-compatible semantic structure

Do not encode hierarchy through font weight alone.

## 04.27 Typography and content length

Designs must tolerate:

- long headings
- long project names
- long task names
- long user names
- long AI responses
- long document titles
- long metadata

Never solve long content by making text microscopic.

Use:

- wrapping
- truncation only when semantically safe
- tooltips where appropriate
- detail views
- responsive reflow

## 04.28 Typography anti-patterns

Do not:

- mix fonts without semantic reason
- use random weights
- use excessive 800 weight
- use monospace for ordinary UI
- use decorative fonts for interface text
- use tiny text to increase density
- use all-caps as the main hierarchy mechanism
- use letter spacing arbitrarily
- use manually tuned font sizes on every page
- substitute a font because Stitch thinks it "looks better"

## 04.29 Stitch typography instruction

Stitch must follow this exact conceptual rule:

> **Use Manrope as the canonical GrowFlow typeface across all public, authenticated, BUILD, SUPERVISE, GOVERN, navigation, forms, dashboards, documents, AI, workflows, and system interfaces. Use the canonical GrowFlow typography scale and approved weights. Use JetBrains Mono only for explicitly technical content such as code, JSON, YAML, logs, IDs, hashes, API payloads, file paths, and traces. Do not introduce another UI font, decorative font, handwritten font, serif font, or alternate typography system.**

## 04.30 Typography acceptance criteria

A generated or implemented page passes typography review only if:

- [ ] Manrope is the normal interface family
- [ ] approved weights are used appropriately
- [ ] heading hierarchy is recognizable
- [ ] body text is readable
- [ ] metadata is subordinate
- [ ] controls use correct emphasis
- [ ] technical content uses JetBrains Mono where appropriate
- [ ] ordinary content does not become monospace
- [ ] no unauthorized third family appears
- [ ] mobile typography remains readable
- [ ] dark-mode typography remains legible
- [ ] accessibility requirements are satisfied
- [ ] long content does not break the layout

# 05. Color Architecture

## 05.1 Color philosophy

GrowFlow uses:

- warm neutral foundations
- restrained text hierarchy
- one subtle sage primary accent
- semantic status colors
- a restrained deeper AI variant

Color should communicate hierarchy and state.

## 05.2 Light theme — canonical values

### Backgrounds and surfaces

| Token | Value | Purpose |
|---|---|---|
| Background | `#F7F7F4` | Primary application/page background |
| Surface | `#FFFFFF` | Primary elevated/content surface |
| Secondary | `#F2F2EE` | Secondary surface |
| Tertiary | `#EDEDE8` | Tertiary grouping / subtle contrast |

### Text

| Token | Value | Purpose |
|---|---|---|
| Primary Text | `#1C1C1A` | Main content |
| Secondary Text | `#5F625D` | Supporting content |
| Tertiary Text | `#858780` | Metadata / subdued content |

### Borders

| Token | Value | Purpose |
|---|---|---|
| Border Subtle | `#E5E5DF` | Low-emphasis separation |
| Border Standard | `#D9D9D2` | Standard component borders |
| Border Strong | `#C9C9C0` | Strong boundaries / focus context |

## 05.3 Light accent

| Token | Value |
|---|---|
| Accent | `#6F7F63` |
| Accent Hover | `#607055` |
| Accent Active | `#526149` |
| Accent Soft | `#E9EDE5` |
| Accent Border | `#B8C2AE` |

Primary accent is **GrowFlow Sage**.

Use for:

- primary actions
- selected navigation
- meaningful progress
- controlled emphasis
- interactive highlights

Do not use as:

- full-page background
- arbitrary decoration
- AI glow
- large gradient field
- default text color everywhere

## 05.4 Light semantic colors

### Success

- Primary: `#477A5A`
- Soft: `#E7F0E9`

### Warning

- Primary: `#9A7135`
- Soft: `#F5EDDD`

### Danger

- Primary: `#A6534D`
- Soft: `#F6E8E6`

### Info

- Primary: `#54718A`
- Soft: `#E8EEF3`

Semantic colors must never be communicated by color alone.

## 05.5 AI colors

### Light

- AI: `#5F6B7A`
- AI Surface: `#ECEEF1`
- AI Border: `#D4D8DD`
- AI Emphasis: `#424D5A`

AI presentation should feel slightly deeper and distinct from ordinary application surfaces while remaining native to GrowFlow.

---

# 06. Dark Theme

## 06.1 Philosophy

Dark mode is not a color inversion.

It is a deliberately composed counterpart preserving:

- hierarchy
- softness
- readability
- restrained contrast
- GrowFlow identity

## 06.2 Dark surfaces

| Token | Value |
|---|---|
| Background | `#171816` |
| Secondary | `#1E201D` |
| Tertiary | `#262824` |
| Surface | `#20221F` |
| Elevated | `#272925` |
| Muted | `#2D302B` |

## 06.3 Dark text

| Token | Value |
|---|---|
| Primary Text | `#F0F1EC` |
| Secondary Text | `#C2C5BD` |
| Tertiary Text | `#91958C` |

## 06.4 Dark borders

| Token | Value |
|---|---|
| Subtle | `#30332E` |
| Standard | `#3A3D37` |
| Strong | `#4A4E47` |

## 06.5 Dark accent

| Token | Value |
|---|---|
| Accent | `#9AAA8D` |
| Hover | `#A8B79C` |
| Active | `#B7C5AB` |
| Soft | `#2B3328` |

## 06.6 Dark semantic colors

- Success: `#7FB18C`
- Warning: `#D0A962`
- Danger: `#D27A72`
- Info: `#88A8C0`

## 06.7 Dark AI

- AI Surface: `#292D30`
- AI Border: `#3C4246`
- AI Emphasis: `#A9B2BB`

---

# 07. Spacing System

Canonical spacing values:

`2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128px`

## 07.1 Spacing philosophy

Use spacing to communicate grouping.

General relationship:

- 2–4: micro separation
- 8–12: tightly related elements
- 16–24: standard component grouping
- 32–48: section grouping
- 64+: major composition separation
- 80–128: editorial/public composition where appropriate

Do not create arbitrary spacing values without reason.

---

# 08. Radius System

Canonical radii:

- 4px
- 6px
- 8px
- 12px
- 16px
- 20px
- 9999px

## 08.1 Usage

- 4: subtle structural elements
- 6: compact controls
- 8: standard controls and components
- 12: larger surfaces/cards
- 16: prominent surfaces
- 20: major editorial/hero surfaces where appropriate
- 9999: pills/circular elements only when semantically appropriate

Avoid excessive pill styling.

---

# 09. Elevation and Shadows

## 09.1 Levels

### L0

No shadow.

### L1

`0 1px 2px rgba(0,0,0,0.04)`

### L2

`0 4px 12px rgba(0,0,0,0.06)`

### L3

`0 12px 32px rgba(0,0,0,0.08)`

## 09.2 Rules

Default UI should favor L0/L1.

L2 is for meaningful elevation.

L3 is reserved for:

- major floating surfaces
- dialogs
- high-priority overlays
- major editorial floating compositions

Do not use large shadows to manufacture hierarchy.

---

# 10. Sizing System

## 10.1 Buttons

### Standard

- height: 40px
- horizontal padding: 16px
- radius: 8px
- text: 14px
- weight: 600

### Large CTA

- height: 48px
- horizontal padding: 20px
- radius: 8px
- text: 15–16px
- weight: 600

### Compact

- height: 32px
- horizontal padding: 12px
- radius: 6px
- text: 13px
- weight: 600

## 10.2 Inputs

### Standard

- height: 40px
- horizontal padding: 12px
- radius: 6px
- text: 14px

### Large

- height: 48px

### Compact

- height: 36px

### Textarea

- minimum height: 96px
- padding: 12px
- line-height: 1.5

## 10.3 Touch targets

Interactive controls should generally provide a minimum effective touch target of:

**44 × 44px**

Visual bounds may be smaller only when the effective interactive area still satisfies accessibility requirements.

---

# 11. Layout System

## 11.1 Breakpoints

| Category | Range |
|---|---|
| Mobile | `<768px` |
| Tablet | `768–1199px` |
| Desktop | `>=1200px` |

These are structural breakpoints, not merely device labels.

## 11.2 Container philosophy

Use a consistent container system with:

- predictable maximum width
- responsive horizontal padding
- strong alignment
- controlled reading measure

Exact page-specific max-width may vary by composition, but arbitrary container widths are prohibited.

## 11.3 Grid philosophy

Use grid for:

- dashboards
- feature sections
- project overview
- dense information layouts
- responsive cards where cards are semantically useful

Use flexible stacks for:

- forms
- document reading
- chat
- sequential workflows

Do not force every page into a rigid card grid.

---

# 12. Public Website Visual Language

The public website is the most expressive portion of GrowFlow.

It may use:

- larger typography
- editorial imagery
- greater whitespace
- stronger composition
- storytelling
- controlled asymmetry
- subtle motion
- larger visual moments

It must still remain consistent with the same foundation.

## 12.1 Public visual priority

1. statement
2. story
3. product value
4. evidence
5. interaction
6. navigation

## 12.2 Hero

Hero direction:

**Statement + visual storytelling**

Avoid:

- generic SaaS split-screen hero
- huge gradient blob
- generic AI illustration
- floating dashboard screenshot overload
- excessive animation

Hero may use:

- editorial image
- contextual product visual
- abstract flow composition
- restrained motion
- carefully composed product evidence

---

# 13. Authenticated Workplace Visual Language

Authenticated interfaces are:

- calm
- information-dense
- operational
- consistent
- task-oriented

Prioritize:

- information density
- scannability
- predictable navigation
- clear states
- low interaction friction

## 13.1 Density

Dense interfaces should remain readable.

Increase density through:

- compact spacing
- integrated tables
- clear typography
- aligned columns
- progressive disclosure

not tiny text.

---

# 14. Application Shell Visual Rules

## 14.1 Public navigation

Public navigation height:

**68–76px**

## 14.2 Authenticated top navigation

Authenticated navigation height:

**64px**

## 14.3 Sidebar

Default width:

**248px**

Acceptable structural range:

**240–264px**

Collapsed width:

**72px**

## 14.4 Sidebar item

- height: 36–40px
- horizontal padding: 8–12px
- icon: 18–20px
- icon/text gap: 10–12px
- radius: 6–8px

## 14.5 Navigation philosophy

Navigation should be:

- predictable
- quiet
- role-aware
- persistent where appropriate
- visually subordinate to content

Selected state may use:

- subtle accent surface
- controlled accent indicator
- stronger text

Do not use oversized glowing active states.

---

# 15. Workplace Selector

The Workplace selector exposes the GrowFlow role environments:

- **BUILD** — Student
- **SUPERVISE** — Mentor
- **GOVERN** — Admin

The visual treatment remains one unified GrowFlow system.

Do not give each workplace a separate theme.

Use:

- role label
- icon where appropriate
- contextual description
- permission-aware availability

Role selection should feel like choosing a workspace, not changing the brand.

---

# 16. Cards and Surfaces

## 16.1 Card philosophy

Cards are **quiet**.

Use cards for:

- meaningful grouping
- independent actions
- isolated content
- summaries
- contextual modules

Do not card:

- every metric
- every paragraph
- every table row
- every navigation item
- every section

## 16.2 Card composition

Typical structure:

```text
Title
Supporting context
Primary content
Optional metadata
Optional action
```

Hierarchy comes from:

- typography
- spacing
- surface contrast
- borders
- alignment

not decorative effects.

---

# 17. Tables

Tables are a major workplace primitive.

## 17.1 Philosophy

Tables should feel **integrated**, not like spreadsheet widgets pasted into the application.

Prioritize:

- alignment
- readable density
- consistent row height
- subtle separators
- clear column hierarchy
- predictable actions

## 17.2 Table rules

- Use strong headers.
- Keep metadata subordinate.
- Use semantic status indicators.
- Avoid excessive borders.
- Avoid zebra striping unless it materially improves scanability.
- Do not use decorative color for ordinary rows.
- Preserve accessible table semantics.
- On mobile, transform intelligently rather than shrinking into unreadability.

---

# 18. Forms and Controls

Controls should feel precise and quiet.

## 18.1 Button hierarchy

Primary:

- accent-filled
- strong text contrast
- reserved for primary action

Secondary:

- neutral surface/border
- lower emphasis

Tertiary:

- text or low-emphasis treatment

Danger:

- semantic danger treatment
- used only for destructive action

## 18.2 Focus

Focus must be visibly identifiable.

Focus cannot rely only on color changes.

## 18.3 Inputs

Inputs should have:

- visible label
- predictable height
- clear focus
- clear error state
- clear disabled state
- helper text when needed

Avoid placeholder-only labels.

---

# 19. Feedback States

Every meaningful interactive component must account for:

- default
- hover where applicable
- focus
- active
- disabled
- loading
- success where applicable
- error where applicable

## 19.1 Loading

Loading must communicate:

- what is loading
- expected scope
- whether interaction is blocked
- whether work is continuing in the background

Avoid fake AI typing as a substitute for actual progress.

## 19.2 Empty

Empty states should explain:

1. what is empty
2. why it may be empty
3. what the user can do next

## 19.3 Error

Error states should be:

- specific
- actionable
- calm
- non-blaming

## 19.4 Success

Success should be clear without excessive celebration.

Avoid confetti-like visual language unless a future product decision explicitly requires it.

---

# 20. Status and Semantic Visual Language

Semantic states:

- success
- warning
- danger
- info

must be represented using more than color.

Combine color with:

- icon
- text
- shape
- position
- label

Never communicate critical state solely through:

- green
- yellow
- red
- blue

---

# 21. Data Visualization

Dashboard visuals are **data instruments**, not decoration.

## 21.1 Principles

Charts must:

- communicate a real metric
- have readable labels
- preserve scale integrity
- use restrained visual encoding
- support accessibility
- remain useful in dark mode

## 21.2 Color

Use the GrowFlow palette.

Do not automatically create rainbow charts.

Prefer:

- neutral baseline
- accent for primary series
- semantic colors only where semantics exist

## 21.3 Dashboard hierarchy

Typical priority:

1. key state
2. key metric
3. trend
4. breakdown
5. detail
6. action

---

# 22. Progress Visual Language

Progress represents real project state.

Possible representations:

- progress bar
- percentage
- milestone sequence
- timeline position
- phase indicator
- completion state

Never imply progress that does not exist.

Progress visuals must derive from canonical state.

---

# 23. Task Visual Language

Tasks should clearly expose:

- title
- status
- priority where applicable
- due date where applicable
- ownership
- milestone relationship where applicable
- completion state

Do not overload task rows with every possible metadata field.

---

# 24. Milestone Visual Language

Milestones represent meaningful project checkpoints.

Visual hierarchy should distinguish:

- upcoming
- active
- completed
- blocked
- at-risk where applicable

Milestones should be visually stronger than ordinary tasks but weaker than page-level navigation.

---

# 25. Risk Visual Language

Risk is semantic and actionable.

Represent:

- risk level
- status
- impact
- likelihood where applicable
- mitigation
- ownership
- affected project context

Do not use alarming visuals by default.

Danger color should be reserved for meaningful risk semantics.

---

# 26. Roadmap / Timeline

Roadmaps should communicate temporal structure.

Use:

- phases
- milestones
- tasks
- dependencies where applicable
- current position
- planned vs actual where supported

Avoid ornamental timelines that communicate no useful temporal information.

---

# 27. Document Visual Language

Documents should feel like first-class product content.

Prioritize:

- reading comfort
- hierarchy
- version visibility
- metadata
- actions
- search/navigation where applicable

Do not make documents look like raw database records.

---

# 28. Markdown Rendering

Markdown content should preserve:

- heading hierarchy
- paragraph rhythm
- lists
- tables
- links
- code
- blockquotes
- emphasis
- metadata

Use a readable measure.

Avoid excessively wide prose columns.

---

# 29. Code Blocks

Code should use a restrained technical surface.

Do not introduce a completely unrelated developer-tool theme.

Code presentation should support:

- readable typography
- syntax distinction
- copy action
- horizontal overflow handling
- dark/light compatibility

---

# 30. GitHub Surfaces

GitHub-related UI should be recognizable as integration content but remain within GrowFlow's design system.

Use GitHub-specific identity only where semantically necessary.

Do not allow integration branding to replace GrowFlow branding.

---

# 31. AI Visual Language

AI is a **slightly deeper variant** of GrowFlow.

AI should feel:

- intelligent
- calm
- focused
- contextual
- trustworthy

AI should not feel:

- neon
- magical
- cyberpunk
- robotic
- glowing
- detached from the product

## 31.1 AI surfaces

Use:

- `#ECEEF1` light AI surface
- `#D4D8DD` light AI border
- `#424D5A` light AI emphasis
- corresponding dark AI values

## 31.2 AI hierarchy

AI UI should distinguish:

1. user input
2. AI response
3. system/tool state
4. execution progress
5. validation
6. completion/failure

## 31.3 AI status truthfulness

Never visually imply:

- thinking when the system is not thinking
- completion when generation is still running
- success before validation
- persistence before canonical persistence

AI visual state must match actual execution state.

---

# 32. AI Mentor

AI Mentor is an integrated product surface, not a separate chatbot product.

It should use:

- GrowFlow shell
- GrowFlow typography
- restrained AI surfaces
- clear conversational hierarchy
- contextual project information
- visible execution state where appropriate

Chat UI should avoid excessive bubble decoration.

---

# 33. AI Generation

For long-running generation:

Show:

- operation identity
- progress where available
- current stage
- meaningful status
- cancellation when supported
- recovery/retry when supported

Do not simulate progress numerically if the backend does not provide real progress.

---

# 34. Workflow Interfaces

Long-running workflows include:

- project creation
- assessment
- blueprint generation
- project changes
- document generation
- investigations

Workflow visual design should prioritize:

- current stage
- completed stages
- next action
- resumability
- errors
- context preservation

A workflow may be visually rich, but it must remain operationally clear.

---

# 35. Assessment Interfaces

Assessment should prioritize:

- question clarity
- progress
- response controls
- contextual guidance
- completion status

Avoid distracting decorative elements during focused assessment.

Adaptive assessment should communicate progression without exposing implementation internals unnecessarily.

---

# 36. Blueprint Interfaces

Blueprint is a major GrowFlow product artifact.

Visual hierarchy should distinguish:

- blueprint identity
- project context
- generation status
- version
- sections
- validation state
- QA/Judge state
- actions

Blueprint review should feel deliberate and trustworthy.

---

# 37. Project Change Interfaces

Project change is an impact-aware workflow.

Visual stages:

```text
Change Request
    ↓
Impact Analysis
    ↓
Impact Review
    ↓
Regeneration
    ↓
Validation
    ↓
QA/Judge
    ↓
Persisted Change
```

Do not visually skip the distinction between proposal and persisted change.

---

# 38. Authentication Visual Language

Login is a **distinct composition within the same design system**.

It may use:

- stronger whitespace
- focused layout
- brand mark
- restrained editorial visual
- simplified navigation

It must still use:

- Manrope
- GrowFlow colors
- GrowFlow controls
- GrowFlow radii
- GrowFlow motion rules

Avoid generic authentication templates.

---

# 39. Dashboard Visual Language

Dashboards are **highly visual data instruments**.

A dashboard should not become:

> a grid of identical cards with numbers.

Use:

- hierarchy
- trend
- activity
- progress
- risk
- actionable summaries
- integrated data
- contextual visualizations

Choose visual forms according to information meaning.

---

# 40. Editorial and Imagery System

## 40.1 Image philosophy

Images should be:

- contextual
- editorial
- human
- purposeful
- compositionally calm
- consistent with the product's quiet intelligence

## 40.2 Avoid

- generic corporate stock
- overly posed people
- cliché startup imagery
- AI robots
- brains
- circuit boards
- glowing technology
- generic laptop mockups everywhere
- unrelated decorative photography

## 40.3 Image treatment

Images may use:

- natural cropping
- restrained radius
- subtle tonal treatment
- controlled contrast
- editorial composition

Do not apply a universal heavy filter.

## 40.4 Image role

Every image should have one or more purposes:

- explain
- contextualize
- establish mood
- demonstrate product
- support storytelling

Decorative images should remain subordinate to content.

---

# 41. Illustration Direction

Illustrations should follow:

- simple geometry
- restrained palette
- structured flow
- human warmth
- minimal abstraction

Avoid:

- generic AI illustrations
- 3D blobs
- neon gradients
- cartoon mascots
- excessive isometric SaaS illustrations

---

# 42. Iconography

Icons should be:

- consistent
- simple
- readable
- semantically clear
- visually quiet

Do not mix multiple icon families arbitrarily.

Icon sizing should align with component dimensions.

Typical UI icon size:

**18–20px**

Smaller sizes may be used for metadata where readability remains acceptable.

---

# 43. Logo Rules

## 43.1 Primary logo

Use the approved GrowFlow wordmark + connected flow/abstract G mark.

## 43.2 Mark

Standalone mark is appropriate for:

- favicon
- compact navigation
- app icon
- small contextual branding

## 43.3 Monochrome

Monochrome variants are required for contexts where full color is inappropriate.

## 43.4 Clear space

A consistent clear-space rule must be applied around the logo.

Exact production clear-space measurement is `TBD` until the final vector asset package establishes the canonical geometry.

## 43.5 Do not

- stretch
- skew
- rotate
- recolor arbitrarily
- add glow
- add gradients without approval
- place on visually hostile backgrounds
- combine with separate role branding

---

# 44. Motion System

Motion follows:

**Subtle physical movement**

The goal is to make interfaces feel alive without making them feel animated.

## 44.1 Float → Settle

Primary scroll/entry behavior:

> Elements may appear to float gently into place and then settle.

Movement should be:

- short
- subtle
- physically plausible
- non-distracting

## 44.2 Motion principles

Use motion for:

- orientation
- feedback
- state transition
- spatial continuity
- hierarchy

Do not use motion merely because animation is available.

## 44.3 Avoid

- excessive parallax
- constant floating
- animated backgrounds
- fake AI typing
- bouncing elements
- aggressive spring motion
- attention-seeking transitions

## 44.4 Reduced motion

Respect:

`prefers-reduced-motion`

When reduced motion is enabled:

- remove decorative movement
- minimize transitions
- preserve state visibility
- preserve functional feedback

---

# 45. Interaction States

Every interactive element should account for:

```text
Default
Hover
Focus
Active
Disabled
Loading
Success
Error
```

Not every component needs every state visually, but every state must be considered.

Hover must never be the only way to discover functionality.

---

# 46. Responsive Design

## 46.1 Mobile

`<768px`

Mobile is a first-class composition.

Do not merely shrink desktop.

Expected transformations include:

- sidebar → drawer
- multi-column → stacked
- table → contextual mobile representation
- split pane → sequential sections
- dense controls → grouped controls
- horizontal navigation → scroll/drawer patterns

## 46.2 Tablet

`768–1199px`

Tablet must receive explicit layout consideration.

Do not assume desktop or mobile behavior automatically works.

## 46.3 Desktop

`>=1200px`

Desktop may use:

- persistent sidebar
- multi-column dashboard
- split workspace
- dense tables
- wider document composition

---

# 47. Responsive Invariants

Responsive transformation must **not change**:

- meaning
- authorization
- security
- resource identity
- workflow state
- canonical status

Only representation changes.

---

# 48. Accessibility

Accessibility is part of the design system.

## 48.1 Required principles

- keyboard accessibility
- visible focus
- semantic HTML
- accessible names
- meaningful headings
- landmarks
- labels for inputs
- useful error messages
- sufficient contrast
- non-color state communication
- reduced motion
- readable touch targets

## 48.2 Focus

Focus must remain visible and understandable in:

- light mode
- dark mode
- dialogs
- drawers
- menus
- tabs
- forms
- AI interfaces

## 48.3 Screen readers

Dynamic content must be announced where necessary.

Important live events include:

- completion
- meaningful errors
- navigation changes
- relevant AI state changes

Avoid announcing every tiny streaming update.

---

# 49. Dark Mode Accessibility

Dark mode must preserve:

- hierarchy
- contrast
- focus visibility
- semantic state distinction
- readable metadata

Do not simply invert light-theme colors.

---

# 50. Density System

GrowFlow supports different information densities.

## Public

Low-to-medium density.

Focus:

- storytelling
- value
- visual composition

## Workplace

Medium-to-high density.

Focus:

- productivity
- scanning
- state
- action

## Admin

High density where operationally useful.

Focus:

- observability
- tables
- metrics
- traces
- audit
- system state

Density must never become illegibility.

---

# 51. Public vs Workplace Rules

| Dimension | Public | Workplace |
|---|---|---|
| Expression | Higher | Lower |
| Density | Lower | Higher |
| Imagery | Editorial | Contextual |
| Typography | Larger | More compact |
| Motion | More noticeable but restrained | Minimal |
| Cards | Selective | Functional |
| Tables | Occasional | Important |
| Data | Demonstrative | Operational |
| AI | Storytelling | Functional |

Both remain one GrowFlow identity.

---

# 52. Component Visual Rules

All components must derive from:

```text
Design Tokens
    ↓
Foundation
    ↓
Primitive
    ↓
Composite
    ↓
Domain Component
    ↓
Workflow Component
    ↓
Page
```

A page must not invent an isolated component style when an existing component can satisfy the requirement.

---

# 53. Component Consistency

Across all roles:

- same button geometry
- same input geometry
- same typography
- same radius language
- same status semantics
- same focus behavior
- same motion philosophy
- same surface hierarchy

Context may change composition; the design language does not.

---

# 54. State Visual Language

System states include:

- loading
- empty
- error
- success
- warning
- unavailable
- processing
- queued
- running
- completed
- failed
- cancelled
- retrying

These states must be visually distinguishable and semantically truthful.

---

# 55. Async and Streaming Visual Language

Streaming interfaces must communicate:

- connection state where useful
- execution state
- current progress
- completion
- failure
- recovery

SSE is a delivery mechanism, not a visual state source by itself.

UI state must ultimately reconcile with canonical backend state.

---

# 56. Notifications

Notifications should be:

- concise
- actionable
- contextual
- timestamped where useful
- linked to the canonical resource

Visual priority should match notification importance.

Do not make every notification visually urgent.

---

# 57. Search

Global search should visually support:

- query
- results
- type
- context
- role-appropriate access
- empty state
- loading
- errors

Search results should not expose unauthorized information.

---

# 58. Profile and Settings

Profile/settings should feel like part of the same workplace system.

Avoid a separate visual subsystem.

Use:

- consistent forms
- clear grouping
- predictable navigation
- explicit save state
- accessible feedback

---

# 59. Data Resilience

Design must tolerate:

- long titles
- long names
- missing metadata
- empty lists
- large numbers
- long project names
- long AI responses
- long document titles
- many table rows
- errors
- partial data

Do not assume ideal content.

---

# 60. Content Overflow

Interfaces must define behavior for:

- long text
- long labels
- overflowing tables
- code
- Markdown
- images
- AI responses
- narrow mobile widths

Never solve overflow by silently clipping meaningful information.

---

# 61. Visual Hierarchy Rules

Hierarchy should be created in this order:

1. placement
2. typography
3. spacing
4. surface contrast
5. border
6. accent
7. elevation
8. motion

Do not jump directly to color or shadow.

---

# 62. Accent Usage Rules

Accent should answer:

> "Where should the user look or act?"

It should not answer:

> "How do we make this page colorful?"

Use accent sparingly.

---

# 63. AI Accent Restraint

AI does not get a separate neon identity.

AI distinction comes from:

- slightly deeper neutral palette
- subtle surface
- semantic iconography
- contextual placement
- execution state
- content hierarchy

not glow.

---

# 64. Surface Hierarchy

Recommended light progression:

```text
Background
    ↓
Secondary / Tertiary
    ↓
Surface
    ↓
Elevated
```

Surfaces should remain close in tone.

Large visual separation is reserved for meaningful hierarchy.

---

# 65. Border Hierarchy

Use:

- subtle borders for structure
- standard borders for controls
- strong borders for important boundaries/focus contexts

Do not outline everything heavily.

---

# 66. Shadows and Depth

Depth should be subtle.

Prefer:

- surface contrast
- borders
- spacing

before:

- heavy shadows
- blur
- glow

---

# 67. Decorative Gradients

Gradients are not a core GrowFlow visual mechanism.

Do not introduce gradients merely to make a design look "AI".

If a gradient is ever used, it must have a documented compositional reason and remain restrained.

---

# 68. Glassmorphism

Glassmorphism is not part of the core GrowFlow visual language.

Avoid:

- frosted glass everywhere
- transparent cards over busy backgrounds
- excessive blur
- translucent navigation

---

# 69. Generic SaaS Anti-Pattern

Avoid the formula:

```text
Top nav
+
giant gradient
+
three feature cards
+
floating dashboard screenshot
+
customer logos
+
CTA
```

GrowFlow should have a more editorial and intentional visual composition.

---

# 70. Card Overload Anti-Pattern

Do not convert every content unit into:

```text
white rectangle
rounded corners
shadow
padding
```

This weakens hierarchy.

---

# 71. Role Theme Anti-Pattern

Do not create:

- green Student
- blue Mentor
- purple Admin

or any equivalent role color system.

One GrowFlow identity is required.

---

# 72. AI Anti-Pattern

Never default to:

- neon purple
- cyan glow
- holographic orb
- robot head
- brain graphic
- circuit pattern
- animated particles

AI is integrated intelligence, not a separate visual universe.

---

# 73. Motion Anti-Pattern

Avoid:

- constant movement
- infinite floating
- excessive parallax
- animated backgrounds
- unnecessary counters
- fake typing
- bouncing buttons

---

# 74. Image Anti-Pattern

Avoid stock imagery that:

- feels staged
- repeats generic startup tropes
- competes with product content
- has inconsistent visual treatment

---

# 75. Responsive Anti-Pattern

Never:

- simply scale desktop down
- shrink tables until unreadable
- rely on hover on touch devices
- hide essential actions
- alter domain semantics on mobile

---

# 76. Accessibility Anti-Pattern

Never rely on:

- color alone
- placeholder-only labels
- hover-only actions
- invisible focus
- tiny touch targets
- motion as the only state indicator

---

# 77. Stitch Interpretation Contract

Stitch must interpret this document as a **constraint system**, not as loose inspiration.

## 77.1 Stitch must preserve

- Manrope
- exact palette
- unified role theme
- Soft Intelligence
- warm light default
- soft charcoal dark
- quiet surfaces
- restrained accent
- dense integrated workplace UI
- editorial public website
- restrained AI
- subtle physical motion
- responsive rules
- accessibility principles

## 77.2 Stitch must not invent

- new primary brand colors
- separate role themes
- alternate typography systems
- neon AI styling
- arbitrary gradients
- unrelated visual language
- unrelated icon family
- excessive glassmorphism
- excessive card styling

## 77.3 Reference interpretation

Reference screenshots communicate:

- composition
- hierarchy
- density
- interaction patterns
- visual mood

They do not authorize literal copying.

---

# 78. Stitch Prompt Foundation

Every page-generation prompt should conceptually inherit:

```text
Use the GrowFlow Master Design system.

Identity:
Soft Intelligence.

Typography:
Manrope using the canonical GrowFlow type scale.

Color:
Warm neutral light theme with GrowFlow Sage accent and semantic colors.
Use the defined dark counterpart when dark mode is required.

Surfaces:
Quiet, restrained, softly differentiated.

Components:
Use the canonical GrowFlow component language.

AI:
Slightly deeper neutral treatment; never neon/cyberpunk.

Roles:
BUILD, SUPERVISE, GOVERN share one design system.

Motion:
Subtle physical movement; Float → Settle where appropriate.

Responsive:
Mobile <768, Tablet 768–1199, Desktop >=1200.

Accessibility:
Keyboard, focus, semantic structure, contrast, non-color semantics, reduced motion.

Do not invent a new visual system.
```

The later `Stitch_Instructions.md` will expand this into reusable prompt blocks.

---

# 79. Page Composition Contract

Every page must establish:

1. page purpose
2. primary user
3. primary action
4. primary information
5. secondary information
6. navigation context
7. state
8. responsive composition
9. accessibility requirements

Visual composition must follow product meaning.

---

# 80. Visual Hierarchy Contract

Every page should have:

- one dominant visual hierarchy
- clear primary action
- clear content entry point
- controlled secondary actions
- predictable metadata
- meaningful whitespace

Avoid competing focal points.

---

# 81. Interaction Priority

When multiple actions exist, use:

```text
Primary
↓
Secondary
↓
Tertiary
↓
Destructive / exceptional
```

Visual weight should reflect this hierarchy.

---

# 82. Form Hierarchy

Forms should generally follow:

```text
Context
↓
Field grouping
↓
Primary inputs
↓
Optional inputs
↓
Review
↓
Primary action
```

Do not overwhelm users with simultaneous secondary actions.

---

# 83. Workflow Hierarchy

Long workflows should expose:

- current step
- progress
- context
- required action
- validation state
- recovery

Do not visually imply that a background operation has completed simply because the user navigated away.

---

# 84. Loading Composition

Use the least disruptive loading representation that accurately communicates state.

Prefer:

- skeletons for known content structures
- progress indicators for measurable operations
- spinners for short indeterminate actions

Do not overuse spinners.

---

# 85. Error Composition

Error UI should answer:

- what happened
- what is affected
- whether anything was saved
- what can be done next

Use technical details only where useful to the target user.

---

# 86. Empty Composition

An empty state is not a failure.

Use:

- explanation
- context
- appropriate illustration/icon if useful
- next action

Keep decoration subordinate.

---

# 87. Success Composition

Success should confirm:

- what happened
- whether persistence completed
- what happens next

Avoid excessive celebration.

---

# 88. Responsive Typography

Typography may scale or recompose responsively where appropriate.

Do not sacrifice:

- readability
- hierarchy
- line length
- accessibility

Public display typography may require stronger mobile scaling than workplace headings.

Exact page-specific responsive typography is governed by the relevant page specification and token system.

---

# 89. Mobile Navigation

On mobile:

- global top navigation remains available
- authenticated sidebar becomes a drawer
- navigation remains keyboard/screen-reader accessible
- drawer focus is managed correctly
- essential actions remain discoverable

---

# 90. Mobile Tables

Do not force wide desktop tables into narrow screens.

Possible transformations:

- horizontal scroll when tabular comparison remains essential
- priority-column reduction
- row-to-detail composition
- stacked metadata
- contextual action menus

The correct transformation depends on the information meaning.

---

# 91. Mobile Dashboards

Prioritize:

1. key state
2. key metric
3. urgent/actionable information
4. trends
5. detail

Do not simply stack every desktop card vertically without reconsidering hierarchy.

---

# 92. Mobile AI Interfaces

AI interfaces must preserve:

- conversation order
- user/AI distinction
- generation state
- action controls
- readable response width
- input accessibility

Do not allow long AI content to destroy the page layout.

---

# 93. Accessibility — Motion

Reduced-motion users must receive equivalent information.

Do not encode critical meaning only through animation.

---

# 94. Accessibility — Color

All critical semantics must remain understandable without color perception.

Use:

- labels
- icons
- patterns
- position
- typography

where appropriate.

---

# 95. Accessibility — Keyboard

Keyboard users must be able to:

- reach every action
- understand focus
- navigate menus
- operate dialogs
- operate tabs
- operate drawers
- submit forms
- recover from errors

---

# 96. Accessibility — Dialogs

Dialogs must:

- trap focus appropriately
- expose an accessible name
- provide a clear close mechanism
- restore focus appropriately
- avoid unnecessary nested dialogs

---

# 97. Accessibility — Drawers

Drawers should behave as controlled dialogs/navigation surfaces where applicable.

They must not create inaccessible background interaction.

---

# 98. Accessibility — Dynamic Content

Use appropriate live-region behavior for meaningful changes.

Avoid flooding assistive technology with high-frequency streaming events.

---

# 99. Visual QA

Every Stitch output should be reviewed against:

### Brand

- logo
- identity
- no role theme divergence

### Typography

- Manrope
- correct hierarchy
- correct weights
- correct scale

### Color

- exact tokens
- restrained accent
- correct semantic colors
- dark counterpart

### Layout

- correct shell
- correct spacing
- correct density
- correct hierarchy

### Components

- canonical controls
- consistent radius
- consistent states

### AI

- restrained
- truthful
- integrated

### Responsive

- mobile
- tablet
- desktop

### Accessibility

- focus
- contrast
- semantics
- touch targets
- reduced motion

---

# 100. Visual Regression Principle

A new page must not introduce visual language that would make another GrowFlow page look unrelated.

When a new component is required:

1. search for an existing pattern
2. extend existing component if appropriate
3. create a new component only when necessary
4. add it to the component system
5. update the relevant design documentation

---

# 101. Design Change Control

Once this document is frozen, a design change should identify:

- affected token
- affected components
- affected pages
- affected Stitch instructions
- affected assets
- affected Figma system
- migration implications
- visual regression scope

Do not silently change foundation values.

---

# 102. Token Governance

Exact values in this document are canonical unless superseded by an explicitly approved later version.

Do not create:

- `#6F8063` because it "looks close"
- a second sage
- arbitrary spacing
- arbitrary radius
- arbitrary shadow

Reuse canonical tokens.

---

# 103. Asset Governance

Assets must have:

- stable name
- known purpose
- known category
- light/dark suitability where relevant
- source/license status where applicable
- usage guidance

Reference images must be explicitly marked as references.

---

# 104. Font Governance

Manrope is canonical.

New fonts require explicit design-system approval.

Font substitutions should occur only when:

- technical fallback is required
- licensing requires it
- a specific platform constraint exists

---

# 105. Logo Governance

The approved Connected Flow / Abstract G direction is the primary GrowFlow identity.

Future variants must preserve:

- recognizability
- simplicity
- flow metaphor
- abstract G relationship
- restrained character

---

# 106. Dark Mode Governance

Every new component must be reviewed in:

- light
- dark

A component is not complete if its dark treatment is merely inverted or unreadable.

---

# 107. Responsive Governance

Every page must be reviewed at:

- mobile
- tablet
- desktop

Do not treat desktop approval as responsive approval.

---

# 108. Accessibility Governance

Every page must pass:

- keyboard review
- focus review
- semantic review
- contrast review
- responsive touch review
- reduced-motion review

---

# 109. Performance Visual Rule

Visual quality must not depend on expensive effects.

Avoid unnecessary:

- blur
- massive background images
- animated gradients
- heavy parallax
- oversized video
- continuous canvas effects

Prefer performant composition.

---

# 110. Image Performance

Images should support:

- responsive sizing
- appropriate dimensions
- lazy loading where appropriate
- modern formats where supported
- meaningful alt text when informative

Decorative images should not create unnecessary accessibility noise.

---

# 111. Content Performance

Avoid rendering large visual systems when the user cannot currently see or use them.

Progressive disclosure is both a UX and performance strategy.

---

# 112. Information Density Rule

Density should be intentional.

Increase density by:

- removing unnecessary decoration
- improving alignment
- reducing redundant labels
- grouping related metadata

Do not increase density by:

- shrinking typography excessively
- removing whitespace indiscriminately
- cramming controls together

---

# 113. Whitespace Rule

Whitespace is structural.

Use it to separate:

- unrelated sections
- primary and secondary content
- navigation and content
- actions and information

Do not eliminate whitespace merely to "fit more."

---

# 114. Alignment Rule

Strong alignment is a major part of GrowFlow's visual polish.

Prefer shared:

- left edges
- column lines
- content baselines
- container boundaries

Avoid arbitrary offsets.

---

# 115. Editorial Asymmetry

Public pages may use controlled asymmetry.

Asymmetry must still preserve:

- balance
- hierarchy
- reading flow
- responsive integrity

Asymmetry is a composition technique, not disorder.

---

# 116. Workplace Symmetry and Structure

Authenticated pages should generally favor stronger structural alignment than public editorial pages.

This supports:

- scanning
- productivity
- predictability

---

# 117. Icon + Text Rule

When an icon accompanies text:

- icon must reinforce meaning
- text remains primary
- icon should not overpower label
- spacing must be consistent

Avoid decorative icon clutter.

---

# 118. Metadata Rule

Metadata should be visually subordinate.

Use:

- Metadata 12px / 500
- Caption 13px / 400
- Body Small 14px / 400

as appropriate.

Do not make metadata compete with primary content.

---

# 119. Status Badge Rule

Badges should be:

- compact
- semantic
- readable
- restrained

Avoid turning every metadata value into a pill.

---

# 120. Tooltip Rule

Tooltips are for:

- clarification
- icon-only controls
- abbreviated information

Do not hide essential information exclusively in tooltips.

---

# 121. Menu Rule

Menus should prioritize:

- clear grouping
- predictable order
- keyboard support
- adequate target size
- destructive separation where needed

---

# 122. Search Result Rule

Search results should make:

- resource identity
- type
- context
- relevance

clear without excessive decoration.

---

# 123. Notification Visual Priority

Recommended hierarchy:

```text
Critical / action required
        ↓
Important
        ↓
Informational
        ↓
Low-priority activity
```

Visual urgency must correspond to real urgency.

---

# 124. Admin Visual Language

GOVERN uses the same brand but may use higher information density.

Admin surfaces may emphasize:

- metrics
- system health
- audit
- traces
- tables
- filtering
- monitoring

Do not make admin look like a separate enterprise product.

---

# 125. Mentor Visual Language

SUPERVISE emphasizes:

- students
- groups
- projects
- risks
- activity
- notes
- help requests
- project definitions

Visual design should support oversight without becoming surveillance-like.

---

# 126. Student Visual Language

BUILD emphasizes:

- project progression
- tasks
- milestones
- blueprint
- assessment
- risks
- roadmap
- AI Mentor
- feedback

Visual design should support action and learning.

---

# 127. Project Workspace Visual Language

The project workspace is the core operational environment.

It should maintain:

- persistent project context
- predictable secondary navigation
- strong current-page indication
- contextual actions
- consistent state presentation

---

# 128. Project Identity

Project identity should be visible without dominating every page.

Use:

- project name
- lifecycle/status
- contextual metadata
- relevant ownership

Keep repeated project identity compact in dense views.

---

# 129. Version Visual Language

Versioned resources should communicate:

- current version
- historical version
- draft
- generated
- approved
- superseded

Version state must never be ambiguous.

---

# 130. Canonical State Visual Rule

Visual state must reflect canonical backend state.

Do not design UI that suggests:

- persistence before confirmation
- completion before completion
- approval before approval
- deployment before deployment

This is especially important for AI workflows.

---

# 131. Long-Running Operation Rule

A long-running operation must remain understandable when:

- user stays on page
- user navigates away
- user returns
- browser reconnects
- operation completes
- operation fails

The visual system must support persistent state rather than browser-dependent animation.

---

# 132. Error Recovery Rule

Recovery actions should be explicit.

Examples:

- Retry
- Resume
- Reconnect
- View details
- Return
- Contact mentor

Do not expose technical recovery mechanisms that the target user cannot understand.

---

# 133. Visual Language for Confidence

GrowFlow should communicate confidence through:

- consistency
- precise status
- clear provenance
- calm UI
- predictable behavior

not through:

- glossy effects
- futuristic graphics
- excessive motion

---

# 134. Visual Language for Intelligence

Intelligence should emerge from:

- organization
- contextual information
- useful automation
- precise recommendations
- structured AI output

not from "AI-looking" decoration.

---

# 135. Visual Language for Growth

Growth should be represented through:

- progression
- milestones
- completion
- trends
- flow
- movement through lifecycle

Avoid literal growth clichés wherever possible.

---

# 136. Visual Language for Flow

Flow is represented through:

- connected stages
- transitions
- relationships
- progression
- timelines
- navigation continuity
- the brand mark

---

# 137. Public Documentation Visual Language

Documentation should feel:

- editorial
- structured
- readable
- trustworthy
- technically credible

Use strong:

- headings
- navigation
- code presentation
- search
- metadata
- cross-links

Avoid excessive decorative elements.

---

# 138. Contact Visual Language

Contact should feel:

- direct
- trustworthy
- simple
- human

Avoid excessive form complexity.

---

# 139. Footer Visual Language

Footer should provide:

- navigation
- documentation
- contact
- product context
- legal information where required

It should remain visually quiet.

---

# 140. Login Visual Language

Login should optimize for:

- confidence
- clarity
- low friction
- identity
- accessibility

Do not turn authentication into a marketing page.

---

# 141. Registration Visual Language

Registration should prioritize:

- clear steps
- concise forms
- validation
- confidence
- progress where multi-step

---

# 142. Onboarding Visual Language

Onboarding may use more visual explanation than ordinary workplace pages.

Still preserve:

- Soft Intelligence
- restrained palette
- clear hierarchy
- low cognitive load

---

# 143. System Error Pages

System-level error pages should remain within the GrowFlow identity.

They may use:

- strong heading
- explanation
- recovery action
- minimal illustration

Avoid dramatic failure graphics.

---

# 144. 404 Visual Language

404 should be:

- calm
- useful
- lightly expressive

Primary action should return the user to a meaningful destination.

---

# 145. 403 / 401 Visual Language

Authorization/authentication failures should explain the state without exposing sensitive information.

Use clear action paths such as:

- sign in
- return
- request access

---

# 146. AI Unavailable Visual Language

AI service unavailability should not make the entire product feel broken.

Clearly separate:

- GrowFlow availability
- AI availability

Provide alternative navigation where possible.

---

# 147. Document Processing Visual Language

Document processing should expose:

- processing
- completed
- failed
- retryable state

Use progress only when it is real.

---

# 148. RAG Visual Language

RAG-related states are primarily operational/admin concepts.

Do not expose unnecessary implementation details to ordinary users.

When surfaced, distinguish:

- source
- processing
- indexed
- unavailable

---

# 149. Visual Privacy Rule

Visual design must not reveal information merely because it exists in the interface.

Access-controlled content must remain access-controlled.

Do not use preview cards, search suggestions, notifications, or metadata to leak restricted information.

---

# 150. Design-System Extension Rule

A new visual pattern is justified only when:

1. existing components cannot express the requirement,
2. the new pattern has a clear semantic purpose,
3. responsive behavior is defined,
4. accessibility is defined,
5. dark mode is defined,
6. states are defined,
7. it is documented,
8. it does not conflict with Soft Intelligence.

---

# 151. Reference Image Rule

When using references:

### Extract

- hierarchy
- spacing rhythm
- composition
- density
- interaction
- visual tone

### Do not extract literally

- exact branding
- exact copy
- proprietary assets
- unrelated colors
- unrelated typography
- unrelated layout constraints

---

# 152. Stitch Reference Rule

If multiple references disagree:

1. this Master Design wins
2. frozen token system wins
3. approved component system wins
4. page specification wins for page-specific composition
5. reference images are lowest authority

---

# 153. Design Token Mapping

The visual token system should map conceptually as:

```text
Color Tokens
Typography Tokens
Spacing Tokens
Radius Tokens
Elevation Tokens
Size Tokens
Motion Tokens
Responsive Tokens
Accessibility Tokens
AI Tokens
```

The implementation token file (`Phase 06C`) remains the detailed engineering mapping.

This Master Design defines the visual intent and exact canonical values.

---

# 154. Canonical Token Summary

## Color — Light

```text
Background       #F7F7F4
Surface          #FFFFFF
Secondary        #F2F2EE
Tertiary         #EDEDE8

Primary Text     #1C1C1A
Secondary Text   #5F625D
Tertiary Text    #858780

Border Subtle    #E5E5DF
Border Standard  #D9D9D2
Border Strong    #C9C9C0

Accent           #6F7F63
Accent Hover     #607055
Accent Active    #526149
Accent Soft      #E9EDE5
Accent Border    #B8C2AE

Success          #477A5A
Success Soft     #E7F0E9
Warning          #9A7135
Warning Soft     #F5EDDD
Danger           #A6534D
Danger Soft      #F6E8E6
Info             #54718A
Info Soft        #E8EEF3

AI               #5F6B7A
AI Surface       #ECEEF1
AI Border        #D4D8DD
AI Emphasis      #424D5A
```

## Color — Dark

```text
Background       #171816
Secondary        #1E201D
Tertiary         #262824
Surface          #20221F
Elevated         #272925
Muted            #2D302B

Primary Text     #F0F1EC
Secondary Text   #C2C5BD
Tertiary Text    #91958C

Border Subtle    #30332E
Border Standard  #3A3D37
Border Strong    #4A4E47

Accent           #9AAA8D
Accent Hover     #A8B79C
Accent Active    #B7C5AB
Accent Soft      #2B3328

Success          #7FB18C
Warning          #D0A962
Danger           #D27A72
Info             #88A8C0

AI Surface       #292D30
AI Border        #3C4246
AI Emphasis      #A9B2BB
```

## Spacing

```text
2 4 8 12 16 20 24 32 40 48 64 80 96 128
```

## Radius

```text
4 6 8 12 16 20 9999
```

## Elevation

```text
L0 none
L1 0 1px 2px rgba(0,0,0,0.04)
L2 0 4px 12px rgba(0,0,0,0.06)
L3 0 12px 32px rgba(0,0,0,0.08)
```

## Breakpoints

```text
Mobile  <768px
Tablet  768–1199px
Desktop >=1200px
```

---

# 155. Canonical Component Dimensions

```text
Authenticated TopNav      64px
Public TopNav             68–76px

Sidebar                   248px
Sidebar range             240–264px
Collapsed Sidebar         72px

Standard Button           40px
Large CTA                 48px
Compact Button            32px

Standard Input            40px
Large Input               48px
Compact Input             36px

Touch Target              44×44px
```

---

# 156. Design Invariants

The following must remain true across GrowFlow:

1. Manrope remains the canonical typeface.
2. Soft Intelligence remains the design identity.
3. Warm light remains the default appearance.
4. Dark mode remains a soft charcoal counterpart.
5. One unified design system serves all roles.
6. GrowFlow Sage remains the primary accent.
7. Accent use remains restrained.
8. Semantic colors remain meaningful.
9. AI remains a deeper but integrated variant.
10. AI never becomes neon/cyberpunk by default.
11. Cards remain quiet.
12. Tables remain integrated and dense.
13. Public interfaces remain editorial/contextual.
14. Workplace interfaces remain operational.
15. Dashboards remain data instruments.
16. Hero remains statement + storytelling.
17. Motion remains subtle.
18. Float → Settle remains the preferred scroll interaction.
19. Reduced motion is respected.
20. Mobile is first-class.
21. Accessibility is part of visual completion.
22. References do not override the system.
23. Stitch does not invent the foundation.
24. New components inherit the existing language.
25. Visual state must remain truthful to actual application state.
26. Manrope is the canonical GrowFlow UI/editorial typeface.
27. JetBrains Mono is reserved for explicitly technical content.
28. No third font family is permitted without design-system change control.

---

# 157. Do Not Violate

The following are hard visual prohibitions unless explicitly approved in a future design revision:

- generic AI neon
- cyberpunk AI
- glowing UI everywhere
- rainbow role themes
- excessive gradients
- excessive glassmorphism
- card-everything
- giant pills everywhere
- heavy shadows everywhere
- animated backgrounds
- excessive parallax
- fake AI typing
- generic brain/circuit/robot imagery
- arbitrary fonts
- arbitrary primary colors
- arbitrary spacing systems
- decorative charts
- unreadable dense interfaces
- hover-only essential interactions
- color-only semantic communication
- dark-mode inversion
- literal copying of reference screenshots

---

# 158. Design Completion Checklist

A visual design is not complete until:

### Identity

- [ ] GrowFlow identity is recognizable
- [ ] Connected Flow / Abstract G direction is respected
- [ ] no role-specific branding exists

### Typography

- [ ] Manrope is used
- [ ] hierarchy follows canonical scale
- [ ] weights are appropriate
- [ ] body readability is preserved

### Color

- [ ] canonical palette is used
- [ ] accent is restrained
- [ ] semantic colors are meaningful
- [ ] AI treatment is restrained
- [ ] dark mode is intentional

### Layout

- [ ] spacing follows token system
- [ ] alignment is deliberate
- [ ] density matches page purpose
- [ ] containers are consistent

### Components

- [ ] canonical components are reused
- [ ] radius language is consistent
- [ ] states are defined
- [ ] focus is visible

### Imagery

- [ ] imagery is contextual
- [ ] imagery does not compete with content
- [ ] references are not copied literally

### Motion

- [ ] movement is purposeful
- [ ] Float → Settle is subtle
- [ ] reduced motion works

### Responsive

- [ ] mobile reviewed
- [ ] tablet reviewed
- [ ] desktop reviewed
- [ ] no semantic changes across breakpoints

### Accessibility

- [ ] keyboard usable
- [ ] focus visible
- [ ] semantic structure valid
- [ ] color not sole semantic mechanism
- [ ] touch targets adequate

### Stitch

- [ ] no new visual system invented
- [ ] master tokens respected
- [ ] anti-patterns avoided
- [ ] output remains recognizably GrowFlow

---

# 159. Master Design Decision Boundary

This document defines **visual truth**.

It does not redefine:

- database architecture
- API architecture
- domain behavior
- authorization policy
- canonical state
- AI orchestration
- persistence
- event architecture
- backend implementation

Those remain governed by the corresponding architecture documents.

Visual design must represent those systems accurately but must not redefine them.

---

# 160. Relationship to Later Stitch Documentation

This document is the parent reference for:

```text
Master_Design.md
        ↓
Stitch_Instructions.md
        ↓
Asset Manifest
        ↓
Figma Design System
        ↓
Page Specification
        ↓
Page-specific Stitch Prompt
        ↓
Stitch Output
        ↓
Visual QA
```

The later Stitch instruction document should **reference and operationalize** this master design rather than duplicate it unnecessarily.

---

# 161. Relationship to Figma

The `.fig` design-system asset must visually implement this document.

Figma should represent:

- colors
- typography
- spacing
- components
- states
- responsive compositions
- dark mode
- AI surfaces
- brand assets

Any divergence between Figma and this document must be explicitly reviewed.

---

# 162. Relationship to Assets

Brand assets must implement this document.

Font package:

- Manrope
- approved weights

Logo package:

- approved GrowFlow identity
- light/dark/monochrome variants
- mark
- wordmark
- favicon/app icon

Reference package:

- classified by purpose
- clearly marked as inspiration

---

# 163. Relationship to Stitch

Stitch is a design-generation tool within this system.

Stitch should:

- compose
- explore
- visualize
- iterate

Stitch should not:

- redefine brand
- redefine tokens
- redefine architecture
- redefine role themes
- redefine accessibility semantics
- invent backend state

---

# 164. Final Master Design Contract

The definitive GrowFlow visual experience is:

> **Soft Intelligence expressed through a warm, restrained, editorial-to-operational interface system built around Manrope, quiet neutral surfaces, a subtle sage accent, strong typographic hierarchy, integrated dense data presentation, contextual imagery, subtle physical motion, and a slightly deeper but non-neon AI layer.**

The system must feel:

**calm on the surface, powerful underneath.**

The system must communicate:

**growth, flow, progression, structure, mentorship, execution, and intelligence.**

The system must remain:

**unified across BUILD, SUPERVISE, and GOVERN.**

---

# 165. Freeze Status

**Master Design v1.0**

Status:

**FOUNDATION DRAFT v1.1 — READY FOR REVIEW**

Before final freeze, the following must be completed or explicitly marked:

- [ ] final logo vector assets
- [ ] final logo geometry / clear-space measurements
- [ ] final font asset package (Manrope + JetBrains Mono, subject to final licensing/package verification)
- [ ] icon family selection
- [ ] final image/reference classification
- [ ] Figma implementation
- [ ] Stitch instruction extraction
- [ ] final visual QA against representative pages

No page-by-page Stitch generation should be considered visually final until this foundation is approved.

---

## End of Master Design
