# GrowFlow — Part 5A: Application Foundation
## Final V1 Specification

**Status:** FROZEN  
**Part:** 5A — Application Foundation  
**Scope:** Public entry experience, authentication, registration, onboarding, role routing, global application shell, navigation, sharing, scrolling, responsive behavior, profile/settings placement, and foundational UX rules.

---

# 1. Purpose

This document defines the common application foundation used by GrowFlow's three platform roles:

- Student
- Mentor
- Admin

It establishes how users enter GrowFlow, authenticate, reach their role-specific application, and navigate the platform.

The foundation is intentionally shared at the **application-shell level** while keeping each role's experience, permissions, and navigation separate.

---

# 2. Core Application Principle

GrowFlow should feel like **one unified application**, not three unrelated websites.

The application therefore uses:

- one visual/design system
- one consistent top navigation position
- one consistent left navigation position
- one consistent sidebar behavior
- one consistent scrolling model
- one consistent profile/settings placement
- one consistent sharing mechanism
- role-specific navigation and authorization

Conceptually:

```text
                         GROWFLOW
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
          STUDENT         MENTOR         ADMIN
             |              |              |
             +--------------+--------------+
                            |
                    Shared Application
                         Foundation
```

The shell is shared.

The permissions and role-specific capabilities are not.

---

# 3. Public Application Entry

GrowFlow's public application should primarily expose two user paths:

```text
Student
Mentor
```

Admin is a controlled operational role and is not presented as a normal public signup option.

## Recommended entry experience

```text
                  GROWFLOW

        AI Project Mentoring Platform

     Turn your project idea into a real project.

             [ Continue as Student ]

             [ Continue as Mentor ]
```

The landing experience should explain GrowFlow clearly without attempting to display every feature.

The primary objective is:

```text
Understand
    ↓
Trust
    ↓
Enter Application
```

---

# 4. Separate Student and Mentor Authentication

Student and Mentor authentication are intentionally separate user experiences.

The application does not use a shared:

> "Select your role → Next"

login flow.

Instead, each role has its own entry point.

---

# 5. Student Authentication

Conceptual route:

```text
/login/student
```

## Student Login

The Student login provides:

- Email
- Password
- Login
- Continue with Google
- Continue with GitHub
- Forgot Password
- Create Student Account

## Student Registration

Conceptual route:

```text
/register/student
```

Registration contains:

- name
- email
- password
- confirm password
- required student identity information
- subsequent project-oriented onboarding

---

# 6. Mentor Authentication

Conceptual route:

```text
/login/mentor
```

## Mentor Login

The Mentor login provides:

- Email
- Password
- Login
- Continue with Google
- Continue with GitHub
- Forgot Password
- Create Mentor Account

## Mentor Registration

Conceptual route:

```text
/register/mentor
```

Registration contains:

- name
- email
- password
- confirm password
- mentor information
- subsequent mentor-oriented onboarding

---

# 7. Student ↔ Mentor Authentication Switcher

Student and Mentor authentication pages should include a simple switcher.

Example:

```text
        Student       |       Mentor
           ●                    ○
```

On the Mentor page:

```text
        Student       |       Mentor
           ○                    ●
```

Selecting the other role navigates directly to that role's authentication page.

The same concept should be available across:

- Login
- Registration
- Forgot Password

This provides role clarity without forcing users through a separate role-selection screen.

---

# 8. Authentication Infrastructure

Although Student and Mentor have separate UI entry points, GrowFlow should not build completely separate authentication infrastructures.

The preferred architecture is:

```text
Separate Auth UX
       ↓
Shared Authentication Infrastructure
       ↓
Authenticated Identity
       ↓
GrowFlow Account
       ↓
Role Verification
       ↓
Authorization
```

This reduces duplication while preserving clear role boundaries.

---

# 9. Google and GitHub OAuth

Both Student and Mentor authentication support:

- Google OAuth
- GitHub OAuth

OAuth must resolve to the correct GrowFlow account and role.

For example:

```text
/login/student
       ↓
Google OAuth
       ↓
Authenticated Identity
       ↓
Student GrowFlow Account
```

The system must not silently convert a Student authentication attempt into a Mentor account.

Account role and authorization remain authoritative on the backend.

---

# 10. Registration Rules

## Student

Self-registration:

**Allowed**

## Mentor

Self-registration:

**Allowed**, with optional controlled approval depending on deployment requirements.

## Admin

Public self-registration:

**Not allowed**

Admin accounts are provisioned through a controlled process.

---

# 11. Admin Access

Admin is intentionally hidden from the public application experience.

There should be no normal:

- Admin button
- Admin role selector
- Admin registration
- Admin navigation link
- public Admin login option

Admin uses a dedicated protected route known to the platform's authorized administrators.

Conceptually:

```text
/admin/<protected-admin-entry>
```

The exact route should be configurable and should not be exposed through normal public navigation.

## Critical security rule

A hidden route is **not** the security mechanism.

Actual Admin protection is:

```text
Protected route
      +
Authentication
      +
ADMIN role verification
      +
Backend authorization
      +
Security controls
```

Even if the route is discovered, unauthorized users must receive no Admin access.

---

# 12. Password Recovery

Student and Mentor have separate password-recovery experiences.

```text
Student
  ↓
Forgot Password
  ↓
Student recovery flow
```

and:

```text
Mentor
  ↓
Forgot Password
  ↓
Mentor recovery flow
```

The underlying recovery infrastructure can remain shared.

Admin account recovery remains a controlled administrative process rather than a public recovery experience.

---

# 13. Onboarding

Onboarding is role-specific.

A user should not repeatedly see onboarding after it has been completed.

The application tracks onboarding completion.

```text
Login
  ↓
Authentication
  ↓
Load Account
  ↓
Check Onboarding State
  |
  +-- Incomplete → Resume Onboarding
  |
  +-- Complete → Application
```

---

# 14. Student Onboarding

Student onboarding is project-oriented and intentionally concise.

## Identity

- Name
- Student ID
- required identity information

## Project Context

- technologies known
- technologies previously worked with
- technologies interested in learning
- project interests
- project goals
- learning goals

The onboarding should collect useful project context without becoming an unnecessary personality questionnaire.

After onboarding:

```text
Student Onboarding Complete
        ↓
Student Dashboard
        ↓
Create / Select Project
```

---

# 15. Mentor Onboarding

Mentor onboarding is focused on mentorship management.

It can include:

- name
- mentor identity/institution information
- expertise
- relevant technologies

Then the mentor can proceed to:

```text
Create First Group
```

Project creation does not need to be forced during onboarding.

---

# 16. Admin Onboarding

There is no normal public Admin onboarding.

Admin accounts are:

```text
Provisioned
    ↓
Authenticated
    ↓
ADMIN authorization
    ↓
Admin application
```

---

# 17. Role-Based Routing

After authentication, the system resolves the user's role.

```text
                    AUTHENTICATION
                           |
                           v
                    Authenticated
                           |
                           v
                      Role Check
             +-------------+-------------+
             |             |             |
             v             v             v
          STUDENT       MENTOR         ADMIN
             |             |             |
             v             v             v
       Student App    Mentor App    Admin App
```

Conceptual route namespaces:

```text
/student/*
/mentor/*
/admin/*
```

The exact route structure can be refined during implementation.

---

# 18. Unauthorized Route Protection

Frontend route guards improve UX, but they are not the security boundary.

GrowFlow must enforce authorization on the backend.

Example:

```text
Student
   ↓
/admin
   ↓
Frontend Guard
   ↓
Backend Authorization
   ↓
DENIED
```

Authorization must also apply to:

- database queries
- project access
- group access
- AI tools
- RAG retrieval
- GitHub resources
- administrative operations

---

# 19. Global Application Shell

After authentication, every role uses the same fundamental application-shell structure.

```text
+----------------------------------------------------------+
| TOP NAVIGATION                                           |
+----------------+-----------------------------------------+
|                |                                         |
| LEFT NAV       |             MAIN CONTENT                |
|                |                                         |
|                |                                         |
|                |                                         |
+----------------+-----------------------------------------+
```

The position of the primary navigation does not change between roles.

---

# 20. Top Navigation

The Top Navigation remains fixed at the top of the application.

Recommended conceptual structure:

```text
+----------------------------------------------------------+
| ☰  GrowFlow          Search          Share        🔔     |
+----------------------------------------------------------+
```

The exact icons and labels can be finalized during UI implementation.

The important architectural rule is:

> The Top Navigation is always at the top and remains visually persistent.

---

# 21. Share Feature

A **Share** action is part of the global Top Navigation.

It is intentionally simple.

## Behavior

When the user selects Share:

```text
Current page / current view
          ↓
Generate / resolve shareable URL
          ↓
Copy URL automatically
```

The URL is copied automatically.

There is no need for a large sharing dialog.

No:

- social sharing suite
- email-sharing workflow
- complicated share configuration
- multi-step sharing form

The V1 feature is simply:

> **Share → URL copied**

---

# 22. What Is Shared

The Share action should resolve the URL representing the user's **current authorized application view**.

Examples:

```text
Project Overview
       ↓
Share
       ↓
Project Overview URL copied
```

or:

```text
Project Risk
       ↓
Share
       ↓
Risk view URL copied
```

or:

```text
Current project document
       ↓
Share
       ↓
Document view URL copied
```

The URL must still enforce normal authorization when opened.

Sharing a URL does not grant access to private content.

If the recipient is not authorized to view the target resource, the normal access-control behavior applies.

---

# 23. Share Security

The Share feature must never bypass:

- authentication
- authorization
- project isolation
- group isolation
- student privacy
- mentor access boundaries
- admin privacy rules

The URL identifies a resource/view.

It does not grant permission.

---

# 24. Notification Placement

Notifications remain in the Top Navigation.

Conceptually:

```text
Top Nav:

☰   GrowFlow     Search     Share     🔔
```

The notification center is centralized across the application.

Role-specific notifications are determined by the backend.

---

# 25. Profile Placement — Final Decision

The Profile should **not** appear in the Top Navigation.

The user correctly identified that Profile would otherwise be duplicated.

Therefore:

> **Profile exists in one place only: the bottom section of the Left Navigation.**

The Top Navigation does not contain a profile button.

---

# 26. Bottom Left Navigation — Profile + Settings

The bottom of the Left Navigation contains:

```text
+----------------------+
|                      |
|    Main Navigation   |
|                      |
|                      |
|                      |
|                      |
|                      |
+----------------------+
|  [Avatar]            |
|  User Name           |
|  Role / account info |
|                      |
|  ⚙ Settings          |
+----------------------+
```

This bottom section is persistent and does not scroll with the main navigation items.

It is part of the application shell.

---

# 27. Bottom Section Behavior

The bottom profile/settings section remains visible regardless of how long the main navigation becomes.

Therefore:

```text
LEFT NAV
│
├── Scrollable Navigation
│
│       ↕
│
│   Dashboard
│   Projects
│   Groups
│   Students
│   ...
│
├─────────────────────
│   Profile            ← fixed bottom area
│   Settings           ← fixed bottom area
└─────────────────────
```

The profile/settings area is not part of the scrolling navigation list.

---

# 28. Profile Display

The profile area should show:

- avatar
- user's name
- relevant role/account identifier

For example:

```text
┌────────────────────────┐
│  AP   Ankhush Poonia   │
│       Student          │
│                    ⚙  │
└────────────────────────┘
```

The visual style can follow the uploaded reference concept while being redesigned for GrowFlow.

---

# 29. Settings

Settings are accessed from the bottom of the Left Navigation.

Settings can contain:

- account settings
- password/security
- connected accounts
- notification preferences
- relevant application preferences
- session/account management

Settings should not duplicate project-specific information.

---

# 30. Left Navigation

The primary Left Navigation remains on the left side.

Its contents change by role, but its:

- position
- behavior
- collapse mechanism
- scrolling model
- bottom profile/settings area

remain consistent.

---

# 31. Student Left Navigation

Recommended V1:

```text
Dashboard

Projects

Mentor

Notifications

────────────────────

Profile
Settings
```

Project-specific navigation appears after a project is opened rather than making the global navigation excessively large.

---

# 32. Mentor Left Navigation

Recommended V1:

```text
Overview

Groups

Students

Projects

At Risk

AI Mentor

Notifications

────────────────────

Profile
Settings
```

---

# 33. Admin Left Navigation

Recommended V1:

```text
Overview

Mentors
Students
Groups
Projects

AI Observatory
Cost & Usage
System Health
Documents & RAG
Security & Audit
Platform Analytics

────────────────────

Profile
Settings
```

---

# 34. Project-Level Navigation

The global Student navigation should not contain every project function.

After selecting a project:

```text
Projects
   ↓
Select Project
   ↓
Project Workspace
```

The Project Workspace provides contextual navigation:

```text
Project Name

Overview
Blueprint
Tasks
Milestones
Risks
Documents
GitHub
Activity
AI Mentor
```

This keeps the global navigation clean while giving each project a complete workspace.

---

# 35. Sidebar Collapse

The Left Navigation supports two primary desktop states.

## Expanded

```text
+----------------------+
| 🏠 Dashboard         |
| 📁 Projects          |
| 👨‍🏫 Mentor            |
| 🔔 Notifications     |
|                      |
|                      |
| 👤 User              |
| ⚙ Settings           |
+----------------------+
```

## Collapsed

The sidebar does **not disappear completely**.

Instead, it becomes an icon-only navigation rail.

```text
+------+
|  🏠  |
|  📁  |
|  👨‍🏫 |
|  🔔  |
|      |
|      |
|  👤  |
|  ⚙  |
+------+
```

This preserves orientation and quick navigation.

---

# 36. Collapsed Sidebar Interaction

When the sidebar is collapsed:

1. User clicks an icon.
2. Sidebar automatically expands.
3. The application navigates to that section.

Example:

```text
Collapsed Sidebar
       ↓
Click Projects
       ↓
Sidebar expands
       ↓
Projects page opens
```

This behavior is intentional.

The user does not have to:

```text
Expand
   ↓
Find item
   ↓
Click item
```

The icon itself remains a direct navigation control.

---

# 37. Sidebar Tooltips

When collapsed, icons should provide a clear label on hover/focus.

Example:

```text
     📁
      ↓
   Projects
```

This prevents ambiguity when labels are hidden.

---

# 38. Sidebar State Persistence

The expanded/collapsed state should persist.

Example:

```text
User collapses sidebar
        ↓
Navigate
        ↓
Sidebar remains collapsed
        ↓
Refresh
        ↓
Sidebar remains collapsed
```

The state can be stored as an application preference.

---

# 39. Navigation Scrolling

The main Left Navigation content may have its own scroll container.

However, the bottom Profile + Settings area remains fixed.

Conceptually:

```text
+----------------------+
| Logo                 |
|                      |
| Dashboard            |
| Projects             |
| Groups               |
| Students             |
| ...                  |
|                      |
|       ↕ SCROLL       |
|                      |
+----------------------+
| Profile              |
| Settings             |
+----------------------+
```

Only the navigation list scrolls.

The bottom account section does not.

---

# 40. Main Content Scrolling

The Main Content area has its own independent scrolling.

The browser window should not behave like a conventional long webpage where the entire application shell scrolls away.

Conceptually:

```text
+----------------------------------------------------------+
| TOP NAV — FIXED                                          |
+----------------+-----------------------------------------+
| LEFT NAV       | MAIN CONTENT                            |
|                |                                         |
| fixed shell    |          ↕ independent scroll           |
|                |                                         |
| navigation ↕   |                                         |
|                |                                         |
| profile fixed  |                                         |
+----------------+-----------------------------------------+
```

---

# 41. Scrolling Rules

