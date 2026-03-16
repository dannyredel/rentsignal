"""Supabase JWT authentication middleware for FastAPI."""

import os
from typing import Optional

from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError


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
        # Decode header first to check algorithm
        import base64
        header_b64 = token.split(".")[0]
        # Add padding
        header_b64 += "=" * (4 - len(header_b64) % 4)
        import json as _json
        header = _json.loads(base64.urlsafe_b64decode(header_b64))
        alg = header.get("alg", "unknown")

        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=[alg],
            audience="authenticated",
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, detail="Invalid token: no sub claim")
        return User(user_id=user_id, email=payload.get("email"))
    except JWTError as e:
        raise HTTPException(401, detail=f"Token validation failed: {e}")


async def get_optional_user(
    authorization: str = Header(default=""),
) -> Optional[User]:
    """Like get_current_user but returns None instead of 401.

    Use for endpoints that work for both anonymous and authenticated users
    (e.g., free compliance check — no login for first use).
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None
