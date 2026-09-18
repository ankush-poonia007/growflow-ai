# GrowFlow — DESIGN.md
## Complete Visual Design System & Stitch Design Specification

**Status:** FROZEN / AUTHORITATIVE  
**Version:** 1.0  
**Product:** GrowFlow  
**Design System:** Soft Intelligence  
**Default Theme:** Warm Light  
**Secondary Theme:** Soft Charcoal Dark  
**Primary Typeface:** Manrope  
**Primary Brand Accent:** Muted Olive Green  
**Audience:** Google Stitch + frontend implementation team  
**Purpose:** Define the complete visual language, measurable design tokens, component geometry, visual states, responsive rules, interaction language, and design constraints for every GrowFlow interface.

---

# 00. DOCUMENT AUTHORITY

This document is the compact visual authority supplied to Stitch.

It does **not** replace GrowFlow's complete product, information-architecture, frontend, or backend documentation.

Use the following authority hierarchy:

1. Security and authorization constraints
2. Frozen GrowFlow Phase 05 application/integration architecture
3. Frozen Phase 02 information architecture and routing
4. Frozen Phase 03 visual design direction
5. Frozen Phase 04 frontend page documentation contract
6. Frozen Phase 06 frontend foundation specification
7. This DESIGN.md
8. Page-specific approved requirements
9. Stitch-generated visual exploration

A page-specific instruction must not silently redefine a higher-level rule.

If a visual choice is unspecified, choose the smallest, calmest, most consistent solution that fits this system.

---

# 01. PURPOSE

GrowFlow must look and feel like a mature, coherent product rather than a collection of independently generated screens.

This document defines:

- exact font family and weights
- typography scale
- color tokens
- surface hierarchy
- borders
- shadows
- radii
- spacing
- component dimensions
- navigation dimensions
- responsive breakpoints
- visual density
- states
- motion
- imagery
- public-site composition
- authenticated-workplace composition
- BUILD / SUPERVISE / GOVERN visual behavior
- AI visual behavior
- document styling
- data visualization rules
- accessibility expectations
- Stitch generation rules
- prohibited visual patterns

The goal is to remove visual ambiguity wherever a deterministic rule is useful.

---

# 02. PRODUCT CONTEXT

GrowFlow is an agentic project-management and mentorship platform.

Major capabilities include:

- project discovery
- project assessment
- adaptive assessment
- blueprint generation
- project planning
- tasks
- milestones
- risks
- roadmap/timeline
- documents
- README/document rendering
- GitHub integration
- mentor supervision
- AI Mentor
- project changes
- AI observability
- system governance
- analytics

GrowFlow has three workplace contexts:

| Workplace | User | Core orientation |
|---|---|---|
| BUILD | Student | Build, learn, execute, progress |
| SUPERVISE | Mentor | Observe, guide, intervene, supervise |
| GOVERN | Admin | Govern, investigate, observe, operate |

These are contextual modes of the same product.

They are **not separate visual themes**.

---

# 03. CORE DESIGN PHILOSOPHY

## 03.1 Soft Intelligence

The central visual idea is:

> **Calm on the surface. Powerful underneath.**

The interface should feel:

- intelligent
- precise
- trustworthy
- calm
- human
- modern
- sophisticated
- operational
- focused

It should not feel:

- robotic
- cyberpunk
- neon
- childish
- excessively playful
- visually noisy
- sterile
- generic SaaS
- template-generated

## 03.2 Hierarchy Over Decoration

Visual hierarchy must come primarily from:

1. typography
2. spacing
3. alignment
4. surface contrast
5. restrained borders
6. limited accent color
7. controlled motion

Decoration is secondary.

## 03.3 Productive Sophistication

The visual system should look premium because it is **precise**, not because it is overloaded with effects.

---

# 04. DESIGN PERSONALITY

Every GrowFlow interface should balance:

```text
CALM
  +
INTELLIGENT
  +
PRECISE
  +
HUMAN
  +
OPERATIONAL
```

Priority:

1. clarity
2. hierarchy
3. usability
4. consistency
5. visual sophistication
6. decoration

Never reverse this priority.

---

# 05. VISUAL MATURITY

GrowFlow should look like a production software platform.

Avoid aesthetics associated with:

- student portfolio sites
- hackathon landing pages
- generic AI startups
- template marketplaces
- concept-only Dribbble designs
- dashboard mockups with no functional logic

Visual design must remain implementable.

---

# 06. DESIGN SYSTEM ARCHITECTURE

Use:

```text
Primitive Tokens
      ↓
Semantic Tokens
      ↓
Component Tokens
      ↓
Components
      ↓
Patterns
      ↓
Page Layouts
      ↓
Pages
```

Do not bypass this hierarchy unless a genuine implementation requirement exists.

---

# 07. TYPOGRAPHY — PRIMARY FONT

## 07.1 Canonical Typeface

**Manrope**

GrowFlow's canonical typeface is **Manrope**, not merely a "Manrope-style" substitute.

Use the actual Manrope font files supplied with the design package.

## 07.2 CSS Family

```css
font-family: "Manrope", sans-serif;
```

## 07.3 Font Loading

Ship only the weights actually used by the application.

Recommended weights:

- 400 Regular
- 500 Medium
- 600 SemiBold
- 700 Bold
- 800 ExtraBold

Use `font-display: swap` or the equivalent production-safe loading strategy.

## 07.4 Weight Usage

| Weight | Name | Usage |
|---:|---|---|
| 400 | Regular | body copy, descriptions, long-form content |
| 500 | Medium | labels, metadata, navigation, secondary emphasis |
| 600 | SemiBold | buttons, section titles, important labels, table resource names |
| 700 | Bold | H1–H3, dashboard emphasis, major headings |
| 800 | ExtraBold | selected public hero/display emphasis only |

Do not use 800 as a normal application weight.

---

# 08. TYPOGRAPHY SCALE

## 08.1 Display Scale

| Token | Size | Weight | Line height | Letter spacing |
|---|---:|---:|---:|---:|
| Display XL | 64px | 700 | 1.05 | -0.03em |
| Display L | 56px | 700 | 1.08 | -0.03em |
| Display M | 48px | 700 | 1.10 | -0.025em |

Use display sizes primarily on public marketing pages.

## 08.2 Heading Scale

| Token | Size | Weight | Line height | Letter spacing |
|---|---:|---:|---:|---:|
| H1 | 40px | 700 | 1.15 | -0.02em |
| H2 | 32px | 700 | 1.20 | -0.015em |
| H3 | 26px | 700 | 1.25 | -0.01em |
| H4 | 22px | 600 | 1.30 | -0.005em |
| H5 | 18px | 600 | 1.35 | 0 |
| H6 | 16px | 600 | 1.40 | 0 |

## 08.3 Body Scale

| Token | Size | Weight | Line height |
|---|---:|---:|---:|
| Body Large | 17px | 400 | 1.60 |
| Body | 15px | 400 | 1.55 |
| Body Small | 14px | 400 | 1.50 |
| Caption | 13px | 400 | 1.45 |
| Metadata | 12px | 500 | 1.40 |

**12px is the minimum standard UI metadata size.**

Do not use 10px or 11px for ordinary product information.

---

# 09. RESPONSIVE TYPOGRAPHY

## 09.1 Public Hero

Desktop:

- 56–64px
- weight 700
- line height 1.05–1.10

Tablet:

- 48–56px

Mobile:

- 36–44px
- line height approximately 1.10

## 09.2 Application H1

Desktop:

- 40px

Tablet:

- 36px

Mobile:

- 32px

## 09.3 Application H2

Desktop:

- 32px

Tablet:

- 28px

Mobile:

- 24px

## 09.4 Application Body

Remain approximately:

- 15px desktop
- 15px tablet
- 15–16px mobile

Do not shrink application text excessively to fit content.

---

# 10. LETTER SPACING

Default body:

```text
0
```

Display:

```text
-0.02em to -0.03em
```

Small uppercase labels:

```text
0.04em
```

Only use uppercase when it improves categorization or hierarchy.

Avoid aggressive letter spacing.

---

# 11. COLOR SYSTEM — GOVERNING RULES

The palette is intentionally restrained.

Use:

- warm neutrals
- one primary brand accent
- semantic status colors
- deeper AI surfaces
- neutral contrast

Do not introduce arbitrary colors.

All colors below are canonical unless a future documented design revision replaces them.

---

# 12. LIGHT THEME — PAGE BACKGROUND

## 12.1 Primary Background

```text
#F7F7F4
```

Token:

```text
color.background.primary
```

Usage:

- application canvas
- large empty page areas
- authenticated workplace background

## 12.2 Secondary Background

```text
#F2F2EE
```

Usage:

- secondary regions
- grouped content
- muted control areas

## 12.3 Tertiary Background

```text
#EDEDE8
```

Usage:

- selected muted regions
- dense grouping
- inactive surfaces

Do not use tertiary background as the main page background.

---

# 13. LIGHT THEME — SURFACES

## 13.1 Primary Surface

```text
#FFFFFF
```

Usage:

- cards
- panels
- dialogs
- elevated content
- form surfaces

## 13.2 Raised Surface

```text
#FFFFFF
```

Use border/elevation to distinguish it.

## 13.3 Muted Surface

```text
#F2F2EE
```

## 13.4 Subtle Surface

```text
#EDEDE8
```

---

# 14. LIGHT THEME — TEXT

## 14.1 Primary

```text
#1C1C1A
```

Usage:

- page titles
- headings
- primary body content
- primary controls

## 14.2 Secondary

```text
#5F625D
```

Usage:

- descriptions
- supporting copy
- secondary labels

## 14.3 Tertiary

```text
#858780
```

Usage:

- timestamps
- low-priority metadata
- secondary contextual information

Never use tertiary text for critical information.

---

# 15. LIGHT THEME — BORDERS

## 15.1 Subtle

```text
#E5E5DF
```

Primary use:

- card borders
- separators
- table row structure

## 15.2 Standard

```text
#D9D9D2
```

Use for:

- inputs
- stronger separators
- component boundaries

## 15.3 Strong

```text
#C9C9C0
```

Use sparingly:

- focused/important structural boundaries
- strong table header separation

---

# 16. PRIMARY BRAND ACCENT

## 16.1 Canonical Brand Accent

```text
#6F7F63
```

Name:

**GrowFlow Olive**

Character:

- muted
- natural
- mature
- intelligent
- calm

Use for:

- primary CTA
- active navigation
- selected state
- key links
- important product emphasis

Do not use it everywhere.

---

# 17. BRAND ACCENT STATES

| Token | Hex | Usage |
|---|---|---|
| Accent Default | `#6F7F63` | primary interactive |
| Accent Hover | `#607055` | hover |
| Accent Active | `#526149` | pressed/active |
| Accent Soft | `#E9EDE5` | selected/soft background |
| Accent Border | `#B8C2AE` | accent boundary |

---

# 18. ACCENT USAGE PROPORTION

A typical screen should remain predominantly neutral.

Approximate visual balance:

```text
70–80% neutral surfaces
10–15% text/borders
5–10% accent + semantic emphasis
```

This is a visual guideline, not a pixel-level requirement.

The core rule is:

> Accent color must remain scarce enough to preserve emphasis.

---

# 19. SEMANTIC COLORS

## 19.1 Success

Primary:

```text
#477A5A
```

Soft:

```text
#E7F0E9
```

Use for:

- successful operation
- healthy state
- completed state
- confirmed positive outcome

## 19.2 Warning

Primary:

```text
#9A7135
```

Soft:

```text
#F5EDDD
```

Use for:

- attention required
- elevated risk
- pending decision

## 19.3 Danger

Primary:

```text
#A6534D
```

Soft:

```text
#F6E8E6
```

Use for:

- destructive actions
- critical failure
- severe risk

## 19.4 Information

Primary:

```text
#54718A
```

Soft:

```text
#E8EEF3
```

Use for:

- informational context
- neutral system information

---

# 20. SEMANTIC COLOR RULES

Never use semantic colors as decoration.

Never communicate status with color alone.

Use:

```text
color
+
text
+
icon/shape where useful
```

rather than color alone.

---

# 21. AI COLOR SYSTEM

AI receives a slightly deeper visual treatment.

## 21.1 AI Primary

```text
#5F6B7A
```

## 21.2 AI Soft Surface

```text
#ECEEF1
```

## 21.3 AI Border

```text
#D4D8DD
```

## 21.4 AI Emphasis

```text
#424D5A
```

AI styling should communicate:

- depth
- analysis
- intelligence
- process
- transparency

It must not communicate cyberpunk/futurism.

---

# 22. DARK THEME — BACKGROUNDS

## 22.1 Primary

```text
#171816
```

## 22.2 Secondary

```text
#1E201D
```

## 22.3 Tertiary

```text
#262824
```

---

# 23. DARK THEME — SURFACES

Primary surface:

```text
#20221F
```

Elevated surface:

```text
#272925
```

Muted surface:

```text
#2D302B
```

Use subtle differentiation rather than bright outlines.

---

# 24. DARK THEME — TEXT

Primary:

```text
#F0F1EC
```

Secondary:

```text
#C2C5BD
```

Tertiary:

```text
#91958C
```

