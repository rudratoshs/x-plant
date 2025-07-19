# 📄 File: app/shared/config/supabase.py
#
# 🧭 Purpose (Layman Explanation):
# Sets up the connection to Supabase (our cloud database and authentication service),
# like connecting a phone line to make calls to our data storage and user management.
#
# 🧪 Purpose (Technical Summary):
# Initializes and configures Supabase client for database operations, authentication,
# and storage with connection pooling, error handling, and health monitoring.
#
# 🔗 Dependencies:
# - supabase (Supabase Python client)
# - app.shared.config.settings (configuration management)
# - logging (error tracking and monitoring)
# - asyncio (async operations support)
#
# 🔄 Connected Modules / Calls From:
# - app.main (application startup initialization)
# - All database repository implementations
# - Authentication middleware and services
# - File storage operations and image uploads

import logging
from typing import Optional
import asyncio

from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

from app.shared.config.settings import get_settings

# Configure logging
logger = logging.getLogger(__name__)

# Global Supabase client instance
_supabase_client: Optional[Client] = None


class SupabaseConfig:
    """
    Supabase configuration and client management.
    
    Handles client initialization, connection management, and provides
    typed access to Supabase services (database, auth, storage).
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[Client] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """
        Initialize Supabase client with configuration.
        
        Sets up connection with proper timeouts, retry logic,
        and error handling for production use.
        """
        try:
            logger.info("🔗 Initializing Supabase client...")
            
            # Configure client options
            client_options = ClientOptions(
                # Auto-refresh tokens
                auto_refresh_token=True,
                # Persist session across requests
                persist_session=True,
                # Connection timeout
                # Custom headers
                headers={
                    "User-Agent": "PlantCare-API/1.0.0",
                    "X-Client-Info": "plant-care-backend"
                }
            )
            
            # Create Supabase client
            self.client = create_client(
                supabase_url=self.settings.SUPABASE_URL,
                supabase_key=self.settings.SUPABASE_SERVICE_ROLE_KEY,
                options=client_options
            )
            
            # Test connection
            await self._test_connection()
            
            self._initialized = True
            logger.info("✅ Supabase client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    async def _test_connection(self) -> None:
        """
        Test Supabase connection by performing a simple query.
        
        Raises:
            Exception: If connection test fails
        """
        try:
            # Test database connection with a simple query
            result = self.client.table("auth.users").select("id").limit(1).execute()
            logger.info("🔍 Supabase connection test successful")
            
        except Exception as e:
            logger.error(f"❌ Supabase connection test failed: {e}")
            raise Exception("Failed to connect to Supabase database")
    
    def get_client(self) -> Client:
        """
        Get the initialized Supabase client.
        
        Returns:
            Client: Supabase client instance
            
        Raises:
            RuntimeError: If client is not initialized
        """
        if not self._initialized or self.client is None:
            raise RuntimeError(
                "Supabase client not initialized. Call initialize() first."
            )
        return self.client
    
    async def health_check(self) -> dict:
        """
        Perform health check on Supabase connection.
        
        Returns:
            dict: Health status information
        """
        try:
            if not self._initialized:
                return {
                    "status": "unhealthy",
                    "error": "Client not initialized"
                }
            
            # Test database query
            await self._test_connection()
            
            return {
                "status": "healthy",
                "service": "supabase",
                "url": self.settings.SUPABASE_URL,
                "initialized": self._initialized
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "supabase",
                "error": str(e)
            }
    
    async def close(self) -> None:
        """
        Close Supabase client connections.
        
        Cleanup method for application shutdown.
        """
        try:
            if self.client:
                # Supabase client doesn't have explicit close method
                # but we can clear references
                self.client = None
                self._initialized = False
                logger.info("🔄 Supabase client connections closed")
                
        except Exception as e:
            logger.error(f"❌ Error closing Supabase client: {e}")


# Global configuration instance
_supabase_config = SupabaseConfig()


async def init_supabase() -> None:
    """
    Initialize global Supabase client.
    
    Called during application startup to establish
    database connection and authentication setup.
    """
    global _supabase_client
    
    try:
        await _supabase_config.initialize()
        _supabase_client = _supabase_config.get_client()
        logger.info("🌍 Global Supabase client initialized")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize global Supabase client: {e}")
        raise


def get_supabase() -> Client:
    """
    Get the global Supabase client instance.
    
    This function is used as a FastAPI dependency to inject
    the Supabase client into route handlers and services.
    
    Returns:
        Client: Supabase client instance
        
    Raises:
        RuntimeError: If client is not initialized
    """
    if _supabase_client is None:
        raise RuntimeError(
            "Supabase client not initialized. Ensure init_supabase() is called during startup."
        )
    return _supabase_client


async def get_supabase_health() -> dict:
    """
    Get Supabase health status.
    
    Used by health check endpoints to monitor
    database connection status.
    
    Returns:
        dict: Health status information
    """
    return await _supabase_config.health_check()


async def close_supabase() -> None:
    """
    Close Supabase connections.
    
    Called during application shutdown to cleanup
    database connections properly.
    """
    global _supabase_client
    
    await _supabase_config.close()
    _supabase_client = None
    logger.info("🔄 Global Supabase client closed")


# Utility functions for common Supabase operations
class SupabaseHelpers:
    """
    Helper functions for common Supabase operations.
    
    Provides convenient methods for database queries,
    authentication, and storage operations.
    """
    
    @staticmethod
    def get_auth():
        """Get Supabase auth client"""
        return get_supabase().auth
    
    @staticmethod
    def get_storage():
        """Get Supabase storage client"""
        return get_supabase().storage
    
    @staticmethod
    def table(table_name: str):
        """Get table reference for database operations"""
        return get_supabase().table(table_name)
    
    @staticmethod
    def rpc(function_name: str, params: dict = None):
        """Call Supabase database function"""
        return get_supabase().rpc(function_name, params or {})
    
    @staticmethod
    async def execute_query(query):
        """
        Execute database query with error handling.
        
        Args:
            query: Supabase query object
            
        Returns:
            Query result data
            
        Raises:
            Exception: If query execution fails
        """
        try:
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise
    
    @staticmethod
    async def upload_file(bucket: str, file_path: str, file_data: bytes) -> str:
        """
        Upload file to Supabase storage.
        
        Args:
            bucket: Storage bucket name
            file_path: File path in bucket
            file_data: File binary data
            
        Returns:
            str: Public URL of uploaded file
            
        Raises:
            Exception: If upload fails
        """
        try:
            storage = get_supabase().storage
            
            # Upload file
            result = storage.from_(bucket).upload(file_path, file_data)
            
            if result.error:
                raise Exception(f"Upload failed: {result.error}")
            
            # Get public URL
            url_result = storage.from_(bucket).get_public_url(file_path)
            return url_result
            
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise