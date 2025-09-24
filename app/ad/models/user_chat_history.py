from django.db import models
from core.base import BaseModelV2
from django.conf import settings


class UserChatHistory(BaseModelV2):

    class Meta:
        db_table = "ad_user_chat_history"

    content = models.TextField()
    content_destination = models.TextField(default=None, null=True)
    destination_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="destination_user_chat_history",
    )
    booking = models.ForeignKey(
        "ad.PatientBooking",
        on_delete=models.CASCADE,
        related_name="booking_id_rel",
        null=True,
        default=None,
    )

    def __str__(self):
        return f"{self.id}"