Avoid pure `#FFFFFF` for all text.

---

# 25. DARK THEME — BORDERS

Subtle:

```text
#30332E
```

Standard:

```text
#3A3D37
```

Strong:

```text
#4A4E47
```

---

# 26. DARK THEME — ACCENT

Default:

```text
#9AAA8D
```

Hover:

```text
#A8B79C
```

Active:

```text
#B7C5AB
```

Soft:

```text
#2B3328
```

---

# 27. DARK SEMANTIC COLORS

Success:

```text
#7FB18C
```

Warning:

```text
#D0A962
```

Danger:

```text
#D27A72
```

Information:

```text
#88A8C0
```

Use these for readability against dark surfaces.

---

# 28. DARK AI SURFACES

AI surface:

```text
#292D30
```

AI border:

```text
#3C4246
```

AI emphasis:

```text
#A9B2BB
```

AI must remain visibly integrated into the product.

No glow is required.

---

# 29. SPACING SYSTEM

Use an 8px base rhythm.

| Token | Value |
|---|---:|
| XXS | 2px |
| XS | 4px |
| S | 8px |
| SM | 12px |
| M | 16px |
| ML | 20px |
| L | 24px |
| XL | 32px |
| 2XL | 40px |
| 3XL | 48px |
| 4XL | 64px |
| 5XL | 80px |
| 6XL | 96px |
| 7XL | 128px |

2px is reserved for fine alignment/borders.

---

# 30. SPACING USAGE

Typical examples:

| Relationship | Default |
|---|---:|
| icon ↔ label | 8px |
| label ↔ input | 6–8px |
| input ↔ input | 16px |
| form section ↔ form section | 24–32px |
| card internal padding | 20–24px |
| page section | 32–48px |
| major public section | 64–128px |

Adjust according to density mode.

---

# 31. BORDER RADIUS

Canonical radius tokens:

| Token | Value | Usage |
|---|---:|---|
| Radius XS | 4px | fine controls |
| Radius S | 6px | inputs |
| Radius M | 8px | buttons, standard controls |
| Radius L | 12px | cards, panels |
| Radius XL | 16px | large surfaces |
| Radius 2XL | 20px | major editorial surfaces |
| Radius Full | 9999px | avatars/pills |

Avoid large radii as a default.

---

# 32. ELEVATION

## Level 0

No shadow.

## Level 1

```text
0 1px 2px rgba(0,0,0,0.04)
```

## Level 2

```text
0 4px 12px rgba(0,0,0,0.06)
```

## Level 3

```text
0 12px 32px rgba(0,0,0,0.08)
```

Use Level 3 primarily for major overlays.

Dark mode must use appropriately reduced/adjusted shadow treatment rather than blindly reusing light-mode shadows.

---

# 33. BORDER-FIRST ELEVATION PHILOSOPHY

Preferred hierarchy:

```text
Spacing
 ↓
Surface
 ↓
Border
 ↓
Shadow
```

Do not use shadows to compensate for weak layout hierarchy.

---

# 34. ICONOGRAPHY

Use one coherent icon family throughout GrowFlow.

Sizes:

| Context | Size |
|---|---:|
| compact | 16px |
| standard | 18–20px |
| large contextual | 24px |
| hero/decorative | 28–32px only where justified |

Interactive icons must have accessible names.

Do not mix visual icon families.

---

# 35. ICON WEIGHT

Use a consistent stroke/weight family.

Avoid mixing:

- filled icons
- outlined icons
- hand-drawn icons
- 3D icons

unless a specific documented context requires it.

---

# 36. BUTTON SYSTEM

## 36.1 Standard Primary

- height: 40px
- horizontal padding: 16px
- radius: 8px
- font: 14px / 600
- icon gap: 8px

## 36.2 Large CTA

- height: 48px
- horizontal padding: 20px
- radius: 8px
- font: 15–16px / 600

## 36.3 Compact

- height: 32px
- horizontal padding: 12px
- radius: 6px
- font: 13px / 600

---

# 37. BUTTON VISUAL STATES

Every interactive button supports:

```text
Default
Hover
Active
Focus
Disabled
Loading
```

Loading must preserve approximate geometry.

Avoid dramatic hover transformations.

---

# 38. PRIMARY BUTTON

Use the GrowFlow accent for the highest-priority action.

Light:

```text
background #6F7F63
text #FFFFFF
```

Hover:

```text
background #607055
```

Active:

```text
background #526149
```

Ensure contrast remains accessible.

---

# 39. SECONDARY BUTTON

Use neutral surfaces and borders.

Recommended:

```text
background #FFFFFF
border #D9D9D2
text #1C1C1A
```

Hover:

```text
background #F2F2EE
```

---

# 40. TERTIARY / GHOST BUTTON

Use primarily for secondary actions.

Avoid turning an entire page into a collection of low-contrast ghost controls.

---

# 41. INPUT SYSTEM

Standard:

```text
height: 40px
padding: 0 12px
radius: 6px
font-size: 14px
```

Large:

```text
height: 48px
```

Compact:

```text
height: 36px
```

Textarea:

- minimum height: 96px
- padding: 12px
- line height: 1.5

---

# 42. INPUT STATES

Support:

- default
- hover
- focus
- filled
- disabled
- read-only
- error
- success

Focus must be visually stronger than hover.

---

# 43. FORM LABELS

Standard:

```text
14px
500
#1C1C1A
```

Supporting description:

```text
13–14px
400
#5F625D
```

Error:

```text
13px
500
#A6534D
```

---

# 44. CHECKBOX / RADIO / SWITCH

Controls must:

- use the same accent system
- maintain clear selected state
- support keyboard interaction
- maintain adequate touch target
- provide text labels

Do not enlarge controls merely for decoration.

---

# 45. BADGES

Standard badge:

```text
height: 24px
horizontal padding: 8px
font: 12–13px / 500
radius: 9999px
```

Compact:

```text
height: 20px
```

Use pills for:

- status
- tags
- categories
- compact state

Not for every UI element.

---

# 46. STATUS INDICATORS

Recommended structure:

```text
indicator
+
status text
```

Optional:

```text
icon
+
indicator
+
status text
```

Color alone is insufficient.

---

# 47. AVATARS

Standard:

- 24px
- 32px
- 40px
- 48px

Use 56px+ only for profile/detail contexts.

Do not use oversized avatars in dense workplace screens.

---

# 48. TOOLTIP

Use tooltips for unfamiliar controls.

Do not hide essential information inside tooltips.

Tooltips should be:

- short
- contextual
- readable
- keyboard accessible

---

# 49. TOP NAVIGATION

Authenticated application:

```text
64px height
```

Public site:

```text
68–76px
```

