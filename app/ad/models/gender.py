from django.db import models
from core.base import BaseModelV2


class Gender(BaseModelV2):

    title = models.CharField(max_length=20)
    doctor = models.ManyToManyField("ad.Doctor", related_name="genders")

    def __str__(self):
        return f"{self.title}"
