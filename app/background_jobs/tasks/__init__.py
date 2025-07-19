# 📄 File: app/background_jobs/tasks/__init__.py
#
# 🧭 Purpose (Layman Explanation):
# Organizes all the specific background tasks our plant care app can perform,
# like a directory of all the automated jobs that run behind the scenes.
#
# 🧪 Purpose (Technical Summary):
# Task module package for Celery workers containing all asynchronous task
# implementations for care reminders, health monitoring, and system maintenance.
#
# 🔗 Dependencies:
# - celery (task decoration and execution)
# - Individual task modules (system_health, care_reminders, etc.)
# - Shared application configuration and utilities
#
# 🔄 Connected Modules / Calls From:
# - app.background_jobs.celery_app (task discovery and registration)
# - Celery workers (task execution)
# - Periodic task scheduler (beat scheduler)
# - Application modules (task triggering)

"""
Background Tasks

Collection of asynchronous tasks for the Plant Care application
including system health monitoring, care reminders, notifications,
analytics processing, and external API integrations.
"""

# Import available tasks for registration
from .system_health import (
    celery_health_check,
    check_external_apis,
    system_metrics_collection
)

# Task registry for auto-discovery
__all__ = [
    'celery_health_check',
    'check_external_apis', 
    'system_metrics_collection'
]