The application follows these rules:

### Top Navigation

Fixed.

### Left Navigation

Persistent.

### Main Navigation List

Scrollable if necessary.

### Profile + Settings

Fixed at bottom of Left Navigation.

### Main Content

Primary independent scroll container.

### Browser Window

Should not be the primary application scroll container.

---

# 42. Avoid Excessive Nested Scrollbars

Although multiple application regions can scroll independently, GrowFlow should avoid creating unnecessary nested scrolling.

Rule:

> **Use one primary scroll container per application region and introduce nested scrolling only when the interaction genuinely requires it.**

This is especially important for:

- tables
- documents
- AI chat
- project dashboards
- large task lists

---

# 43. Responsive Behavior

Desktop and mobile should use the same information architecture but different navigation mechanics.

## Desktop

```text
Top Navigation
+
Left Sidebar
+
Main Content
```

Sidebar:

```text
Expanded ↔ Collapsed
```

## Mobile

The Left Navigation becomes a drawer.

```text
+------------------------+
| ☰ GrowFlow       🔔    |
+------------------------+
|                        |
|       Content          |
|                        |
+------------------------+
```

Selecting the menu button opens the navigation drawer.

The same role-specific navigation is used.

---

# 44. Responsive Profile / Settings

On mobile, the profile/settings section remains part of the navigation drawer.

The information architecture remains consistent even though the visual layout changes.

---

# 45. Application Shell Consistency Rule

This is a formal GrowFlow design rule:

> **The primary navigation position and interaction model must remain consistent throughout the authenticated application.**

Therefore:

| Element | Position |
|---|---|
| Top Navigation | Top |
| Primary Navigation | Left |
| Main Content | Right of Left Navigation |
| Profile | Bottom of Left Navigation |
| Settings | Bottom of Left Navigation |
| Share | Top Navigation |
| Notifications | Top Navigation |

---

# 46. Profile Duplication Rule

The application must not duplicate Profile navigation.

## Removed

```text
Top Navigation → Profile
```

## Final

```text
Left Navigation Bottom
   ↓
Profile
```

This applies consistently to:

- Student
- Mentor
- Admin

---

# 47. Share Placement Rule

Share is not placed inside the Left Navigation.

It belongs to the Top Navigation.

Final Top Navigation concept:

```text
☰   GrowFlow        Search       Share       Notifications
```

The exact ordering can be refined visually, but Share remains a global top-level action.

---

# 48. Search

Search is part of the Top Navigation.

Search remains role-scoped.

## Student

Can search within authorized personal/project resources such as:

- projects
- tasks
- milestones
- documents
- project content

## Mentor

Can search authorized:

- students
- groups
- projects

## Admin

Can search authorized platform-level:

- students
- mentors
- groups
- projects
- execution IDs
- operational identifiers

Authorization must be applied before results are returned.

---

# 49. Notifications

Notifications are centralized.

The Top Navigation contains the notification entry.

Examples:

## Student

- mentor note
- help-request update
- project risk
- deadline warning
- milestone event
- blueprint completion/failure
- document regeneration
- GitHub activity warning
- recommended action

## Mentor

- student help request
- project risk
- important student/project event
- milestone/project activity

## Admin

- infrastructure failure
- AI failure
- provider/rate-limit issue
- cost threshold
- security event
- system health issue

---

# 50. Share + Authorization

A shared URL must never become a permission token.

Correct model:

```text
Share
  ↓
URL copied
  ↓
Recipient opens URL
  ↓
Authentication / authorization
  ↓
Resource access decision
```

Therefore, private project resources remain private.

---

# 51. Foundation Architecture

The resulting application shell is:

```text
+-----------------------------------------------------------+
| ☰  GrowFlow      Search      Share      Notifications     |
+------------------+----------------------------------------+
|                  |                                        |
| ROLE NAVIGATION  |                                        |
|                  |                                        |
| Dashboard        |                                        |
| Projects         |          MAIN CONTENT                  |
| ...              |                                        |
|                  |             ↕ scroll                   |
|                  |                                        |
|                  |                                        |
|                  |                                        |
+------------------+----------------------------------------+
| PROFILE          |                                        |
| SETTINGS         |                                        |
+------------------+----------------------------------------+
```

