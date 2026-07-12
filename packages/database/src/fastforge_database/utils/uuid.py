"""UUID utilities."""

import secrets
import time
import uuid

_UUID7_VERSION = 0x7
_UUID_VARIANT_RFC_4122 = 0b10
_UUID_TIMESTAMP_BITS = 48
_UUID_RANDOM_A_BITS = 12
_UUID_RANDOM_B_BITS = 62


def generate_uuid7() -> uuid.UUID:
    """Generate a UUIDv7 identifier.

    UUIDv7 keeps identifiers sortable by creation time while preserving enough
    random entropy for distributed inserts.
    """
    timestamp_ms = int(time.time() * 1000) & ((1 << _UUID_TIMESTAMP_BITS) - 1)
    random_a = secrets.randbits(_UUID_RANDOM_A_BITS)
    random_b = secrets.randbits(_UUID_RANDOM_B_BITS)

    value = timestamp_ms << 80
    value |= _UUID7_VERSION << 76
    value |= random_a << 64
    value |= _UUID_VARIANT_RFC_4122 << 62
    value |= random_b

    return uuid.UUID(int=value)