depending on composition.

Use:

- subtle bottom border
- warm neutral surface
- restrained branding
- consistent alignment

Avoid:

- floating glass nav
- excessive blur
- giant pills

---

# 50. SIDEBAR

Desktop default:

```text
248px
```

Allowed implementation range:

```text
240–264px
```

Collapsed:

```text
72px
```

The sidebar is integrated into the application surface.

---

# 51. SIDEBAR ITEM

Typical:

```text
height: 36–40px
padding: 8–12px
icon: 18–20px
gap: 10–12px
radius: 6–8px
```

Active state uses subtle accent tint and/or a small leading indicator.

Do not create giant colored navigation blocks.

---

# 52. MOBILE NAVIGATION

At mobile widths:

```text
Sidebar → Drawer
```

The drawer must:

- open predictably
- close predictably
- maintain focus behavior
- preserve navigation hierarchy
- avoid blocking essential context unnecessarily

---

# 53. PAGE CONTAINERS

Authenticated application:

```text
max-width: approximately 1440px
```

Typical desktop horizontal padding:

```text
24–40px
```

Large desktop:

```text
40–64px
```

Public site:

```text
max-width: approximately 1280–1440px
```

depending on composition.

---

# 54. DENSITY MODES

## Editorial

Used for:

- landing
- public features
- public storytelling

Characteristics:

- large spacing
- larger typography
- visual narrative

## Standard

Used for:

- most authenticated pages

Characteristics:

- balanced spacing
- clear information hierarchy

## Dense

Used for:

- tables
- admin observability
- project management

Characteristics:

- compact rows
- efficient controls
- high information density

---

# 55. PAGE HEADER

Authenticated page header:

```text
Title
Supporting description
Primary action(s)
Optional contextual metadata
```

Typical bottom spacing:

```text
24–32px
```

Avoid excessive empty header space.

---

# 56. SECTION HEADER

Structure:

```text
Section title
Optional description
Optional action
```

Keep section titles visually subordinate to the page title.

---

# 57. CARD PHILOSOPHY

Cards are structural tools.

Use a card when it improves:

- grouping
- hierarchy
- separation
- scanability

If the page reads better without a card, do not add one.

---

# 58. CARD DEFAULTS

Typical:

```text
background: #FFFFFF
border: 1px solid #E5E5DF
radius: 12px
padding: 20–24px
```

Do not automatically apply a shadow.

---

# 59. TABLE SYSTEM

Tables are a first-class GrowFlow pattern.

They should be:

- dense
- aligned
- readable
- quiet
- integrated

Do not make them look like spreadsheets pasted into the product.

---

# 60. TABLE DIMENSIONS

Default row:

```text
44–48px
```

Dense row:

```text
40–44px
```

Header:

```text
40–44px
```

---

# 61. TABLE TYPOGRAPHY

Header:

```text
12–13px
500–600
```

Body:

```text
13–14px
400–500
```

Primary resource name:

```text
14px
600
```

---

# 62. TABLE STATES

Support where applicable:

- hover
- selected
- sorting
- filtering
- pagination
- loading
- empty
- error
- row actions
- expansion

Hover should be subtle.

---

# 63. MOBILE TABLES

Do not force all columns into a narrow viewport.

Choose based on content:

- horizontal scrolling
- prioritized columns
- row expansion
- detail drawer

---

# 64. DASHBOARD SYSTEM

Dashboards are **visual data instruments**.

Preferred information hierarchy:

```text
Context
 ↓
Key metrics
 ↓
Attention / risk
 ↓
Primary work
 ↓
Trend
 ↓
Supporting information
```

---

# 65. METRIC BLOCKS

A metric should contain:

- label
- value
- optional trend
- optional contextual interpretation

Do not manufacture trend data merely for visual completeness.

---

# 66. CHART SYSTEM

Charts must:

- represent meaningful data
- use restrained colors
- have labels
- remain readable
- work in light/dark themes
- have accessible alternatives where necessary

Avoid:

- 3D charts
- decorative donut charts
- excessive gradients
- chart overload

---

# 67. CHART COLOR PRIORITY

Prefer:

1. GrowFlow accent
2. neutral secondary series
3. semantic colors where meaningful
4. additional muted tones only when multiple series genuinely require them

Do not default to rainbow charts.

---

# 68. TIMELINE SYSTEM

Timelines communicate:

- phase
- milestone
- date
- progress
- dependency
- risk
- status

Use restrained connectors and clear hierarchy.

---

# 69. PROJECT WORKSPACE

Common structure:

```text
Project Header
      ↓
Project Context
      ↓
Project Navigation
      ↓
Current Resource
```

The workspace must preserve project identity while navigating between resources.

---

# 70. PROJECT HEADER

Include as relevant:

- project name
- lifecycle status
- current phase
- relevant actions
- important metadata

Avoid excessively tall headers.

---

# 71. PROJECT LIFECYCLE

Represent:

```text
IDEA
→
ASSESSMENT
→
BLUEPRINT
→
PLANNING
→
IMPLEMENTATION
→
TESTING
→
DEPLOYMENT
→
COMPLETED
```

Current state receives the strongest visual emphasis.

Completed states should be visually quieter.

Future states should remain visible but subdued.

---

# 72. TASK VISUAL LANGUAGE

Prioritize:

1. task name
2. status
3. priority
4. owner
5. due date
6. milestone
7. progress

Do not overdecorate individual task rows.

---

# 73. MILESTONE VISUAL LANGUAGE

Emphasize:

- milestone name
- target
- completion
- status
- timeline
- task relationship

---

# 74. RISK VISUAL LANGUAGE

Represent:

- risk
- severity
- likelihood
- impact
- mitigation
- status
- owner
- affected project element

Not every risk should visually scream.

Use danger color primarily for genuinely critical states.

---

# 75. HEALTH VISUAL LANGUAGE

Health is a derived representation.

Do not introduce a competing arbitrary health system.

Show meaningful underlying signals when useful.

---

# 76. DOCUMENT SYSTEM

Documents should feel editorial and readable.

Use:

- generous line-height
- clear headings
- consistent spacing
- subtle separators
- readable code
- strong hierarchy

Do not make document pages resemble raw browser HTML.

---

# 77. MARKDOWN SYSTEM

Markdown rendering must support:

- headings
- paragraphs
- lists
- tables
- links
- quotes
- code
- structured content

Untrusted content must be safely sanitized.

---

# 78. DOCUMENT TYPOGRAPHY

Reading content should generally use:

```text
15–17px body
1.55–1.70 line height
```

Long-form content should generally remain within approximately:

```text
60–80 characters per line
```

when possible.

---

# 79. CODE SYSTEM

