# GrowFlow — Stitch Instructions

**Document:** `Stitch_Instructions.md`  
**Version:** 1.0  
**Status:** FOUNDATION / READY FOR STITCH USE  
**Purpose:** Reusable, implementation-oriented instruction library for generating GrowFlow interfaces in Stitch  
**Parent authority:** `GrowFlow_Master_Design.md`  
**Applies to:** Public website, authentication, BUILD, SUPERVISE, GOVERN, shared authenticated surfaces, workflows, AI interfaces, responsive layouts, and visual refinement

---

# 00. Document Purpose

This document converts the GrowFlow Master Design System into **operational instructions for Stitch**.

The Master Design defines:

> What GrowFlow looks like.

This document defines:

> How Stitch must be instructed to produce GrowFlow interfaces consistently.

The goal is to minimize repeated prompt content while maximizing:

- visual consistency
- design precision
- brand consistency
- component consistency
- responsive quality
- accessibility
- visual hierarchy
- AI visual restraint
- page-to-page continuity

---

# 01. Authority Model

Stitch must follow this authority order:

```text
Product / Domain Architecture
        ↓
GrowFlow Master Design
        ↓
Design Tokens
        ↓
Core Component System
        ↓
Application Shell
        ↓
Page Specification
        ↓
Stitch Instructions
        ↓
Reference Images
```

When instructions conflict:

1. Product meaning wins for functionality.
2. Master Design wins for visual language.
3. Design tokens win for exact values.
4. Component system wins for reusable component behavior.
5. Page specification wins for page-specific composition.
6. Reference images provide inspiration only.

Stitch must not invent a competing design system.

---

# 02. Master Stitch Directive

Use this directive at the beginning of a new Stitch generation when the tool requires a complete foundation statement.

```text
Design this interface as part of GrowFlow's unified visual system.

GrowFlow's design identity is "Soft Intelligence":
calm on the surface, powerful underneath.

Use Manrope as the canonical typeface for all normal UI and editorial content.
Use JetBrains Mono only for explicitly technical content such as code, logs,
IDs, hashes, API payloads, traces, file paths, JSON, YAML, and similar machine-oriented data.

Use GrowFlow's warm neutral light theme as the default:
Background #F7F7F4
Surface #FFFFFF
Secondary #F2F2EE
Tertiary #EDEDE8

Primary text:
#1C1C1A
Secondary text:
#5F625D
Tertiary text:
#858780

Primary accent:
#6F7F63
Hover:
#607055
Active:
#526149
Soft:
#E9EDE5
Border:
#B8C2AE

Use the canonical semantic colors and AI palette from the GrowFlow Master Design.

Keep surfaces quiet, cards selective, tables integrated and dense,
and hierarchy primarily typographic and spatial.

Use one unified GrowFlow identity across BUILD, SUPERVISE, and GOVERN.
Do not create separate role color themes.

AI interfaces should use a slightly deeper neutral treatment,
not neon, cyberpunk, holographic, or glowing visual language.

Public pages may be editorial and expressive.
Authenticated workplace pages should be calm, dense, structured, and productive.

Use subtle physical motion only.
Prefer the GrowFlow "Float → Settle" interaction language where motion is appropriate.

Respect responsive behavior for mobile, tablet, and desktop.
Respect accessibility, keyboard interaction, visible focus, semantic hierarchy,
touch targets, contrast, and reduced motion.

Do not invent new fonts, brand colors, role themes, decorative systems,
or unrelated component styles.
```

---

# 03. Foundation Loading Instruction

When creating a new page:

```text
Use the GrowFlow Master Design as the visual source of truth.

Use the GrowFlow Core Component System for reusable components.

Use the GrowFlow Application Shell for global navigation and authenticated structure.

Use the page-specific requirements supplied in this prompt for page composition.

Treat all supplied reference images as inspiration for composition and hierarchy,
not as templates to copy literally.
```

---

# 04. Brand Instruction

```text
Preserve GrowFlow's identity as Soft Intelligence.

The visual identity should communicate:
growth,
flow,
progression,
structure,
mentorship,
execution,
clarity,
and intelligence.

Use the Connected Flow + Abstract G brand direction.

The brand should feel:
calm,
intelligent,
human,
structured,
modern,
trustworthy,
and quietly sophisticated.

Do not use generic AI imagery, brains, robots, circuit boards,
neon technology, cyberpunk effects, or literal growth clichés.
```

---

# 05. Logo Instruction

```text
Use the approved GrowFlow logo asset.

The logo consists of the GrowFlow wordmark and the Connected Flow / Abstract G mark.

Use the provided asset rather than recreating the logo with ordinary text.

Preserve proportions and clear space.

Do not:
stretch,
skew,
rotate,
glow,
arbitrarily recolor,
add gradients,
or create role-specific logo variants.

Use monochrome variants where required by the background.
```

---

# 06. Typography Instruction

```text
Typography is fixed.

Use Manrope for:
headings,
body,
navigation,
buttons,
forms,
metadata,
dashboards,
tables,
documents,
AI responses,
workflows,
public marketing,
BUILD,
SUPERVISE,
GOVERN,
and all ordinary interface content.

Use the canonical GrowFlow typography scale.

Use:
400 Regular,
500 Medium,
600 SemiBold,
700 Bold,
800 ExtraBold.

Use JetBrains Mono only for:
code,
JSON,
YAML,
XML,
SQL,
technical logs,
execution IDs,
trace IDs,
hashes,
commit SHAs,
file paths,
API payloads,
and other explicitly technical representations.

Do not introduce any third UI font.
Do not use handwritten fonts for interface text.
Do not use serif or decorative fonts.
```

---

# 07. Typography Hierarchy Instruction

```text
Use typography as the primary hierarchy mechanism.

Do not manufacture hierarchy with excessive color, shadows, cards, or gradients.

Use:
Display XL 64px / 1.05 / 700 / -0.03em
Display L 56px / 1.08 / 700 / -0.03em
Display M 48px / 1.10 / 700 / -0.025em
H1 40px / 1.15 / 700 / -0.02em
H2 32px / 1.20 / 700 / -0.015em
H3 26px / 1.25 / 700 / -0.01em
H4 22px / 1.30 / 600 / -0.005em
H5 18px / 1.35 / 600
H6 16px / 1.40 / 600
Body Large 17px / 1.60 / 400
Body 15px / 1.55 / 400
Body Small 14px / 1.50 / 400
Caption 13px / 1.45 / 400
Metadata 12px / 1.40 / 500

Use larger display styles primarily for public/editorial compositions.
Use compact hierarchy for dense workplace screens.
```

---

# 08. Color Instruction

```text
Use only the approved GrowFlow palette.

Default light appearance:
warm off-white background,
white primary surfaces,
soft neutral secondary surfaces,
dark warm-neutral text,
muted sage accent.

Use the primary accent sparingly.

Accent should indicate:
primary action,
selection,
meaningful progress,
controlled emphasis,
or interaction.

Do not use accent as generic decoration.

Do not invent additional brand colors.
Do not create rainbow UI.
Do not make every element colorful.
```

---

# 09. Dark Mode Instruction

```text
When dark mode is required, use GrowFlow's soft charcoal counterpart.

Do not invert the light theme mechanically.

Use:
Background #171816
Secondary #1E201D
Tertiary #262824
Surface #20221F
Elevated #272925
Muted #2D302B

Primary text #F0F1EC
Secondary text #C2C5BD
Tertiary text #91958C

Border subtle #30332E
Border standard #3A3D37
Border strong #4A4E47

Accent #9AAA8D
Hover #A8B79C
Active #B7C5AB
Soft #2B3328

Preserve the same visual identity and hierarchy.
```

