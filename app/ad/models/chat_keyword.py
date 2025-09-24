from django.db import models
from core.base import BaseModelV2


class ChatKeyword(BaseModelV2):

    class Meta:
        db_table = "ad_chat_keyword"

    keywords = models.JSONField()
    chat_history_category = models.ForeignKey(
        "ad.ChatHistoryCategory",
        on_delete=models.CASCADE,
        related_name="chat_keywords",
        null=True,
        default=None,
    )

    def __str__(self):
        return f"{self.id}"

