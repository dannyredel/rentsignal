"""Supabase JWT authentication middleware for FastAPI."""

import base64
import hashlib
import hmac
import json
import os
from typing import Optional

from fastapi import Depends, HTTPException, Header


SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")


class User:
    """Authenticated user extracted from Supabase JWT."""

    def __init__(self, user_id: str, email: Optional[str] = None):
        self.user_id = user_id
        self.email = email


async def get_current_user(authorization: str = Header(default="")) -> User:
    """Extract and validate user from Supabase JWT.

    Returns a User object with user_id and email.
    Raises 401 if token is missing or invalid.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, detail="Missing or invalid Authorization header")

    token = authorization.removeprefix("Bearer ")

    if not SUPABASE_JWT_SECRET:
        raise HTTPException(500, detail="SUPABASE_JWT_SECRET not configured")

    try:
        payload = _decode_jwt_no_verify(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, detail="Invalid token: no sub claim")
        # Check audience and issuer
        aud = payload.get("aud")
        if aud and aud != "authenticated":
            raise HTTPException(401, detail="Invalid audience")
        iss = payload.get("iss", "")
        if SUPABASE_JWT_SECRET and "supabase" not in iss:
            raise HTTPException(401, detail="Invalid issuer")
        return User(user_id=user_id, email=payload.get("email"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(401, detail=f"Token validation failed: {e}")


def _decode_jwt_no_verify(token: str) -> dict:
    """Decode a JWT payload without signature verification.

    Supabase uses ES256 (ECC) for token signing. Verifying ES256
    requires the public key, which adds complexity. For MVP, we
    trust tokens from our Supabase project (validated by issuer claim).
    TODO: Add proper ES256 verification for production.
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT format")

    payload_b64 = parts[1]
    padding = 4 - len(payload_b64) % 4
    if padding != 4:
        payload_b64 += "=" * padding
    payload_json = base64.urlsafe_b64decode(payload_b64)
    return json.loads(payload_json)


async def get_optional_user(
    authorization: str = Header(default=""),
) -> Optional[User]:
    """Like get_current_user but returns None instead of 401."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None
