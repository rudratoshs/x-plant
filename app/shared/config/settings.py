# 📄 File: app/shared/config/settings.py
#
# 🧭 Purpose (Layman Explanation):
# Stores all the app's configuration settings like passwords, API keys, and feature toggles
# in one secure place, like a digital safe that keeps all important settings organized.
#
# 🧪 Purpose (Technical Summary):
# Centralized configuration management using Pydantic for type validation and environment
# variable loading, providing typed access to all application settings with validation.
#
# 🔗 Dependencies:
# - pydantic (settings validation and type checking)
# - pydantic-settings (environment variable loading)
# - python-dotenv (loads .env files)
# - typing (type hints and annotations)
#
# 🔄 Connected Modules / Calls From:
# - app.main (application initialization and configuration)
# - app.shared.config.supabase (Supabase client setup)
# - app.shared.infrastructure.database.connection (database config)
# - app.shared.infrastructure.cache.redis_client (Redis config)
# - All modules requiring configuration access

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable support and validation.
    
    All settings can be overridden via environment variables or .env file.
    Critical settings are validated for security and correctness.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore unknown environment variables
    )
    
    # =============================================================================
    # APPLICATION CONFIGURATION
    # =============================================================================
    ENVIRONMENT: str = Field(default="development", description="Application environment")
    DEBUG: bool = Field(default=True, description="Debug mode toggle")
    APP_HOST: str = Field(default="0.0.0.0", description="Application host")
    APP_PORT: int = Field(default=8000, description="Application port")
    
    # Allowed hosts for CORS and security
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1", "0.0.0.0"],
        description="Allowed hosts for CORS"
    )
    
    # =============================================================================
    # SUPABASE CONFIGURATION
    # =============================================================================
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_ANON_KEY: str = Field(..., description="Supabase anonymous key")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(..., description="Supabase service role key")
    
    @field_validator("SUPABASE_URL")
    @classmethod
    def validate_supabase_url(cls, v):
        if not v.startswith("https://"):
            raise ValueError("Supabase URL must start with https://")
        if ".supabase.co" not in v:
            raise ValueError("Invalid Supabase URL format")
        return v
    
    # =============================================================================
    # SECURITY CONFIGURATION
    # =============================================================================
    JWT_SECRET_KEY: str = Field(..., description="JWT signing secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, 
        description="Access token expiration in minutes"
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=30, 
        description="Refresh token expiration in days"
    )
    
    # Admin authentication
    ADMIN_SECRET_KEY: str = Field(..., description="Admin authentication secret")
    
    @field_validator("JWT_SECRET_KEY", "ADMIN_SECRET_KEY")
    @classmethod
    def validate_secret_keys(cls, v):
        if len(v) < 32:
            raise ValueError("Secret keys must be at least 32 characters long")
        return v
    
    # =============================================================================
    # REDIS CONFIGURATION
    # =============================================================================
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0", 
        description="Redis connection URL"
    )
    REDIS_MAX_CONNECTIONS: int = Field(
        default=20, 
        description="Maximum Redis connections"
    )
    REDIS_CONNECTION_TIMEOUT: int = Field(
        default=30, 
        description="Redis connection timeout in seconds"
    )
    
    # =============================================================================
    # PLANT IDENTIFICATION APIS
    # =============================================================================
    PLANTNET_API_KEY: Optional[str] = Field(
        default=None, 
        description="PlantNet API key"
    )
    PLANT_ID_API_KEY: Optional[str] = Field(
        default=None, 
        description="Plant.id API key"
    )
    TREFLE_API_KEY: Optional[str] = Field(
        default=None, 
        description="Trefle API key"
    )
    KINDWISE_API_KEY: Optional[str] = Field(
        default=None, 
        description="Kindwise API key"
    )
    
    # =============================================================================
    # WEATHER APIS
    # =============================================================================
    OPENWEATHER_API_KEY: Optional[str] = Field(
        default=None, 
        description="OpenWeatherMap API key"
    )
    TOMORROW_IO_API_KEY: Optional[str] = Field(
        default=None, 
        description="Tomorrow.io API key"
    )
    WEATHERSTACK_API_KEY: Optional[str] = Field(
        default=None, 
        description="Weatherstack API key"
    )
    VISUAL_CROSSING_API_KEY: Optional[str] = Field(
        default=None, 
        description="Visual Crossing API key"
    )
    
    # =============================================================================
    # PAYMENT GATEWAYS
    # =============================================================================
    # Razorpay (India)
    RAZORPAY_KEY_ID: Optional[str] = Field(
        default=None, 
        description="Razorpay key ID"
    )
    RAZORPAY_KEY_SECRET: Optional[str] = Field(
        default=None, 
        description="Razorpay secret key"
    )
    
    # Stripe (Global)
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(
        default=None, 
        description="Stripe publishable key"
    )
    STRIPE_SECRET_KEY: Optional[str] = Field(
        default=None, 
        description="Stripe secret key"
    )
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(
        default=None, 
        description="Stripe webhook secret"
    )
    
    # =============================================================================
    # NOTIFICATION SERVICES
    # =============================================================================
    # Firebase Cloud Messaging
    FCM_PROJECT_ID: Optional[str] = Field(
        default=None, 
        description="FCM project ID"
    )
    FCM_PRIVATE_KEY_ID: Optional[str] = Field(
        default=None, 
        description="FCM private key ID"
    )
    FCM_PRIVATE_KEY: Optional[str] = Field(
        default=None, 
        description="FCM private key"
    )
    FCM_CLIENT_EMAIL: Optional[str] = Field(
        default=None, 
        description="FCM client email"
    )
    FCM_CLIENT_ID: Optional[str] = Field(
        default=None, 
        description="FCM client ID"
    )
    
    # SendGrid Email
    SENDGRID_API_KEY: Optional[str] = Field(
        default=None, 
        description="SendGrid API key"
    )
    SENDGRID_FROM_EMAIL: Optional[str] = Field(
        default=None, 
        description="SendGrid from email"
    )
    SENDGRID_FROM_NAME: str = Field(
        default="Plant Care App", 
        description="SendGrid from name"
    )
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(
        default=None, 
        description="Telegram bot token"
    )
    
    # =============================================================================
    # AI SERVICES
    # =============================================================================
    OPENAI_API_KEY: Optional[str] = Field(
        default=None, 
        description="OpenAI API key"
    )
    OPENAI_ORG_ID: Optional[str] = Field(
        default=None, 
        description="OpenAI organization ID"
    )
    GEMINI_API_KEY: Optional[str] = Field(
        default=None, 
        description="Google Gemini API key"
    )
    CLAUDE_API_KEY: Optional[str] = Field(
        default=None, 
        description="Anthropic Claude API key"
    )
    
    # =============================================================================
    # TRANSLATION SERVICES
    # =============================================================================
    GOOGLE_TRANSLATE_API_KEY: Optional[str] = Field(
        default=None, 
        description="Google Translate API key"
    )
    DEEPL_API_KEY: Optional[str] = Field(
        default=None, 
        description="DeepL API key"
    )
    AZURE_TRANSLATOR_KEY: Optional[str] = Field(
        default=None, 
        description="Azure Translator key"
    )
    AZURE_TRANSLATOR_REGION: Optional[str] = Field(
        default=None, 
        description="Azure Translator region"
    )
    
    # =============================================================================
    # ANALYTICS & MONITORING
    # =============================================================================
    MIXPANEL_PROJECT_TOKEN: Optional[str] = Field(
        default=None, 
        description="Mixpanel project token"
    )
    GA_MEASUREMENT_ID: Optional[str] = Field(
        default=None, 
        description="Google Analytics measurement ID"
    )
    SENTRY_DSN: Optional[str] = Field(
        default=None, 
        description="Sentry DSN for error monitoring"
    )
    
    # =============================================================================
    # RATE LIMITING & CACHING
    # =============================================================================
    DEFAULT_RATE_LIMIT_PER_HOUR: int = Field(
        default=1000, 
        description="Default rate limit per hour"
    )
    DEFAULT_RATE_LIMIT_BURST: int = Field(
        default=10, 
        description="Default rate limit burst"
    )
    
    # Cache TTL settings (in seconds)
    CACHE_TTL_PLANT_LIBRARY: int = Field(
        default=86400, 
        description="Plant library cache TTL"
    )
    CACHE_TTL_WEATHER_DATA: int = Field(
        default=3600, 
        description="Weather data cache TTL"
    )
    CACHE_TTL_API_RESPONSES: int = Field(
        default=300, 
        description="API responses cache TTL"
    )
    
    # =============================================================================
    # FILE STORAGE
    # =============================================================================
    MAX_IMAGE_SIZE_MB: int = Field(
        default=10, 
        description="Maximum image size in MB"
    )
    MAX_FILE_SIZE_MB: int = Field(
        default=50, 
        description="Maximum file size in MB"
    )
    ALLOWED_IMAGE_EXTENSIONS: List[str] = Field(
        default=["jpg", "jpeg", "png", "webp"], 
        description="Allowed image extensions"
    )
    ALLOWED_FILE_EXTENSIONS: List[str] = Field(
        default=["pdf", "doc", "docx"], 
        description="Allowed file extensions"
    )
    
    # =============================================================================
    # COMPUTED PROPERTIES
    # =============================================================================
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def database_url(self) -> str:
        """Get PostgreSQL connection URL from Supabase"""
        # Supabase provides direct PostgreSQL access
        # Format: postgresql://[user[:password]@][netloc][:port][/dbname]
        return f"postgresql://postgres:[password]@{self.SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')}.supabase.co:5432/postgres"
    
    @property
    def redis_config(self) -> dict:
        """Get Redis configuration dictionary"""
        return {
            "url": self.REDIS_URL,
            "max_connections": self.REDIS_MAX_CONNECTIONS,
            "connection_timeout": self.REDIS_CONNECTION_TIMEOUT
        }
    
    # Remove the old Config class since we're using model_config now


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Uses LRU cache to avoid re-parsing environment variables on every call.
    Cache is cleared when the process restarts.
    
    Returns:
        Settings: Application configuration instance
    """
    return Settings()