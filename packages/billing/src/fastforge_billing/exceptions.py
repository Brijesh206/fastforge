"""Billing exceptions, built on the shared error hierarchy."""

from http import HTTPStatus

from fastforge_common.exceptions import AppError, AuthorizationError


class BillingError(AppError):
    """Base for billing failures."""

    message = "A billing error occurred."


class BillingNotConfiguredError(BillingError):
    """Raised when a Stripe credential needed for the operation is missing."""

    status_code = HTTPStatus.SERVICE_UNAVAILABLE
    message = "Billing is not configured."


class WebhookVerificationError(BillingError):
    """Raised when a webhook signature or payload fails verification."""

    status_code = HTTPStatus.BAD_REQUEST
    message = "The webhook could not be verified."


class NoActiveSubscriptionError(AuthorizationError):
    """Raised when an action requires an active subscription and there is none."""

    message = "An active subscription is required."
