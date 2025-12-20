"""
Health check endpoint for EduLite backend.

This module provides a simple health check endpoint that Docker can use
to verify the backend service is running and healthy.
"""

from typing import Any, Dict
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache


def health_check(request):
    """
    Health check endpoint.

    Returns HTTP 200 with service status if healthy.
    Returns HTTP 503 if any critical service is down.

    Checks:
    - Database connectivity
    - Redis connectivity (via Django cache)
    """
    status: Dict[str, Any] = {
        "status": "healthy",
        "service": "edulite-backend",
        "checks": {},
    }

    http_status = 200

    # Check database
    try:
        connection.ensure_connection()
        status["checks"]["database"] = "ok"
    except Exception as e:
        status["checks"]["database"] = f"error: {str(e)}"
        status["status"] = "unhealthy"
        http_status = 503

    # Check Redis (via cache backend)
    try:
        cache.set("health_check", "ok", 10)
        if cache.get("health_check") == "ok":
            status["checks"]["redis"] = "ok"
        else:
            status["checks"]["redis"] = "error: cache test failed"
            status["status"] = "unhealthy"
            http_status = 503
    except Exception as e:
        status["checks"]["redis"] = f"error: {str(e)}"
        status["status"] = "degraded"
        # Don't fail health check for Redis issues (non-critical)

    return JsonResponse(status, status=http_status)
