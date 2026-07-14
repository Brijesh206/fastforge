"""Email schemas."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmailMessage(BaseModel):
    """A rendered email, ready for a provider to deliver.

    The recipient is validated here so an invalid address fails before it
    reaches a provider.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    to: EmailStr
    subject: str = Field(min_length=1, max_length=200)
    html: str = Field(min_length=1)
    text: str = Field(min_length=1)