---

# 10. AI Color Instruction

```text
AI should feel slightly deeper than ordinary GrowFlow surfaces.

Light:
AI #5F6B7A
AI Surface #ECEEF1
AI Border #D4D8DD
AI Emphasis #424D5A

Dark:
AI Surface #292D30
AI Border #3C4246
AI Emphasis #A9B2BB

Do not use neon purple, cyan glow, holographic effects,
cyberpunk gradients, glowing particles, or "AI magic" decoration.
```

---

# 11. Surface Instruction

```text
Use quiet neutral surfaces.

Hierarchy should generally be:
page background
→ secondary/tertiary grouping
→ primary surface
→ elevated surface.

Keep adjacent surfaces close in tone.

Use borders and spacing before shadows.

Do not turn every content block into a floating white card.
```

---

# 12. Card Instruction

```text
Cards are functional grouping devices.

Use cards only when content represents:
an independent module,
a summary,
a meaningful grouping,
an actionable object,
or a visually isolated unit.

Prefer sections, dividers, whitespace, and integrated rows
when a card is unnecessary.

Cards should be quiet:
subtle surface,
restrained border,
minimal elevation,
consistent radius.

Do not use card-everything layouts.
```

---

# 13. Radius Instruction

```text
Use only canonical radii:
4px,
6px,
8px,
12px,
16px,
20px,
9999px.

Use 9999px only for genuinely pill-shaped semantic elements.

Do not make every control a pill.

Default controls generally use 6–8px.
Larger surfaces generally use 12–16px.
```

---

# 14. Elevation Instruction

```text
Use minimal elevation.

L0:
no shadow.

L1:
0 1px 2px rgba(0,0,0,0.04)

L2:
0 4px 12px rgba(0,0,0,0.06)

L3:
0 12px 32px rgba(0,0,0,0.08)

Prefer L0 and L1.

Use L2/L3 only for meaningful floating surfaces,
dialogs, major overlays, or carefully justified compositions.

Do not use heavy shadows to create hierarchy.
```

---

# 15. Spacing Instruction

```text
Use the canonical spacing scale:

2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128px.

Use spacing to communicate relationships.

Tight relationships:
2–12px.

Component grouping:
16–24px.

Section grouping:
32–48px.

Major composition:
64px and above.

Do not invent arbitrary spacing values.
```

---

# 16. Layout Instruction

```text
Build layouts around clear alignment and hierarchy.

Use:
shared content edges,
consistent containers,
intentional grid,
predictable spacing,
and meaningful grouping.

Use grid for dashboards and structured data.

Use stacks for:
forms,
documents,
chat,
sequential workflows.

Do not force every page into a card grid.
```

---

# 17. Public Website Instruction

```text
Public GrowFlow pages should be more expressive than authenticated pages.

Use:
editorial composition,
larger typography,
contextual imagery,
controlled asymmetry,
generous whitespace,
clear storytelling,
and subtle motion.

Do not use generic SaaS templates.

The public website should feel like a product with a distinct visual identity,
not a dashboard marketing wrapper.
```

---

# 18. Hero Instruction

```text
Hero composition should communicate a clear statement and visual story.

Prioritize:
headline,
supporting message,
primary CTA,
secondary CTA,
visual evidence,
and brand identity.

Use contextual or editorial imagery where appropriate.

Avoid:
generic gradient blobs,
generic AI illustrations,
excessive dashboard mockups,
floating UI clutter,
neon effects,
and overly busy compositions.

Hero imagery should support the story rather than compete with the headline.
```

---

# 19. Feature Section Instruction

```text
Each feature section should have:
a clear feature statement,
supporting explanation,
meaningful visual evidence,
and an appropriate action if needed.

Do not make every feature identical.

Vary composition while preserving the same design system.

Use actual product UI when a feature is best demonstrated through interface.
Use editorial imagery when the feature is better communicated through context.
```

---

# 20. Documentation Page Instruction

```text
Documentation should feel editorial and technically credible.

Use:
strong heading hierarchy,
readable prose,
structured navigation,
code presentation,
metadata,
search where specified,
and contextual examples.

Do not overdecorate technical content.

Use Manrope for prose and JetBrains Mono for actual technical artifacts.
```

---

# 21. Authentication Instruction

```text
Authentication uses a distinct composition within the same GrowFlow system.

Prioritize:
clarity,
trust,
focus,
low friction,
accessibility,
and brand identity.

Use restrained visual support.

Do not turn sign-in into a marketing page.

Do not introduce a different font, palette, radius language,
or visual system.
```

---

# 22. Onboarding Instruction

```text
Onboarding may use more visual explanation than ordinary workplace screens.

Use progressive disclosure.

Clearly communicate:
current step,
purpose,
progress,
required action,
and next action.

Keep cognitive load low.

Use imagery only when it improves understanding or motivation.
```

---

# 23. BUILD / Student Instruction

```text
BUILD is the Student workspace.

Use the unified GrowFlow visual system.

Prioritize:
project progression,
tasks,
milestones,
roadmap,
blueprint,
assessment,
risks,
documents,
AI Mentor,
feedback,
and actionable project state.

The visual tone should support:
learning,
building,
confidence,
clarity,
and forward movement.

Do not create a separate student color theme.
```

---

# 24. SUPERVISE / Mentor Instruction

```text
SUPERVISE is the Mentor workspace.

Prioritize:
students,
groups,
projects,
project definitions,
project instances,
risk,
activity,
notes,
help requests,
and oversight.

The interface may be denser than BUILD.

Keep the tone:
calm,
structured,
supportive,
operational.

Do not create a separate mentor color theme.
```

---

# 25. GOVERN / Admin Instruction

```text
GOVERN is the Admin workspace.

Prioritize:
observability,
system health,
AI executions,
cost,
usage,
RAG,
documents,
security,
audit,
investigations,
and analytics.

Use higher information density where useful.

Prefer:
integrated tables,
metrics,
charts,
filters,
trace views,
and structured operational layouts.

Avoid editorial photography and decorative UI where it does not add meaning.

Do not create a separate admin color theme.
```

---

# 26. Dashboard Instruction

```text
Dashboards are visual data instruments.

Do not create a grid of identical metric cards.

Establish hierarchy:
key state
→ key metric
→ trend
→ breakdown
→ detail
→ action.

Use charts only when they communicate real data.

Avoid decorative charts.

Use restrained color encoding.
```

---

# 27. Table Instruction

```text
Tables should feel integrated into the application.

Use:
clear headers,
aligned columns,
readable row density,
subtle separators,
semantic status,
and predictable actions.

Avoid excessive borders and decorative striping.

Do not shrink text to fit excessive columns.

For mobile, transform the representation intelligently
while preserving the information meaning.
```

---

# 28. Form Instruction

```text
Forms should be precise and calm.

Every input must have:
a visible accessible label,
clear value area,
focus state,
validation state,
disabled state when relevant,
and helper/error text when needed.

Use:
standard input 40px,
large input 48px,
compact input 36px.

Use 6px radius for standard inputs unless the component specification requires otherwise.
```

---

# 29. Button Instruction