The Profile/Settings block is visually anchored to the bottom of the Left Navigation, while the navigation list above it can scroll independently.

---

# 52. Authentication-to-Application Flow

```text
                         LANDING
                            |
              +-------------+-------------+
              |                           |
              v                           v
        STUDENT ENTRY                MENTOR ENTRY
              |                           |
              v                           v
       Student Login                Mentor Login
              |                           |
       +------+-------+             +-----+------+
       |      |       |             |     |      |
     Email  Google  GitHub        Email Google GitHub
       |      |       |             |     |      |
       +------+-------+             +-----+------+
              |                           |
              v                           v
        Authentication              Authentication
              |                           |
              v                           v
        Role Verification            Role Verification
              |                           |
              v                           v
        Onboarding Check             Onboarding Check
              |                           |
              v                           v
         Student App                 Mentor App


                         ADMIN
                           |
                           v
                  Protected Admin Route
                           |
                           v
                    Authentication
                           |
                           v
                    ADMIN Verification
                           |
                           v
                     Admin App
```

---

# 53. Foundation Security Model

Authentication and authorization remain separate.

## Authentication

Answers:

> Who is this user?

## Authorization

Answers:

> What may this user access?

The complete request path is:

```text
User
 ↓
Authentication
 ↓
Identity
 ↓
Role
 ↓
Membership / Resource Relationship
 ↓
Authorization
 ↓
Application / API / AI / RAG
```

This same authorization chain must apply to normal application requests and AI-powered requests.

---

# 54. Final Foundation Decisions

| Area | Final Decision |
|---|---|
| Public role selection | ❌ Removed |
| Student authentication | Separate |
| Mentor authentication | Separate |
| Student ↔ Mentor switching | Yes |
| Student registration | Yes |
| Mentor registration | Yes |
| Google OAuth | Student + Mentor |
| GitHub OAuth | Student + Mentor |
| Admin public registration | ❌ No |
| Admin public role selector | ❌ No |
| Admin entry | Protected non-public route |
| Admin security | Route + authentication + role authorization + backend authorization |
| Student onboarding | Project-oriented |
| Mentor onboarding | Mentor/group-oriented |
| Admin onboarding | Provisioned |
| Top Navigation | Fixed |
| Left Navigation | Persistent |
| Main Content | Independent scrolling |
| Left navigation list | Independent scrolling when necessary |
| Profile | Left Navigation bottom only |
| Settings | Left Navigation bottom only |
| Profile in Top Navigation | ❌ Removed |
| Share | Top Navigation |
| Share behavior | Copy current authorized view URL automatically |
| Share dialog | ❌ Not required |
| Notifications | Top Navigation |
| Search | Top Navigation |
| Sidebar | Collapsible |
| Collapsed state | Icon-only, never completely hidden |
| Collapsed icon click | Expand + navigate |
| Sidebar state | Persistent |
| Mobile sidebar | Drawer |
| Project navigation | Contextual inside Project Workspace |
| Shell | Shared across all roles |
| Role navigation | Separate |
| Authorization | Backend authoritative |

---

# 55. Decisions and Solutions — User Feedback Log

This section records the questions/changes raised during application-foundation discussion and the final solution adopted.

---

## A. Role Selection Screen

### User decision

The application should not ask users to select Student/Mentor inside a shared login flow.

### Solution

Create separate authentication experiences:

```text
Student Login
Mentor Login
```

with a simple Student ↔ Mentor switcher.

Admin remains separate.

---

## B. Two Login Systems

### User decision

Student and Mentor should have their own login, registration, and password recovery.

### Solution

Separate UX routes:

```text
/login/student
/login/mentor

/register/student
/register/mentor
```

while allowing the underlying authentication infrastructure to remain shared.

---

## C. Admin Access

### User decision

