# Authentication Guide

> Authentication, authorization, identity management, and security standards for FastForge.

---

# Purpose

Authentication is one of the core platform modules.

It should be completely reusable across every product.

The objective is to build the authentication system **once** and never rewrite it again.

This package is responsible for:

- Users
- Login
- Registration
- Sessions
- JWT
- Refresh Tokens
- OAuth
- Email Verification
- Password Reset
- Roles
- Permissions
- Organizations
- API Keys

---

# Design Principles

Authentication should be:

- Secure
- Stateless where possible
- Extensible
- Vendor-independent
- Easy to understand

Security should never be sacrificed for convenience.

---

# Responsibilities

The Authentication package owns:

- User lifecycle
- Credential validation
- Password hashing
- Session management
- Token generation
- Authorization helpers
- Current user resolution
- OAuth integration
- Email verification
- Password reset

Other packages should never implement authentication logic.

---

# User Model

Every product shares the same base user model.

Minimum fields:

```text
id

email

password_hash

full_name

avatar_url

is_active

is_verified

last_login_at

created_at

updated_at
```

Optional fields:

```text
timezone

locale

phone

metadata
```

Avoid product-specific fields in the shared user model.

---

# Identity

The email address is the primary identity.

Rules:

- Unique
- Case-insensitive
- Verified before sensitive actions

Future support for username login can be added without breaking existing APIs.

---

# Registration Flow

```
User

↓

Validate Request

↓

Check Existing User

↓

Hash Password

↓

Create User

↓

Create Verification Token

↓

Queue Verification Email

↓

Return Success
```

Registration should not automatically authenticate the user unless explicitly configured.

---

# Login Flow

```
Email + Password

↓

Validate Input

↓

Lookup User

↓

Verify Password

↓

Check Active Status

↓

Generate Access Token

↓

Generate Refresh Token

↓

Update Last Login

↓

Return Tokens
```

---

# Password Hashing

Use:

```
Argon2id
```

Alternative:

```
bcrypt
```

Never:

- Encrypt passwords
- Store plaintext
- Log passwords

Passwords are never recoverable.

---

# Password Policy

Minimum recommendations:

- 12 characters
- Mixed case
- Number
- Special character

Enforcement should remain configurable.

Avoid arbitrary complexity rules that harm usability.

---

# Password Reset

Flow:

```
Forgot Password

↓

Generate Reset Token

↓

Queue Email

↓

User Opens Link

↓

Validate Token

↓

Choose New Password

↓

Invalidate Token

↓

Success
```

Reset tokens:

- Single use
- Short-lived
- Random
- Cryptographically secure

---

# Email Verification

Verification flow:

```
Register

↓

Verification Email

↓

Verification Link

↓

Validate Token

↓

Mark Verified
```

Verification tokens should expire automatically.

---

# Sessions

Support multiple active sessions.

Examples:

```
Laptop

Phone

Tablet
```

Users should be able to revoke sessions individually.

---

# JWT Strategy

Two-token approach:

Access Token

- Short lifetime
- Sent with API requests

Refresh Token

- Longer lifetime
- Used only to refresh access tokens

Never use refresh tokens as authentication tokens.

---

# JWT Claims

Recommended claims:

```
sub

email

role

organization_id

session_id

exp

iat
```

Keep tokens small.

Avoid embedding frequently changing data.

---

# Token Lifetime

Recommended defaults:

Access Token:

```
15 minutes
```

Refresh Token:

```
30 days
```

Values should be configurable.

---

# Token Revocation

Support revocation for:

- Logout
- Password reset
- Email change
- Suspicious activity

Revoked refresh tokens must not be reusable.

---

# Logout

Logout should:

- Invalidate refresh token
- Optionally revoke current session
- Leave other sessions untouched unless requested

Support:

```
Logout Current Session

Logout All Sessions
```

---

# OAuth

Initial providers:

- Google
- GitHub

Future:

- Microsoft
- GitLab
- Apple

Each provider implements the same adapter interface.

---

# OAuth Flow

```
User

↓

Provider

↓

Authorization Code

↓

Exchange Token

↓

Retrieve Profile

↓

Create or Link User

↓

Generate Session

↓

Return Tokens
```

---

# Account Linking

Allow multiple providers for one account.

Example:

```
Email

+

Google

+

GitHub
```

Link accounts by verified email where appropriate.

---

# Current User

Provide a reusable dependency:

```python
CurrentUser
```

Every authenticated endpoint should use the same dependency.

Avoid duplicating authentication logic.

---

# Authorization

Authentication answers:

> Who is the user?

Authorization answers:

> What may the user do?

Keep these concerns separate.

---

# Roles

Base roles:

```
Admin

Member
```

Future products may extend roles.

Roles should remain simple.

Use permissions for fine-grained control.

---

# Permissions

Examples:

```
projects:create

projects:update

projects:delete

billing:view

billing:update

api_keys:create
```

Permission names should follow:

```
resource:action
```

---

# Organizations

Many products require organization support.

Relationships:

```
Organization

↓

Members

↓

Users
```

A user may belong to multiple organizations.

Organization context should be explicit in authenticated requests.

---

# Organization Membership

Membership should be modeled explicitly.

Relationship:

```text
User

↓

OrganizationMember

↓

Organization
```

The membership table should contain:

