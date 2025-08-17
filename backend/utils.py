from __future__ import annotations

import re
from typing import Any, Dict, Tuple

from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify


EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,50}$")


def hash_password(plain: str) -> str:
    return generate_password_hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return check_password_hash(hashed, plain)


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email))


def is_valid_username(username: str) -> bool:
    return bool(USERNAME_RE.match(username))


def error_response(message: str, status_code: int = 400) -> Tuple[Any, int]:
    return jsonify({"error": message}), status_code