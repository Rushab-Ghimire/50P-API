"""
URL mappings for the Salon app.
"""

from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from salon import views


router = DefaultRouter()
router.register("salon", views.SalonViewSet, basename="salon")
app_name = "salon"

urlpatterns = [
    path("", include(router.urls)),
]
