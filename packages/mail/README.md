# fastforge-mail

Transactional email for FastForge. Provider-independent, template-driven, and
built on the standard library — no new dependencies.

## Architecture

```text
Application → EmailService → EmailProvider (interface) → SMTP / console
```

Applications depend on `EmailService` only. They never import a provider.

## Usage

```python
from fastforge_mail import EmailService, MailSettings, create_email_provider

settings = MailSettings()
service = EmailService(create_email_provider(settings), settings)

await service.send_verification_email(
    to="user@example.com",
    verification_url="https://app.example.com/verify?token=...",
    expires_in="24 hours",
)
```

Send from a FastAPI route with `BackgroundTasks` so the HTTP request never
waits on the mail server.

## Providers

| `MAIL_PROVIDER` | Behaviour |
|---|---|
| `console` (default) | Logs the email instead of sending it. Development only. |
| `smtp` | Delivers over SMTP. Point it at Mailpit locally (`docker compose up -d mailpit`, inbox at <http://localhost:8025>) or a real provider in production. |

The default is `console`, so a fresh checkout cannot email a real person by
accident.

## Templates

Templates live in `src/fastforge_mail/templates/` as `<name>.html` and
`<name>.txt` pairs. Every HTML email is wrapped in `_layout.html`, which
carries the product name and support address.

Rendering uses `string.Template`. Values are HTML-escaped in the HTML part, so
a hostile URL or product name cannot inject markup. `$` inside a value (say, a
price in a URL) is safe — values are never re-scanned.

Currently shipped: `verify_email`, `password_reset`.

## Configuration

All settings are read from the environment with the `MAIL_` prefix. See
`.env.example`.

## Not implemented yet

Deliberately out of scope until something needs them:

- **Retries / queue.** A send that fails is logged and lost. Add a worker
  queue when a dropped verification email actually costs something.
- **Rate limiting.** Needs Redis (post-v1).
- **Bounce and complaint webhooks, delivery tracking, localization,
  attachments, batch sending.**

See `docs/11-email.md` for the full target design.
