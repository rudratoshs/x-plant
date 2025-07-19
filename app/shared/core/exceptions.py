# 📄 File: app/shared/core/exceptions.py
#
# 🧭 Purpose (Layman Explanation):
# Defines all the different types of errors that can happen in our plant care app,
# like having specific error messages for different problems that might occur.
#
# 🧪 Purpose (Technical Summary):
# Custom exception classes with standardized error codes, HTTP status codes,
# and structured error responses for consistent API error handling across modules.
#
# 🔗 Dependencies:
# - fastapi (HTTPException base class)
# - typing (type hints for error details)
#
# 🔄 Connected Modules / Calls From:
# - app.main (global exception handler)
# - All domain services (business logic errors)
# - API route handlers (HTTP error responses)
# - Middleware components (request validation errors)

from typing import Any, Dict, Optional
from fastapi import HTTPException


class PlantCareException(HTTPException):
    """
    Base exception class for Plant Care application.
    
    Provides structured error handling with standardized error codes
    and consistent response format across all API endpoints.
    """
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


# =============================================================================
# AUTHENTICATION & AUTHORIZATION EXCEPTIONS
# =============================================================================

class AuthenticationError(PlantCareException):
    """Authentication failed"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code="AUTHENTICATION_FAILED"
        )


class AuthorizationError(PlantCareException):
    """Insufficient permissions"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=403,
            detail=detail,
            error_code="AUTHORIZATION_FAILED"
        )


class InvalidTokenError(PlantCareException):
    """Invalid or expired token"""
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code="INVALID_TOKEN"
        )


class AdminAccessRequiredError(PlantCareException):
    """Admin access required"""
    def __init__(self, detail: str = "Admin access required"):
        super().__init__(
            status_code=403,
            detail=detail,
            error_code="ADMIN_ACCESS_REQUIRED"
        )


# =============================================================================
# USER MANAGEMENT EXCEPTIONS
# =============================================================================

class UserNotFoundError(PlantCareException):
    """User not found"""
    def __init__(self, detail: str = "User not found"):
        super().__init__(
            status_code=404,
            detail=detail,
            error_code="USER_NOT_FOUND"
        )


class UserAlreadyExistsError(PlantCareException):
    """User already exists"""
    def __init__(self, detail: str = "User already exists"):
        super().__init__(
            status_code=409,
            detail=detail,
            error_code="USER_ALREADY_EXISTS"
        )


class InvalidCredentialsError(PlantCareException):
    """Invalid login credentials"""
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code="INVALID_CREDENTIALS"
        )


class AccountSuspendedError(PlantCareException):
    """User account suspended"""
    def __init__(self, detail: str = "Account suspended"):
        super().__init__(
            status_code=403,
            detail=detail,
            error_code="ACCOUNT_SUSPENDED"
        )


# =============================================================================
# PLANT MANAGEMENT EXCEPTIONS
# =============================================================================

class PlantNotFoundError(PlantCareException):
    """Plant not found"""
    def __init__(self, detail: str = "Plant not found"):
        super().__init__(
            status_code=404,
            detail=detail,
            error_code="PLANT_NOT_FOUND"
        )


class PlantLimitExceededError(PlantCareException):
    """Plant limit exceeded for user tier"""
    def __init__(self, detail: str = "Plant limit exceeded for your subscription"):
        super().__init__(
            status_code=402,
            detail=detail,
            error_code="PLANT_LIMIT_EXCEEDED"
        )


class PlantIdentificationError(PlantCareException):
    """Plant identification failed"""
    def __init__(self, detail: str = "Unable to identify plant"):
        super().__init__(
            status_code=422,
            detail=detail,
            error_code="PLANT_IDENTIFICATION_FAILED"
        )


class InvalidPlantDataError(PlantCareException):
    """Invalid plant data provided"""
    def __init__(self, detail: str = "Invalid plant data"):
        super().__init__(
            status_code=422,
            detail=detail,
            error_code="INVALID_PLANT_DATA"
        )