Code blocks use a dedicated surface.

Light:

```text
#F0F1ED
```

Dark:

```text
#111310
```

Use a monospace font.

Code blocks support:

- copy
- language identification where useful
- horizontal overflow
- accessible labels

---

# 80. GITHUB STATES

Represent:

```text
Not Connected
Connecting
Connected
Syncing
Synced
Error
Unavailable
```

Do not imply "connected" means "healthy."

---

# 81. AI VISUAL PHILOSOPHY

AI is a deeper layer of Soft Intelligence.

It should communicate:

```text
Intelligence
+
Context
+
Process
+
Transparency
```

It must not become a visually separate cyberpunk product.

---

# 82. AI SURFACES

Use the defined AI palette.

AI surfaces should be subtly differentiated from ordinary application surfaces.

Avoid:

- glow
- neon borders
- excessive gradients
- animated particles

---

# 83. AI EXECUTION STATES

Use:

```text
QUEUED
↓
RUNNING
↓
VALIDATING
↓
QA
↓
COMPLETED
```

Failure/alternate states:

```text
FAILED
CANCELLED
RETRYING
```

---

# 84. AI PROGRESS

Only show progress that corresponds to actual backend execution information.

Never fabricate percentage progress.

If exact percentage is unavailable, use stage-based status.

---

# 85. AI LOADING

Do not simulate human typing.

Preferred:

- execution indicator
- stage indicator
- subtle activity
- structured loading state

---

# 86. AI FAILURE

AI failure should be calm and actionable.

Preferred hierarchy:

```text
Generation could not be completed
Context/reason
Retry
View execution
```

Avoid full-screen alarm states for recoverable AI failures.

---

# 87. AI RESULT PRESENTATION

Use:

- readable content width
- clear hierarchy
- structured output
- contextual source/provenance where available
- validation state where applicable
- relevant actions

Do not make AI responses enormous chat bubbles.

---

# 88. AI MENTOR

AI Mentor is a project intelligence workspace.

It may show contextual references to:

- project
- blueprint
- task
- milestone
- risk
- document
- activity

The visual system should make context visible without overwhelming the conversation.

---

# 89. AI OBSERVABILITY

Admin AI interfaces should distinguish:

- usage
- executions
- traces
- quality
- cost

Do not visually merge these into one generic "AI dashboard."

---

# 90. AI TRACE

Trace detail may expose:

- execution
- stages
- agent activity
- timing
- provider/model information where authorized
- validation
- failures
- cost
- correlation

The visual treatment should remain technical but calm.

---

# 91. MODAL SYSTEM

Standard modal:

```text
480–640px
```

Large modal:

```text
720–960px
```

Use modals for focused actions.

Do not move full multi-step workflows into arbitrary dialogs.

---

# 92. DRAWER SYSTEM

Use drawers for:

- contextual detail
- quick inspection
- filters
- mobile navigation
- secondary information

Drawers must preserve focus behavior.

---

# 93. TOAST SYSTEM

Toasts are:

- short
- contextual
- non-blocking

Typical duration:

```text
3–5 seconds
```

Important information must also exist persistently when necessary.

---

# 94. EMPTY STATES

Structure:

```text
Icon/visual
 ↓
Title
 ↓
Explanation
 ↓
Primary action
```

Keep illustrations restrained.

---

# 95. ERROR STATES

Structure:

```text
What failed
+
Impact/status
+
Recovery action
```

When retry is safe, provide retry.

When retry is not safe, explain the next action instead.

---

# 96. LOADING STATES

Use:

- skeletons
- section loading
- inline progress
- execution states

Avoid unnecessary full-page spinners.

---

# 97. SUCCESS STATES

Success should be:

- visible
- reassuring
- restrained

Avoid excessive celebration animations.

---

# 98. MOTION SYSTEM

Core philosophy:

> **Float → Settle**

Motion should feel:

- subtle
- physical
- intentional
- fast enough for productivity

---

# 99. MOTION DURATIONS

| Token | Duration |
|---|---:|
| Micro | 100ms |
| Fast | 150ms |
| Standard | 200ms |
| Medium | 300ms |
| Large | 400ms |

Avoid slow decorative transitions.

---

# 100. MOTION EASING

Default:

```text
ease-out
```

Use more physical easing only for larger spatial transitions.

---

# 101. HOVER MOTION

If used:

```text
translateY(-1px)
```

maximum for ordinary cards/buttons unless a page-specific interaction has a reason for more.

Avoid dramatic floating.

---

# 102. PAGE TRANSITIONS

Preferred:

```text
opacity
+
small positional adjustment
```

Avoid cinematic transitions.

---

# 103. SCROLL INTERACTION

Public storytelling may use subtle Float → Settle transitions.

Authenticated application pages should avoid heavy parallax.

---

# 104. REDUCED MOTION

When reduced motion is enabled:

- remove decorative movement
- reduce transition distance
- preserve functional state change

---

# 105. PUBLIC WEBSITE

Public pages are expressive and editorial.

Priorities:

- storytelling
- visual hierarchy
- contextual imagery
- typography
- product narrative
- controlled interaction

They must still belong to GrowFlow.

---

# 106. HERO

Preferred structure:

```text
Statement
+
Supporting explanation
+
Primary CTA
+
Secondary action
+
Visual storytelling
```

Avoid generic:

```text
Huge heading
+
gradient blob
+
three floating cards
```

---

# 107. HERO VISUALS

Hero imagery should communicate:

- intelligent project building
- planning
- mentorship
- structured workflows
- product intelligence

Avoid generic office stock photography.

---

# 108. PUBLIC FEATURE SECTIONS

Use varied editorial rhythm:

```text
Statement
 ↓
Explanation
 ↓
Visual
 ↓
Evidence
```

Do not repeat identical card grids.

---

# 109. LOGIN

Login is a distinct composition using the same system.

Priorities:

- trust
- focus
- clarity
- brand recognition

Do not allow marketing visuals to compete with authentication.

---

# 110. ONBOARDING

Onboarding should feel:

- guided
- progressive
- reassuring
- intelligent

Use progressive disclosure rather than overwhelming forms.

---

# 111. ASSESSMENT

Assessment should prioritize:

- question comprehension
- focus
- progress
- confidence
- low distraction

Do not turn the assessment interface into a decorative dashboard.

---

# 112. BLUEPRINT

Blueprint is a high-information artifact.

Use:

- structured sections
- readable hierarchy
- version information
- generation status
- validation state
- QA state

---

# 113. PROJECT CHANGE

Project changes must visually communicate:

```text
What changed?
Why?
What is affected?
What will regenerate?
What requires review/approval?
```

Do not silently represent a major project mutation as an ordinary save.

---

