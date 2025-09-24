from django.db import models
from core.base import BaseModel
from django.utils.text import slugify

class Country(BaseModel):
    name = models.CharField(max_length=255)
    abbr = models.CharField(max_length=5)
    slug = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

    def generate_slug(text):
        original_slug = slug = slugify(text)
        counter = 1
        while Country.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1

        return slug

    def __str__(self):
        return f"{self.name} - {self.abbr}"