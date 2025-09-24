"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from subscription import views

router = DefaultRouter()

app_name = 'subscription'

router.register("", views.SubscriptionView, basename="subscription")

urlpatterns = [
    path('', include(router.urls)),
]
