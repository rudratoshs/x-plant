# 📄 File: app/main.py
#
# 🧭 Purpose (Layman Explanation):
# The main entrance door to our plant care app - when someone visits our website or app,
# this file welcomes them and directs them to the right features they're looking for.
#
# 🧪 Purpose (Technical Summary):
# FastAPI application entry point that initializes the app, configures middleware, registers
# routers, sets up error handling, and provides health checks for container orchestration.
#
# 🔗 Dependencies:
# - fastapi (web framework)
# - app.shared.config.settings (configuration management)
# - app.api.v1.router (API route registration)
# - app.shared.core.middleware (custom middleware)
# - app.shared.infrastructure.database.connection (DB initialization)
#
# 🔄 Connected Modules / Calls From:
# - uvicorn server (application startup)
# - Docker container (main process)
# - Health check endpoints (container monitoring)
# - All API routes and middleware chains

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import configurations and settings
from app.shared.config.settings import get_settings
from app.shared.core.exceptions import PlantCareException
from app.shared.core.middleware import (
    RequestLoggingMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware
)

# Import API routers
from app.api.v1.router import api_v1_router

# Import infrastructure initialization
from app.shared.infrastructure.database.connection import init_database
from app.shared.infrastructure.cache.redis_client import init_redis
from app.shared.config.supabase import init_supabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown events.
    Handles initialization and cleanup of external resources.
    """
    logger.info("🌱 Plant Care Application starting up...")
    
    try:
        # Get application settings
        settings = get_settings()
        
        # Initialize Supabase client
        logger.info("🔗 Initializing Supabase connection...")
        await init_supabase()
        
        # Initialize Redis connection
        logger.info("📦 Initializing Redis cache...")
        await init_redis()
        
        # Initialize database connection
        logger.info("🗄️ Initializing database connection...")
        await init_database()
        
        logger.info("✅ Plant Care Application startup complete!")
        
        # Application is ready to serve requests
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize application: {e}")
        raise
    
    finally:
        # Cleanup on shutdown
        logger.info("🔄 Plant Care Application shutting down...")
        
        # Close database connections
        # Close Redis connections
        # Cleanup background tasks
        
        logger.info("✅ Plant Care Application shutdown complete!")


def create_application() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()
    
    # Create FastAPI application with lifespan management
    app = FastAPI(
        title="Plant Care API",
        description="""
        🌱 **Plant Care Application API**
        
        A comprehensive plant care management system that helps users:
        - 🪴 Manage their plant collection
        - 📅 Schedule and track care activities
        - 🏥 Monitor plant health and get AI diagnosis
        - 📈 Track growth with photo journals
        - 🤖 Get AI-powered care recommendations
        - 👥 Connect with plant care community
        
        **Features:**
        - Multi-language support
        - Weather-based care adjustments
        - Plant identification using AI
        - Premium subscription plans
        - Real-time notifications
        """,
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Request-ID"]
    )
    
    # Add trusted host middleware
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS
        )
    
    # Add custom middleware
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    
    # Register API routes
    app.include_router(
        api_v1_router,
        prefix="/api/v1",
        tags=["API v1"]
    )
    
    # Global exception handler
    @app.exception_handler(PlantCareException)
    async def plant_care_exception_handler(request: Request, exc: PlantCareException):
        """Handle custom application exceptions"""
        logger.error(f"Application error: {exc.detail} | Path: {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.detail,
                    "request_id": getattr(request.state, "request_id", None)
                }
            }
        )
    
    @app.exception_handler(500)
    async def internal_server_error_handler(request: Request, exc: Exception):
        """Handle unexpected server errors"""
        logger.error(f"Internal server error: {str(exc)} | Path: {request.url.path}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "request_id": getattr(request.state, "request_id", None)
                }
            }
        )
    
    # Health check endpoints
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Basic health check endpoint for container monitoring"""
        return {
            "status": "healthy",
            "service": "plant-care-api",
            "version": "1.0.0"
        }
    
    @app.get("/health/detailed", tags=["Health"])
    async def detailed_health_check():
        """Detailed health check including dependencies"""
        try:
            # Check database connection
            # Check Redis connection
            # Check external API availability
            
            return {
                "status": "healthy",
                "service": "plant-care-api",
                "version": "1.0.0",
                "dependencies": {
                    "database": "healthy",
                    "redis": "healthy",
                    "supabase": "healthy"
                },
                "timestamp": "2024-01-01T00:00:00Z"
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": str(e)
                }
            )
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information"""
        return {
            "message": "🌱 Welcome to Plant Care API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }
    
    return app


# Create the application instance
app = create_application()


if __name__ == "__main__":
    """Run the application directly (for development)"""
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )