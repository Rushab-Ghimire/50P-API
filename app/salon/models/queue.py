from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2
from django.conf import settings

class Queue(BaseModelV2):
    customer = models.ForeignKey(
        "salon.CustomerSalon",
        on_delete = models.SET_NULL,
        null = True
    )
    queue_date_time = models.DateTimeField(auto_now_add=False)
    note = models.TextField(null=True)
    booking = models.ForeignKey(
        'salon.Booking',
        on_delete = models.SET_NULL,
        null = True
    )

    def __str__(self):
        return f"{self.customer.first_name} {self.customer.last_name}"
