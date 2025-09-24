from django.db import models
from core.base import BaseModel


class EducationTraining(BaseModel):

    class Meta:
        db_table = "ad_education_training"


    title = models.CharField(max_length=255)
    doctor = models.ForeignKey("ad.Doctor", on_delete=models.CASCADE, related_name="education_trainings")

    def __str__(self):
        return f"{self.title}"
