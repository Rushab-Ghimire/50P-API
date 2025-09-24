"""
URL mappings for the user API.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from authtf.views.role_v import (
    RoleViewSet
)

router = DefaultRouter()

router.register('role', RoleViewSet)

# app_name = 'authtf'

urlpatterns = [
    path('', include(router.urls)),
]
