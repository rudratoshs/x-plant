# 📄 File: app/api/v1/__init__.py
#
# 🧭 Purpose (Layman Explanation):
# Marks this folder as containing version 1 of our plant care app's web API,
# like putting a "Version 1.0" label on our app's communication interface.
#
# 🧪 Purpose (Technical Summary):
# API v1 package initialization providing versioned endpoint organization
# and backward compatibility management for the Plant Care REST API.
#
# 🔗 Dependencies:
# - fastapi (routing and endpoint management)
# - Module-specific routers (user, plant, care, etc.)
#
# 🔄 Connected Modules / Calls From:
# - app.api.v1.router (main v1 router aggregation)
# - Client applications (mobile app, admin panel)
# - API documentation and testing tools

"""
API Version 1

First version of the Plant Care REST API providing access to all
application features including user management, plant care, health
monitoring, and administrative functions.
"""