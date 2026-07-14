"""Tests for email template rendering."""

import pytest
from fastforge_mail.exceptions import TemplateNotFoundError
from fastforge_mail.rendering import render

VARIABLES = {
    "action_url": "https://app.example.com/verify?token=abc123",
    "expires_in": "24 hours",
    "product_name": "FastForge",
    "support_email": "support@example.com",
}


def test_render_returns_html_and_text_containing_the_action_url() -> None:
    html, text = render("verify_email", VARIABLES)

    assert "https://app.example.com/verify?token=abc123" in html
    assert "https://app.example.com/verify?token=abc123" in text
    assert "$action_url" not in html
    assert "$action_url" not in text


def test_render_wraps_html_in_the_shared_layout() -> None:
    html, _ = render("password_reset", VARIABLES)

    assert html.startswith("<!doctype html>")
    assert "support@example.com" in html
    assert "Reset your password" in html


def test_render_escapes_html_in_values() -> None:
    hostile = {**VARIABLES, "product_name": "<script>alert(1)</script>"}

    html, text = render("verify_email", hostile)

    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    # The plain text part is not markup, so it is not escaped.
    assert "<script>" in text


def test_render_preserves_dollar_signs_in_values() -> None:
    with_dollar = {**VARIABLES, "action_url": "https://example.com/r?p=$99&t=x"}

    html, text = render("verify_email", with_dollar)

    assert "p=$99" in text
    assert "p=$99" in html


def test_render_raises_for_unknown_template() -> None:
    with pytest.raises(TemplateNotFoundError):
        render("does_not_exist", VARIABLES)
