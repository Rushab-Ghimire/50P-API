"""
URL mappings for the user API.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from .views import (
    OrganizationViewSet
)

router = DefaultRouter()

router.register('organization', OrganizationViewSet)

# app_name = 'authtf'

urlpatterns = [
    path('', include(router.urls)),
]
