"""Authentication provider contracts.

Services depend on these interfaces, never on a concrete adapter or
provider SDK directly, so implementations can be swapped without
changing business logic.
"""

from fastforge_auth.interfaces.password_hasher import PasswordHasher
from fastforge_auth.interfaces.token_service import TokenService

__all__ = ["PasswordHasher", "TokenService"]
