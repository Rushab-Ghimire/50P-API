"""
URL mappings for the tileflex app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from .views import (
    #BusinessViewSet,
    TaskViewSet,
)

router = DefaultRouter()

#router.register('task', TaskViewSet)
#router.register('business', BusinessViewSet)

app_name = 'business'

urlpatterns = [
    path('', include(router.urls)),
]