# =============================================================================
# SUBSCRIPTION & PAYMENT EXCEPTIONS
# =============================================================================

class SubscriptionRequiredError(PlantCareException):
    """Premium subscription required"""
    def __init__(self, detail: str = "Premium subscription required"):
        super().__init__(
            status_code=402,
            detail=detail,
            error_code="SUBSCRIPTION_REQUIRED"
        )


class PaymentFailedError(PlantCareException):
    """Payment processing failed"""
    def __init__(self, detail: str = "Payment processing failed"):
        super().__init__(
            status_code=402,
            detail=detail,
            error_code="PAYMENT_FAILED"
        )


class SubscriptionNotFoundError(PlantCareException):
    """Subscription not found"""
    def __init__(self, detail: str = "Subscription not found"):
        super().__init__(
            status_code=404,
            detail=detail,
            error_code="SUBSCRIPTION_NOT_FOUND"
        )


# =============================================================================
# API & EXTERNAL SERVICE EXCEPTIONS
# =============================================================================

class ExternalAPIError(PlantCareException):
    """External API service error"""
    def __init__(self, detail: str = "External service temporarily unavailable"):
        super().__init__(
            status_code=503,
            detail=detail,
            error_code="EXTERNAL_API_ERROR"
        )


class APIRateLimitExceededError(PlantCareException):
    """API rate limit exceeded"""
    def __init__(self, detail: str = "API rate limit exceeded"):
        super().__init__(
            status_code=429,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED"
        )


class APIKeyInvalidError(PlantCareException):
    """Invalid API key"""
    def __init__(self, detail: str = "Invalid API key"):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code="INVALID_API_KEY"
        )


# =============================================================================
# FILE & STORAGE EXCEPTIONS
# =============================================================================

class FileUploadError(PlantCareException):
    """File upload failed"""
    def __init__(self, detail: str = "File upload failed"):
        super().__init__(
            status_code=422,
            detail=detail,
            error_code="FILE_UPLOAD_FAILED"
        )


class FileSizeExceededError(PlantCareException):
    """File size exceeded limit"""
    def __init__(self, detail: str = "File size exceeds limit"):
        super().__init__(
            status_code=413,
            detail=detail,
            error_code="FILE_SIZE_EXCEEDED"
        )


class InvalidFileTypeError(PlantCareException):
    """Invalid file type"""
    def __init__(self, detail: str = "Invalid file type"):
        super().__init__(
            status_code=422,
            detail=detail,
            error_code="INVALID_FILE_TYPE"
        )


# =============================================================================
# VALIDATION EXCEPTIONS
# =============================================================================

class ValidationError(PlantCareException):
    """Data validation error"""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=422,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )


class ConfigurationError(PlantCareException):
    """System configuration error"""
    def __init__(self, detail: str = "System configuration error"):
        super().__init__(
            status_code=500,
            detail=detail,
            error_code="CONFIGURATION_ERROR"
        )


# =============================================================================
# DATABASE EXCEPTIONS
# =============================================================================

class DatabaseConnectionError(PlantCareException):
    """Database connection error"""
    def __init__(self, detail: str = "Database connection failed"):
        super().__init__(
            status_code=503,
            detail=detail,
            error_code="DATABASE_CONNECTION_ERROR"
        )


class DatabaseOperationError(PlantCareException):
    """Database operation error"""
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=500,
            detail=detail,
            error_code="DATABASE_OPERATION_ERROR"
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_error_response(exception: PlantCareException, request_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create standardized error response dictionary.
    
    Args:
        exception: PlantCareException instance
        request_id: Optional request ID for tracking
        
    Returns:
        dict: Standardized error response
    """
    return {
        "error": {
            "code": exception.error_code,
            "message": exception.detail,
            "status_code": exception.status_code,
            "request_id": request_id
        }
    }