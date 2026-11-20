"""Root URL configuration for Morning Cafe."""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Web pages (step 7) and API (step 6) are added here.
]
