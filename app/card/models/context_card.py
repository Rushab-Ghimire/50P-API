from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import json
from django.forms.models import model_to_dict
from rest_framework import serializers
from core.base import BaseModel

class ContextCard(BaseModel):
    """ContextCard object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null = True
    )
    context = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    parent = models.IntegerField(default=-1)
    graph_attributes = models.TextField(blank=True, default="")
    is_deleted = models.BooleanField(default=False)
    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.SET_NULL,
        null=True,
        default=None,
    )

    def __str__(self):
        return self.title

class ContextCardSerializer(serializers.ModelSerializer):
    """Serializer for ContextCard."""

    class Meta:
        model = ContextCard
        fields = ['id', 'title', 'context', 'description', 'parent']
        read_only_fields = ['id']
