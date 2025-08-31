"""
Main FastAPI application for BazaarBrain-Pro.

This module sets up the FastAPI server with:
- CORS middleware
- Authentication middleware
- API routers
- Health checks
- Error handling
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime

from .routers import health, receipts, simulations
from .db import health_check as db_health_check
from .config import config
from .auth import auth_middleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BazaarBrain-Pro API",
    description="AI-powered business assistant for shopkeepers using GPT + Gemini",
    version="1.0.0",
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None
)

# Add CORS middleware
if config.ALLOWED_ORIGINS == ["*"]:
    allow_origins = ["*"]
else:
    allow_origins = config.ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add auth logging middleware
app.middleware("http")(auth_middleware)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(receipts.router, prefix="/api/v1", tags=["receipts"])
app.include_router(simulations.router, prefix="/api/v1", tags=["simulations"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to BazaarBrain-Pro API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs" if config.DEBUG else "Documentation disabled in production",
        "timestamp": datetime.utcnow().isoformat()
    }

# Health check endpoint (detailed)
@app.get("/health")
async def health_check():
    """Comprehensive health check including database status."""
    try:
        db_status = db_health_check()
        return {
            "status": "healthy" if db_status else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "api": "healthy",
                "database": "healthy" if db_status else "unhealthy"
            },
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "api": "healthy",
                "database": "unhealthy"
            },
            "error": str(e),
            "version": "1.0.0"
        }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("🚀 BazaarBrain-Pro API starting up...")
    
    # Test database connection
    if db_health_check():
        logger.info("✅ Database connection established")
    else:
        logger.warning("⚠️  Database connection failed - some features may not work")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("🛑 BazaarBrain-Pro API shutting down...")

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
    "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )
