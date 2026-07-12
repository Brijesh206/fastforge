# Storage Guide

> Reusable file storage architecture for every product built on FastForge.

---

# Purpose

Almost every SaaS product needs file storage.

Rather than coupling applications directly to a storage provider, FastForge provides a reusable storage abstraction.

Applications should never know whether files are stored in:

- Supabase Storage
- Cloudflare R2
- AWS S3
- MinIO
- Local Storage (development)

The application only communicates with `StorageService`.

---

# Design Principles

The storage system should be:

- Vendor Independent
- Secure
- Scalable
- Observable
- Easy to Replace
- Easy to Test

The implementation should change without affecting business logic.

---

# Responsibilities

The Storage package owns:

- File uploads
- File downloads
- Signed URLs
- Public URLs
- File deletion
- Bucket management
- Metadata
- Storage providers
- Content validation

Applications should never import provider SDKs directly.

---

# Architecture

```text
Application

↓

StorageService

↓

StorageProvider

↓

StorageAdapter

↓

Storage Provider

↓

Stored File
```

Future providers can be added by implementing the StorageProvider interface.

---

# Supported Providers

Initial:

- Supabase Storage

Future:

- Cloudflare R2
- AWS S3
- MinIO
- Google Cloud Storage
- Azure Blob Storage

The interface remains unchanged.

---

# Storage Provider Interface

Every provider implements the same contract.

Required methods:

```python
upload()

download()

delete()

exists()

copy()

move()

get_public_url()

generate_signed_url()

list_files()
```

Applications should depend only on this interface.

---

# Buckets

Organize files into logical buckets.

Examples:

```
avatars

documents

uploads

exports

reports

attachments
```

Avoid placing unrelated files in the same bucket.

---

# Naming Strategy

Object names should be predictable.

Recommended format:

```text
<resource>/<uuid>/<filename>
```

Example:

```text
avatars/

3e3a7f0e.../

profile.png
```

Avoid exposing user-generated filenames directly as object keys.

---

# File Metadata

Store metadata separately from file contents.

Recommended fields:

```text
id

bucket

path

filename

mime_type

size

owner_id

organization_id

checksum

created_at
```

Metadata belongs in PostgreSQL.

The file belongs in object storage.

---

# Ownership

Every uploaded file should have a clear owner.

Examples:

```text
owner_id

organization_id
```

Authorization should be enforced before generating download URLs.

---

# Upload Flow

```
Client

↓

API

↓

StorageService

↓

StorageProvider

↓

Storage Backend

↓

Metadata Saved

↓

Response
```

Business logic should not depend on storage implementation.

---

# Download Flow

```
Client

↓

API

↓

Authorization

↓

StorageService

↓

Signed URL

↓

Storage Provider
```

Private files should never expose raw provider URLs.

---

# Public Files

Examples:

- Logos
- Public avatars
- Marketing assets

These may use public URLs.

Public access should be explicit.

---

# Private Files

Examples:

- Reports
- Exports
- User documents
- Billing invoices

Private files should always use signed URLs.

Never expose permanent public links.

---

# Signed URLs

Signed URLs should:

- Expire automatically
- Be generated on demand
- Never be stored permanently

Example expiration:

```
15 minutes
```

Expiration should be configurable.

---

# File Validation

Validate uploads before storage.

Check:

- MIME type
- File size
- Extension
- Filename
- Virus scanning (future)

Validation should happen before uploading.

---

# File Size Limits

Configure limits per bucket.

Example:

```text
Avatars

5 MB
```

```text
Documents

25 MB
```

```text
Exports

500 MB
```

Limits should remain configurable.

---

# Allowed MIME Types

Whitelist MIME types.

Example:

```
image/png

image/jpeg

application/pdf

text/csv
```

Avoid relying solely on file extensions.

---

# Duplicate Files

Optional optimization:

Use checksum comparison.

Benefits:

- Storage savings
- Faster uploads

This should remain optional.

---

# File Deletion

Deletion flow:

```
Application

↓

Authorization

↓

Delete Metadata

↓

Delete Storage Object
```

Both metadata and file should remain synchronized.

---

# Soft Delete

For important resources, consider:

```
deleted_at
```

before permanent deletion.

This enables recovery when required.

---

# Moving Files

Applications should request moves through StorageService.

Never manipulate object keys directly.

Example:

```
Temporary Upload

↓

Permanent Location
```

---

# Copying Files

Support provider-independent copy operations.

Avoid downloading and re-uploading when providers support native copy.

---

# Temporary Uploads

Temporary uploads should expire automatically.

Examples:

- Import files
- Draft attachments

Background jobs should clean expired objects.

---

# Image Storage

Images should remain in original quality.

Future processing:

- Resize
- Thumbnails
- Compression
- WebP conversion

Image processing belongs in background workers.

Never block uploads waiting for transformations.

---

# CDN Strategy

Every production deployment should serve static assets through a CDN.

Initial provider support:

- Supabase CDN

Future providers:

- Cloudflare CDN
- CloudFront
- Fastly

Applications should never depend on CDN-specific URLs.

The Storage Provider is responsible for generating the correct URL.

---

# Image Processing

Image transformations should happen asynchronously.

Examples:

- Thumbnail generation
- Image resizing
- WebP conversion
- AVIF conversion
- Compression
- Watermarking (future)

Workflow:

