"""Supabase client singleton for backend database operations."""

import os

from supabase import create_client, Client

_client: Client | None = None


def get_supabase() -> Client:
    """Get or create the Supabase client (service role for backend ops)."""
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        if not url or not key:
            from fastapi import HTTPException
            raise HTTPException(
                503,
                detail="Database not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.",
            )
        _client = create_client(url, key)
    return _client
