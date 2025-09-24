from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.forms.models import model_to_dict
from core.base import BaseModel

class Process(BaseModel):
    """Process object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null = True
    )
    title = models.CharField(max_length=255)
    in_params = models.JSONField(blank=True)
    api_endpoint = models.TextField(blank=True)
    out_params = models.JSONField(blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title



class ProcessFlow(BaseModel):
    """ProcessFlow object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null = True
    )
    title = models.CharField(max_length=255)
    specification = models.JSONField(blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title