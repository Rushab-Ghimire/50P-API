from django.db import models
from core.base import BaseModel
from django.utils.text import slugify

class City(BaseModel):
    state = models.ForeignKey('State', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    lat = models.FloatField(null=True, default=None)
    lng = models.FloatField(null=True, default=None)
    is_deleted = models.BooleanField(default=False)

    def generate_slug(text):
        original_slug = slug = slugify(text)
        counter = 1
        while City.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1

        return slug

    def __str__(self):
        return f"{self.name}"