from django.db import models
from core.base import BaseModelV2
from django.conf import settings


class PatientBookingStatuses(models.TextChoices):
    NEW = "new", "New"
    UNDER_REVIEW = "under_review", "Under Review"
    CANCELLED = "cancelled", "Cancelled"
    CONFIRMED = "confirmed", "Confirmed"
    NO_SHOW = "no_show", "No Show"
    QUEUED = "queued", "Queued"


class PatientBooking(BaseModelV2):
    class Meta:
        db_table = "ad_patient_booking"

    booking_date_time = models.DateTimeField(auto_now_add=False)
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="patient_bookings",
    )
    insurance_file_uuid = models.CharField(null=True, default=None, max_length=36)
    report_file_uuid = models.CharField(null=True, default=None, max_length=36)
    custom_note = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=16, default="new"
    )  # new, under_review, cancelled, confirmed
    postal_code = models.CharField(max_length=16, null=True, default=None)
    insurance_provider = models.IntegerField(null=True, blank=True, default=None)
    subscription_number = models.TextField(null=True, blank=True, default=None)
    member_id = models.TextField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.user.first_name} for {self.provider.first_name} on {self.booking_date_time}"
