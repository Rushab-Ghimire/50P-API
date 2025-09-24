"""
URL mappings for the uiservice app.
"""
from django.urls import (
    path,
)

from uiservice import views as uiservice_views

app_name = 'uiservice'

urlpatterns = [
    path('ui/business/', uiservice_views.business),
]