```text
id

organization_id

user_id

role

status

joined_at

created_at
```

Benefits:

- Multiple organizations per user
- Organization-specific roles
- Invitations
- Future billing support

---

# Organization Roles

Roles apply within an organization.

Recommended defaults:

```text
Owner

Admin

Member
```

Responsibilities:

Owner

- Delete organization
- Manage billing
- Transfer ownership

Admin

- Manage members
- Manage projects
- Manage API keys

Member

- Access assigned resources

Authorization should always check both:

- User
- Organization Context

---

# Invitation Flow

Organization invitations should follow this workflow:

```
Owner

↓

Invite User

↓

Generate Invitation Token

↓

Queue Email

↓

User Accepts

↓

Create Membership

↓

Invalidate Invitation
```

Invitation tokens should:

- Expire automatically
- Be single-use
- Be cryptographically secure

---

# API Keys

Developer-focused products should support API keys.

Structure:

```text
id

user_id

organization_id

name

prefix

hashed_key

last_used_at

expires_at

created_at
```

Never store plaintext API keys.

---

# API Key Format

Example:

```text
fastforge_live_xxxxxxxxxxxxxxxxx
```

Separate environments:

```text
fastforge_live_

fastforge_test_
```

Prefixes make debugging easier and reduce accidental misuse.

---

# API Key Authentication

Flow:

```text
Incoming Request

↓

Extract API Key

↓

Lookup Prefix

↓

Verify Hash

↓

Resolve User

↓

Resolve Organization

↓

Check Permissions

↓

Continue Request
```

All API key validation should happen through the Authentication package.

---

# Session Management

Users should be able to:

- View active sessions
- Revoke individual sessions
- Revoke all sessions
- View last activity
- View IP address (if stored)
- View device information (if available)

This improves account security and user trust.

---

# Device Tracking

Optional session metadata:

```text
Device

Browser

Operating System

IP Address

Last Activity
```

Treat this as user-facing information, not a security boundary.

---

# Security Headers

The backend should include standard security headers.

Examples:

- HSTS
- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy
- Content-Security-Policy (where appropriate)

Security headers should be configured centrally.

---

# Cookies

For web applications:

Use:

- Secure
- HttpOnly
- SameSite=Lax (or Strict where appropriate)

Never expose refresh tokens to JavaScript.

---

# Rate Limiting

Authentication endpoints require stricter limits.

Examples:

```text
Login

5 attempts / minute
```

Password reset:

```text
3 requests / hour
```

Email verification resend:

```text
5 requests / day
```

Limits should be configurable.

---

# Brute Force Protection

Implement protections for:

- Login attempts
- Password reset abuse
- Verification spam

Possible strategies:

- Redis counters
- Temporary lockouts
- Progressive delays

Avoid permanent account lockouts.

---

# Multi-Factor Authentication (Future)

The authentication package should remain ready for MFA.

Future methods:

- TOTP
- Passkeys (WebAuthn)
- Security Keys

Initial implementation is out of scope, but the architecture should not prevent it.

---

# Audit Logging

Authentication events should be logged.

Examples:

- Login
- Logout
- Failed login
- Password change
- Password reset
- Email verification
- Session revoked
- API key created
- API key revoked

Audit logs should be immutable.

---

# Authentication Middleware

Authentication middleware should:

- Resolve identity
- Validate tokens
- Attach current user
- Reject unauthorized requests

Authorization remains the responsibility of services.

---

# Authorization Helpers

Provide reusable helpers such as:

```python
require_authenticated_user()

require_verified_email()

require_organization_member()

require_permission("projects:create")
```

These helpers should simplify route definitions while keeping business logic in services.

---

# Testing Strategy

Authentication requires comprehensive testing.

Unit Tests:

- Password hashing
- Token generation
- Permission helpers

Integration Tests:

- Login
- Registration
- OAuth
- Session management

API Tests:

- Protected routes
- Token refresh
- Logout
- Password reset

Security-sensitive code should have high test coverage.

---

# Security Checklist

Every authentication change should verify:

- [ ] Passwords are hashed
- [ ] Tokens expire correctly
- [ ] Refresh tokens rotate or revoke properly
- [ ] Email verification enforced where required
- [ ] API keys are hashed
- [ ] Authorization checks exist
- [ ] Rate limiting configured
- [ ] Audit logging included
- [ ] Tests updated

---

# Anti-Patterns

Avoid:

- Plaintext passwords
- Plaintext API keys
- Long-lived access tokens
- LocalStorage for refresh tokens
- Authorization checks in repositories
- Hardcoded roles
- Duplicated authentication logic
- Logging sensitive credentials
- Trusting client-provided user IDs
- Skipping email verification for sensitive actions

---

# Authentication Definition of Done

An authentication feature is complete only when:

- Identity is securely verified.
- Authorization is enforced.
- Sensitive data is protected.
- Tokens are managed correctly.
- Audit logs are generated.
- Rate limits are applied.
- Tests pass.
- Documentation is updated.

---

# Summary

Authentication is the security foundation of every product built on FastForge.

The system should remain:

- Secure
- Predictable
- Extensible
- Vendor-independent
- Reusable

Every product should consume this package rather than implementing its own authentication logic.

Building it correctly once eliminates one of the highest-risk areas of future product development.