"""Rendering of transactional email templates.

Templates are plain files rendered with string.Template. Values are HTML
escaped before substitution, so a hostile name or URL cannot inject markup
into the HTML part.
"""

from collections.abc import Mapping
from html import escape
from pathlib import Path
from string import Template

from fastforge_mail.exceptions import TemplateNotFoundError

TEMPLATE_DIR = Path(__file__).parent / "templates"
_LAYOUT = "_layout.html"


def _read(filename: str) -> str:
    try:
        return (TEMPLATE_DIR / filename).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise TemplateNotFoundError(f"Email template '{filename}' does not exist.") from exc


def render(name: str, variables: Mapping[str, str]) -> tuple[str, str]:
    """Render template `name` and return its (html, text) parts.

    Requires `product_name` and `support_email` in `variables`; the shared
    layout wraps every HTML email with them.
    """
    escaped = {key: escape(value) for key, value in variables.items()}

    body = Template(_read(f"{name}.html")).substitute(escaped)
    html = Template(_read(_LAYOUT)).substitute(
        content=body,
        product_name=escaped["product_name"],
        support_email=escaped["support_email"],
    )
    text = Template(_read(f"{name}.txt")).substitute(variables)
    return html, text
