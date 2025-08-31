"""
Auth routes for BazaarBrain-Pro.

Provides simple development-friendly authentication:
- POST /auth/register
- POST /auth/login
- GET /auth/me

In development, accepts any email/password and issues an HS256 JWT
signed with the configured SUPABASE_SERVICE_ROLE_KEY (or fallback).
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Any, Dict
import logging
import uuid
import jwt

from ..config import config
from ..auth import get_current_user_payload

logger = logging.getLogger(__name__)
router = APIRouter()

JWT_SECRET = config.SUPABASE_SERVICE_ROLE_KEY or "dev-secret-key"


class Credentials(BaseModel):
    email: EmailStr
    password: str


def _issue_token(email: str, role: str = "shopkeeper") -> str:
    """Create a signed JWT suitable for dev/testing flows."""
    # Stable UUID from email for repeatable identity in demos
    user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, email))
    payload: Dict[str, Any] = {
        "sub": user_id,
        "email": email,
        "aud": "authenticated",
        "user_metadata": {"roles": [role], "role": role, "permissions": []},
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token


@router.post("/register")
def register(creds: Credentials):
    """Dev-only register that issues a JWT for the provided email."""
    try:
        token = _issue_token(creds.email)
        return {"success": True, "token": token, "user": {"id": jwt.decode(token, JWT_SECRET, algorithms=["HS256"])['sub'], "email": creds.email}}
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login")
def login(creds: Credentials):
    """Dev login: accepts any email/password and returns a JWT."""
    try:
        token = _issue_token(creds.email)
        return {"success": True, "token": token, "user": {"id": jwt.decode(token, JWT_SECRET, algorithms=["HS256"])['sub'], "email": creds.email}}
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.get("/me")
def me(user: Dict[str, Any] = Depends(get_current_user_payload)):
    """Return the current user payload from JWT."""
    return {"success": True, "user": user}