```text
Use a clear button hierarchy.

Primary:
GrowFlow Sage filled.

Secondary:
neutral surface/border.

Tertiary:
low-emphasis text/button.

Destructive:
semantic danger treatment.

Standard:
40px height,
16px horizontal padding,
8px radius,
14px / 600.

Large CTA:
48px height,
20px horizontal padding,
8px radius,
15–16px / 600.

Compact:
32px height,
12px horizontal padding,
6px radius,
13px / 600.

Do not make every button primary.
```

---

# 30. Navigation Instruction

```text
Navigation is quiet and predictable.

Authenticated TopNav:
64px.

Public TopNav:
68–76px.

Sidebar:
248px default,
240–264px acceptable range,
72px collapsed.

Sidebar items:
36–40px height,
8–12px horizontal padding,
18–20px icon,
10–12px icon/text gap,
6–8px radius.

Use subtle selected states.

Do not use glowing active navigation.
```

---

# 31. Workplace Selector Instruction

```text
Represent the three GrowFlow workplaces:

BUILD
SUPERVISE
GOVERN

Use one unified visual system.

The selector should feel like a workspace switcher,
not a theme switcher.

Do not assign separate colors to each role.
```

---

# 32. Search Instruction

```text
Global search should feel integrated into the shell.

Represent:
query,
resource identity,
resource type,
context,
relevance where applicable,
loading,
empty,
error,
and restricted-access behavior.

Keep search results visually scannable.
```

---

# 33. Notification Instruction

```text
Notifications should be concise and actionable.

Use visual priority according to actual importance.

Do not make every notification visually urgent.

Use:
icon,
text,
timestamp where useful,
status,
and canonical destination.

Avoid excessive decorative notification cards.
```

---

# 34. AI Mentor Instruction

```text
AI Mentor is a native GrowFlow capability.

Use:
GrowFlow typography,
GrowFlow spacing,
restrained AI surfaces,
clear conversational hierarchy,
project context,
and meaningful execution states.

Do not use generic chatbot styling.

Avoid excessive chat bubbles.

Distinguish clearly:
user message,
AI response,
tool/system state,
execution progress,
validation,
completion,
and failure.
```

---

# 35. AI Generation Instruction

```text
For AI generation workflows, visually communicate the real execution state.

Possible states:
QUEUED
RUNNING
COMPLETED
FAILED
CANCELLED
RETRYING

Show progress only when the system provides meaningful progress.

Never fabricate percentages or stages.

Do not show "complete" before actual completion and validation.
```

---

# 36. AI Streaming Instruction

```text
Streaming should feel calm and purposeful.

Do not simulate typing simply to look intelligent.

Use actual streaming state when available.

Keep high-frequency technical events out of the primary visual hierarchy.

Show meaningful state changes:
started,
progressing,
completed,
failed,
reconnecting.

Preserve the final canonical result.
```

---

# 37. Blueprint Instruction

```text
Blueprint interfaces should communicate:
project identity,
generation state,
version,
sections,
validation,
QA/Judge status,
and available actions.

Treat Blueprint as a first-class product artifact.

Make version and approval state clear.

Do not visually imply approval before approval exists.
```

---

# 38. Assessment Instruction

```text
Assessment is a focused workflow.

Prioritize:
question,
answer controls,
progress,
context,
and next action.

Do not overload the screen with decorative imagery.

Adaptive assessment should communicate progression
without exposing unnecessary implementation details.
```

---

# 39. Roadmap Instruction

```text
Roadmap must communicate temporal structure.

Use:
phases,
milestones,
tasks,
current position,
dependencies where relevant,
and planned/actual distinction where available.

Do not create decorative timelines without meaningful temporal information.
```

---

# 40. Risk Instruction

```text
Risk interfaces should communicate:
severity,
likelihood where applicable,
impact,
status,
mitigation,
ownership,
and affected context.

Use semantic danger/warning treatment only where the state warrants it.

Do not make ordinary risk information visually alarming.
```

---

# 41. Task Instruction

```text
Task interfaces should make the following easy to scan:
title,
status,
priority where applicable,
due date,
owner,
milestone relationship,
and completion.

Do not display every possible metadata field simultaneously.
```

---

# 42. Milestone Instruction

```text
Milestones represent meaningful project checkpoints.

Visually distinguish:
upcoming,
active,
completed,
blocked,
and at-risk where applicable.

Milestones should have stronger hierarchy than ordinary tasks.
```

---

# 43. Document Instruction

```text
Documents are first-class product artifacts.

Prioritize:
reading comfort,
hierarchy,
version,
metadata,
actions,
and navigation.

Use Manrope for prose.
Use JetBrains Mono for technical content.
```

---

# 44. GitHub Instruction

```text
GitHub integration surfaces should remain GrowFlow-native.

Use GitHub identity only where semantically necessary.

Do not let integration branding replace GrowFlow's visual identity.
```

---

# 45. Empty State Instruction

```text
An empty state should answer:
what is empty,
why it may be empty,
and what the user can do next.

Use a simple icon or illustration only when it helps.

Do not overdecorate empty states.
```

---

# 46. Loading Instruction

```text
Choose loading feedback based on the operation.

Known content structure:
use skeletons.

Short indeterminate action:
use spinner or compact progress indicator.

Measurable long-running work:
use real progress.

Do not show generic spinners for every page.
```

---

# 47. Error Instruction

```text
Error states should be calm, specific, and actionable.

Explain:
what happened,
what was affected,
whether anything was saved,
and what the user can do next.

Avoid exposing unnecessary internal implementation details.
```

---

# 48. Success Instruction

```text
Success states should confirm:
what happened,
whether persistence completed,
and what happens next.

Use restrained confirmation.

Do not use excessive celebration or gamified effects.
```

---

# 49. Responsive Master Instruction

```text
Design for three structural ranges:

Mobile <768px
Tablet 768–1199px
Desktop >=1200px

Do not simply scale desktop down.

Mobile is a first-class composition.

Transform:
sidebar → drawer,
multi-column → stacked,
split panes → sequential/contextual views,
dense tables → appropriate mobile representation.

Do not change domain meaning, authorization, or state across breakpoints.
```

---

# 50. Mobile Instruction

```text
Mobile must remain fully usable.

Prioritize:
primary content,
primary action,
navigation,
state,
and essential context.

Use 44×44px effective touch targets.

Do not rely on hover.

Do not hide critical actions simply to preserve desktop composition.
```

---

# 51. Tablet Instruction

```text
Treat tablet as its own composition.

Do not assume desktop automatically works at tablet widths.

Consider:
sidebar behavior,
multi-column collapse,
table density,
content width,
navigation,
and control grouping.
```

---

# 52. Accessibility Instruction

```text
Build accessibility into the visual composition.

Ensure:
semantic headings,
visible focus,
keyboard operation,
accessible names,
labels,
sufficient contrast,
non-color state communication,
adequate touch targets,
reduced-motion support,
and readable dynamic content.

Do not use color as the only status indicator.
```

---

# 53. Focus Instruction

```text
Every interactive element must have a clearly visible focus state.

Focus must work in:
light mode,
dark mode,
dialogs,
drawers,
menus,
tabs,
forms,
AI interfaces,
and navigation.

Do not use an invisible or extremely subtle focus treatment.
```

---

# 54. Reduced Motion Instruction

```text
Respect prefers-reduced-motion.

When reduced motion is active:
remove decorative motion,
minimize transitions,
preserve state visibility,
and preserve functional feedback.

Do not encode essential information solely through animation.
```

---

# 55. Motion Instruction

```text
Motion should feel physically subtle.

Preferred:
short transitions,
soft entrance,
gentle movement,
spatial continuity,
Float → Settle.

Avoid:
bouncing,
constant floating,
aggressive springs,
excessive parallax,
animated backgrounds,
glowing effects,
fake typing,
and continuous decorative motion.
```

