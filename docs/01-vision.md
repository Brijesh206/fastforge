# Vision

> **Build Once. Reuse Forever. Ship Fast.**

---

# Introduction

FastForge is not a SaaS application.

It is an internal engineering platform whose purpose is to make building SaaS applications dramatically faster.

Every product built on top of this platform should strengthen the platform itself.

The platform is considered a long-term investment.

Rather than rebuilding common functionality for every idea, we build reusable modules once and compose them into future products.

---

# Mission

Reduce the engineering effort required to launch a production-ready SaaS from **weeks** to **days**.

The platform should provide everything required for a modern SaaS except the domain-specific business logic.

Developers should spend time solving customer problems—not rebuilding infrastructure.

---

# Long-Term Vision

The long-term goal is to create a product factory.

Launching a new SaaS should eventually look like this:

```
Clone Repository

↓

Rename Project

↓

Configure Environment Variables

↓

Configure Branding

↓

Implement Business Logic

↓

Deploy

↓

Launch
```

Everything else should already exist.

---

# Product Factory Philosophy

Most SaaS products share approximately 80–90% of their infrastructure.

Examples include:

- Authentication
- User Management
- Organizations
- Teams
- Billing
- Payments
- Emails
- Storage
- Logging
- Monitoring
- API Keys
- Background Jobs
- Analytics
- Deployment
- CI/CD
- Dashboards
- Settings
- Landing Pages

The remaining 10–20% is what makes the product unique.

This platform exists to eliminate rebuilding the first 80%.

---

# Core Principles

## 1. Ship Fast

The objective is not perfect software.

The objective is validated software.

Shipping quickly creates opportunities for feedback.

Feedback creates better products.

Perfect architecture without users has little value.

Every architectural decision should support faster delivery.

---

## 2. Build Once, Reuse Forever

Every reusable component should become part of the platform.

If a solution is copied between products, it belongs inside a shared package.

Examples:

- Authentication
- Storage adapters
- Stripe integration
- Email templates
- Logging
- Pagination
- Rate limiting

Future products should benefit automatically.

---

## 3. Modular Architecture

Everything should be modular.

Applications should compose reusable packages.

Packages should remain independent from application code.

This allows improvements in one place to benefit every product.

---

## 4. AI-First Engineering

The platform is intentionally designed for AI-assisted development.

Architecture should be predictable.

Folder structures should be consistent.

Documentation should be comprehensive.

Naming conventions should be explicit.

AI coding agents should understand the repository with minimal prompting.

Documentation is considered part of the source code.

---

## 5. Simplicity

Complexity is expensive.

Prefer:

- Simple architecture
- Clear abstractions
- Small services
- Predictable folder structures
- Familiar technologies

Avoid introducing technology simply because it is popular.

---

## 6. Vendor Independence

External services should remain replaceable.

Examples:

Storage:

```
Supabase Storage

↓

Cloudflare R2

↓

AWS S3
```

Payments:

```
Stripe

↓

Future providers
```

Email:

```
SMTP

↓

Resend

↓

Postmark
```

Business logic should never depend directly on vendors.

Always communicate through adapters.

---

## 7. Documentation Driven Development

Every architectural decision should be documented.

Every reusable module should have documentation.

Every package should explain:

- Purpose
- Responsibilities
- Constraints
- Extension points

The documentation should become the engineering handbook for the platform.

---

# Target Developer

The platform is optimized for:

- Solo founders
- Indie hackers
- Technical entrepreneurs
- Small engineering teams
- AI-assisted development

It intentionally avoids enterprise complexity.

---

# Product Strategy

Products should solve one problem exceptionally well.

Do not build large platforms initially.

Instead:

```
Identify Problem

↓

Validate Demand

↓

Build MVP

↓

Launch

↓

Measure

↓

Improve or Archive
```

Small products compound into a valuable portfolio.

---

# Product Lifecycle

Every product follows the same lifecycle.

## Phase 1 — Discovery

Sources include:

- Reddit
- Hacker News
- Product Hunt
- X (Twitter)
- GitHub Discussions
- Developer Communities
- Personal frustration

Look for repeated pain points rather than isolated complaints.

---

## Phase 2 — Validation

Questions to answer:

- Does the problem exist?
- Who experiences it?
- How frequently?
- Are people already paying?
- Can it be solved quickly?

Do not build before validation.

---

## Phase 3 — Development

Clone the platform.

Configure the project.

Implement only the business logic.

Avoid modifying reusable infrastructure unless improvements benefit future products.

---

## Phase 4 — Launch

Deploy immediately.

Collect real-world feedback.

Avoid waiting for perfection.

---

## Phase 5 — Evaluation

Measure:

- Traffic
- Signups
- Activation
- Revenue
- Retention
- Feedback

Data determines future investment.

---

## Phase 6 — Decision

If the product gains traction:

Continue investing.

Otherwise:

Archive it.

Move on.

The platform remains improved regardless of product outcome.

---

# Definition of Success

The platform succeeds if:

- A new SaaS can be started in under one day.
- Authentication is never rewritten.
- Billing is never rewritten.
- Storage is never rewritten.
- AI agents consistently generate high-quality code.
- Every product strengthens the platform.

Success is measured by reduced development time rather than repository size.

---

# Non-Goals

The platform is **not** intended to become:

- A low-code platform
- A visual website builder
- A generic open-source framework
- An enterprise microservices architecture
- A Kubernetes showcase
- A collection of experimental technologies

It is a practical engineering toolkit.

---

# Technology Philosophy

Technology choices should maximize:

- Productivity
- Stability
- Developer experience
- Community support
- AI familiarity

Technology should only change when there is a measurable improvement.

Avoid chasing trends.

---

# Engineering Values

Every contribution should improve at least one of the following:

- Reusability
- Maintainability
- Readability
- Performance
- Developer experience
- AI compatibility
- Documentation
- Testing

If a change improves none of these, reconsider it.

---

# Success Metrics

The platform should continuously reduce:

- Time to first commit
- Time to first deployment
- Time to production
- Repeated engineering effort
- Context switching
- Manual configuration

The platform should continuously increase:

- Code reuse
- Deployment frequency
- Product quality
- Documentation quality
- AI productivity
- Engineering consistency

---

# Guiding Principle

Every engineering decision should answer one question:

> **Will this make the next product easier to build?**

If the answer is **yes**, it aligns with the vision.

If the answer is **no**, reconsider the decision.

The platform exists to compound engineering effort over time.

Every product is an investment in the next one.