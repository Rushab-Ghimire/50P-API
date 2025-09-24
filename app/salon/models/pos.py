from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2

class Pos(BaseModelV2):
    title = models.CharField(null=False, default=None, max_length=255)
    entity_type = models.ForeignKey(
        "salon.EntityType",
        on_delete = models.SET_NULL,
        null = True
    )
    floorplan = models.ForeignKey(
        "salon.Floorplan",
        on_delete = models.SET_NULL,
        null = True
    )
    position = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title}"
