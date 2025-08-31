"""
Authentication module for BazaarBrain-Pro API.

Handles:
- JWT token verification
- User ID extraction from Supabase tokens
- Authentication middleware
- User validation
"""

import jwt
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import config

logger = logging.getLogger(__name__)

# Security scheme for JWT tokens
security = HTTPBearer()

# Supabase JWT secret (you'll need to get this from your Supabase dashboard)
# For now, we'll use a placeholder - in production, get this from environment
SUPABASE_JWT_SECRET = config.SUPABASE_SERVICE_ROLE_KEY or "dev-secret-key"

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a JWT token and extract payload.
    
    Args:
        token: JWT token string
        
    Returns:
        Token payload if valid, None otherwise
    """
    try:
        # Decode the JWT token
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        
        # Validate required fields
        if not payload.get("sub") or not payload.get("email"):
            logger.warning("Token missing required fields: sub or email")
            return None
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error verifying JWT token: {e}")
        return None

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract current user ID from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        User ID string
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        token = credentials.credentials
        
        # Verify the token
        payload = verify_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
        
        # Extract user ID from token
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Token missing user ID"
            )
        
        return user_id
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )

def get_current_user_email(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract current user email from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        User email string
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        token = credentials.credentials
        
        # Verify the token
        payload = verify_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
        
        # Extract user email from token
        user_email = payload.get("email")
        
        if not user_email:
            raise HTTPException(
                status_code=401,
                detail="Token missing user email"
            )
        
        return user_email
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )

def get_current_user_payload(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get the full user payload from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Full token payload
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        token = credentials.credentials
        
        # Verify the token
        payload = verify_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
        
        return payload
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )

def optional_auth(request: Request) -> Optional[Dict[str, Any]]:
    """
    Optional authentication - returns user info if token is valid, None otherwise.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User payload if authenticated, None otherwise
    """
    try:
        # Check if Authorization header exists
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        # Extract token
        token = auth_header.split(" ")[1]
        
        # Verify token
        payload = verify_jwt_token(token)
        return payload
        
    except Exception as e:
        logger.debug(f"Optional auth failed: {e}")
        return None

# Middleware function for logging authentication attempts
async def auth_middleware(request: Request, call_next):
    """
    Middleware to log authentication attempts and add user info to request state.
    """
    # Extract user info if available
    user_info = optional_auth(request)
    
    if user_info:
        request.state.user = user_info
        logger.info(f"Authenticated request from user {user_info.get('email', 'unknown')}")
    else:
        request.state.user = None
        logger.debug("Unauthenticated request")
    
    # Continue processing
    response = await call_next(request)
    return response

# Utility function to check if user has specific role
def has_role(user_payload: Dict[str, Any], required_role: str) -> bool:
    """
    Check if user has a specific role.
    
    Args:
        user_payload: User token payload
        required_role: Required role string
        
    Returns:
        True if user has the role, False otherwise
    """
    try:
        user_roles = user_payload.get("user_metadata", {}).get("roles", [])
        return required_role in user_roles
    except Exception:
        return False

# Utility function to check if user has specific permission
def has_permission(user_payload: Dict[str, Any], required_permission: str) -> bool:
    """
    Check if user has a specific permission.
    
    Args:
        user_payload: User token payload
        required_permission: Required permission string
        
    Returns:
        True if user has the permission, False otherwise
    """
    try:
        user_permissions = user_payload.get("user_metadata", {}).get("permissions", [])
        return required_permission in user_permissions
    except Exception:
        return False