```text
Upload

↓

Store Original

↓

Queue Job

↓

Generate Variants

↓

Store Variants

↓

Update Metadata
```

Always preserve the original image.

---

# Image Variants

Recommended variants:

```text
thumbnail

small

medium

large

original
```

Applications should request variants through StorageService rather than constructing paths manually.

---

# Background Jobs

Storage workers may handle:

- Image processing
- Cleanup of temporary uploads
- Expired signed URL cleanup (if applicable)
- Metadata synchronization
- Orphan file detection
- Storage migration

Large file operations should never block HTTP requests.

---

# Lifecycle Policies

Configure lifecycle rules per bucket.

Examples:

Temporary uploads:

```text
Delete after 24 hours
```

Exports:

```text
Delete after 30 days
```

Backups:

```text
Archive after 90 days
```

Lifecycle policies should be provider-managed whenever possible.

---

# Storage Migration

Future provider migration should follow this process:

```text
Old Provider

↓

Copy Objects

↓

Verify Integrity

↓

Update Metadata

↓

Switch Provider

↓

Remove Old Objects
```

Applications should continue using StorageService throughout the migration.

---

# Checksums

Store a checksum for uploaded files.

Recommended:

```text
SHA-256
```

Benefits:

- Integrity verification
- Duplicate detection
- Migration validation

Checksums should be calculated once during upload.

---

# Versioning

Support optional file versioning.

Useful for:

- Documents
- Reports
- Generated assets

Version history should be modeled separately from object paths.

---

# Security

All uploads should enforce:

- Authorization
- Size validation
- MIME validation
- Filename sanitization

Never trust client-provided metadata.

The backend is the authority.

---

# Signed Upload URLs (Future)

Large files may use direct uploads.

Workflow:

```text
Client

↓

Request Upload URL

↓

StorageService

↓

Signed Upload URL

↓

Client Uploads Directly

↓

Completion Callback

↓

Metadata Saved
```

This reduces backend bandwidth usage.

---

# File Permissions

Each file should define its visibility.

Supported values:

```text
public

private
```

Visibility should be explicit.

Avoid implicit defaults.

---

# Audit Logging

Log important storage events.

Examples:

- Upload completed
- File deleted
- Signed URL generated
- Storage migration
- Bucket cleanup

Do not log sensitive file contents.

---

# Monitoring

Track metrics such as:

- Upload count
- Download count
- Storage usage
- Error rate
- Upload duration
- Download duration

These metrics help identify bottlenecks and estimate storage costs.

---

# Cost Optimization

Monitor storage growth.

Recommendations:

- Delete temporary files automatically
- Compress images
- Remove orphaned objects
- Archive infrequently accessed files
- Avoid duplicate uploads

Storage costs should remain predictable.

---

# Backup Strategy

Critical uploads should be backed up.

Options include:

- Provider-managed backups
- Cross-region replication
- Secondary storage provider

Backup strategy should match business requirements.

---

# Local Development

Use one of:

- Local filesystem
- MinIO
- Supabase local stack

Developers should not require cloud credentials for basic development.

The provider should be selected through configuration.

---

# Testing Strategy

Storage testing should include:

## Unit Tests

Test:

- StorageService
- Path generation
- Validation logic

Mock provider implementations.

---

## Integration Tests

Test:

- Upload
- Download
- Delete
- Signed URLs

Use a local storage provider where possible.

---

## End-to-End Tests

Critical workflows:

- Avatar upload
- Report export
- File download
- Permission enforcement

Verify the complete user experience.

---

# Error Handling

Return standardized errors.

Examples:

```text
FILE_TOO_LARGE

INVALID_FILE_TYPE

FILE_NOT_FOUND

UPLOAD_FAILED

ACCESS_DENIED
```

Avoid leaking provider-specific errors to clients.

---

# Configuration

Storage configuration should include:

```text
Provider

Bucket Names

Maximum File Size

Allowed MIME Types

Signed URL Expiration

Public Base URL
```

Configuration belongs in Pydantic Settings.

Never hardcode storage values.

---

# Storage Checklist

Before shipping storage functionality:

- [ ] Provider abstraction implemented
- [ ] Validation configured
- [ ] Authorization enforced
- [ ] Metadata stored
- [ ] Signed URLs implemented
- [ ] Background jobs configured
- [ ] Lifecycle policies reviewed
- [ ] Tests passing
- [ ] Monitoring enabled
- [ ] Documentation updated

---

# Anti-Patterns

Avoid:

- Direct provider SDK usage in application code
- Public URLs for private files
- Trusting client MIME types
- Storing metadata only in object storage
- Hardcoded bucket names
- Blocking requests during image processing
- Manual path generation across the codebase
- Exposing provider-specific errors

---

# Storage Definition of Done

A storage feature is complete only when:

- Provider abstraction is respected.
- Validation is enforced.
- Authorization is verified.
- Metadata is synchronized.
- Signed URLs are supported where required.
- Background processing is configured.
- Tests pass.
- Documentation is updated.

---

# Summary

The Storage package provides a provider-independent abstraction for all file operations.

Applications interact only with `StorageService`, allowing storage providers to change without affecting business logic.

This architecture supports:

- Secure uploads
- Private and public assets
- Signed URLs
- Background image processing
- Lifecycle management
- Future provider migration

By isolating storage concerns, every future product can reuse the same implementation with minimal configuration, accelerating development while maintaining consistency and scalability.