---

# 56. Image Instruction

```text
Use imagery as contextual/editorial support.

Images should feel:
human,
calm,
purposeful,
editorial,
natural,
and compositionally controlled.

Avoid:
generic corporate stock,
AI robots,
brains,
circuit boards,
holographic technology,
neon technology,
and overly staged startup imagery.

Do not use an image merely because an empty space exists.
```

---

# 57. Reference Image Instruction

```text
Treat supplied screenshots and references as inspiration.

Extract:
composition,
hierarchy,
density,
spacing rhythm,
interaction pattern,
and visual mood.

Do not copy:
branding,
logos,
proprietary text,
exact colors,
exact layout,
or unrelated typography.

GrowFlow Master Design always wins over a reference image.
```

---

# 58. Product UI Reference Instruction

```text
When a reference shows a dashboard, table, chat interface,
roadmap, or document, use it to understand composition.

Do not reproduce the reference as a fake final product screenshot.

The eventual product UI must be generated from GrowFlow's own component system.
```

---

# 59. Public Image Composition Instruction

```text
Public imagery may use stronger editorial composition.

Prefer:
natural light,
warm neutral environments,
human context,
real project work,
subtle greenery,
calm materials,
structured desks/workspaces,
and authentic creative/technical activity.

Keep the GrowFlow palette visible without forcing every image to be monochrome green.
```

---

# 60. Abstract Visual Instruction

```text
Abstract GrowFlow visuals should express:
flow,
connection,
progression,
growth,
structure,
and continuity.

Prefer simple geometry and restrained movement.

Do not use:
neon gradients,
glowing particles,
generic AI orbs,
complex circuit diagrams,
or decorative 3D blobs.
```

---

# 61. Data Visualization Instruction

```text
Charts must represent real meaning.

Use:
neutral baseline,
GrowFlow accent for primary emphasis,
semantic colors only where semantics exist.

Avoid rainbow palettes.

Preserve readable scales and labels.

Do not create charts merely to fill dashboard space.
```

---

# 62. Metadata Instruction

```text
Metadata must remain subordinate.

Prefer:
12px / 500 for compact metadata,
13px / 400 for captions,
14px / 400 for small supporting content.

Do not make metadata compete with primary content.
```

---

# 63. Status Instruction

```text
Status must be communicated through more than color.

Combine:
label,
icon where useful,
color,
position,
and context.

Do not represent important state only with green, yellow, red, or blue.
```

---

# 64. Overlay Instruction

```text
Dialogs, drawers, popovers, and menus must remain part of the GrowFlow surface system.

Use restrained elevation.

Maintain focus management and accessible names.

Do not create unrelated overlay styling.
```

---

# 65. Modal Instruction

```text
Use modals for focused short actions.

Examples:
confirm delete,
create task,
edit task,
add risk,
assign student,
share.

Do not put long multi-stage workflows inside a small modal.
```

---

# 66. Drawer Instruction

```text
Use drawers for contextual secondary information or mobile navigation.

Drawers should preserve:
context,
focus,
close behavior,
keyboard operation,
and responsive integrity.
```

---

# 67. Workflow Instruction

```text
Long-running or multi-stage workflows should visually expose:
current stage,
completed stages,
next action,
state,
recovery,
and resumability.

Do not visually collapse proposal, processing, validation,
and persistence into one ambiguous "done" state.
```

---

# 68. Project Change Instruction

```text
Project change workflows must visually preserve:

Change Request
→ Impact Analysis
→ Impact Review
→ Regeneration
→ Validation
→ QA/Judge
→ Persisted Change

Do not visually imply that a requested change is already canonical.
```

---

# 69. Versioning Instruction

```text
When a resource is versioned, make version state explicit.

Distinguish:
current,
draft,
generated,
approved,
historical,
superseded.

Do not make multiple versions visually indistinguishable.
```

---

# 70. Long-Running Operation Instruction

```text
Design long-running operations so they remain understandable
if the user:
stays on the page,
navigates away,
returns,
loses connection,
reconnects,
or encounters failure.

Do not depend on browser animation to communicate actual job state.
```

---

# 71. State Truthfulness Instruction

```text
Never visually imply a state that the backend has not confirmed.

Do not show:
completed before completion,
approved before approval,
saved before persistence,
deployed before deployment,
or validated before validation.

Visual state must correspond to real application state.
```

---

# 72. Content Resilience Instruction

```text
Design for real content, not ideal placeholder content.

Test with:
long project names,
long task names,
long user names,
long AI responses,
long document titles,
large numbers,
missing metadata,
empty lists,
many rows,
and errors.

Do not solve overflow by making typography microscopic.
```

---

# 73. Page Hierarchy Instruction

```text
Every page should have:
one dominant hierarchy,
one primary content entry point,
one clear primary action where applicable,
controlled secondary actions,
supporting metadata,
and meaningful whitespace.

Do not create multiple competing focal points.
```

---

# 74. Primary Action Instruction

```text
Each page should make its primary action visually obvious.

Use:
position,
typography,
button hierarchy,
and restrained accent.

Do not make every action equally prominent.
```

---

# 75. Dense Workplace Instruction

```text
For dense workplace pages:
reduce decorative elements,
tighten spacing within logical groups,
use integrated tables,
use compact typography,
and preserve readable line height.

Density should come from organization, not tiny text.
```

---

# 76. Admin Density Instruction

```text
GOVERN may use higher density for:
tables,
traces,
metrics,
system health,
audit,
AI execution,
and analytics.

Maintain:
readability,
clear hierarchy,
strong alignment,
and accessible interaction.
```

---

# 77. Editorial Asymmetry Instruction

```text
Public pages may use controlled asymmetry.

Asymmetry must still preserve:
balance,
reading flow,
hierarchy,
responsive integrity,
and brand calmness.

Do not use asymmetry as visual disorder.
```

---

# 78. Alignment Instruction

```text
Prefer strong shared alignment.

Align:
page headings,
body copy,
cards,
tables,
controls,
sections,
and navigation to meaningful container boundaries.

Avoid arbitrary offsets.
```

---

# 79. Whitespace Instruction

```text
Whitespace is structural.

Use whitespace to separate:
unrelated content,
major sections,
navigation from content,
primary information from metadata,
and actions from descriptive content.

Do not remove whitespace simply to fit more content.
```

---

# 80. Anti-Pattern Instruction

```text
Do not generate:
generic SaaS templates,
rainbow role themes,
neon AI,
cyberpunk UI,
excessive glassmorphism,
card-everything,
giant pills,
heavy shadows,
animated backgrounds,
fake AI typing,
decorative charts,
excessive gradients,
excessive parallax,
robot/brain/circuit imagery,
random fonts,
random icon families,
or dark-mode inversions.
```

---

# 81. No Visual Drift Instruction

```text
Every new page must look like it belongs to the same GrowFlow product.

Reuse:
typography,
colors,
spacing,
radii,
surface language,
buttons,
inputs,
navigation,
status semantics,
motion,
and AI treatment.

Do not reinvent the visual language for each page.
```

---

# 82. Component Reuse Instruction

```text
Prefer existing GrowFlow components.

Before inventing a new component:
1. identify whether an existing component can solve the need,
2. compose existing primitives where appropriate,
3. extend an existing component if the variation is semantic,
4. create a new component only when genuinely necessary.

A new visual pattern must remain consistent with the Master Design.
```

---

