# 📄 File: app/background_jobs/__init__.py
#
# 🧭 Purpose (Layman Explanation):
# Marks this folder as containing all the background task workers for our plant care app,
# like a filing cabinet label for all the behind-the-scenes automation.
#
# 🧪 Purpose (Technical Summary):
# Python package initialization for background job processing with Celery,
# including task discovery, worker configuration, and job scheduling.
#
# 🔗 Dependencies:
# - Python interpreter (package recognition)
# - celery (distributed task queue)
# - Background job modules and tasks
#
# 🔄 Connected Modules / Calls From:
# - Celery worker processes (task discovery and execution)
# - Application startup (background job initialization)
# - Task scheduling and monitoring systems

"""
Background Jobs Package

Distributed task processing using Celery for asynchronous operations
including care reminders, health monitoring, analytics processing,
and external API integrations.
"""

from .celery_app import celery_app, get_celery_app

__all__ = ['celery_app', 'get_celery_app']