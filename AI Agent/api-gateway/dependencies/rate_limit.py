"""Rate limiting dependencies."""

from slowapi import Limiter
from slowapi.util import get_remote_address


def get_user_identifier(request) -> str:
    """Get rate limit key - uses IP by default."""
    return get_remote_address(request)


limiter = Limiter(key_func=get_user_identifier)
