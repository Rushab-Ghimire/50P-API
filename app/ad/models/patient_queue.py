from django.db import models
from core.base import BaseModelV2
from django.conf import settings

class PatientQueue(BaseModelV2):
    class Meta:
        db_table = "ad_patient_queue"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_queues"
    )
    queue_date_time = models.DateTimeField(auto_now_add=False)
    note = models.TextField(null=True)
    booking = models.ForeignKey(
        'ad.PatientBooking',
        on_delete = models.CASCADE,
        null = True,
        related_name="patient_queues"
    )
    is_rescheduled = models.BooleanField(default=False, null=True)

    def __str__(self):
        return f"{self.customer.first_name} {self.customer.last_name}"
