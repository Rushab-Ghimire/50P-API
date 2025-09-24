from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2


class BookingService(BaseModelV2):
    booking = models.ForeignKey("salon.Booking", on_delete=models.SET_NULL, null=True)
    service = models.ForeignKey("salon.Service", on_delete=models.SET_NULL, null=True)
    beautician = models.ForeignKey(
        "salon.Beautician", on_delete=models.SET_NULL, null=True
    )
    unit_price = models.FloatField(default=0.0)
    quantity = models.IntegerField(default=1)
    subtotal = models.FloatField(default=0.0)
    pos_id = models.IntegerField(null=True, default=None)
    status = models.ForeignKey(
        "salon.SessionStatus", on_delete=models.SET_NULL, null=True
    )
    open_date_time = models.DateTimeField(null=True, auto_now_add=False)
    close_date_time = models.DateTimeField(null=True, auto_now_add=False)

    def __str__(self):
        return f"{self.booking.booking_date_time}"
