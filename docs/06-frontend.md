# Frontend Development Guide

> Complete frontend engineering standards for FastForge.

---

# Purpose

This document defines how every frontend feature should be built.

The frontend should be:

- Fast
- Predictable
- Accessible
- Responsive
- AI-friendly
- Easy to maintain

The frontend is responsible for **presentation**, not business logic.

Business rules belong in the backend.

---

# Technology Stack

| Layer | Technology |
|--------|------------|
| Framework | Next.js (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS |
| Components | shadcn/ui |
| Marketing UI | Magic UI |
| Forms | React Hook Form |
| Validation | Zod |
| Server State | TanStack Query |
| Icons | Lucide React |
| Animation | Framer Motion |
| Theme | next-themes |

---

# Design Principles

The frontend follows five principles.

## Server First

Prefer Server Components whenever possible.

Advantages:

- Smaller bundles
- Faster rendering
- Better SEO
- Less JavaScript
- Better performance

Only use Client Components when browser APIs or interactivity are required.

---

## Thin UI

Components display data.

Business logic belongs in:

- Backend services
- Custom hooks
- Utility functions

Avoid embedding workflows directly inside components.

---

## Feature-Based Organization

Organize code by feature rather than by file type.

Good:

```text
features/

billing/

dashboard/

projects/

settings/
```

Avoid:

```text
components/

pages/

hooks/

utils/

everything...
```

Feature ownership should be obvious.

---

## Composition

Prefer small reusable components.

Bad:

```
Dashboard.tsx

2000+ lines
```

Good:

```
DashboardHeader

DashboardSidebar

DashboardStats

DashboardTable

DashboardFilters
```

---

## Accessibility

Every UI should be accessible.

Minimum requirements:

- Keyboard navigation
- Proper labels
- Focus states
- Semantic HTML
- Color contrast

Accessibility is not optional.

---

# Folder Structure

```
src/

app/

features/

components/

hooks/

lib/

providers/

types/
```

---

# app/

Contains:

- layouts
- routes
- pages
- loading.tsx
- error.tsx
- not-found.tsx

Business logic should not live here.

---

# Features

Each feature owns everything related to itself.

Example:

```text
features/

projects/

components/

hooks/

api/

types/

utils/

constants/

schemas/
```

Everything related to Projects remains inside Projects.

---

# Components

Components fall into three categories.

## Shared Components

Reusable across the application.

Example:

```
Button

Dialog

Input

Table

Badge

Avatar
```

Most of these come from shadcn/ui.

---

## Feature Components

Specific to one feature.

Example:

```
ProjectCard

ApiKeyTable

BillingSummary
```

Never move feature-specific components into shared components.

---

## Layout Components

Responsible for page structure.

Examples:

```
Sidebar

Navbar

Footer

DashboardLayout

SettingsLayout
```

---

# Component Guidelines

A component should ideally have one responsibility.

Good:

```
UserAvatar
```

Bad:

```
UserDashboardSettingsCardWithBilling
```

Break large components into smaller pieces.

---

# Naming Conventions

Components:

```
PascalCase
```

Examples:

```
ProjectCard

BillingTable

CreateApiKeyDialog
```

Hooks:

```
useCurrentUser

useProjects

useDebounce
```

Utilities:

```
camelCase
```

Files:

```
kebab-case.tsx
```

Example:

```
project-card.tsx

billing-table.tsx
```

---

# Server Components

Default choice.

Use when:

- Fetching data
- Rendering pages
- Reading cookies
- Reading headers
- Static content

Benefits:

- No hydration
- Better SEO
- Smaller bundles

---

# Client Components

Only use `"use client"` when necessary.

Examples:

- Forms
- Dialogs
- Dropdowns
- Charts
- Browser APIs
- Interactive tables

Avoid converting entire pages into Client Components.

---

# Routing

Use App Router.

Example:

```text
app/

(page)

dashboard/

settings/

projects/

billing/
```

Keep routing simple.

---

# Data Fetching

Server Components:

Use backend API.

Client Components:

Use TanStack Query.

Avoid calling fetch repeatedly inside components.

---

# TanStack Query

Responsible for:

- API requests
- Cache
- Refetching
- Background updates

Example responsibilities:

```
useProjects()

useCurrentUser()

useBilling()
```

Do not duplicate fetch logic.

---

# API Layer

Every feature owns its API client.

Example:

```text
features/projects/api/

get-projects.ts

create-project.ts

delete-project.ts
```

Avoid one giant `api.ts`.

---

# Forms

Every form should use:

- React Hook Form
- Zod

Flow:

```
User Input

↓

React Hook Form

↓

Zod Validation

↓

API

↓

Backend Validation

↓

Response
```

Never rely only on frontend validation.

---

# Validation

Frontend validation improves UX.

Backend validation guarantees correctness.

Both are required.

---

# State Management

Priority:

1. URL State
2. Server State
3. React State
4. Context
5. Zustand (rare)

Avoid Redux.

Most SaaS applications do not require it.

---

# URL State

Store filters in the URL.

Example:

```
?page=2

?search=test

?sort=name
```

Benefits:

- Shareable URLs
- Refresh-safe
- Browser history

---

# React Context

Use only for global concerns.

Examples:

- Theme
- Authentication
- Query Client

Avoid placing business state inside Context.

---

# Custom Hooks

Extract reusable logic.

Good:

```
useCurrentUser()

useDebounce()

useClipboard()

useSearch()
```

Avoid large hooks with unrelated responsibilities.

---

# Styling

Tailwind CSS only.

Avoid:

- Inline styles
- CSS modules
- Styled Components

Keep styling consistent.

---

# Design Tokens

All colors, spacing, and typography should come from Tailwind configuration or CSS variables.

Avoid hardcoding values throughout the application.

Example:

```
Primary

Secondary

Muted

Destructive

Accent
```

Not:

```
#4285F4
```

directly inside components.

---

# Icons

Use Lucide React.

Avoid mixing icon libraries.

Consistency improves the overall interface.

---

# Authentication UI

Authentication should feel consistent across every product.

Supported flows:

- Login
- Register
- Forgot Password
- Reset Password
- Verify Email
- OAuth Login

Providers:

- Google
- GitHub

Future providers should integrate without changing existing UI architecture.

---

# Dashboard Architecture

Every SaaS dashboard should follow a familiar layout.

```
Dashboard

├── Sidebar
├── Navbar
├── Breadcrumb
├── Content
└── Footer (optional)
```

Navigation should remain consistent across all products.

Users should never need to relearn the interface.

---

# Page Layout

Every page should follow the same structure.

```
Page

↓

Header

↓

Actions

↓

Content

↓

Pagination (if applicable)
```

Avoid inconsistent layouts between pages.

---

# Tables

Use reusable table components.

Tables should support:

- Pagination
- Sorting
- Searching
- Empty state
- Loading state
- Row actions
- Bulk actions (future)

Avoid rewriting table logic for every feature.

---

# Forms

Every form should provide:

- Labels
- Placeholder text where appropriate
- Inline validation
- Loading state
- Disabled submit during submission
- Success feedback
- Error feedback

Submit buttons should clearly communicate state.

Example:

```
Save

Saving...

Saved
```

---

# Dialogs

Dialogs should be used for:

- Confirmation
- Create
- Edit
- Delete

Avoid placing large workflows inside modal dialogs.

Complex workflows deserve dedicated pages.

---

# Toast Notifications

Use toast notifications sparingly.

Good examples:

- Saved successfully
- API key created
- Project deleted

Avoid showing toasts for expected navigation.

---

# Loading States

Every asynchronous page should provide a loading state.

Examples:

- Skeleton loaders
- Progress indicators
- Loading buttons

Avoid blank pages during loading.

---

# Skeletons

Prefer skeleton loaders over spinners.

Example:

Instead of:

```
Loading...
```

Use placeholder cards or table rows.

This provides a better perceived performance.

---

# Empty States

Every list should define an empty state.

Example:

```
No API Keys

Create your first API key to begin using the service.
```

Include a primary call-to-action whenever possible.

---

# Error States

Every page should gracefully handle errors.

Examples:

- Failed to load data
- Network error
- Permission denied

Provide:

- Clear explanation
- Retry action
- Support link (future)

Avoid exposing raw backend errors.

---

# Confirmation Dialogs

Dangerous actions require confirmation.

Examples:

- Delete Project
- Cancel Subscription
- Revoke API Key

Confirmation should clearly describe the consequence.

---

# Navigation

Primary navigation belongs in the sidebar.

Secondary actions belong in page headers.

Avoid hiding important navigation inside dropdown menus.

---

# Search

Search should be debounced.

Recommended delay:

```
300–500ms
```

Avoid sending requests on every keystroke.

---

# Pagination

Prefer server-side pagination.

Standard controls:

- Previous
- Next
- Page size selector
- Current page

Do not fetch the entire dataset for large tables.

---

# Optimistic Updates

Use optimistic updates only when failure is unlikely.

Examples:

- Toggle settings
- Mark notification as read

Avoid optimistic updates for:

- Payments
- Billing
- Destructive actions

---

# File Uploads

Large uploads should display:

- Progress
- Cancel option
- Retry option (future)

Do not freeze the interface during uploads.

---

# Theme

Support:

- Light
- Dark
- System

Use `next-themes`.

Never hardcode colors inside components.

---

# Responsive Design

Every page should support:

- Mobile
- Tablet
- Desktop

Mobile-first design is encouraged.

Common breakpoints:

- sm
- md
- lg
- xl
- 2xl

---

# Accessibility

Every feature should support:

- Keyboard navigation
- Screen readers
- Focus indicators
- ARIA attributes where appropriate

Buttons should always have accessible labels.

Forms must associate labels with inputs.

---

# Performance

Optimize:

- Images
- Fonts
- Bundle size
- Server rendering
- Lazy loading

Avoid unnecessary Client Components.

Measure before optimizing.

---

# Images

Use Next.js Image component.

Benefits:

- Lazy loading
- Responsive sizing
- Optimization

Avoid plain `<img>` unless necessary.

---

# Fonts

Use `next/font`.

Avoid loading fonts from external CDNs.

Self-host fonts whenever practical.

---

# SEO

Marketing pages should include:

- Title
- Description
- Open Graph
- Twitter Cards
- Canonical URL

Use Next.js Metadata API.

Dashboard pages generally do not require SEO optimization.

---

# Analytics

Track meaningful events.

Examples:

- Signup
- Login
- Project Created
- Subscription Started
- API Key Generated

Avoid tracking every click.

Collect useful business metrics instead.

---

# Error Boundaries

Use route-level error boundaries.

Provide users with:

- Friendly error message
- Retry button
- Navigation back to safety

---

# Testing Strategy

Frontend tests include:

## Component Tests

Test:

- Rendering
- Props
- User interaction

---

## Integration Tests

Test:

- Forms
- API integration
- Authentication flows

---

## End-to-End Tests

Critical workflows:

- Login
- Registration
- Billing
- Dashboard
- API Key creation

---

# Code Quality

Every frontend contribution should include:

- Strict TypeScript
- Small reusable components
- Accessible markup
- Responsive layouts
- Loading states
- Error states
- Empty states

Readable code is preferred over clever abstractions.

---

# Frontend Checklist

Before merging a frontend feature:

- [ ] Responsive
- [ ] Accessible
- [ ] Loading state implemented
- [ ] Error state implemented
- [ ] Empty state implemented
- [ ] Form validation included
- [ ] Types added
- [ ] API client implemented
- [ ] Tests added (where appropriate)
- [ ] Documentation updated (if reusable)

---

# Anti-Patterns

Avoid:

- Large page components
- Business logic inside components
- Deep prop drilling
- Uncontrolled forms
- Inline styles
- Multiple UI libraries
- Global mutable state
- Copy-pasted components
- Hardcoded colors
- Client Components by default

---

# Frontend Definition of Done

A frontend feature is complete only when:

- UI matches the design system.
- Responsive behavior is verified.
- Accessibility requirements are met.
- Loading, empty, and error states exist.
- API integration is complete.
- Types are defined.
- Components are reusable where appropriate.
- Tests are added where practical.

---

# Summary

The frontend architecture prioritizes:

- Simplicity
- Consistency
- Accessibility
- Performance
- Reusability

Every product built on FastForge should feel familiar to users and developers alike.

The frontend should provide an excellent user experience while remaining easy to maintain and straightforward for AI coding agents to extend.