# 83. Page Generation Prompt Template

Use this structure for page-specific prompts:

```text
GROWFLOW FOUNDATION:
Use GrowFlow Master Design and Stitch Instructions.
Do not invent a new visual system.

PAGE:
[Page ID and name]

ROUTE:
[Canonical route]

ROLE:
[Public / BUILD / SUPERVISE / GOVERN]

PURPOSE:
[What this page accomplishes]

PRIMARY USER GOAL:
[Most important user objective]

PRIMARY ACTION:
[Primary action]

SECONDARY ACTIONS:
[Secondary actions]

CONTENT:
[Required content]

LAYOUT:
[Page composition]

COMPONENTS:
[Required GrowFlow components]

DATA:
[Information displayed]

STATES:
[Loading / Empty / Error / Success / Processing / etc.]

AI:
[AI requirements, if any]

RESPONSIVE:
[Mobile / Tablet / Desktop behavior]

ACCESSIBILITY:
[Page-specific accessibility requirements]

MOTION:
[Page-specific motion]

IMAGERY:
[Required image assets or no-image instruction]

REFERENCE:
[Approved reference images, if any]

ANTI-PATTERNS:
[Specific things this page must avoid]

OUTPUT:
[What Stitch should produce]
```

---

# 84. Short Page Prompt Template

When the foundation is already loaded or available:

```text
Use the GrowFlow Master Design and approved Stitch foundation.

Create:
[PAGE NAME]

Route:
[ROUTE]

Role:
[ROLE]

Purpose:
[PURPOSE]

Primary action:
[ACTION]

Composition:
[LAYOUT]

Required content:
[CONTENT]

Required components:
[COMPONENTS]

States:
[STATES]

Responsive:
[RESPONSIVE]

Accessibility:
[ACCESSIBILITY]

Use approved GrowFlow assets only.
Do not invent a new visual system.
```

---

# 85. Refinement Prompt

Use after an initial Stitch generation:

```text
Refine this page while preserving its existing information architecture.

Do not redesign the page from scratch.

Correct only the following:
[LIST OF ISSUES]

Maintain:
GrowFlow Soft Intelligence,
Manrope,
canonical palette,
quiet surfaces,
restrained accent,
canonical component language,
responsive behavior,
accessibility,
and restrained motion.

Do not introduce new colors, fonts, role themes, or unrelated visual patterns.
```

---

# 86. Visual Correction Prompt

```text
Perform a visual-system correction pass.

Check:
typography,
spacing,
alignment,
color,
surface hierarchy,
radius,
elevation,
button hierarchy,
navigation,
status semantics,
AI treatment,
and visual density.

Replace any non-GrowFlow pattern with the canonical GrowFlow pattern.

Do not change product meaning or information architecture.
```

---

# 87. Typography Correction Prompt

```text
Perform a typography-only correction pass.

Use Manrope for all normal GrowFlow content.

Use only the approved GrowFlow type scale and weights.

Use JetBrains Mono only for explicitly technical content.

Remove:
unauthorized fonts,
random font weights,
oversized body text,
unnecessary bolding,
and decorative typography.

Do not change layout or product functionality.
```

---

# 88. Color Correction Prompt

```text
Perform a color-system correction pass.

Use only the GrowFlow canonical palette.

Correct:
background,
surface,
text,
border,
accent,
semantic,
and AI colors.

Reduce unnecessary accent usage.

Remove unauthorized gradients, neon colors,
rainbow status systems, and role-specific color themes.

Do not change content or layout.
```

---

# 89. Responsive Correction Prompt

```text
Perform a responsive correction pass.

Check:
mobile <768px,
tablet 768–1199px,
desktop >=1200px.

Do not simply scale the desktop layout.

Correct:
navigation,
sidebar/drawer,
grid,
tables,
forms,
dialogs,
AI content,
document reading,
and action placement.

Preserve domain meaning and authorization.
```

---

# 90. Accessibility Correction Prompt

```text
Perform an accessibility-focused visual correction pass.

Check:
heading hierarchy,
focus visibility,
keyboard reachability,
touch targets,
contrast,
non-color state communication,
labels,
dialog/drawer behavior,
dynamic content,
and reduced motion.

Do not redesign unrelated visual elements.
```

---

# 91. AI Correction Prompt

```text
Perform an AI visual correction pass.

AI must feel slightly deeper than normal GrowFlow UI,
but remain calm and native.

Remove:
neon,
glow,
cyberpunk,
holographic,
robotic,
and generic chatbot styling.

Ensure AI state is visually truthful.

Use approved AI colors and typography.
```

---

# 92. Density Correction Prompt

```text
Perform a density correction pass.

If the page is too sparse:
improve information grouping and alignment before adding decoration.

If the page is too dense:
remove redundancy and improve spacing before shrinking typography.

Do not solve density problems with arbitrary font sizes.
```

---

# 93. Consistency Correction Prompt

```text
Compare this page against the established GrowFlow visual language.

Correct inconsistencies in:
buttons,
inputs,
radii,
shadows,
spacing,
typography,
navigation,
status,
cards,
tables,
AI surfaces,
and responsive behavior.

The result must feel like the same product as existing approved GrowFlow pages.
```

---

# 94. Final QA Prompt

```text
Perform a final GrowFlow visual QA pass.

Check:

1. Brand
2. Typography
3. Color
4. Surfaces
5. Borders
6. Radius
7. Elevation
8. Spacing
9. Layout
10. Navigation
11. Components
12. States
13. AI
14. Imagery
15. Responsive behavior
16. Accessibility
17. Motion
18. Content resilience
19. Role consistency
20. Dark mode if applicable

Do not introduce new design decisions.

Fix only issues that violate the established GrowFlow system.
```

---

# 95. Public Page Prompt Formula

```text
Foundation
+
Page identity
+
Editorial composition
+
Product evidence
+
Contextual imagery
+
CTA hierarchy
+
Responsive behavior
+
Accessibility
```

Public pages may be expressive, but remain recognizably GrowFlow.

---

# 96. Authenticated Page Prompt Formula

```text
Foundation
+
Application shell
+
Role
+
Resource context
+
Information hierarchy
+
Action hierarchy
+
Data density
+
State handling
+
Responsive behavior
+
Accessibility
```

Authenticated pages should prioritize usability over marketing expression.

---

# 97. BUILD Page Prompt Formula

```text
Foundation
+
BUILD role
+
Project context
+
Progression
+
Action
+
Learning context
+
AI where relevant
+
Responsive
+
Accessibility
```

---

# 98. SUPERVISE Page Prompt Formula

```text
Foundation
+
SUPERVISE role
+
Student/group/project context
+
Oversight
+
Risk
+
Activity
+
Mentor action
+
Responsive
+
Accessibility
```

---

# 99. GOVERN Page Prompt Formula

```text
Foundation
+
GOVERN role
+
Operational data
+
Observability
+
Filtering
+
Tables
+
Charts
+
Audit/security context
+
Responsive
+
Accessibility
```

---

# 100. AI Page Prompt Formula

```text
Foundation
+
AI context
+
User/project context
+
Conversation or execution
+
Truthful state
+
Structured output
+
Recovery
+
Accessibility
+
Responsive
```

---

# 101. Asset Instruction

```text
Use approved GrowFlow assets only.

When an asset is specified by asset ID:
use that asset for its intended purpose.

Do not substitute a different image simply because it fits the composition.

Do not modify the GrowFlow logo.

Do not treat reference images as final assets.
```

---

# 102. Image Selection Instruction

