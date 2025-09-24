from django.db import models
from core.base import BaseModel
from rest_framework import serializers

class Subscriber(BaseModel):
    """Newsletter subscribed member."""

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for newsletter subscribed users"""
    class Meta:
        model = Subscriber
        fields = ['name', 'email', "phone_number"]

    def create(self, validated_data):
        """
        Check if the email is already in subscription list.
        If so, check if it is active.
        If it is not active, update to active.
        If email does not exist, create new subscription.
        """
        try:
            subscriber = Subscriber.objects.get(email=validated_data.get("email"))
            if not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save()
            return subscriber
        except Subscriber.DoesNotExist:
            return Subscriber.objects.create(**validated_data)
