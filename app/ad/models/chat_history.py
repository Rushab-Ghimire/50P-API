from django.db import models
from core.base import BaseModelV2


class ChatHistory(BaseModelV2):

    class Meta:
        db_table = "ad_chat_history"

    content = models.TextField()
    source = models.CharField(max_length=16)  # bot, user
    chat_history_category = models.ForeignKey(
        "ad.ChatHistoryCategory",
        on_delete=models.CASCADE,
        related_name="chat_histories",
        null=True,
        default=None,
    )

    def __str__(self):
        return f"{self.id} - {self.source}"
