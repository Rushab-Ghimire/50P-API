from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import json
from django.forms.models import model_to_dict
from rest_framework import serializers
from core.base import BaseModel

class Contact(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null = True,
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(blank=True, max_length=255)
    email = models.CharField(max_length=255)
    primary_phone = models.CharField(blank=True, max_length=255)
    primary_address = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    #state table banayera....state_id field add garne

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
