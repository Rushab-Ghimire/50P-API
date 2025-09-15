"""
URL mappings for the AD app.
"""

from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from ad import views


router = DefaultRouter()
router.register("ad", views.ADViewSet, basename="ad")
app_name = "ad"

urlpatterns = [
    path("", include(router.urls)),
]
