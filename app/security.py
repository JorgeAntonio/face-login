import base64
import hashlib
import hmac
import os

from app.config import PBKDF2_ITERATIONS


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return "$".join(
        [
            "pbkdf2_sha256",
            str(PBKDF2_ITERATIONS),
            base64.b64encode(salt).decode("ascii"),
            base64.b64encode(derived_key).decode("ascii"),
        ]
    )


def verify_password(password: str, password_hash: str) -> bool:
    algorithm, iterations, salt_b64, hash_b64 = password_hash.split("$")
    if algorithm != "pbkdf2_sha256":
        return False

    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        base64.b64decode(salt_b64.encode("ascii")),
        int(iterations),
    )
    return hmac.compare_digest(
        derived_key,
        base64.b64decode(hash_b64.encode("ascii")),
    )
