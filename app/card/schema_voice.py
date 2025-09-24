import graphene
from graphene_django import DjangoObjectType
from django.db import models
from django.conf import settings
import json
import requests

class TokenModel(models.Model):
    session = models.JSONField(blank=True)

    class Meta:
      managed = False
      abstract = True

class TokenModelType(DjangoObjectType):
  class Meta:
    model = TokenModel
    fields = ("__all__")

class Query(graphene.ObjectType):
  rtc_connect = graphene.Field(TokenModelType)

  def resolve_rtc_connect(self, info, **kwargs):

    url = "https://api.openai.com/v1/realtime/sessions"
    data = {
        "model": "gpt-4o-realtime-preview",
        "voice": "verse",
        "turn_detection": {
          "type": "semantic_vad",
          # "threshold": 0.75,
          # "prefix_padding_ms": 300,
          # "silence_duration_ms": 500,
        },
        "input_audio_noise_reduction": {
          "type": "far_field"
        }
    }

    #print(f"Bearer {settings.OPENAI_API_KEY}")
    headers = {
      "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
      "Content-Type": "application/json",
    }

    response = requests.post(url, json = data, headers = headers)
    return TokenModelType(session = response.json())

schema_voice = graphene.Schema(query=Query)
