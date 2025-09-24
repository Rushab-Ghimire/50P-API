from django.db import models
from core.base import BaseModel
from rest_framework import serializers


class Role(BaseModel):
    """User role object."""

    name = models.CharField(max_length=255)
    identifier = models.CharField(max_length=255, unique=True, default=None)

    def __str__(self):
        return self.name


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "identifier"]
        read_only_fields = ["id"]
