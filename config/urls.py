"""Root URL configuration for Morning Cafe."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # REST API (/api/v1/) is added here later.
    path("", include("apps.web.urls")),
]
