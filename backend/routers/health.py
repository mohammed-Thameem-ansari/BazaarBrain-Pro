"""
Health check router for BazaarBrain-Pro API.

Provides endpoints to monitor the health and status of:
- API server
- Database connection
- External services
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import Dict, Any

from ..db import health_check as db_health_check
from ..config import config

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns:
        Dict containing health status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "bazaarbrain-pro-api"
    }

@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check including database status.
    
    Returns:
        Dict containing comprehensive health information
    """
    try:
        db_status = db_health_check()
        
        return {
            "status": "healthy" if db_status else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "bazaarbrain-pro-api",
            "version": "1.0.0",
            "environment": config.ENVIRONMENT,
            "services": {
                "api": {
                    "status": "healthy",
                    "uptime": "running"
                },
                "database": {
                    "status": "healthy" if db_status else "unhealthy",
                    "connection": "established" if db_status else "failed"
                }
            }
        }
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check for Kubernetes/container orchestration.
    
    Returns:
        Dict indicating if the service is ready to receive traffic
    """
    try:
        db_status = db_health_check()
        
        if not db_status:
            raise HTTPException(
                status_code=503,
                detail="Database not ready"
            )
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "bazaarbrain-pro-api"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service not ready: {str(e)}"
        )

@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check for Kubernetes/container orchestration.
    
    Returns:
        Dict indicating if the service is alive
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "bazaarbrain-pro-api"
    }
