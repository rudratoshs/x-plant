# 📄 File: app/api/v1/router.py
#
# 🧭 Purpose (Layman Explanation):
# Acts like a traffic director for our plant care app, routing user requests
# to the right departments (user management, plant care, etc.) based on what they want to do.
#
# 🧪 Purpose (Technical Summary):
# Main API router that aggregates all module-specific routers into a single v1 API,
# providing centralized route registration and versioning for the entire application.
#
# 🔗 Dependencies:
# - fastapi (APIRouter for route organization)
# - All module presentation routers (when implemented)
# - Authentication and middleware dependencies
#
# 🔄 Connected Modules / Calls From:
# - app.main (router registration in FastAPI app)
# - All API client requests (mobile app, admin panel)
# - API documentation generation (OpenAPI/Swagger)
# - Route testing and validation

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

# Import module routers (will be added as modules are implemented)
# from app.modules.user_management.presentation.api.v1.auth import router as auth_router
# from app.modules.user_management.presentation.api.v1.users import router as users_router
# from app.modules.plant_management.presentation.api.v1.plants import router as plants_router
# from app.modules.admin_management.presentation.api.v1.admin_dashboard import router as admin_router

# Import dependencies
from app.shared.config.supabase import get_supabase_health

# Create main API v1 router
api_v1_router = APIRouter()


# =============================================================================
# HEALTH CHECK ENDPOINTS
# =============================================================================

@api_v1_router.get("/health", tags=["Health"])
async def api_health_check():
    """
    API v1 health check endpoint.
    
    Returns the health status of the API and its dependencies.
    Used for monitoring and load balancer health checks.
    """
    try:
        # Check Supabase connection
        supabase_health = await get_supabase_health()
        
        # Aggregate health status
        is_healthy = supabase_health.get("status") == "healthy"
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "version": "1.0.0",
            "api_version": "v1",
            "dependencies": {
                "supabase": supabase_health
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "version": "1.0.0",
                "api_version": "v1"
            }
        )


@api_v1_router.get("/", tags=["Root"])
async def api_v1_root():
    """
    API v1 root endpoint with available endpoints information.
    
    Provides an overview of available API endpoints and their documentation.
    """
    return {
        "message": "🌱 Plant Care API v1",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/api/v1/health",
        "endpoints": {
            "authentication": "/api/v1/auth",
            "users": "/api/v1/users", 
            "plants": "/api/v1/plants",
            "care": "/api/v1/care",
            "health": "/api/v1/plant-health",
            "growth": "/api/v1/growth",
            "community": "/api/v1/community",
            "ai": "/api/v1/ai",
            "weather": "/api/v1/weather",
            "analytics": "/api/v1/analytics",
            "notifications": "/api/v1/notifications",
            "payments": "/api/v1/payments",
            "content": "/api/v1/content",
            "admin": "/api/v1/admin"
        },
        "features": [
            "🔐 Supabase Authentication",
            "🪴 Plant Management", 
            "📅 Care Scheduling",
            "🏥 Health Monitoring",
            "📈 Growth Tracking",
            "👥 Community Features",
            "🤖 AI Recommendations",
            "🌤️ Weather Integration",
            "📊 Analytics & Insights",
            "🔔 Notifications",
            "💳 Payment Processing",
            "🌍 Multilingual Support",
            "⚙️ Admin Management"
        ]
    }


# =============================================================================
# MODULE ROUTER REGISTRATION
# =============================================================================

# NOTE: Module routers will be registered here as they are implemented
# Following the development order:

# Phase 1: Foundation
# api_v1_router.include_router(
#     admin_router,
#     prefix="/admin",
#     tags=["Admin Management"]
# )

# api_v1_router.include_router(
#     auth_router,
#     prefix="/auth", 
#     tags=["Authentication"]
# )

# api_v1_router.include_router(
#     users_router,
#     prefix="/users",
#     tags=["User Management"]
# )

# Phase 2: Core Features  
# api_v1_router.include_router(
#     plants_router,
#     prefix="/plants",
#     tags=["Plant Management"]
# )

# api_v1_router.include_router(
#     content_router,
#     prefix="/content",
#     tags=["Content Management"]
# )

# api_v1_router.include_router(
#     care_router,
#     prefix="/care", 
#     tags=["Care Management"]
# )

# Phase 3: Advanced Features
# api_v1_router.include_router(
#     health_router,
#     prefix="/plant-health",
#     tags=["Health Monitoring"]
# )

# api_v1_router.include_router(
#     weather_router,
#     prefix="/weather",
#     tags=["Weather & Environment"]
# )

# api_v1_router.include_router(
#     growth_router,
#     prefix="/growth",
#     tags=["Growth Tracking"]
# )

# Phase 4: Smart & Social
# api_v1_router.include_router(
#     ai_router,
#     prefix="/ai",
#     tags=["AI & Smart Features"]
# )

# api_v1_router.include_router(
#     analytics_router,
#     prefix="/analytics",
#     tags=["Analytics & Insights"]
# )

# api_v1_router.include_router(
#     community_router,
#     prefix="/community",
#     tags=["Community & Social"]
# )

# Phase 5: Business & Operations
# api_v1_router.include_router(
#     payments_router,
#     prefix="/payments",
#     tags=["Payment & Subscription"]
# )

# api_v1_router.include_router(
#     notifications_router,
#     prefix="/notifications", 
#     tags=["Notification & Communication"]
# )


# =============================================================================
# DEVELOPMENT UTILITIES
# =============================================================================

@api_v1_router.get("/debug/routes", tags=["Development"])
async def list_routes():
    """
    List all registered API routes (development only).
    
    Useful for debugging and understanding the API structure
    during development.
    """
    routes_info = []
    
    for route in api_v1_router.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes_info.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'Unknown'),
                "tags": getattr(route, 'tags', [])
            })
    
    return {
        "total_routes": len(routes_info),
        "routes": routes_info
    }