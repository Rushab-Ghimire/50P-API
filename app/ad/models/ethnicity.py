from django.db import models
from core.base import BaseModelV2

class Ethnicity(BaseModelV2):

    title = models.CharField(max_length=255)
    doctor = models.ManyToManyField("ad.Doctor", related_name="ethnicities")

    def __str__(self):
        return f"{self.title}"
