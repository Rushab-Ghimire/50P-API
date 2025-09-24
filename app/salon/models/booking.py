from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2


class BookingStatus(models.TextChoices):
    NEW = "new", "New"
    COMPLETED = "completed", "Completed"
    CANCELED = "canceled", "Canceled"
    NOSHOW = "noshow", "No show"


class Booking(BaseModelV2):
    booking_date_time = models.DateTimeField(auto_now_add=False)
    checkin_date_time = models.DateTimeField(auto_now_add=False)
    checkout_date_time = models.DateTimeField(auto_now_add=False)
    customer = models.ForeignKey(
        "salon.CustomerSalon",
        on_delete=models.SET_NULL,
        null=True,
        related_name="bookings",
    )
    services = models.ManyToManyField("salon.Service", through="salon.BookingService")
    beauticians = models.ManyToManyField(
        "salon.Beautician", through="salon.BookingService"
    )
    status = models.CharField(
        max_length=16, choices=BookingStatus.choices, default=BookingStatus.NEW
    )

    def __str__(self):
        return f"{self.customer.first_name} {self.booking_date_time}"
