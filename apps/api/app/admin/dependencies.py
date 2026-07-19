"""Admin dependencies: the admin gate and the admin service."""

from fastapi import Depends
from fastforge_auth import User, UserRepository
from fastforge_billing import SubscriptionRepository
from fastforge_common.exceptions import AuthorizationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.service import AdminService
from app.auth.dependencies import get_current_user
from app.config import get_settings
from app.dependencies.database import get_db_transaction


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Allow only verified users whose email is on the ADMIN_EMAILS allowlist.

    Verification is required so an attacker cannot gain admin by registering
    an allowlisted address before its real owner does — only someone who can
    read that inbox can become admin.

    Returns 403 for authenticated non-admins, 401 for unauthenticated callers
    (raised earlier by get_current_user).
    """
    if not current_user.is_verified or not get_settings().is_admin(current_user.email):
        raise AuthorizationError("Admin access required.")
    return current_user


def get_admin_service(
    session: AsyncSession = Depends(get_db_transaction),
) -> AdminService:
    """Build the admin service. Uses a transactional session so the write
    endpoints (activate/deactivate) commit; reads are unaffected."""
    return AdminService(UserRepository(session), SubscriptionRepository(session))