# 114. MENTOR NOTES

Where note visibility differs, the visual language must communicate that distinction clearly.

Private mentor notes must not look identical to student-visible feedback.

---

# 115. GOVERN / ADMIN

GOVERN may be denser and more technical.

It must not become:

- cyberpunk
- hacker-themed
- neon
- terminal cosplay

The visual tone remains Soft Intelligence.

---

# 116. BUILD / STUDENT

BUILD should emphasize:

- progress
- next action
- learning
- project execution
- personal context

No separate color theme.

---

# 117. SUPERVISE / MENTOR

SUPERVISE should emphasize:

- students
- groups
- project health
- risk
- intervention
- progress

No separate color theme.

---

# 118. GOVERN / ADMIN

GOVERN should emphasize:

- observability
- auditability
- system health
- AI quality
- cost
- security
- investigations

No separate color theme.

---

# 119. ROLE DIFFERENTIATION RULE

Differentiate roles through:

- information hierarchy
- navigation
- density
- terminology
- actions
- data visualization

Never through completely different:

- colors
- typography
- shells
- card systems

---

# 120. RESPONSIVE BREAKPOINTS

Use these implementation defaults:

```text
Mobile: < 768px
Tablet: 768–1199px
Desktop: ≥ 1200px
```

These are default system breakpoints and may be tuned where actual component geometry requires it.

Do not create arbitrary breakpoints for individual pages.

---

# 121. DESKTOP BEHAVIOR

Prioritize:

- information density
- persistent context
- multi-column composition
- full navigation
- efficient tables

---

# 122. TABLET BEHAVIOR

Prioritize:

- adaptive columns
- preserved context
- selective stacking
- reduced horizontal padding

---

# 123. MOBILE BEHAVIOR

Prioritize:

- focused workflows
- progressive disclosure
- touch interaction
- prioritized information
- drawer navigation

---

# 124. TOUCH TARGETS

Interactive targets should generally provide at least:

```text
44 × 44px
```

touch area even if the visible icon is smaller.

---

# 125. RESPONSIVE INFORMATION PRIORITY

When space decreases, hide/reduce in this order:

```text
Decorative information
↓
Secondary metadata
↓
Secondary actions
↓
Secondary content
```

Primary content must survive.

---

# 126. MOBILE FORMS

Forms should:

- stack logically
- maintain readable labels
- preserve errors
- maintain comfortable touch targets
- avoid cramped multi-column arrangements

---

# 127. MOBILE HERO

Reduce:

- display typography
- decorative imagery
- horizontal complexity

Preserve:

- statement
- purpose
- CTA
- brand identity

---

# 128. ACCESSIBILITY

All screens must support:

- keyboard access
- visible focus
- readable contrast
- semantic hierarchy
- accessible names
- non-color status communication
- reduced motion

---

# 129. FOCUS

Interactive controls must have a visible focus state.

Proposed baseline:

```text
2px outer focus ring
```

using the accessible accent/focus token.

Never remove focus indication.

---

# 130. CONTRAST

Do not weaken text opacity until content becomes difficult to read.

Tertiary text must not be used for essential information.

---

# 131. ACCESSIBLE STATUS

Do not communicate:

```text
green = success
red = error
```

alone.

Use:

```text
icon/indicator + text + color
```

where practical.

---

# 132. IMAGE ACCESSIBILITY

Meaningful images require appropriate alternative descriptions.

Decorative images should not create unnecessary screen-reader noise.

---

# 133. DOCUMENT ACCESSIBILITY

Reading interfaces must preserve:

- heading hierarchy
- link distinction
- readable line length
- keyboard access
- code readability

---

# 134. SEARCH

Global search should feel:

- fast
- structured
- keyboard-friendly
- role-aware
- authorization-aware

Result presentation should clearly identify resource type and relevance.

---

# 135. NOTIFICATIONS

Notifications should communicate:

- event
- source
- timestamp
- read/unread
- action/deep link where available

Unread indication must be subtle.

---

# 136. ACTIVITY

Activity entries should communicate:

```text
Actor
+
Action
+
Resource
+
Timestamp
```

Activity is not visually interchangeable with audit logs.

---

# 137. STATUS VOCABULARY

Use domain-defined status terms consistently.

Do not casually interchange terms such as:

- Done
- Complete
- Finished
- Closed
- Resolved

when they have different domain meanings.

---

# 138. CONTENT REALISM

Generated screens must use realistic GrowFlow language.

Prefer:

- Project Blueprint
- Project Health
- Milestone Progress
- Assessment Result
- AI Execution
- Risk Level
- Generation Status

Avoid:

- Lorem ipsum
- Test Project
- random placeholder users
- meaningless percentages

---

# 139. DATA REALISM

Mock data must be internally coherent.

Example:

A project at 75% completion should not randomly contain milestone/task data that contradicts that state unless the discrepancy is intentional and meaningful.

---

# 140. INTERACTION REALISM

A control's visual affordance must match its actual intended behavior.

Do not visually imply unsupported functionality.

---

# 141. STATE REALISM

Do not visually represent contradictory states simultaneously.

Example:

A blueprint cannot visually communicate both:

```text
Generating
```

and:

```text
Approved
```

at the same time.

---

# 142. REFERENCE IMAGE POLICY

Provided visual references are:

> **visual evidence and inspiration, not literal templates.**

Use their useful:

- composition
- rhythm
- hierarchy
- interaction ideas
- density
- visual treatment

but synthesize them into GrowFlow.

Do not copy another product's branding or exact screen.

---

# 143. FIGMA POLICY

If a GrowFlow `.fig` file is supplied:

- use its approved components
- use its approved typography
- use its approved colors
- use its approved spacing
- use its approved relationships

The Figma file must remain consistent with this DESIGN.md.

---

# 144. CODE POLICY

If frontend code/components are supplied:

Design around the existing component vocabulary whenever practical.

Do not generate visually attractive designs that require unnecessary architectural rewrites.

---

# 145. LOGO POLICY

Use the supplied GrowFlow logo assets.

Never:

- distort
- stretch
- recolor arbitrarily
- add glow
- add bevels
- add shadows
- redesign

the logo.

---

# 146. FONT POLICY

Use the supplied **Manrope** font files.

Do not substitute another font when Manrope is available.

Do not silently introduce:

- Inter
- Poppins
- Roboto
- Arial
- other generic system fonts

for primary product typography.

A monospace font is permitted only for code/technical content.

---

# 147. IMAGE POLICY

Use designated GrowFlow assets where supplied.

Do not assume images appearing in inspiration screenshots are GrowFlow assets.

---

# 148. COMPONENT CONSISTENCY

The same conceptual component must look and behave like the same component everywhere.

