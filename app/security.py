import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt


# Secret key used for JWT tokens.
SECRET_KEY = "faceattend-development-secret-change-later"

# JWT signing algorithm.
ALGORITHM = "HS256"

# Token validity period.
ACCESS_TOKEN_EXPIRE_MINUTES = 120


def hash_password(password: str) -> str:
    """
    Create a secure password hash using PBKDF2.
    """

    salt = os.urandom(16)

    iterations = 600_000

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )

    return (
        f"pbkdf2_sha256${iterations}$"
        f"{salt.hex()}${password_hash.hex()}"
    )


def verify_password(
    password: str,
    stored_hash: str,
) -> bool:
    """
    Verify a password against a stored PBKDF2 hash.
    """

    try:
        algorithm, iterations, salt_hex, hash_hex = (
            stored_hash.split("$")
        )

        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations)

        salt = bytes.fromhex(salt_hex)

        expected_hash = bytes.fromhex(hash_hex)

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )

        return hmac.compare_digest(
            actual_hash,
            expected_hash,
        )

    except (ValueError, TypeError):
        return False


def create_access_token(company_id: int) -> str:
    """
    Create a JWT token containing the company ID.
    """

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(company_id),
        "type": "company",
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> int:
    """
    Decode the JWT token and return the company ID.
    """

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        company_id = payload.get("sub")

        token_type = payload.get("type")

        if not company_id:
            raise ValueError("Missing company ID.")

        if token_type != "company":
            raise ValueError("Invalid token type.")

        return int(company_id)

    except (JWTError, ValueError, TypeError):
        raise ValueError(
            "Invalid or expired token."
        )