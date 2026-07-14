"""Tests for the SMTP provider."""

import smtplib

import pytest
from fastforge_mail.adapters.smtp_provider import SmtpEmailProvider
from fastforge_mail.config import MailSettings
from fastforge_mail.exceptions import EmailSendError
from fastforge_mail.schemas import EmailMessage

MESSAGE = EmailMessage(
    to="user@example.com",
    subject="Verify your email",
    html="<p>hello</p>",
    text="hello",
)


def _provider() -> SmtpEmailProvider:
    return SmtpEmailProvider(
        MailSettings(
            MAIL_FROM_ADDRESS="no-reply@acme.test",
            MAIL_FROM_NAME="Acme",
            MAIL_REPLY_TO="help@acme.test",
            _env_file=None,
        )
    )


def test_build_mime_message_sets_headers_and_both_body_parts() -> None:
    mime = _provider().build_mime_message(MESSAGE)

    assert mime["From"] == "Acme <no-reply@acme.test>"
    assert mime["To"] == "user@example.com"
    assert mime["Subject"] == "Verify your email"
    assert mime["Reply-To"] == "help@acme.test"

    types = {part.get_content_type() for part in mime.walk()}
    assert {"text/plain", "text/html"} <= types


async def test_send_wraps_provider_failure_in_email_send_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def explode(*args: object, **kwargs: object) -> None:
        raise smtplib.SMTPConnectError(421, "unavailable")

    monkeypatch.setattr(smtplib, "SMTP", explode)

    with pytest.raises(EmailSendError):
        await _provider().send(MESSAGE)
