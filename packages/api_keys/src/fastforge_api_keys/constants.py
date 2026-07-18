"""API key constants."""

# Prefixes every issued key, so a token in a log or header is immediately
# recognizable as an API key rather than a JWT — and lets the app layer route
# an incoming Authorization header to the right verification path by a cheap
# string check, before touching the database.
API_KEY_PREFIX = "ffk_"

# Characters of the raw key stored in plaintext (key_prefix) for display in a
# key-management UI, e.g. "ffk_xK9f2Lq…". Never enough to reconstruct the key.
DISPLAY_PREFIX_LENGTH = 12

DEFAULT_RATE_LIMIT_PER_MINUTE = 60
DEFAULT_RATE_LIMIT_WINDOW_SECONDS = 60