```text
Choose imagery according to semantic purpose.

Use:
editorial imagery for storytelling,
product UI for feature demonstration,
abstract brand visuals for flow/progression,
and no image when imagery adds no meaning.

Do not add decorative images to empty space without a reason.
```

---

# 103. Asset Reuse Instruction

```text
Reuse approved imagery where it strengthens visual continuity.

Do not create multiple nearly identical images for the same purpose.

If two pages require the same visual story,
prefer one approved asset with appropriate cropping.
```

---

# 104. Logo Placement Instruction

```text
Use the approved logo according to its context.

Public:
prominent but restrained.

Authenticated:
recognizable but subordinate to workspace navigation.

Mobile:
use compact mark when required by available space.

Never distort or recreate the logo.
```

---

# 105. Reference Conflict Instruction

```text
If a reference image conflicts with GrowFlow:
ignore the conflicting part.

GrowFlow Master Design wins.

Do not import:
foreign colors,
fonts,
radii,
role themes,
AI styling,
or unrelated navigation patterns
from a reference.
```

---

# 106. No Prompt-Level Token Reinvention

```text
Do not redefine the GrowFlow design system inside each page prompt.

Reference the established foundation.

Only include page-specific deviations when explicitly approved.

This keeps prompts small and prevents token drift.
```

---

# 107. Prompt Economy

The ideal prompt should contain:

```text
Foundation reference
+
Page-specific requirements
+
Unique constraints
+
Approved assets
+
States
+
Responsive requirements
```

Do not repeat the entire Master Design in every prompt.

---

# 108. Prompt Specificity

A short prompt is not a vague prompt.

A good short prompt explicitly states:

- page
- route
- role
- purpose
- primary action
- required content
- required components
- required states
- responsive behavior
- accessibility requirements
- approved assets
- anti-patterns

---

# 109. Page-by-Page Workflow

For every page:

```text
01. Identify Page ID
02. Identify Route
03. Identify Role
04. Identify Purpose
05. Identify Primary User Goal
06. Identify Primary Action
07. Identify Data
08. Identify Components
09. Identify States
10. Identify AI behavior
11. Identify imagery
12. Identify responsive behavior
13. Identify accessibility requirements
14. Write compact Stitch prompt
15. Generate
16. Review
17. Correct
18. Responsive review
19. Accessibility review
20. Approve
21. Record approved design
22. Move to next page
```

---

# 110. Do Not Skip Review

A Stitch generation is a proposal, not automatically an approved design.

Approval requires:

- visual review
- component review
- responsive review
- accessibility review
- architecture/behavior consistency review

---

# 111. Approval Rule

A page is approved only when:

- its visual system matches GrowFlow
- its product meaning is correct
- its states are correct
- its responsive behavior is acceptable
- its accessibility is acceptable
- no major visual drift remains

---

# 112. Stitch Output Is Not Backend Truth

Stitch should never be treated as authoritative for:

- API behavior
- canonical state
- authorization
- persistence
- AI orchestration
- event semantics
- security

The Stitch output is a visual composition.

---

# 113. Stitch Output and Real Product UI

For product surfaces:

```text
Stitch
→ visual exploration
→ review
→ Figma/system alignment
→ frontend implementation
→ real data/state
```

Do not mistake a static generated representation for production behavior.

---

# 114. Generated UI State Instruction

When generating static design representations, use realistic but clearly representative content.

Do not imply that fictional statistics are real production metrics.

For marketing visuals, avoid fabricated claims unless the content is explicitly supplied by the page specification.

---

# 115. Content Integrity Instruction

Do not invent:

- real customer counts
- real institutional claims
- real user testimonials
- real performance statistics
- real security certifications
- real AI quality metrics

unless supplied by the approved product content.

---

# 116. Placeholder Instruction

If content is not yet known:

Use clearly identifiable placeholder content or neutral representative copy.

Do not accidentally turn placeholder metrics into permanent product claims.

---

# 117. Localization Readiness

Design should tolerate text expansion.

Avoid compositions that only work for one exact sentence length.

Buttons, headings, navigation, and tables must remain robust if text changes.

---

# 118. Accessibility Content Instruction

Use meaningful visible labels.

Do not replace meaningful labels with icon-only controls unless the action is universally understandable and an accessible name is provided.

---

# 119. Icon Instruction

Use one coherent icon family.

Icons should:

- reinforce meaning
- remain visually subordinate to text
- use consistent stroke/weight language
- align with component dimensions

Do not mix unrelated icon styles.

---

# 120. Public Motion Instruction

Public pages may use slightly more visible motion than workplace pages.

Still maintain:

- subtle physical movement
- controlled duration
- reduced-motion support
- no continuous decorative animation

---

# 121. Workplace Motion Instruction

Workplace motion should be more restrained.

Prefer motion for:

- state transition
- spatial continuity
- feedback
- orientation

Avoid motion during repetitive work.

---

# 122. Dashboard Motion Instruction

Dashboard motion should never obscure data.

Use animation only for:

- meaningful state transition
- live update where appropriate
- entry/orientation

Do not continuously animate charts.

---

# 123. AI Motion Instruction

AI generation may show subtle state progression.

Never fabricate intelligence through endless typing animation.

The actual backend state should determine the visual state.

---

# 124. Scroll Instruction

Use the GrowFlow:

**Float → Settle**

language for appropriate public-page scroll transitions.

Elements should enter gently and settle.

Do not make the entire page move continuously.

---

# 125. Dark/Public/Workplace Combination Instruction

When a page is both:

- public + dark
- authenticated + dark
- AI + dark

apply all relevant rules together.

Do not create a special hybrid theme.

---

# 126. Design Token Compliance Instruction

All generated UI must use:

- canonical colors
- canonical typography
- canonical spacing
- canonical radius
- canonical elevation
- canonical dimensions

If a new value appears necessary, flag it as a design-system gap instead of silently inventing it.

---

# 127. New Component Instruction

If Stitch creates a component not already represented:

1. determine whether it is actually necessary,
2. identify its semantic purpose,
3. define its states,
4. define responsive behavior,
5. define accessibility,
6. align it with existing tokens,
7. document it before treating it as canonical.

---

# 128. Design Gap Instruction

If a page cannot be designed without inventing a new foundation rule:

```text
STOP INVENTION.

Identify the missing design decision.

Mark it as:
DESIGN GAP / TBD

Do not silently create a permanent visual rule.
```

---

# 129. Visual Regression Instruction

Before approving a page, compare it conceptually against approved pages.

Check for:

- font drift
- accent drift
- radius drift
- shadow drift
- card drift
- density drift
- AI styling drift
- role-theme drift
- navigation drift

---

# 130. Multi-Page Consistency Instruction

When multiple pages are generated:

```text
First page:
establish pattern.

Later pages:
reuse pattern.

Do not redesign the same component differently on each page.
```

---

# 131. Public Website Consistency

Across:

- Landing
- Features
- Documentation
- Contact

maintain:

- same top navigation
- same brand
- same typography
- same CTA language
- same footer
- same image treatment
- same motion philosophy

---

# 132. Authenticated Consistency

Across BUILD, SUPERVISE, and GOVERN:

maintain:

- same top navigation
- same shell geometry
- same sidebar language
- same controls
- same status system
- same typography
- same surfaces

Only information and composition should change according to role.

---

# 133. State Consistency

A status should look the same wherever the same semantic state appears.

Example:

`COMPLETED`

must not be green in one component and blue in another without a semantic reason.

---

# 134. AI Consistency

