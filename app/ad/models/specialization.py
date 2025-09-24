from django.db import models
from core.base import BaseModelV2
from django.utils.text import slugify

class Specialization(BaseModelV2):
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    description = models.TextField(null=True, default=None)
    specialization_category = models.ForeignKey(
        "ad.SpecializationCategory", on_delete=models.SET_NULL, default=None, null=True
    )

    def generate_slug(text):
        original_slug = slug = slugify(text)
        counter = 1
        while Specialization.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1

        return slug

    def __str__(self):
        return f"{self.title}"
