"""
URL mappings for the newsletter API.
"""
from django.urls import (
    path,
    include,
)

from newsletter import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

app_name = 'newsletter'

urlpatterns = [
    path('subscribe/', views.NewsletterSubscriptionView.as_view(), name='newsletter-subscription'),
    path('subscribe/count', views.NewsletterSubscriberCountView.as_view(), name='newsletter-subscriber-count'),
    path('', include(router.urls)),
]
