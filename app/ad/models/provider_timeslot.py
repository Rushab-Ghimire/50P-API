from django.db import models
from core.base import BaseModelV2


class ProviderTimeslot(BaseModelV2):
    class Meta:
        db_table = "ad_provider_timeslot"

    # combination of availability_date and timeslot is in UTC
    availability_date = models.DateField()
    timeslot = models.TimeField()

    def __str__(self):
        return f"{self.availability_date}"
