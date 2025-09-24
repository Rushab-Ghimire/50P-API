from django.db import models
from django.conf import settings
from core.base import BaseModelV2


class Feedback(BaseModelV2):
    unique_id = models.CharField(max_length=36)
    order = models.ForeignKey(
        "salon.Order", on_delete=models.CASCADE, related_name="feedbacks"
    )
    rating = models.FloatField()
    comment = models.TextField(null=True)

    def get_link(self):
        return f"{settings.SYSTEM_APP_URL}/feedback?code={self.unique_id}"

    def __str__(self):
        return f"{self.unique_id}"
