# 📄 File: app/shared/core/middleware.py
#
# 🧭 Purpose (Layman Explanation):
# Creates security guards and traffic monitors for our plant care app,
# like having digital bouncers that check every request and keep logs.
#
# 🧪 Purpose (Technical Summary):
# FastAPI middleware implementations for security headers, rate limiting,
# request logging, and authentication with proper error handling.
#
# 🔗 Dependencies:
# - fastapi (middleware base classes)
# - starlette (middleware foundation)
# - app.shared.config.settings (configuration access)
# - logging (request logging functionality)
#
# 🔄 Connected Modules / Calls From:
# - app.main (middleware registration in FastAPI app)
# - All HTTP requests (middleware chain execution)
# - Authentication system (auth middleware)
# - Rate limiting system (rate limit middleware)

import time
import uuid
import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi import HTTPException

from app.shared.config.settings import get_settings

# Configure logging
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    
    Logs request details including method, path, response time,
    and status code for monitoring and debugging purposes.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request start
        start_time = time.time()
        logger.info(
            f"Request started: {request.method} {request.url.path} | "
            f"Request ID: {request_id} | "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate request duration
            duration = time.time() - start_time
            
            # Log successful response
            logger.info(
                f"Request completed: {request.method} {request.url.path} | "
                f"Status: {response.status_code} | "
                f"Duration: {duration:.3f}s | "
                f"Request ID: {request_id}"
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate request duration for failed requests
            duration = time.time() - start_time
            
            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path} | "
                f"Error: {str(e)} | "
                f"Duration: {duration:.3f}s | "
                f"Request ID: {request_id}"
            )
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred",
                        "request_id": request_id
                    }
                },
                headers={"X-Request-ID": request_id}
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers to all responses.
    
    Adds security headers like CSP, HSTS, X-Frame-Options
    to protect against common web vulnerabilities.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
        }
        
        # Add HSTS header for HTTPS
        if request.url.scheme == "https":
            security_headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Apply headers to response
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests.
    
    Implements basic rate limiting to prevent abuse and
    ensure fair usage of API resources.
    """
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls  # Number of calls allowed
        self.period = period  # Time period in seconds
        self.clients = {}  # In-memory storage (will be moved to Redis later)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/health/detailed"]:
            return await call_next(request)
        
        # Check rate limit (simplified implementation)
        current_time = time.time()
        
        # Clean old entries (simplified)
        self.clients = {
            ip: calls for ip, calls in self.clients.items()
            if current_time - calls.get("last_reset", 0) < self.period
        }
        
        # Initialize or update client data
        if client_ip not in self.clients:
            self.clients[client_ip] = {
                "count": 0,
                "last_reset": current_time
            }
        
        client_data = self.clients[client_ip]
        
        # Reset count if period has passed
        if current_time - client_data["last_reset"] >= self.period:
            client_data["count"] = 0
            client_data["last_reset"] = current_time
        
        # Check if limit exceeded
        if client_data["count"] >= self.calls:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded: {self.calls} requests per {self.period} seconds",
                        "retry_after": self.period - (current_time - client_data["last_reset"])
                    }
                },
                headers={
                    "Retry-After": str(int(self.period - (current_time - client_data["last_reset"]))),
                    "X-RateLimit-Limit": str(self.calls),
                    "X-RateLimit-Remaining": str(max(0, self.calls - client_data["count"] - 1)),
                    "X-RateLimit-Reset": str(int(client_data["last_reset"] + self.period))
                }
            )
        
        # Increment counter
        client_data["count"] += 1
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.calls - client_data["count"]))
        response.headers["X-RateLimit-Reset"] = str(int(client_data["last_reset"] + self.period))
        
        return response


class CORSMiddleware(BaseHTTPMiddleware):
    """
    Custom CORS middleware for additional control.
    
    Handles Cross-Origin Resource Sharing with
    environment-specific configurations.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        settings = get_settings()
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = "*" if settings.DEBUG else "https://yourdomain.com"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response.headers["Access-Control-Max-Age"] = "3600"
            return response
        
        # Process request
        response = await call_next(request)
        
        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = "*" if settings.DEBUG else "https://yourdomain.com"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response