Examples:

- Task row
- Project header
- Status badge
- AI execution indicator
- Table
- Modal
- Sidebar item
- Notification item

---

# 149. PAGE CONSISTENCY

Pages must share:

- typography
- spacing
- controls
- shell
- interaction conventions
- status language
- responsive behavior

---

# 150. DESIGN DECISION DEFAULT

When Stitch encounters an unspecified visual decision:

1. reuse an established GrowFlow pattern
2. prefer simplicity
3. preserve accessibility
4. preserve consistency
5. preserve restrained visual language
6. avoid introducing a new visual system

---

# 151. WHAT STITCH MUST NOT INVENT

Do not invent:

- new brand colors
- new fonts
- new role themes
- alternate navigation
- alternate shell
- logo treatments
- unrelated visual language
- unsupported backend workflows
- fake AI states
- fake progress
- unsupported controls

---

# 152. PUBLIC / APPLICATION BALANCE

Public:

> expressive + editorial

Authenticated:

> restrained + operational

Dense areas:

> restrained + information-dense

All remain one GrowFlow product.

---

# 153. VISUAL PRIORITY MATRIX

| Context | Primary visual priority |
|---|---|
| Landing | Story |
| Features | Explanation |
| Documentation | Readability |
| Login | Trust |
| Student Dashboard | Progress |
| Project Workspace | Execution |
| Mentor Dashboard | Supervision |
| Admin Dashboard | Governance |
| AI Mentor | Intelligence |
| AI Observatory | Transparency |
| Documents | Reading |
| Tables | Scanability |

---

# 154. DESIGN REVIEW — BRAND

Before approval:

- GrowFlow identity recognizable
- Soft Intelligence visible
- no competing design language
- logo used correctly
- typography consistent

---

# 155. DESIGN REVIEW — TYPOGRAPHY

Verify:

- Manrope is used
- hierarchy follows scale
- weights are intentional
- metadata remains readable
- line lengths are reasonable
- display type is not overused

---

# 156. DESIGN REVIEW — COLOR

Verify:

- warm neutral foundation
- one restrained accent
- semantic colors meaningful
- no arbitrary colors
- dark theme works independently
- AI treatment is subtle

---

# 157. DESIGN REVIEW — LAYOUT

Verify:

- correct density
- consistent spacing
- strong hierarchy
- correct container behavior
- no unnecessary card nesting

---

# 158. DESIGN REVIEW — COMPONENTS

Verify:

- existing patterns reused
- states are represented
- controls are consistent
- iconography is consistent
- component geometry is coherent

---

# 159. DESIGN REVIEW — AI

Verify:

- no neon
- no fake typing
- no fake progress
- no decorative AI effects
- actual execution states represented

---

# 160. DESIGN REVIEW — RESPONSIVE

Verify:

- desktop
- tablet
- mobile
- touch targets
- mobile navigation
- information prioritization

---

# 161. DESIGN REVIEW — ACCESSIBILITY

Verify:

- contrast
- focus
- keyboard behavior
- semantic hierarchy
- non-color state indicators
- reduced motion

---

# 162. DESIGN REVIEW — IMPLEMENTABILITY

Verify:

- design can use existing components
- no unnecessary new primitives
- page behavior can map to backend contracts
- no unsupported product behavior is implied

---

# 163. ABSOLUTE VISUAL ANTI-PATTERNS

Do not generate:

- generic SaaS template aesthetics
- excessive glassmorphism
- neon AI
- rainbow role themes
- card-everything layouts
- excessive shadows
- giant pills
- unnecessary gradients
- decorative charts
- animated backgrounds
- fake AI typing
- excessive parallax
- stock-heavy storytelling
- tiny unreadable metadata
- inconsistent icon families
- inconsistent radii
- dark-mode inversion
- fake data
- fake progress

---

# 164. PUBLIC WEBSITE ANTI-PATTERNS

Do not use:

- generic startup gradient backgrounds
- giant floating blobs
- excessive 3D illustrations
- repetitive card grids
- generic stock-office hero images
- heavy parallax
- oversized decorative badges

---

# 165. APPLICATION ANTI-PATTERNS

Do not use:

- excessive floating cards
- giant page titles
- oversized empty whitespace in dense workflows
- unnecessary animations
- decorative dashboard widgets
- excessive color

---

# 166. ADMIN ANTI-PATTERNS

Do not make GOVERN resemble:

- hacker terminals
- cyber-security movies
- neon observability tools
- command-center fantasy dashboards

Technical does not mean visually aggressive.

---

# 167. AI ANTI-PATTERNS

Never use:

- neon purple AI
- glowing blue chat
- cyberpunk panels
- neural-network background animation
- floating robot graphics
- fake token counters
- fake typing
- fake percentages
- excessive AI gradients

---

# 168. DECORATION RULE

Every decorative element should have a reason.

If removing it does not reduce:

- comprehension
- hierarchy
- storytelling
- usability
- brand recognition

then it should probably be removed.

---

# 169. GRADIENT RULE

Gradients are allowed only for restrained:

- hero atmosphere
- visual depth
- editorial storytelling

Never use large loud gradients as the default application background.

---

# 170. GLASS RULE

Glass effects are not part of the default GrowFlow language.

Do not use:

- translucent cards everywhere
- blurred panels everywhere
- glass navigation
- glowing glass borders

---

# 171. SHADOW RULE

Shadows communicate elevation.

They do not decorate surfaces.

---

# 172. CARD RULE

If content is clear without a card, consider leaving it on the page surface.

---

# 173. PILL RULE

Pills are reserved primarily for:

- statuses
- tags
- compact selections

Do not make the entire navigation or interface pill-shaped.

---

# 174. DESIGN GENERATION PRIORITY

When generating a screen, prioritize:

```text
1. Correct information hierarchy
2. Correct layout
3. Correct typography
4. Correct component language
5. Correct states
6. Correct color
7. Correct spacing
8. Responsive behavior
9. Accessibility
10. Decorative refinement
```

---

# 175. PAGE-SPECIFIC PROMPT CONTRACT

Future page prompts should reference this DESIGN.md instead of repeating the complete design system.

A page prompt should specify:

- Page ID
- Page name
- Route
- Role
- Purpose
- Entry context
- Layout
- Data
- Components
- Actions
- States
- Responsive behavior
- Accessibility considerations
- Page-specific imagery
- Special requirements

---

# 176. STITCH OUTPUT EXPECTATION

Every generated GrowFlow screen should be:

- visually coherent
- production-oriented
- realistic
- responsive
- accessible
- implementable
- consistent with this design system

---

# 177. IMPLEMENTATION COMPATIBILITY

Visual designs should map naturally to:

```text
Design Tokens
      ↓
Components
      ↓
Patterns
      ↓
Page
```

If a design requires a new reusable primitive, document why it is required before treating it as part of the system.

---

# 178. STITCH DECISION PRIORITY

When instructions conflict visually:

```text
Frozen GrowFlow architecture
        ↓
This DESIGN.md
        ↓
Provided approved Figma/components
        ↓
Provided GrowFlow references
        ↓
Page-specific design requirements
        ↓
Stitch visual interpretation
```

Stitch must not use visual creativity to override higher-level constraints.

---

# 179. FINAL STITCH MASTER INSTRUCTION

When generating GrowFlow:

> Create a mature, production-oriented interface using the GrowFlow Soft Intelligence design system. Use the provided Manrope font, brand assets, Figma system, code/components, and visual references. Preserve the warm-light default and soft-charcoal dark counterpart. Use muted neutral surfaces, one restrained olive accent, semantic status colors, quiet cards, dense integrated tables, editorial public storytelling, operational authenticated layouts, and a slightly deeper but non-neon AI treatment. Preserve consistent typography, spacing, component geometry, responsive behavior, accessibility, and realistic state representation. Do not invent new visual systems, role themes, fonts, brand colors, navigation systems, unsupported functionality, fake AI progress, or decorative UI patterns that conflict with this specification.

---

# 180. FINAL ABSOLUTE DO / DO NOT

## DO

- use Manrope
- use the canonical weights
- use the defined typography scale
- use the canonical color tokens
- use warm light by default
- support soft charcoal dark
- use one muted olive accent
- use semantic colors meaningfully
- use quiet surfaces
- use restrained borders
- use integrated tables
- use contextual editorial imagery
- use subtle physical motion
- use deeper but calm AI surfaces
- use realistic states
- support accessibility
- support responsive layouts
- reuse components
- preserve visual consistency

## DO NOT

- invent colors
- invent fonts
- invent role themes
- use neon AI
- use fake typing
- fabricate progress
- fabricate data
- overuse gradients
- overuse glassmorphism
- overuse cards
- overuse shadows
- use giant pills
- create decorative charts
- create unrelated navigation
- copy reference websites literally
- sacrifice usability for visual novelty
- create designs that require unnecessary architecture changes

---

# 181. CANONICAL TOKEN QUICK REFERENCE

## Typography

```text
Font: Manrope

400 Regular
500 Medium
600 SemiBold
700 Bold
800 ExtraBold

Body: 15px / 1.55
Body Small: 14px / 1.50
Caption: 13px / 1.45
Metadata: 12px / 1.40

H1: 40px / 1.15 / 700
H2: 32px / 1.20 / 700
H3: 26px / 1.25 / 700
H4: 22px / 1.30 / 600
H5: 18px / 1.35 / 600
H6: 16px / 1.40 / 600
```

## Light

```text
Background:       #F7F7F4
Surface:          #FFFFFF
Secondary:        #F2F2EE
Tertiary:         #EDEDE8

Text Primary:     #1C1C1A
Text Secondary:   #5F625D
Text Tertiary:    #858780

Border Subtle:    #E5E5DF
Border Standard:  #D9D9D2
Border Strong:    #C9C9C0

Accent:           #6F7F63
Accent Hover:     #607055
Accent Active:    #526149
Accent Soft:      #E9EDE5
Accent Border:    #B8C2AE

Success:          #477A5A
Success Soft:     #E7F0E9
Warning:          #9A7135
Warning Soft:     #F5EDDD
Danger:           #A6534D
Danger Soft:      #F6E8E6
Info:             #54718A
Info Soft:        #E8EEF3

AI:               #5F6B7A
AI Surface:       #ECEEF1
AI Border:        #D4D8DD
AI Emphasis:      #424D5A
```

## Dark

```text
Background:       #171816
Secondary:        #1E201D
Tertiary:         #262824

Surface:          #20221F
Elevated:         #272925
Muted:            #2D302B

Text Primary:     #F0F1EC
Text Secondary:   #C2C5BD
Text Tertiary:    #91958C

Border Subtle:    #30332E
Border Standard:  #3A3D37
Border Strong:    #4A4E47

Accent:           #9AAA8D
Accent Hover:     #A8B79C
Accent Active:    #B7C5AB
Accent Soft:      #2B3328

Success:          #7FB18C
Warning:          #D0A962
Danger:           #D27A72
Info:             #88A8C0

AI Surface:       #292D30
AI Border:        #3C4246
AI Emphasis:      #A9B2BB
```

## Geometry

```text
Base spacing:     8px
Input:            40px
Large input:      48px
Compact input:    36px
Button:           40px
Large CTA:        48px
Compact button:   32px

Navbar:           64px authenticated
Sidebar:          248px default
Sidebar collapsed:72px

Radius:
XS 4px
S 6px
M 8px
L 12px
XL 16px
2XL 20px
Full 9999px

Mobile breakpoint: <768px
Tablet: 768–1199px
Desktop: ≥1200px
```

---

# 182. FINAL DESIGN PRINCIPLE

The defining GrowFlow rule is:

> **Nothing screams; hierarchy still exists.**

The interface should not demand attention through decoration.

It should earn attention through:

- clarity
- hierarchy
- intelligent information
- meaningful motion
- precise typography
- restrained color
- contextual visuals
- calm confidence

---

# 183. DOCUMENT STATUS

**FROZEN / AUTHORITATIVE**

This document is the compact visual/design specification for Stitch and frontend visual implementation.

The exact values in this document are canonical for the current GrowFlow design system.

Any future change to:

- fonts
- font weights
- typography sizes
- colors
- spacing
- radii
- navigation dimensions
- component geometry
- motion rules
- responsive defaults
- visual identity

must be treated as a design-system change and documented before being propagated to future pages.

---

# 184. RELATIONSHIP TO GROWFLOW PHASES

```text
Phase 01
Frontend Inventory
        ↓
Phase 02
Information Architecture
        ↓
Phase 03
Soft Intelligence Visual Direction
        ↓
Phase 04
Frontend Documentation
        ↓
Phase 05
Application & Integration Architecture
        ↓
Phase 06
Frontend Foundation
        ↓
DESIGN.md
Compact Stitch Visual Authority
        ↓
Page-by-Page Design
        ↓
Frontend Implementation
```

This DESIGN.md must remain consistent with the frozen architecture above.

---

# 185. FINAL FREEZE STATEMENT

**GrowFlow DESIGN.md v1.0 is FROZEN.**

It establishes the visual foundation that Stitch and subsequent frontend implementation must follow.

The next design work should focus on **page-specific composition and behavior**, not re-inventing the global GrowFlow visual system.
