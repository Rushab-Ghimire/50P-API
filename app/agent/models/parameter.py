from django.db import models
from core.base import BaseModelV2

class AgentType(models.TextChoices):
    CHAT = "chat", "Chat"
    VOICE = "voice", "Voice"
    CALL = "call", "Call"

class Parameter(BaseModelV2):
    title = models.CharField(null=False, max_length=255)
    description = models.TextField(null=True, default=None)
    agent_type = models.CharField(
        max_length=16, choices=AgentType.choices, default=AgentType.CHAT
    )
    system_message = models.TextField(null=False, default="You are a helpful agent")
    call_connection_message = models.TextField(null=True, default=None)
    call_initial_message = models.TextField(null=True, default=None)

    def __str__(self):
        return f"{self.title}"
