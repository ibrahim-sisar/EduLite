# backend/EduLite/urls.py

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from users.jwt_views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
)

urlpatterns = [
    # Basic Built In Django URLs
    path("admin/", admin.site.urls),
    path(
        "api-auth/", include("rest_framework.urls", namespace="rest_framework")
    ),  # For browsable API login/logout
    # JWT Token Endpoints
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    # Our own URLs
    path("api/", include("users.urls")),
    path("api/chat/", include("chat.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name='schema'),
    path("swagger/", SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path("redoc/", SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path("api/", include("courses.urls")),
    path("api/", include("notes.urls")),

]