Admin should have special access through a hidden/non-public route known to administrators.

### Solution

Use a protected admin route combined with:

- authentication
- ADMIN role verification
- backend authorization
- security controls

The hidden route is treated as an access-discovery reduction, not the actual security boundary.

---

## D. Consistent Navigation Position

### User decision

Navigation position must remain consistent throughout the application.

### Solution

All roles use:

```text
Top Navigation
+
Left Navigation
+
Main Content
```

Only the contents change by role.

---

## E. Independent Scrolling

### User decision

The main content and navigation should not behave like one large scrolling webpage.

### Solution

Use separate application scroll regions:

- fixed Top Navigation
- persistent Left Navigation
- scrollable navigation list when needed
- independently scrollable Main Content

The browser window should not be the primary application scroll container.

---

## F. Collapsible Sidebar

### User decision

The Left Navigation should collapse but never disappear completely.

### Solution

Two states:

```text
Expanded
Collapsed icon-only
```

When collapsed:

- icons remain visible
- hover/focus provides labels
- clicking an icon expands the sidebar
- the selected section opens automatically

---

## G. Profile Duplication

### User decision

Profile should not exist in both Top Navigation and Left Navigation.

### Solution

Remove Profile from Top Navigation completely.

Place Profile only in the fixed bottom section of the Left Navigation.

---

## H. Settings Placement

### User decision

Profile and Settings should live together consistently across roles.

### Solution

The bottom of the Left Navigation contains:

```text
User Profile
Settings
```

This area does not scroll with the main navigation list.

---

## I. Share Feature

### User decision

Add a simple global Share feature to the Top Navigation.

### Solution

Share performs one primary action:

```text
Share
 ↓
Copy current authorized page/view URL
```

No complicated sharing interface is required.

---

## J. Share Security

### Architectural requirement

A shared URL must not grant access to a private resource.

### Solution

The URL is only a locator.

Normal authentication and authorization still apply when the URL is opened.

---

## K. Large Navigation Lists

### Problem

Some roles, especially Admin, may have more navigation items than fit vertically.

### Solution

Only the main navigation list scrolls.

The Profile + Settings block remains fixed at the bottom.

---

## L. Project Navigation

### Problem

Putting every project feature into the global sidebar would make the navigation unnecessarily large.

### Solution

Use contextual Project Workspace navigation:

```text
Global Navigation
   ↓
Projects
   ↓
Project
   ↓
Project Workspace Navigation
```

This keeps the global application shell clean.

---

## M. Shared Shell vs Shared Experience

### Question

Should all roles have exactly the same interface?

### Solution

No.

They share:

- shell
- navigation position
- sidebar behavior
- scrolling
- notification placement
- search placement
- share placement
- profile/settings placement
- responsive behavior

But they have different:

- navigation items
- permissions
- dashboards
- workflows
- data scope
- capabilities

This creates a unified GrowFlow product without mixing role responsibilities.

---

# 56. Final Part 5A Status

| Part | Status |
|---|---|
| Part 1 — Mentor Side | 🟢 FROZEN |
| Part 2 — Student Side | 🟢 AGREED / FINAL |
| Part 3 — Admin Side | 🟢 FROZEN |
| Part 4 — AI Agent Architecture | 🟢 FROZEN |
| Part 5A — Application Foundation | 🟢 **FROZEN** |

---

# 57. Part 5A Completion Statement

GrowFlow V1 now has a defined application foundation with:

- separate Student and Mentor authentication experiences
- controlled Admin access
- role-specific onboarding
- role-based routing
- shared application shell
- fixed Top Navigation
- persistent Left Navigation
- independent application scrolling
- collapsible icon-only sidebar
- fixed Profile + Settings section
- global Share action
- centralized Notifications
- role-scoped Search
- contextual Project navigation
- responsive mobile navigation
- strict backend authorization

The foundation is intentionally designed so the application can now expand into the detailed **Student, Mentor, Admin, Project Workspace, Blueprint, Documents, and AI Mentor application experiences** without changing the core navigation model.
