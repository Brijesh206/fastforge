"""Tests for EmailService."""

import pytest
from fastforge_mail.config import MailSettings
from fastforge_mail.interfaces.email_provider import EmailProvider
from fastforge_mail.schemas import EmailMessage
from fastforge_mail.service import EmailService, create_email_provider
from pydantic import ValidationError


class FakeProvider(EmailProvider):
    """Captures messages instead of delivering them."""

    def __init__(self) -> None:
        self.sent: list[EmailMessage] = []

    async def send(self, message: EmailMessage) -> None:
        self.sent.append(message)


def _service() -> tuple[EmailService, FakeProvider]:
    provider = FakeProvider()
    settings = MailSettings(
        MAIL_PRODUCT_NAME="Acme", MAIL_SUPPORT_EMAIL="help@acme.test", _env_file=None
    )
    return EmailService(provider, settings), provider


async def test_send_verification_email_renders_subject_and_link() -> None:
    service, provider = _service()

    await service.send_verification_email(
        to="user@example.com",
        verification_url="https://acme.test/verify?token=t1",
        expires_in="24 hours",
    )

    message = provider.sent[0]
    assert message.to == "user@example.com"
    assert message.subject == "Verify your Acme email"
    assert "https://acme.test/verify?token=t1" in message.text
    assert "https://acme.test/verify?token=t1" in message.html
    assert "help@acme.test" in message.html


async def test_send_password_reset_email_renders_subject_and_link() -> None:
    service, provider = _service()

    await service.send_password_reset_email(
        to="user@example.com", reset_url="https://acme.test/reset?token=t2", expires_in="1 hour"
    )

    message = provider.sent[0]
    assert message.subject == "Reset your Acme password"
    assert "https://acme.test/reset?token=t2" in message.text
    assert "1 hour" in message.text


async def test_send_rejects_an_invalid_recipient_before_reaching_the_provider() -> None:
    service, provider = _service()

    with pytest.raises(ValidationError):
        await service.send_verification_email(
            to="not-an-email", verification_url="https://acme.test/verify", expires_in="24 hours"
        )

    assert provider.sent == []


def test_create_email_provider_selects_the_configured_provider() -> None:
    console = create_email_provider(MailSettings(MAIL_PROVIDER="console", _env_file=None))
    smtp = create_email_provider(MailSettings(MAIL_PROVIDER="smtp", _env_file=None))

    assert type(console).__name__ == "ConsoleEmailProvider"
    assert type(smtp).__name__ == "SmtpEmailProvider"
