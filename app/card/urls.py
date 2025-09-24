"""
URL mappings for the tileflex app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from card.views import (
    ContextCardViewSet
)

router = DefaultRouter()

#router.register('context-card', ContextCardViewSet)

app_name = 'card'

urlpatterns = [
    path('', include(router.urls)),
]