AI should look like GrowFlow AI everywhere.

Do not allow:

- AI Mentor
- Blueprint generation
- AI suggestions
- AI observability

to each invent different AI visual identities.

They may have different information density, but they share the same AI token layer.

---

# 135. Document Consistency

Documents should share:

- typography
- reading width
- heading hierarchy
- code styling
- metadata
- version language

across student, mentor, and admin contexts.

---

# 136. Figma Alignment Instruction

When a Stitch composition is approved:

```text
Stitch output
→ compare with Master Design
→ translate into Figma components
→ ensure tokens match
→ ensure component variants match
→ record deviations
```

Do not allow Stitch to become an undocumented second design system.

---

# 137. Asset-to-Page Traceability

Every approved image or brand asset should have:

- asset ID
- purpose
- page usage
- light/dark suitability
- source
- status

Use asset IDs in page prompts whenever possible.

---

# 138. Image Generation Prompt Structure

For future generated imagery, use:

```text
ASSET ID:
[IMG-###]

PURPOSE:
[Why the image exists]

CONTEXT:
[Page/section]

SUBJECT:
[What is shown]

COMPOSITION:
[Placement and visual structure]

BRAND:
[GrowFlow visual language]

PALETTE:
[Approved palette relationship]

LIGHTING:
[Lighting direction]

MOOD:
[Emotional tone]

ASPECT RATIO:
[Required ratio]

AVOID:
[Specific exclusions]

REUSE:
[Potential pages]

OUTPUT:
[Image requirements]
```

---

# 139. Image Generation Consistency

Generated images should form one visual family.

Maintain consistency in:

- lighting
- realism level
- color restraint
- material language
- composition
- human context
- editorial tone

Do not create five unrelated photographic styles for five sections of the same page.

---

# 140. Hero Asset Instruction

Only one hero asset should be designated as the approved primary hero for a given page.

Multiple explorations may exist during design exploration, but only the approved asset becomes canonical.

---

# 141. Product Screenshot Instruction

Actual product screenshots should eventually come from the approved UI.

Do not use fabricated statistics or fictional production state as if it were real.

---

# 142. Placeholder UI Instruction

When Stitch requires visual product UI before frontend implementation:

```text
Use representative sample content.

Keep it clearly aligned with GrowFlow's real information architecture.

Do not invent unsupported features.
Do not invent unsupported metrics.
Do not invent unsupported roles.
```

---

# 143. Accessibility and Imagery Instruction

Informative imagery requires meaningful alternative text in implementation.

Decorative imagery should not create unnecessary screen-reader noise.

Stitch's visual composition must not depend on the image alone to communicate essential meaning.

---

# 144. Performance Instruction

Prefer visual compositions that are efficient to implement.

Avoid designs that require:

- enormous background assets
- continuous animation
- expensive blur layers
- heavy parallax
- unnecessary video
- complex canvas effects

---

# 145. Security-Aware Visual Instruction

Do not design visual components that expose restricted information through:

- search suggestions
- notifications
- previews
- metadata
- hover content
- public URLs

Visual design must respect authorization boundaries.

---

# 146. Role-Aware Instruction

Role differences should appear through:

- navigation
- content
- actions
- density
- contextual information

not through:

- separate colors
- separate fonts
- separate logo treatments
- separate visual identities

---

# 147. Route-Aware Instruction

When a page has a canonical route, reflect the route context in:

- breadcrumb
- heading
- navigation selection
- resource context

Do not create meaningless decorative navigation.

---

# 148. Deep-Link Instruction

A page composition must make sense when entered directly from its canonical URL.

Do not assume the user arrived through the dashboard.

Provide enough context to understand where they are.

---

# 149. Shareable Resource Instruction

When designing shareable resources:

- preserve clear resource identity
- provide context
- keep actions explicit
- do not expose restricted information

---

# 150. Final Page Prompt Checklist

Before sending a page prompt to Stitch:

```text
[ ] Page ID defined
[ ] Route defined
[ ] Role defined
[ ] Purpose defined
[ ] Primary user goal defined
[ ] Primary action defined
[ ] Secondary actions defined
[ ] Content defined
[ ] Layout defined
[ ] Components defined
[ ] Data requirements defined
[ ] States defined
[ ] AI behavior defined if applicable
[ ] Image assets defined
[ ] Responsive behavior defined
[ ] Accessibility defined
[ ] Motion defined
[ ] Reference images classified
[ ] Anti-patterns specified
[ ] No unnecessary foundation repetition
```

---

# 151. Final Visual QA Checklist

After Stitch generates a page:

```text
BRAND
[ ] GrowFlow identity
[ ] Connected Flow / Abstract G
[ ] no role theme

TYPOGRAPHY
[ ] Manrope
[ ] canonical scale
[ ] correct weights
[ ] JetBrains Mono only where technical

COLOR
[ ] canonical palette
[ ] restrained accent
[ ] semantic colors
[ ] AI palette
[ ] dark mode if applicable

LAYOUT
[ ] correct shell
[ ] alignment
[ ] spacing
[ ] density
[ ] hierarchy

COMPONENTS
[ ] canonical buttons
[ ] canonical inputs
[ ] canonical cards
[ ] canonical tables
[ ] canonical states

AI
[ ] restrained
[ ] non-neon
[ ] truthful state

IMAGERY
[ ] purposeful
[ ] contextual
[ ] approved asset

MOTION
[ ] subtle
[ ] purposeful
[ ] reduced motion

RESPONSIVE
[ ] mobile
[ ] tablet
[ ] desktop

ACCESSIBILITY
[ ] focus
[ ] keyboard
[ ] contrast
[ ] semantics
[ ] touch targets
[ ] non-color semantics
```

---

# 152. Final Anti-Pattern QA

Reject or revise if the output contains:

- [ ] neon AI
- [ ] cyberpunk visual language
- [ ] excessive gradients
- [ ] excessive glass
- [ ] card-everything
- [ ] giant pills
- [ ] heavy shadows
- [ ] animated background
- [ ] excessive parallax
- [ ] fake AI typing
- [ ] rainbow charts
- [ ] role-specific color themes
- [ ] unauthorized fonts
- [ ] decorative typography
- [ ] generic AI imagery
- [ ] generic SaaS template
- [ ] excessive stock photography
- [ ] tiny unreadable text
- [ ] hover-only functionality
- [ ] color-only state communication
- [ ] dark-mode inversion
- [ ] inconsistent components
- [ ] unsupported product claims

---

# 153. Master Prompt Economy Rule

Do not send the entire `Master_Design.md` with every page.

Instead use:

```text
Master Design
    ↓
Stitch Foundation
    ↓
Reusable Instruction
    ↓
Page-Specific Prompt
```

The page prompt should contain only what is unique to the page.

---

# 154. Recommended Prompt Layers

Use four layers:

### Layer 1 — Foundation

The GrowFlow visual system.

### Layer 2 — Component/Pattern

The relevant reusable pattern.

### Layer 3 — Page

The page-specific requirements.

### Layer 4 — Correction

Only issues discovered during review.

This keeps prompts compact and precise.

---

# 155. Prompt Reuse Library

The following reusable instruction groups should be copied as needed:

```text
FOUNDATION
BRAND
TYPOGRAPHY
COLOR
DARK MODE
PUBLIC
AUTH
BUILD
SUPERVISE
GOVERN
DASHBOARD
TABLE
FORM
AI
BLUEPRINT
ASSESSMENT
ROADMAP
DOCUMENT
RESPONSIVE
ACCESSIBILITY
MOTION
IMAGE
QA
```

