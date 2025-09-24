from django.db import models
from django.conf import settings
from rest_framework import serializers
from core.base import BaseModel

class Entity(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null = True,
        related_name = 'user_id_for_business'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ['id', 'title', 'description', 'is_active']
        read_only_fields = ['id']
