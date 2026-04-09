"""Password hashing and verification helpers using bcrypt."""

import bcrypt

from app.core.config import get_settings


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password with bcrypt.

    Uses configured rounds, with an enforced minimum cost of 12.
    """
    if not plain_password:
        raise ValueError("Password must not be empty.")

    settings = get_settings()
    rounds = max(12, settings.bcrypt_rounds)
    hashed = bcrypt.hashpw(
        plain_password.encode("utf-8"),
        bcrypt.gensalt(rounds=rounds),
    )
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    if not plain_password or not hashed_password:
        return False

    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        # Invalid hash format
        return False
