from django.db import models
from core.base import BaseModel
from django.conf import settings


class ProviderType(models.TextChoices):
    GOOGLE = "google", "Google"


class SocialLogin(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="social_logins"
    )
    provider_id = models.CharField(null=True, max_length=255)
    provider = models.CharField(
        max_length=16, choices=ProviderType.choices, default=None
    )
    profile_image = models.CharField(null=True, max_length=255, default=None)

    def __str__(self):
        return f"{self.unique_id}"
