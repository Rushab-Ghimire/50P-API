from django.db import models
from core.base import BaseModelV2
from django.utils.text import slugify

class MedicalTypes(models.TextChoices):
    MEDICAL = "medical", "Medical"
    NON_MEDICAL = "non-medical", "Non-Medical"

class SpecializationCategory(BaseModelV2):

    class Meta:
        db_table = "ad_specialization_category"

    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    medical_type = models.TextField(null=True, default=None, max_length=36)

    def generate_slug(text):
        original_slug = slug = slugify(text)
        counter = 1
        while SpecializationCategory.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1

        return slug

    def __str__(self):
        return f"{self.title}"