Do not copy unrelated instruction groups.

---

# 156. Minimal Foundation Prompt

For later sessions where Stitch already has the relevant design context:

```text
Use the approved GrowFlow Master Design and Stitch Instructions.

Preserve:
Soft Intelligence,
Manrope,
canonical GrowFlow palette,
quiet surfaces,
restrained sage accent,
unified BUILD/SUPERVISE/GOVERN identity,
restrained AI,
subtle physical motion,
responsive behavior,
and accessibility.

Do not invent a new visual system.
```

---

# 157. Minimal Correction Prompt

```text
Correct this design to match the approved GrowFlow Master Design.

Do not redesign the information architecture.

Fix only:
[ISSUES]

Preserve all approved content and interactions.
```

---

# 158. Minimal Responsive Prompt

```text
Make this composition fully responsive for:
mobile <768px,
tablet 768–1199px,
desktop >=1200px.

Do not merely scale desktop down.
Preserve hierarchy, meaning, accessibility, and actions.
```

---

# 159. Minimal Accessibility Prompt

```text
Bring this page into compliance with the GrowFlow accessibility foundation.

Preserve the visual identity.

Correct:
focus,
keyboard access,
contrast,
semantic hierarchy,
touch targets,
labels,
non-color states,
and reduced motion.
```

---

# 160. Minimal AI Prompt

```text
Keep AI visually integrated with GrowFlow.

Use the restrained AI neutral layer.
No neon, glow, cyberpunk, holographic, robotic,
or generic chatbot aesthetic.

Represent actual AI execution state truthfully.
```

---

# 161. Stitch Session Start Instruction

At the beginning of a new Stitch design session:

```text
You are designing GrowFlow.

Treat the supplied GrowFlow Master Design as authoritative.

Do not invent a visual system.

Use:
Soft Intelligence,
Manrope,
canonical GrowFlow colors,
quiet surfaces,
restrained sage accent,
unified role identity,
restrained AI,
subtle physical motion,
and accessible responsive composition.

Wait for the page-specific requirements before composing the page.
```

---

# 162. Stitch Session Continuation Instruction

When continuing an existing session:

```text
Continue using the already established GrowFlow design system.

Do not reinterpret:
fonts,
colors,
radii,
spacing,
AI treatment,
navigation,
or role identity.

Only change the page-specific elements requested.
```

---

# 163. Stitch Multi-Page Instruction

When generating several related pages:

```text
Treat previously approved pages as visual references for GrowFlow consistency.

Reuse their established:
component geometry,
typography,
spacing,
surface treatment,
navigation,
status language,
and interaction patterns.

Do not copy page content or layout when the new page has different information needs.
```

---

# 164. Stitch Review Conversation Instruction

When asking Stitch to revise:

```text
Do not make broad aesthetic changes.

Apply targeted corrections.

Preserve:
approved typography,
approved palette,
approved shell,
approved component geometry,
approved content hierarchy,
and approved interaction intent.

Change only the explicitly identified problems.
```

---

# 165. Stitch Design Freeze Instruction

When a page is approved:

```text
Treat the current visual composition as approved GrowFlow design.

Do not introduce further stylistic changes unless explicitly requested.

Future changes should preserve:
GrowFlow Master Design,
component consistency,
responsive behavior,
accessibility,
and established page hierarchy.
```

---

# 166. Foundation Change Instruction

If a design change appears to require a foundation change:

```text
Do not silently modify the GrowFlow foundation.

Identify the proposed change as:
FOUNDATION CHANGE

State:
what changes,
why it is necessary,
what components are affected,
what pages are affected,
and what visual consistency implications exist.

Await explicit design-system approval.
```

---

# 167. Reference Priority Instruction

```text
When references disagree:

1. Master Design
2. Design Tokens
3. Core Components
4. Application Shell
5. Page Specification
6. Approved page examples
7. Reference screenshots

Never reverse this order.
```

---

# 168. Design Quality Definition

A high-quality Stitch result is not the one with the most visual effects.

It is the one that demonstrates:

- clear hierarchy
- coherent spacing
- correct typography
- restrained color
- meaningful surfaces
- useful data representation
- consistent components
- truthful states
- responsive composition
- accessibility
- visual continuity
- product-specific identity

---

# 169. Final Stitch Definition of Done

A Stitch page is ready for approval when:

```text
[ ] It unmistakably looks like GrowFlow.
[ ] It follows Soft Intelligence.
[ ] It uses Manrope correctly.
[ ] Technical content uses JetBrains Mono appropriately.
[ ] It uses canonical colors.
[ ] It uses quiet surfaces.
[ ] It avoids card overload.
[ ] It uses canonical component language.
[ ] It respects role unification.
[ ] AI remains restrained.
[ ] States are truthful.
[ ] Responsive behavior is intentional.
[ ] Accessibility is considered.
[ ] Motion is subtle.
[ ] Imagery is purposeful.
[ ] Content is resilient.
[ ] No visual foundation has been invented.
[ ] It can coexist with other approved GrowFlow pages.
```

---

# 170. Final Non-Negotiable Rules

The following are hard Stitch rules:

1. **Do not invent the GrowFlow design system.**
2. **Use Manrope as the universal normal UI/editorial font.**
3. **Use JetBrains Mono only for explicitly technical content.**
4. **Do not introduce a third font.**
5. **Use the canonical GrowFlow palette.**
6. **Use GrowFlow Sage as the restrained primary accent.**
7. **Do not create separate BUILD/SUPERVISE/GOVERN themes.**
8. **Keep surfaces quiet.**
9. **Do not card-everything.**
10. **Keep tables integrated and dense.**
11. **Treat dashboards as data instruments.**
12. **Keep AI slightly deeper but never neon/cyberpunk.**
13. **Use editorial imagery purposefully.**
14. **Do not copy reference screenshots literally.**
15. **Use subtle physical motion.**
16. **Respect Float → Settle where appropriate.**
17. **Respect reduced motion.**
18. **Design mobile as a first-class composition.**
19. **Treat tablet explicitly.**
20. **Preserve accessibility.**
21. **Do not communicate critical state through color alone.**
22. **Do not fabricate progress.**
23. **Do not imply persistence before confirmation.**
24. **Do not invent unsupported product claims.**
25. **Do not introduce visual drift between pages.**
26. **Reuse canonical components.**
27. **Do not silently create new tokens.**
28. **Do not silently create new foundation rules.**
29. **Approved pages become references for future consistency.**
30. **Master Design remains the visual authority.**

---

# 171. Final Operating Model

The complete Stitch workflow is:

```text
GrowFlow Master Design
        ↓
Stitch Instructions
        ↓
Approved Assets
        ↓
Page Specification
        ↓
Compact Page Prompt
        ↓
Stitch Generation
        ↓
Visual Review
        ↓
Targeted Correction
        ↓
Responsive Review
        ↓
Accessibility Review
        ↓
Consistency Review
        ↓
Approval
        ↓
Figma / Frontend Translation
```

---

# 172. Final Contract

GrowFlow Stitch work must follow one central philosophy:

> **Stitch explores composition inside the GrowFlow system; it does not create the GrowFlow system.**

The visual identity is already defined.

Stitch's job is to:

- compose pages,
- explore layout,
- visualize information,
- apply approved components,
- use approved assets,
- preserve the design language,
- and respond to targeted corrections.

The result should always feel:

> **Calm on the surface. Powerful underneath.**

---

## End of Stitch Instructions
