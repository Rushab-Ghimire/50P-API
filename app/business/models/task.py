from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import json
from django.forms.models import model_to_dict
from rest_framework import serializers
from core.base import BaseModel

class Task(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null = True
    )
    business = models.ForeignKey(
        'business.Entity',
        on_delete = models.SET_NULL,
        null = True
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'is_active']
        read_only_fields = ['id']
