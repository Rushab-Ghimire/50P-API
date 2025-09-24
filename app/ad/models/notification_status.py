from django.db import models
from core.base import BaseModel


class NotificationStatus(BaseModel):
    class Meta:
        db_table = "ad_notification_status"

    booking = models.ForeignKey(
        "ad.PatientBooking",
        on_delete=models.CASCADE,
        related_name="notification_status",
    )
    flag_new = models.BooleanField(default=False)
    flag_cancelled = models.BooleanField(default=False)
    flag_confirmed = models.BooleanField(default=False)
    flag_reminder = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}"
