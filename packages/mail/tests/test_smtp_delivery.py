"""End-to-end delivery test against a real SMTP server on a real socket.

Mocking smtplib proves nothing about the bytes on the wire. This runs a
minimal SMTP sink so the MIME message, the connection, and the send path are
all genuinely exercised. No Docker required.
"""

import asyncio

from fastforge_mail.adapters.smtp_provider import SmtpEmailProvider
from fastforge_mail.config import MailSettings
from fastforge_mail.service import EmailService


class SmtpSink:
    """Accepts one SMTP conversation and records the DATA payload."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    async def _handle(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        body: list[bytes] = []
        reading_data = False
        writer.write(b"220 localhost SMTP\r\n")
        await writer.drain()

        while line := await reader.readline():
            if reading_data:
                if line == b".\r\n":
                    reading_data = False
                    self.messages.append(b"".join(body).decode())
                    writer.write(b"250 OK\r\n")
                else:
                    body.append(line)
                    continue
            elif line.upper().startswith(b"DATA"):
                reading_data = True
                writer.write(b"354 End data with <CR><LF>.<CR><LF>\r\n")
            elif line.upper().startswith(b"QUIT"):
                writer.write(b"221 Bye\r\n")
                await writer.drain()
                break
            else:
                # EHLO/HELO/MAIL FROM/RCPT TO — advertise no extensions.
                writer.write(b"250 localhost\r\n")
            await writer.drain()

        writer.close()


async def test_verification_email_is_delivered_over_smtp() -> None:
    sink = SmtpSink()
    server = await asyncio.start_server(sink._handle, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]

    async with server:
        settings = MailSettings(
            MAIL_PROVIDER="smtp",
            MAIL_SMTP_HOST="127.0.0.1",
            MAIL_SMTP_PORT=port,
            MAIL_SMTP_USE_TLS=False,
            MAIL_FROM_ADDRESS="no-reply@acme.test",
            MAIL_FROM_NAME="Acme",
            MAIL_PRODUCT_NAME="Acme",
            MAIL_SUPPORT_EMAIL="help@acme.test",
            _env_file=None,
        )
        service = EmailService(SmtpEmailProvider(settings), settings)

        await service.send_verification_email(
            to="user@example.com",
            verification_url="https://acme.test/verify?token=live",
            expires_in="24 hours",
        )

    delivered = sink.messages[0]
    assert "Subject: Verify your Acme email" in delivered
    assert "To: user@example.com" in delivered
    assert "From: Acme <no-reply@acme.test>" in delivered
    assert "text/plain" in delivered
    assert "text/html" in delivered
    # The action URL survives MIME encoding (quoted-printable may wrap lines).
    assert "https://acme.test/verify?token=live" in delivered.replace("=\r\n", "")
