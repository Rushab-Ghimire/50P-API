from django.db import models
from core.base import BaseModelV2


class ChatHistoryCategory(BaseModelV2):

    class Meta:
        db_table = "ad_chat_history_category"

    title = models.TextField()

    def __str__(self):
        return f"{self.title}"
