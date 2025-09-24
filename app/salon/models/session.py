from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2

class Session(BaseModelV2):
    open_date_time = models.DateTimeField(auto_now_add=False)
    close_date_time = models.DateTimeField(auto_now_add=False)
    pos = models.ForeignKey(
        'salon.Pos',
        on_delete = models.SET_NULL,
        null = True
    )
    beautician = models.ForeignKey(
        'salon.Beautician',
        on_delete = models.SET_NULL,
        null = True
    )
    status = models.ForeignKey(
        'salon.SessionStatus',
        on_delete = models.SET_NULL,
        null = True
    )
    booking = models.ForeignKey(
        'salon.Booking',
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return f"{self.open_date_time}"
