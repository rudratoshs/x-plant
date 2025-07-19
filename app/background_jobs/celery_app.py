# 📄 File: app/background_jobs/celery_app.py
#
# 🧭 Purpose (Layman Explanation):
# Sets up the background task worker system for our plant care app, like having
# invisible assistants that handle time-consuming jobs while users continue using the app.
#
# 🧪 Purpose (Technical Summary):
# Celery application configuration for distributed task processing with Redis broker,
# task discovery, scheduling, and monitoring for asynchronous operations.
#
# 🔗 Dependencies:
# - celery (distributed task queue)
# - redis (message broker and result backend)
# - app.shared.config.settings (configuration management)
# - kombu (messaging library)
#
# 🔄 Connected Modules / Calls From:
# - docker-compose.yml (celery worker and beat processes)
# - Background task modules (care reminders, notifications, etc.)
# - Periodic task scheduling (cron-like jobs)
# - Task monitoring and management

import os
from celery import Celery
from celery.schedules import crontab

from app.shared.config.settings import get_settings
import logging
# Get application settings
settings = get_settings()

logging.warning(f"settingsRS {settings}")
# Create Celery instance
celery_app = Celery(
    "plant_care_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        # Currently implemented task modules
        'app.background_jobs.tasks.system_health',
        
        # Task modules will be added as they are implemented
        # 'app.background_jobs.tasks.care_reminders',
        # 'app.background_jobs.tasks.health_monitoring', 
        # 'app.background_jobs.tasks.weather_updates',
        # 'app.background_jobs.tasks.analytics_processing',
        # 'app.background_jobs.tasks.notification_sending',
        # 'app.background_jobs.tasks.api_rotation',
        # 'app.background_jobs.tasks.data_cleanup',
        # 'app.background_jobs.tasks.translation_sync',
        # 'app.background_jobs.tasks.multilingual_content',
    ]
)

# Celery configuration
celery_app.conf.update(
    # Timezone settings
    timezone='UTC',
    enable_utc=True,
    
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Task routing and execution
    task_always_eager=False,  # Set to True for testing
    task_eager_propagates=True,
    task_ignore_result=False,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_persistent=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Disable prefetching for better load balancing
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    worker_disable_rate_limits=False,
    
    # Task execution settings
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=600,      # 10 minutes hard limit
    task_acks_late=True,      # Acknowledge task after completion
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_track_started=True,
    
    # Redis specific settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        # Example periodic tasks (will be uncommented as tasks are implemented)
        
        # 'send-care-reminders': {
        #     'task': 'app.background_jobs.tasks.care_reminders.send_due_care_reminders',
        #     'schedule': crontab(minute=0, hour='8,12,18'),  # 8 AM, 12 PM, 6 PM
        # },
        
        # 'update-weather-data': {
        #     'task': 'app.background_jobs.tasks.weather_updates.update_weather_for_all_users',
        #     'schedule': crontab(minute=0, hour='*/3'),  # Every 3 hours
        # },
        
        # 'process-health-alerts': {
        #     'task': 'app.background_jobs.tasks.health_monitoring.check_plant_health_alerts',
        #     'schedule': crontab(minute=0, hour=9),  # Daily at 9 AM
        # },
        
        # 'cleanup-old-data': {
        #     'task': 'app.background_jobs.tasks.data_cleanup.cleanup_old_analytics_data',
        #     'schedule': crontab(minute=0, hour=2, day_of_week=0),  # Weekly on Sunday at 2 AM
        # },
        
        # 'sync-translations': {
        #     'task': 'app.background_jobs.tasks.translation_sync.sync_pending_translations',
        #     'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        # },
        
        # 'rotate-api-keys': {
        #     'task': 'app.background_jobs.tasks.api_rotation.check_api_usage_and_rotate',
        #     'schedule': crontab(minute=0, hour='*/1'),  # Every hour
        # },
        
        # 'process-analytics': {
        #     'task': 'app.background_jobs.tasks.analytics_processing.process_daily_analytics',
        #     'schedule': crontab(minute=0, hour=1),  # Daily at 1 AM
        # },
        
        # Health check task (can be enabled immediately)
        'celery-health-check': {
            'task': 'app.background_jobs.tasks.system_health.celery_health_check',
            'schedule': crontab(minute='*/5'),  # Every 5 minutes
        },
    },
)

# Queue configuration
celery_app.conf.task_routes = {
    # High priority queue for urgent tasks
    'app.background_jobs.tasks.care_reminders.*': {'queue': 'high_priority'},
    'app.background_jobs.tasks.health_monitoring.*': {'queue': 'high_priority'},
    'app.background_jobs.tasks.notification_sending.*': {'queue': 'high_priority'},
    
    # Low priority queue for background processing
    'app.background_jobs.tasks.analytics_processing.*': {'queue': 'low_priority'},
    'app.background_jobs.tasks.data_cleanup.*': {'queue': 'low_priority'},
    'app.background_jobs.tasks.translation_sync.*': {'queue': 'low_priority'},
    
    # Default queue for everything else
    'app.background_jobs.tasks.*': {'queue': 'default'},
}

# Task annotations for different task types
celery_app.conf.task_annotations = {
    'app.background_jobs.tasks.care_reminders.*': {
        'rate_limit': '100/m',  # 100 tasks per minute
        'time_limit': 60,       # 1 minute time limit
    },
    'app.background_jobs.tasks.notification_sending.*': {
        'rate_limit': '500/m',  # 500 notifications per minute
        'time_limit': 30,       # 30 seconds time limit
    },
    'app.background_jobs.tasks.analytics_processing.*': {
        'rate_limit': '10/m',   # 10 analytics tasks per minute
        'time_limit': 300,      # 5 minutes time limit
    },
}

# Development/Testing configuration
if settings.ENVIRONMENT == 'development':
    celery_app.conf.update(
        task_always_eager=False,  # Still use Redis even in development
        worker_log_level='INFO',
    )

# Production optimizations
if settings.ENVIRONMENT == 'production':
    celery_app.conf.update(
        worker_log_level='WARNING',
        worker_hijack_root_logger=False,
        worker_max_memory_per_child=200000,  # 200MB memory limit per worker
    )


# Utility functions for task management
def get_celery_app():
    """Get the configured Celery application instance."""
    return celery_app


def register_task_module(module_path: str):
    """
    Dynamically register a task module.
    
    Args:
        module_path: Python module path (e.g., 'app.background_jobs.tasks.new_module')
    """
    current_includes = list(celery_app.conf.include)
    if module_path not in current_includes:
        current_includes.append(module_path)
        celery_app.conf.include = current_includes
        celery_app.autodiscover_tasks(force=True)


# For backward compatibility and direct imports
app = celery_app